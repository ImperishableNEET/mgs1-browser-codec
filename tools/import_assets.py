"""Extract selected v24 Codec calls from user-supplied Integral discs. No downloads."""
from pathlib import Path
import argparse, hashlib, json, mmap, os, shutil, struct, subprocess, sys, tempfile
from PIL import Image
import disc
from stage_ranges import ranges

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT/'web/assets'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def inspect(path, number):
    if not path.is_file():raise ValueError(f'Image missing: {path}')
    with path.open('rb') as handle,mmap.mmap(handle.fileno(),0,access=mmap.ACCESS_READ) as image:
        root=disc.root_directory(image)
        extent,size=disc.resolve_iso_file(disc.read_user_bin,image,root,'SYSTEM.CNF')
        cnf=disc.read_file(disc.read_user_bin,image,extent,size)
        serial={1:b'SLPM_862.47',2:b'SLPM_862.48'}[number]
        if serial not in cnf:raise ValueError(f'Disc {number} must be Japanese/Asia Integral {serial.decode()}')
        extent,size=disc.resolve_iso_file(disc.read_user_bin,image,root,'MGS/'+serial.decode())
        executable=hashlib.sha256(disc.read_file(disc.read_user_bin,image,extent,size)).hexdigest()
        expected=json.loads((ROOT/'tools/revisions.json').read_text())[str(number)]
        if executable!=expected['executable_sha256']:raise ValueError(f'Unsupported executable revision on disc {number}')
        resources={}
        for name,expected_hash in expected['resources'].items():
            extent,size=disc.resolve_iso_file(disc.read_user_bin,image,root,name)
            actual=hashlib.sha256(disc.read_file(disc.read_user_bin,image,extent,size)).hexdigest()
            if actual!=expected_hash:raise ValueError(f'Unsupported {name} revision on disc {number}')
            resources[name]=actual
    return dict(disc=number,serial=serial.decode(),image_sha256=sha(path),executable_sha256=executable,resources=resources)

def artwork(image_path):
    with image_path.open('rb') as handle,mmap.mmap(handle.fileno(),0,access=mmap.ACCESS_READ) as image:
        root=disc.root_directory(image)
        extent,size=disc.resolve_iso_file(disc.read_user_bin,image,root,'MGS/STAGE.DIR')
        stage=disc.read_file(disc.read_user_bin,image,extent,size)
    count=struct.unpack_from('<I',stage)[0]//12
    entry=next(i for i in range(count) if stage[4+i*12:12+i*12].split(b'\0')[0]==b'init')
    at=struct.unpack_from('<I',stage,12+entry*12)[0]*2048
    blob=stage[at:at+struct.unpack_from('<H',stage,at+2)[0]*2048]
    items={r['id']:blob[r['start']:r['stop']] for r in ranges(blob) if r['ext']=='r'}
    font=items['0xca68'];end=struct.unpack_from('>I',font)[0]
    atlas=Image.new('RGBA',(192,96));metrics={}
    channels=[0x6739&31,(0x6739>>5)&31,(0x6739>>10)&31]
    colors=[(0,0,0,0)]+[tuple((v*n//3)*8 for v in channels)+(255,) for n in (1,2,3)]
    for code in range(32,128):
        g=struct.unpack_from('>I',font,8+(code-32)*4)[0];w=(g>>24)&15;dy=g>>28
        raw=font[end+(g&0xffffff):];pixels=[(b>>s)&3 for b in raw[:(w*12+3)//4] for s in (6,4,2,0)][:w*12]
        x,y=(code-32)%16*12,(code-32)//16*16
        for j,v in enumerate(pixels):atlas.putpixel((x+j%w,y+j//w+dy),colors[v])
        metrics[str(code)]=dict(x=x,y=y,w=w,advance=w)
    atlas.save(OUT/'font.png');(OUT/'font-metrics.json').write_text(json.dumps(metrics))
    resource=items['0x5d43'];n=resource[0]+resource[1];start=4+n*4
    offsets=[start+struct.unpack_from('<I',resource,4+i*4)[0] for i in range(n)]
    for file,spec in json.loads((ROOT/'tools/artwork.json').read_text()).items():
        i,palette=spec['item'],spec['palette'];pos=offsets[i];_,_,w,h=resource[pos:pos+4]
        clut=struct.unpack_from('<16H',resource,offsets[palette]+4)
        colors=[((c&31)*255//31,((c>>5)&31)*255//31,((c>>10)&31)*255//31,0 if c==0 else 255) for c in clut]
        indices=[v for b in resource[pos+4:pos+4+w*2*h] for v in (b&15,b>>4)]
        im=Image.new('RGBA',(w*4,h));im.putdata([colors[v] for v in indices])
        if spec.get('tint'):im.putdata([(min(255,int(r*46/128)),min(255,int(g*71/128)),min(255,int(b*61/128)),a) for r,g,b,a in im.getdata()])
        im.save(OUT/file)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--disc1',type=Path,required=True,help='Integral Disc 1 raw MODE2/2352 BIN')
    parser.add_argument('--disc2',type=Path,required=True,help='Integral Disc 2 raw MODE2/2352 BIN')
    parser.add_argument('--ffmpeg',default='ffmpeg',help='FFmpeg executable with libmp3lame')
    args=parser.parse_args()
    if OUT.exists():parser.error('web/assets already exists; move it aside before reimporting (no overwrite)')
    ff=shutil.which(args.ffmpeg)
    if not ff:parser.error('FFmpeg not found; supply --ffmpeg PATH')
    paths=[args.disc1.resolve(),args.disc2.resolve()]
    receipts=[inspect(p,i) for i,p in enumerate(paths,1)]
    OUT.mkdir()
    # Save local paths only in ignored generated output; never in the public source.
    config=OUT/'import-config.json';config.write_text(json.dumps(dict(discs=[str(p) for p in paths],ffmpeg=ff)))
    env=dict(os.environ,CODEC_IMPORT_CONFIG=str(config))
    try:
        for script in ('catalog_calls.py','extract_calls.py','augment_portraits.py'):
            subprocess.run([sys.executable,str(ROOT/'tools'/script)],env=env,check=True)
        artwork(paths[0])
        data=json.loads((OUT/'scenes.json').read_text())
        for scene in data['scenes']:
            for block in scene['blocks']:block['audio']='assets/'+block['audio']
        for face in data['faces'].values():
            for q in [*face.get('parts',[]),*[f['image'] for f in face.get('frames',[])]]:
                if q and not q['url'].startswith('assets/'):q['url']='assets/'+q['url']
        (OUT/'scenes.json').write_text(json.dumps(data),encoding='utf-8')
        (OUT/'import-manifest.json').write_text(json.dumps(dict(discs=receipts,files={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}),indent=2))
        print('Imported locally into',OUT)
    except Exception:
        print('Import incomplete; generated output preserved for diagnosis. Move web/assets aside before retrying.',file=sys.stderr)
        raise

if __name__=='__main__':main()
