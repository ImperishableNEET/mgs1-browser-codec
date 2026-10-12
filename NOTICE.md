# Attribution and source scope

- Original Metal Gear Solid / Integral game, dialogue, graphics and audio: Konami and original creators. These assets are supplied locally by the user, not included in the repository.
- Recovered game routines: [FoxdieTeam/mgs_reversing](https://github.com/FoxdieTeam/mgs_reversing). `src/recovered_frame.inc` and `src/recovered_animation.inc` derive from `source/menu/radiofacedraw.c`; `src/recovered_panel.inc` and `src/recovered_meter.inc` derive from `source/menu/radio.c`; `src/recovered_voice_cues.inc` derives from `source/game/jimctrl.c`. `src/codec_calls.c` contains adaptation glue and game-derived structures/tables. These are not claimed as independently authored implementations.
- FACE format investigation consulted [metalgeardev/MGS1](https://github.com/metalgeardev/MGS1), including `unFace_v1.1.rb`. The decoder is Python code adapted from the existing side project's extraction scripts, not a bundled copy of that Ruby utility.
- Browser presentation, extraction integration and fixtures: ImperishableNEET / Torment Nexus LLC, 2026, developed with AI assistance through Codex.
- FFmpeg, Pillow and Zig are external tools installed separately; they are not bundled here. Their own terms apply.

The exact recovered-source checkout revision and source hashes used in the preparation are recorded in `tools/source-provenance.json`. No repository-wide licence grant was found in the inspected FoxdieTeam tree. Availability on GitHub does not establish public-domain status. Recovered code and original game rights remain outside any licence offered for independently authored additions.

No relationship with or endorsement by Konami is claimed. The extractor does not provide game images or download links.
