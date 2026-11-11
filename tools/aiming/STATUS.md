# Fixed aiming arm experiment — 2026-11-11

Base: 27b05fcf8fa9a1633fe55b5467721ebf4d0adc07.
Local source compile succeeded using GCC 14 MIPS and repository linker. ROM boots in Mupen64Plus/Rice. Matrix parity tests pass. Visual acceptance FAILED: sampled idle pose does not clearly show forward extended arm/pistol; do not promote this branch.

Changed animation channels for joints 8–11 in idle C3/C4/C5, walking 48 and running 72/73. Other channels preserved. Animation reuse means these edits also affect other actions using the same animations; future implementation should scope by action or use separate animation entries.

Integrated earlier tested pistol transform (15,-5,-14), (11,112,-116), scale 2.25 in all three hand layouts. Fixed missing comma in supplied source patch. Original aligned ROM remains the accepted visual baseline.

Next: trace actual decoded animation channels in emulator and verify animation index convention against runtime; establish source-built alignment parity before accepting pose. Avoid further blind axis changes. No bullet/sound/flash changes.

Build: make VERSION=us COMPILER=gcc -j6 (MIPS toolchain on PATH; LD_LIBRARY_PATH must include tools and extracted toolchain libraries).
