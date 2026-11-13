#!/usr/bin/env bash
# Requires user-extracted Mupen64Plus + headers, GCC, MIPS nm, and an X display.
# Usage: TOOLROOT=/path/to/extracted/usr/.. DISPLAY=localhost:99 bash .../run_replay.sh solid outdir
set -euo pipefail
ROOT=$(git rev-parse --show-toplevel)
TOOLS=${TOOLROOT:?Set TOOLROOT to the extracted packages root}
SCENARIO=${1:?solid, punch, or ground_pound}
OUT=$(realpath -m "${2:?output directory}")
mkdir -p "$OUT/screenshots" "$OUT/config"
export LD_LIBRARY_PATH="$TOOLS/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" SDL_AUDIODRIVER=dummy
cc -shared -fPIC -I "$TOOLS/usr/include/mupen64plus" "$ROOT/tools/asset_lab/scripted_input.c" -ldl -o "$OUT/input.so"
export LAB_MARIO_POINTER=0x$("$TOOLS/usr/bin/mips-linux-gnu-nm" "$ROOT/build/us_n64/sm64.elf" | awk '$3=="gMarioState" {print $1}')
export LAB_INPUT="$ROOT/tools/asset_lab/replays/$SCENARIO.csv" LAB_TRACE="$OUT/$SCENARIO-trace.csv"
printf '[Core]\nVersion = 1.010000\nScreenshotPath = "%s/screenshots"\n' "$OUT" > "$OUT/config/mupen64plus.cfg"
"$TOOLS/usr/games/mupen64plus" --corelib "$TOOLS/usr/lib/x86_64-linux-gnu/libmupen64plus.so.2" --plugindir "$TOOLS/usr/lib/x86_64-linux-gnu/mupen64plus" --datadir "$TOOLS/usr/share/games/mupen64plus" --configdir "$OUT/config" --input "$OUT/input.so" --gfx mupen64plus-video-rice --audio dummy --noosd --resolution 640x480 --testshots 200,300,450,600 "$ROOT/build/us_n64/sm64.z64" > "$OUT/$SCENARIO-emulator.log" 2>&1
