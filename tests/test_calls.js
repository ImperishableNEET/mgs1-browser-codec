const fs=require('fs'),cp=require('child_process'),path=require('path'),assert=require('assert');
(async()=>{const dir='web/assets',data=JSON.parse(fs.readFileSync(dir+'/scenes.json'));
 const e=(await WebAssembly.instantiate(fs.readFileSync('web/codec.wasm'))).instance.exports;
 let tests=0,frames=0,events=0,results=[];
 for(const s of data.scenes.filter(s=>!process.argv[2]||s.id===process.argv[2]))for(const b of s.blocks)for(let k=0;k<b.cues.length;k++){
  const c=b.cues[k],stop=Math.min(b.cues[k+1]?.start??100000,Math.ceil(b.seconds*data.counterHz));
  const file=path.resolve(dir+'/test-cues.bin');fs.writeFileSync(file,Buffer.from(c.bytes));
  for(const id of [...new Set(b.talks.map(t=>t.character))]){
   const native=cp.execFileSync(path.resolve('.local',process.platform==='win32'?'calls-fixture.exe':'calls-fixture'),[file,''+c.start,''+stop,''+id]);
   e.voice_begin(c.start);c.bytes.forEach((v,i)=>e.voice_byte(i,v));const out=Buffer.alloc((stop-c.start+1)*2);let nonzero=0;
   for(let t=c.start;t<=stop;t++){e.voice_tick(t);let v=e.voice_pose(id);out.writeUInt16LE(v,(t-c.start)*2);if(v)nonzero++;}
   assert(native.equals(out),`${s.id}/${b.vox}/${id} native-WASM mismatch`);tests++;frames+=stop-c.start+1;events+=nonzero;results.push({scene:s.id,vox:b.vox,character:id,nonzero});
  }
 }
 assert(events>0);const report={pass:true,tests,frames,events,scope:'Recovered cue interpreter native versus WASM; not audio alignment or original emulator equivalence',results};fs.writeFileSync(dir+(process.argv[2]?'/cue-runtime-tests-'+process.argv[2]+'.json':'/cue-runtime-tests.json'),JSON.stringify(report,null,2));console.log({tests,frames,events});
})();
