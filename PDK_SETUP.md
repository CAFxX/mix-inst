# Sky130 PDK + RTL-to-GDS toolchain — setup notes (2026-10-01)

Source with everything: `source ~/tools/sky130-env.sh`
Wrappers (set LD_LIBRARY_PATH + QT_QPA_PLATFORM=offscreen): `~/tools/sky130bin/openroad`, `~/tools/sky130bin/sta`

## Tool versions (all smoke-tested)
- OpenROAD v2.0-17598-ga008522d8 (Precision Innovations prebuilt .deb for Ubuntu 22.04,
  extracted with dpkg-deb — no apt used)
- OpenSTA 2.6.0 (the `sta` binary bundled in the OpenROAD .deb)
- Yosys 0.69 (conda-forge, micromamba env `sky130`)

## PDK
- Version: volare `c6d73a35f524070e85faff4a6a9eef49553ebc2b`, variant sky130A
- Root: /home/hatch/.volare/volare/sky130/versions/c6d73a35f524070e85faff4a6a9eef49553ebc2b/sky130A
- Liberty (tt_100C_1v80): $PDK_ROOT/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_100C_1v80.lib
- Tech LEF:               $PDK_ROOT/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef
- Std-cell LEF:            $PDK_ROOT/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef
- Primitives LEF:          $PDK_ROOT/libs.ref/sky130_fd_pr/lef/sky130_fd_pr.lef

## Functional smoke tests passed
1. `openroad -no_splash -exit` reading liberty + techlef + both LEFs: 428 lib cells, 14 layers/25 vias.
2. Yosys synth of a 4-bit XOR mapped with dfflibmap+abc against the real liberty: 4x sky130_fd_sc_hd__xor2_1.

## Quirks / workarounds
- `openroad`/`sta` need LD_LIBRARY_PATH=$HOME/tools/syslibs/usr/lib/x86_64-linux-gnu:$HOME/tools/openroad/opt/or-tools/lib
  (Ubuntu 22.04 Qt5/Python3.10/tclreadline/icu/md4c debs extracted via dpkg-deb; libdouble-conversion.so.3 from conda-forge).
- volare crashes on this VM's `no_proxy` (bracketed IPv6 breaks its httpx): run as
  `env -u no_proxy -u NO_PROXY ~/tools/volare-venv/bin/volare ...`
- `volare enable` alone does not download; must `volare fetch` first. NOTE: the first
  `enable` attempt actually tried to download but died with `[Errno 28] No space left on device`
  at 73% of sky130_fd_sc_hd.tar.zst; the subsequent `fetch` retry succeeded and all files
  verified intact afterward (transient — watch disk during large downloads).
  `enable` re-fetched its default library set (added sky130_ml_xx_hd, sky130_sram_macros, sky130_fd_io, sky130_fd_sc_hvl) — total 2.2 GB.
- conda-forge has only yosys among {openroad, opensta, klayout, magic, netgen}; klayout/magic/netgen not installed
  (not needed for OpenROAD-only P&R measurements).

## Disk
~3.2 GB total new: micromamba-root 466M, openroad 249M, syslibs 67M, volare-venv 61M,
~/.volare 2.2G, openroad.deb 55M (kept as reinstall source), debs/ 21M.
