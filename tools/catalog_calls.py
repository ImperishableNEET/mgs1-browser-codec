from pathlib import Path
import importlib.util,sys,struct,mmap,re,json
from codec_config import P, O, m, discs
O.mkdir(exist_ok=True)
allrows=[]
for dn,disc in enumerate(discs,1):
 with disc.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as d:
  pvd=m.read_user_bin(d,16);root=m.parse_directory_entries(m.read_file(m.read_user_bin,d,struct.unpack_from('<I',pvd,158)[0],struct.unpack_from('<I',pvd,166)[0]));ex,sz=m.resolve_iso_file(m.read_user_bin,d,root,'MGS/RADIO.DAT');radio=m.read_file(m.read_user_bin,d,ex,sz);(O/f'radio-{dn}.bin').write_bytes(radio)
  ex,sz=m.resolve_iso_file(m.read_user_bin,d,root,'MGS/VOX.DAT');(O/f'disc-{dn}.json').write_text(json.dumps(dict(disc=str(disc),vox_extent=ex,vox_size=sz)))
 for match in re.finditer(b'\xff\x02',radio):
  pos=match.start();size=int.from_bytes(radio[pos+2:pos+4],'big');end=pos+2+size
  if size<12 or end>len(radio):continue
  part=radio[pos+8:end]
  texts=[];faces=[]
  for q in re.finditer(b'\xff\x01',part):
   a=q.start();n=int.from_bytes(part[a+2:a+4],'big');raw=part[a+10:a+2+n].split(b'\0')[0]
   raw=raw.replace(b'\x80#\x80N',b' ').replace(b'\x80"',b'"');raw=re.sub(b'\x80.',b'',raw)
   if n>=9 and raw and all(32<=c<127 or c in (10,13) for c in raw):
    texts.append(raw.decode('ascii'));faces.append([int.from_bytes(part[a+4:a+6],'big'),int.from_bytes(part[a+6:a+8],'big')])
  if texts:allrows.append(dict(disc=dn,offset=pos,end=end,vox=int.from_bytes(radio[pos+4:pos+8],'big'),text=' | '.join(texts),faces=faces))
(O/'catalog.json').write_text(json.dumps(allrows,indent=2))
