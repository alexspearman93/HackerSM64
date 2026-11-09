#!/usr/bin/env bash
# Watch the feature branch and build new commits privately while this Codespace is running.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
BRANCH="mario-fireball-gun"
INTERVAL="${WATCH_INTERVAL_SECONDS:-90}"
STATE_DIR=".private-build"
mkdir -p "$STATE_DIR"
if [[ ! "$INTERVAL" =~ ^[0-9]+$ ]] || (( INTERVAL < 30 )); then
  echo "WATCH_INTERVAL_SECONDS must be at least 30" >&2; exit 1
fi
if [[ ! -f baserom.us.z64 ]]; then
  echo "Missing baserom.us.z64. Put your private US base ROM in the project root." >&2; exit 1
fi
if [[ "$(git branch --show-current)" != "$BRANCH" ]]; then
  echo "Switch to $BRANCH before starting watcher." >&2; exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo "Tracked working-tree changes detected; refusing automatic update." >&2; exit 1
fi
echo "Watching origin/$BRANCH every ${INTERVAL}s. Ctrl+C stops. Codespace must remain running."
while true; do
  if ! git fetch origin "+refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"; then
    echo "Fetch failed; will retry." >&2
  elif [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
    echo "Tracked local changes found; skipping this check to protect your work." >&2
  else
    remote_sha="$(git rev-parse "refs/remotes/origin/$BRANCH")"
    current_sha="$(git rev-parse HEAD)"
    last_success="$(cat "$STATE_DIR/last-success" 2>/dev/null || true)"
    if [[ "$remote_sha" != "$current_sha" ]]; then
      if git merge-base --is-ancestor HEAD "refs/remotes/origin/$BRANCH"; then
        git merge --ff-only "refs/remotes/origin/$BRANCH" || echo "Fast-forward failed; retry later." >&2
      else
        echo "Local branch diverged; refusing to overwrite it." >&2
      fi
    fi
    current_sha="$(git rev-parse HEAD)"
    if [[ "$current_sha" == "$remote_sha" && "$current_sha" != "$last_success" ]]; then
      echo "Building commit $current_sha..."
      if bash scripts/build-private-rom.sh; then
        printf '%s\n' "$current_sha" > "$STATE_DIR/last-success"
        cp -f build/us_n64/sm64.z64 "$STATE_DIR/sm64-latest.z64"
        printf '%s\n' "$current_sha" > "$STATE_DIR/sm64-latest.commit"
        echo "PRIVATE BUILD READY: $STATE_DIR/sm64-latest.z64 (commit $current_sha)"
      else
        echo "Build failed for $current_sha; will retry." >&2
      fi
    fi
  fi
  sleep "$INTERVAL"
done
