from pathlib import Path
import struct,json,re,mmap,importlib.util,sys,subprocess,hashlib,difflib
from PIL import Image
from codec_config import P, O, m, ff
A=O/'media';A.mkdir(exist_ok=True)
catalog=json.loads((O/'catalog.json').read_text());bypos={(r['disc'],r['offset']):r for r in catalog}
specs=[('intro','First contact & introductions',1,[647199,653343,653456,653567,653838,659502,659628]),('mei','Mei Ling — Without content',1,[161825]),('deep','An unidentified caller',1,[4362261,4362420]),('meryl','Meryl — First contact',1,[32789,38648]),('naomi','Naomi — Difficult questions',2,[872479,874055,875238,876043,876521,877500]),('box','Nastasha — The cardboard box',1,[2921875]),('master','A change on the frequency',2,[886825,888087]),('secdef','A new voice in command',2,[901151,903578]),('otacon','Otacon — Elevator warning',1,[790559]),('wolf','A voice in the storm',1,[796750])]
specs.append(('ravens','Miller — Northern Ravens',2,[1164944,1165122,1167555]))
specs=[(s,t,d,([32789,33277,33380,33916,34107,34775,36756,38648,40114] if s=='meryl' else p)) for s,t,d,p in specs]
def clean(raw):
 raw=raw.split(b'\0')[0].replace(b'\x80#\x80N',b'\n').replace(b'\x80"',b'"')
 return re.sub(b'\x80.',b'',raw).decode('ascii',errors='replace')
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
faces={};allscenes=[];receipts=[]
for slug,title,dn,positions in specs:
 info=json.loads((O/f'disc-{dn}.json').read_text());radio=(O/f'radio-{dn}.bin').read_bytes()
 with open(info['disc'],'rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as disc:
  pvd=m.read_user_bin(disc,16);root=m.parse_directory_entries(m.read_file(m.read_user_bin,disc,struct.unpack_from('<I',pvd,158)[0],struct.unpack_from('<I',pvd,166)[0]));ex,sz=m.resolve_iso_file(m.read_user_bin,disc,root,'MGS/FACE.DAT');face=m.read_file(m.read_user_bin,disc,ex,sz)
  headers=[]
  for h in range(0,len(radio)-8,2048):
   freq=int.from_bytes(radio[h:h+2],'big');v=int.from_bytes(radio[h+2:h+6],'big');start=(v&0xffffff)*2048;length=(v>>24)*2048
   if 14000<=freq<=14300 and length and start+length<=len(face):headers.append((h,freq,start,length))
  blocks=[]
  for pos in positions:
   row=bypos[dn,pos];vox=row['vox'];assert 0<vox<info['vox_size']//2048
   head=max((h for h in headers if h[0]<=pos),key=lambda h:h[0]);_,freq,gstart,glen=head
   n=struct.unpack_from('<I',face,gstart)[0];assert 0<n<200
   group={}
   for i in range(n):
    kind,ident,size,rel=struct.unpack_from('<HHII',face,gstart+4+i*12);group[ident]=(kind,gstart+4+rel,size)
   talks=[];initial=[]
   # A one-sided advice call may contain no Snake TALK at all. Retain the
   # enclosing fragment's first explicit Snake ANIM declaration as its initial portrait.
   prefix=radio[head[0]+8:pos]
   for hit in re.finditer(b'\xff\x03\x00\x08',prefix):
    p=hit.start();char,ident,extra=struct.unpack_from('>HHH',prefix,p+4)
    if char==0x21ca and ident in group:
     initial.append(dict(character=char,face=f'{dn}-{gstart:x}-{ident:04x}',text='',extra=extra,source_offset=head[0]+8+p));break
   part=radio[pos+8:row['end']]
   for hit in re.finditer(b'\xff\x01',part):
    p=hit.start();length=int.from_bytes(part[p+2:p+4],'big')
    if length<9 or p+2+length>len(part):continue
    char,ident,extra=struct.unpack_from('>HHH',part,p+4);text=clean(part[p+10:p+2+length]);key=f'{dn}-{gstart:x}-{ident:04x}'
    talks.append(dict(character=char,face=key,text=text,extra=extra))
   for declaration in talks+initial:
    key=declaration['face'];ident=int(key.rsplit('-',1)[1],16)
    if key in faces:continue
    if ident==0:faces[key]=dict(kind='hidden',parts=[]);continue
    if ident not in group:faces[key]=dict(kind='missing',parts=[]);continue
    kind,base,size=group[ident];parts=[]
    def image(paloff,imgOff,name):
     if not imgOff:return None
     x,y,w,h=face[base+imgOff:base+imgOff+4];assert w*h and base+imgOff+4+w*h<=base+size
     colors=struct.unpack_from('<256H',face,base+paloff);rgb=[((v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3) for v in colors]
     im=Image.new('RGB',(w,h));im.putdata([rgb[b] for b in face[base+imgOff+4:base+imgOff+4+w*h]]);im.save(A/name)
     return dict(url='media/'+name,x=x,y=y,w=w,h=h)
    if kind==0:
     offs=struct.unpack_from('<8I',face,base)
     for j,k in enumerate([1,2,3,5,6]):parts.append(image(offs[0],offs[k],f'{key}-{j}.png'))
     faces[key]=dict(kind='simple',parts=parts)
    else:
     # Preserve full frame metadata; first-image fallback is explicitly labelled.
     count=struct.unpack_from('<I',face,base)[0];full=[];lastpal=0
     for j in range(count):
      pal,img,a,b=struct.unpack_from('<IIhh',face,base+4+12*j)
      if pal:lastpal=pal
      full.append(dict(image=image(lastpal,img,f'{key}-full-{j}.png') if img and lastpal else None,a=a,b=b))
     faces[key]=dict(kind='full',frames=full,parts=[next((q['image'] for q in full if q['image']),None)])
   # Lazy cooked-sector reader, preserving complete stream chunks until declared audio size.
   buf=bytearray();at=0;parts=[];caps=[];wavebytes=None;rate=None;records=[]
   def ensure(end):
    while len(buf)<end:
     assert len(buf)<32*1024*1024
     buf.extend(m.read_user_bin(disc,info['vox_extent']+vox+len(buf)//2048))
   total=0
   while wavebytes is None or total<wavebytes:
    ensure(at+4);tag=int.from_bytes(buf[at:at+4],'little');kind=tag&255;size=tag>>8
    assert 4<=size<=1024*1024,(slug,vox,at,kind,size)
    ensure(at+size);payload=bytes(buf[at+4:at+size]);records.append([at,kind,size])
    if kind==2:
     wavebytes=int.from_bytes(payload[:4],'big');pitch=int.from_bytes(payload[6:8],'big');rate=44100*pitch//4096;channels=1 if payload[8]==1 else 2;assert wavebytes>0
    if kind==1:parts.append(payload);total+=len(payload)
    if kind==6:caps.append(payload)
    at+=size
   raw=b''.join(parts)[:wavebytes];name=f'{dn}-{vox}';vags=[]
   for ch in range(channels):
    channelraw=raw if channels==1 else b''.join(raw[i:i+4096] for i in range(ch*4096,len(raw),8192))
    vag=A/(name+f'-{ch}.vag');vag.write_bytes(b'VAGp'+struct.pack('>III',32,0,len(channelraw))+struct.pack('>I',rate)+bytes(28)+channelraw);vags.append(vag)
   args=[ff,'-y','-v','error']
   for vag in vags:args+=['-i',str(vag)]
   if channels==2:args+=['-filter_complex','[1:a][0:a]amerge=inputs=2[a]','-map','[a]']
   subprocess.run(args+['-c:a','libmp3lame','-b:a','96k',str(A/(name+'.mp3'))],check=True)
   subtitles=[];cueblocks=[]
   for cap in caps:
    start,end,lip,sub,font=struct.unpack_from('<IIHHI',cap);assert 16<=lip<=sub<=font<=len(cap)
    cueblocks.append(dict(start=start,end=end,bytes=list(cap[lip:sub])))
    q=sub
    while q+16<=font:
     size,t,dur,other=struct.unpack_from('<IIII',cap,q)
     if size==0:size=font-q
     if size<16 or q+size>font:break
     text=clean(cap[q+16:q+size]);subtitles.append(dict(start=t,duration=dur,text=text));q+=size
   # Match source dialogue text to original caption entries; never infer a speaker from a name list.
   assert len(subtitles)==len(talks),(slug,vox,'caption/script count mismatch')
   unmatched=[]
   for sub,talk in zip(subtitles,talks):
    if norm(sub['text'])!=norm(talk['text']):unmatched.append(dict(stream=sub['text'],radio=talk['text']))
    sub.update(extra=talk['extra'],character=talk['character'],face=talk['face'],streamText=sub['text'],text=talk['text'] or sub['text'],mapping='ordinal; counts equal; RADIO display text')
   block=dict(disc=dn,radio_offset=pos,vox=vox,frequency=freq,audio='media/'+name+'.mp3',subtitles=subtitles,cues=cueblocks,talks=talks,initial=initial,seconds=len(raw)//16*28/rate/channels)
   blocks.append(block);receipts.append(dict(scene=slug,offset=pos,vox=vox,group=head,records=records,audio_bytes=len(raw),rate=rate,unmatched=unmatched,radio_sha256=hashlib.sha256(radio[pos:row['end']]).hexdigest(),audio_sha256=hashlib.sha256(raw).hexdigest()))
   print(slug,vox,round(block['seconds'],1),'subtitles',len(subtitles),'talks',len(talks),'unmatched',len(unmatched),flush=True)
  allscenes.append(dict(id=slug,title=f"{blocks[0]['frequency']/100:.2f} — {title}",blocks=blocks))
allscenes.sort(key=lambda s: ['intro', 'mei', 'meryl', 'box', 'deep', 'otacon', 'wolf', 'ravens', 'naomi', 'master', 'secdef'].index(s['id']))
(O/'scenes.json').write_text(json.dumps(dict(scenes=allscenes,faces=faces,counterHz=44100/448/4),indent=2))
(O/'extraction-receipts.json').write_text(json.dumps(receipts,indent=2))
