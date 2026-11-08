#!/usr/bin/env bash
# Build HackerSM64 locally without publishing copyrighted ROM data.
set -Eeuo pipefail
cd "$(dirname "$0")/.."

BASE_ROM="baserom.us.z64"
EXPECTED_SHA1="9bef1128717f958171a4afac3ed78ee2bb4e86ce"
OUTPUT="build/us_n64/sm64.z64"

if [[ ! -f "$BASE_ROM" ]]; then
  echo "Missing $BASE_ROM in the repository root." >&2
  echo "Keep your own legally obtained ROM in the Codespace; never commit it." >&2
  exit 1
fi

ACTUAL_SHA1="$(sha1sum "$BASE_ROM" | awk '{print $1}')"
if [[ "$ACTUAL_SHA1" != "$EXPECTED_SHA1" ]]; then
  echo "ROM SHA-1 does not match the supported US base ROM." >&2
  echo "Expected: $EXPECTED_SHA1" >&2
  echo "Actual:   $ACTUAL_SHA1" >&2
  exit 1
fi

if git ls-files --error-unmatch "$BASE_ROM" >/dev/null 2>&1; then
  echo "ERROR: base ROM is tracked by git. Stop before building." >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required for this build script." >&2
  exit 1
fi

echo "Building local Docker image (cached on subsequent runs)..."
docker build -t hackersm64-private-builder .
echo "Compiling ROM locally; no ROM is uploaded by this script..."
docker run --rm -v "$PWD:/hackersm64" hackersm64-private-builder make VERSION=us -j4

if [[ ! -s "$OUTPUT" ]]; then
  echo "Build finished without the expected output: $OUTPUT" >&2
  exit 1
fi
echo "SUCCESS: $OUTPUT"
ls -lh "$OUTPUT"
echo "This ROM is private to your Codespace. Download via the file explorer; do not commit or upload to public Actions artifacts."
