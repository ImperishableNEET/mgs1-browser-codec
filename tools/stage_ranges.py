import struct
def ranges(blob):
 assert blob[0]==1 and len(blob)==struct.unpack_from('<H',blob,2)[0]*2048
 tags=[]
 for pos in range(4,2048,8):
  ident,mode,ext,size=struct.unpack_from('<HBBI',blob,pos)
  if mode==0:break
  tags.append({'id':hex(ident),'mode':chr(mode),'ext':chr(ext) if ext<127 else ext,'size':size})
 else:raise AssertionError('No tag terminator')
 result=[];offset=2048;i=0
 while i<len(tags):
  tag=tags[i];mode=tag['mode']
  if mode=='c':
   group=[]
   while i<len(tags) and tags[i]['mode']=='c':group.append(tags[i]);i+=1
   assert group[-1]['ext']==255;size=group[-1]['size'];assert group[0]['size']==0
   for a,b in zip(group,group[1:]):
    assert a['size']<=b['size']<=size;result.append(dict(a,start=offset+a['size'],stop=offset+b['size']))
  else:
   assert mode in ('s','n','r');size=tag['size'];assert size>0
   if mode in ('n','r'):
    pos=offset
    while pos<offset+size:
     ident,ext,length=struct.unpack_from('<HHI',blob,pos);assert length>0 and pos+8+length<=offset+size;result.append({'id':hex(ident),'mode':mode,'ext':chr(ext),'start':pos+8,'stop':pos+8+length});pos+=8+length
    assert pos==offset+size
   else:result.append(dict(tag,start=offset,stop=offset+size))
   i+=1
  offset+=((size+2047)//2048)*2048;assert offset<=len(blob)
 assert offset==len(blob),('Unexpected extra stage sectors',offset,len(blob))
 return result
