"""Create an allowlisted source archive, excluding locally imported retail payloads."""
from pathlib import Path
import argparse, zipfile, re
root=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('output',type=Path);args=p.parse_args()
files=[root/name for name in ['README.md','NOTICE.md','LICENSE.md','VERIFICATION.md','requirements.txt','.gitignore','web/index.html']]
for directory,extensions in [('src',{'.c','.inc'}),('tools',{'.py','.json'}),('tests',{'.py','.js','.c'})]:
    files.extend(f for f in (root/directory).iterdir() if f.is_file() and f.suffix in extensions)
for f in files:
    content=f.read_text(encoding='utf-8')
    if re.search(r'data:[^\s;]+;base64,[A-Za-z0-9+/=]{100,}',content) or re.search(r'C:[/\\]Users[/\\][A-Za-z0-9]',content):
        raise ValueError(f'Embedded payload/private path in {f.relative_to(root)}')
args.output.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(args.output,'x',compression=zipfile.ZIP_DEFLATED) as archive:
    for f in sorted(files):archive.write(f,Path('mgs1-browser-codec')/f.relative_to(root))
print(f'{len(files)} source files; no generated assets: {args.output.resolve()}')
