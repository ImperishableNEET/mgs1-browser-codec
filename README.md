# MGS1 Browser Codec

An experimental standalone browser Codec demo from PlayStation **Metal Gear Solid Integral**. Recovered C routines execute in WebAssembly; JavaScript/Canvas provide presentation, audio playback and approximate scheduling.

This is the source/local-import edition of the v24 demo published at https://mgs1-browser-codec.netlify.app/. That hosted demo embeds assets; **this repository does not include voices, dialogue scripts, portraits, fonts, disc images, BIOS or saves**. The hosted demo is not an asset source for this importer.

## Run locally

Requirements: Python 3.12 (tested), Pillow, FFmpeg with `libmp3lame`, Zig 0.14.1 (tested), and your own Integral **Disc 1 and Disc 2** raw MODE2/2352 BIN images. No BIOS is needed. Windows was tested; other hosts are not yet verified.

```sh
python -m pip install -r requirements.txt
python tools/import_assets.py --disc1 "PATH/Integral Disc 1.bin" --disc2 "PATH/Integral Disc 2.bin" --ffmpeg "PATH/ffmpeg"
python tools/build_wasm.py --zig "PATH/zig"
python -m http.server 8769 --bind 127.0.0.1 --directory web
```

Open http://127.0.0.1:8769/. Select a call and press **Play / restart call**. Major spoiler selections are marked with an asterisk. Serve over HTTP; opening the HTML directly is unsupported.

The importer reads images without modifying them and does not download content. It verifies Integral serials `SLPM_862.47` / `SLPM_862.48` plus pinned executable/resource SHA-256 hashes before decoding. Similarly named regional/revised discs are not assumed compatible. Current support is the tested Japanese/Asia Integral English-resource revision only. CUE parsing, ISO, CHD and multi-track offset translation are unsupported; provide the matching raw BIN files.

Generated output lives in ignored `web/assets/`, including a local import manifest, hashes and extraction receipts. Existing output is never overwritten. Move that directory aside before another import. Failed imports retain partial output for diagnosis. Do not upload generated output or original discs. Asset offsets and revision hashes in source are metadata, not asset payloads.

## What it demonstrates

- Eleven selected calls, 35 voice blocks, 549 captions.
- Recovered frame geometry, simple portrait animation, cue interpretation and panel/meter routines compiled as C to WebAssembly.
- Selected full portrait sequences, voice playback, selectable text and optional CRT presentation effects.

This is **not** the complete radio VM, an emulator, a whole-game browser port or native-runtime coverage. MP3 is a local derivative of original ADPCM; original SPU mixing/reverb/ambient audio is absent. Portrait scheduling, fades, scan effects and noise are approximations. Conditional scripts, interruptions, call opening/closing and sound-only sequence records are incomplete. Ordinal RADIO/VOX text pairing is supported only for the selected blocks. Later calls contain major spoilers. Audiovisual timing and transitions have not been established equivalent to reference gameplay.

## Checks

After import/build:

```sh
python -m unittest discover -s tests -p "test_*.py"
python tools/build_wasm.py --zig "PATH/zig" --native-fixture
node tests/test_portraits.js
node tests/test_static.js
node tests/test_calls.js
```

Python checks cover ISO-reader boundaries and the source-only package policy. JavaScript checks cover extracted portrait reachability and selected runtime functions; they require Node. These are internal consistency checks, not proof of original-console equivalence. See `VERIFICATION.md` for this preparation's actual results.

## Provenance and licensing

See `NOTICE.md` and `LICENSE.md` **before redistributing**. Recovered routines are from FoxdieTeam's MGS reversing project and are separately identified. No blanket licence is asserted over recovered game/SDK code or Konami assets. The main Reintegrated port and RE:INTEGRAL are separate projects; this browser demo does not use RE:INTEGRAL/PsyZ as its execution runtime.

Repository preparation leaves the original v24 demo, hosted site and main port unchanged.
