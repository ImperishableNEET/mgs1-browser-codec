from pathlib import Path
import os, json
import disc as m
P = Path(__file__).resolve().parent.parent
O = P/'web/assets'
config = json.loads(Path(os.environ['CODEC_IMPORT_CONFIG']).read_text(encoding='utf-8'))
discs = [Path(x) for x in config['discs']]
ff = config['ffmpeg']
