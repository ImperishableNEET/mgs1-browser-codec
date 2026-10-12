from pathlib import Path
import json,struct,mmap,importlib.util,sys,re
from PIL import Image
from codec_config import P, O, m
d=json.loads((O/'scenes.json').read_text());receipts=[]
for dn in (1,2):
 info=json.loads((O/f'disc-{dn}.json').read_text());radio=(O/f'radio-{dn}.bin').read_bytes()
 with open(info['disc'],'rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as disc:
  pvd=m.read_user_bin(disc,16);root=m.parse_directory_entries(m.read_file(m.read_user_bin,disc,struct.unpack_from('<I',pvd,158)[0],struct.unpack_from('<I',pvd,166)[0]));ex,sz=m.resolve_iso_file(m.read_user_bin,disc,root,'MGS/FACE.DAT');face=m.read_file(m.read_user_bin,disc,ex,sz)
 for scene in d['scenes']:
  carried={}
  for block in scene['blocks']:
   if block['disc']!=dn:continue
   pos=block['radio_offset'];end=pos+2+int.from_bytes(radio[pos+2:pos+4],'big');key=block['talks'][0]['face'];group=int(key.split('-')[1],16);n=struct.unpack_from('<I',face,group)[0];entries={}
   for i in range(n):
    kind,ident,size,rel=struct.unpack_from('<HHII',face,group+4+i*12);entries[ident]=(kind,group+4+rel,size)
   # Explicit contiguous ANIM declarations immediately before this VOX initialize both sides.
   at=pos-10;startup=[]
   while at>=0 and radio[at:at+4]==b'\xff\x03\x00\x08':
    char,ident,extra=struct.unpack_from('>HHH',radio,at+4);key=f'{dn}-{group:x}-{ident:04x}'
    if key in d['faces']:startup.append(dict(character=char,face=key,text='',extra=extra,source_offset=at))
    at-=10
   if startup:
    chars={t['character'] for t in startup};block['initial']=[t for t in block['initial'] if t['character'] not in chars]+list(reversed(startup))
   # A selected VOX may contain only one side's dialogue; preserve the other slot.
   present={int(t['character']==0x21ca) for t in block['initial']}
   for side,state in carried.items():
    if side not in present:block['initial'].append(dict(state,text='',extra=0,provenance='previous selected voice block terminal portrait'))
   events=[];pending=[];talkIndex=0
   for hit in re.finditer(b'\xff[\x01\x03]',radio[pos+8:end]):
    at=pos+8+hit.start();length=int.from_bytes(radio[at+2:at+4],'big')
    if length<8 or at+2+length>end:continue
    if radio[at+1]==1:
     if talkIndex>=len(block['subtitles']):break
     boundary=block['subtitles'][talkIndex]['start']/d['counterHz'];total=sum(x['duration'] for x in pending);cursor=max(0,boundary-total)
     for event in pending:event['seconds']=cursor;cursor+=event['duration'];events.append(event)
     pending=[];talkIndex+=1;continue
    char,ident,extra=struct.unpack_from('>HHH',radio,at+4);key=f'{dn}-{group:x}-{ident:04x}'
    if ident==0:
     d['faces'][key]=dict(kind='hidden',parts=[]);pending.append(dict(character=char,face=key,extra=extra,source_offset=at,duration=max(1,extra)/30,timing='explicit code-zero static; caption-anchor phase unverified'));continue
    if ident not in entries:continue
    kind,base,size=entries[ident]
    if key not in d['faces']:
     def image(pal,img,j):
      if not img:return None
      x,y,w,h=struct.unpack_from('<bbBB',face,base+img);assert base+img+4+w*h<=base+size
      colors=struct.unpack_from('<256H',face,base+pal);rgb=[((v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3) for v in colors];im=Image.new('RGB',(w,h));im.putdata([rgb[c] for c in face[base+img+4:base+img+4+w*h]]);name=f'{key}-event-{j}.png';im.save(O/'media'/name);return dict(url='media/'+name,x=x,y=y,w=w,h=h)
     if kind==0:
      offsets=struct.unpack_from('<8I',face,base);parts=[image(offsets[0],offsets[k],j) for j,k in enumerate([1,2,3,5,6])];d['faces'][key]=dict(kind='simple',parts=parts)
     else:
      count=struct.unpack_from('<I',face,base)[0];assert count<2048;frames=[];pal=0
      for j in range(count):
       paloff,img,a,b=struct.unpack_from('<IIhh',face,base+4+j*12)
       if paloff:pal=paloff
       frames.append(dict(image=image(pal,img,j) if img and pal else None,palette=bool(paloff),imagePresent=bool(img),a=a,b=b))
      d['faces'][key]=dict(kind='full',frames=frames,parts=[])
    anim=d['faces'][key];duration=max(1,extra if extra<257 else extra-256)/30
    if anim['kind']=='full':duration=sum(max(0,q['a'])+max(0,q['b'])+1 for q in anim['frames'] if q['image'])/30
    event=dict(character=char,face=key,extra=extra,source_offset=at,duration=duration,timing='preceding next ordinal stream caption; source frame holds; phase unverified');pending.append(event)
   cursor=block['seconds']-sum(x['duration'] for x in pending)
   for event in pending:event['seconds']=max(0,cursor);cursor+=event['duration'];events.append(event)
   block['portraitEvents']=events
   for state in block['initial']:carried[int(state['character']==0x21ca)]={k:state[k] for k in ('character','face')}
   for hit in re.finditer(b'\xff[\x01\x03]',radio[pos+8:end]):
    at=pos+8+hit.start();length=int.from_bytes(radio[at+2:at+4],'big')
    if length<8 or at+2+length>end:continue
    char,ident,extra=struct.unpack_from('>HHH',radio,at+4);key=f'{dn}-{group:x}-{ident:04x}'
    if key in d['faces']:carried[int(char==0x21ca)]=dict(character=char,face=key)
   receipts.append(dict(scene=scene['id'],vox=block['vox'],events=events))
(O/'scenes.json').write_text(json.dumps(d,indent=2));(O/'portrait-event-receipts.json').write_text(json.dumps(receipts,indent=2))
print('Events',sum(len(x['events']) for x in receipts),'Full sequences',[(k,len(v['frames'])) for k,v in d['faces'].items() if v['kind']=='full'])
