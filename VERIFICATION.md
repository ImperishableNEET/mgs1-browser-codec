# Repository preparation — 2026-10-12

Verified on Windows x86-64, Python 3.12.14, Pillow 12.3.0, Zig 0.14.1 and Node 23.5.0. The requirements pin is Pillow 12.3.0 to match the actual environment.

- Both real local Integral images passed serial, executable and resource-hash checks.
- End-to-end import regenerated eleven selections, 35 voice blocks, 549 captions and 114 portrait events. Scene payloads match the existing v24 data after normalizing the intentionally changed URL prefixes.
- Re-extracted frame, font and tinted label PNGs match the v24 artwork byte-for-byte.
- WebAssembly built from source. Its binary hash differs from the prior artifact, so byte identity is not claimed. Native/WASM cue differential checks passed: 69 cases, 89,021 poses, 29,244 nonzero poses.
- Existing portrait checks reach all 37 image-bearing full-sequence records. Static palette, held-frame stability and next-frame animation checks passed.
- Five Python checks passed for ISO bounds/modes, missing paths and source-package exclusion rules.
- In-app browser loaded all eleven selections, started the first call, advanced the audio clock and displayed its first subtitle. No warning/error console entries were observed at readiness. This is a short startup smoke, not an exhaustive replay of all calls or a human listening review.

Reproduction commands are in README.md. Original v24 files, Netlify deployment, main port, discs and saves were left unchanged. The importer writes only ignored output in this separate repository.

Unsupported paths: alternate game/resource revisions, CUE/multitrack offset interpretation, cooked ISO and CHD. Exact audiovisual/reference equivalence remains unverified. Prior demo timing/composition approximations remain.

GitHub publication is pending: this session cannot access the user's Firefox login, and no authenticated GitHub CLI/connector was available. Prepared owner/name: `ImperishableNEET/mgs1-browser-codec`. Source licence scope is documented without assigning rights over recovered game code.
