from pathlib import Path
import argparse, shutil, subprocess, os
root=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description='Compile recovered Codec routines; Zig 0.14.1 tested.')
p.add_argument('--zig',default='zig')
p.add_argument('--native-fixture',action='store_true',help='Also compile host cue comparison fixture')
a=p.parse_args()
zig=shutil.which(a.zig)
if not zig:p.error('Zig not found; supply --zig PATH')
exports=['meter_reset','meter_step','meter_draw','frame_generate','frame_word','anim_step','anim_layer','anim_reset','panel_generate','panel_word','panel_active','voice_byte','voice_reset','voice_tick','voice_pose','voice_begin']
command=[zig,'cc','-target','wasm32-freestanding','-funsigned-char','-O2','-nostdlib',str(root/'src/codec_calls.c'),'-Wl,--no-entry']+[f'-Wl,--export={x}' for x in exports]+['-o',str(root/'web/codec.wasm')]
subprocess.run(command,check=True)
print('Built',root/'web/codec.wasm')
if a.native_fixture:
    (root/'.local').mkdir(exist_ok=True)
    output=root/'.local'/('calls-fixture.exe' if os.name=='nt' else 'calls-fixture')
    subprocess.run([zig,'cc','-funsigned-char','-O2',str(root/'tests/calls-fixture.c'),'-o',str(output)],check=True)
