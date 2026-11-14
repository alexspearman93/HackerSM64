#!/usr/bin/env bash
# Run from repository root. Requires licensed baserom.us.z64, NumPy, Pillow,
# normal HackerSM64 build dependencies and a configured MIPS toolchain.
set -euo pipefail
python3 tools/asset_lab/export_fox.py --asset fox
python3 tools/asset_lab/prepare_fox_c.py
python3 tools/asset_lab/export_fox.py --asset figure
python3 tools/asset_lab/prepare_figure_c.py
make VERSION=us "$@"
