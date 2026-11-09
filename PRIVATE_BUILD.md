# Private ROM build setup (mario-fireball-gun)

This repository deliberately does **not** store the original Super Mario 64 ROM or compiled ROMs. The GitHub Actions workflow runs ROM-free compilation checks; it does **not** create or distribute a playable ROM.

## Build in an existing Codespace

1. Open the Codespace containing your legally obtained US base ROM.
2. Make sure the Codespace is on the `mario-fireball-gun` branch and pull the latest branch changes (`git pull`). If the ROM is in a different Codespace, copy it privately to this one, naming it `baserom.us.z64` in the repository root.
3. Run: `bash scripts/build-private-rom.sh`
4. On success, the playable build is `build/us_n64/sm64.z64`. Download it using the Codespace file explorer.

The script verifies the known US ROM SHA-1, refuses a Git-tracked base ROM, builds with the project's Dockerfile, and checks the output. The base ROM and build output are ignored by Git. **Do not force-add either file, publish them as Actions artifacts, or put them in a public release.**

## Current automation status

- GitHub push: ROM-free MIPS source syntax checks run automatically.
- Codespace: private full ROM build is a single command after syncing code.
- Unattended full builds: **not yet configured**. GitHub-hosted runners cannot read a private file in a Codespace. A future solution needs an access-controlled ROM source and private artifact destination (or an appropriately secured persistent runner). Do not attach a self-hosted runner to an untrusted public-repository workflow.

This file documents the safe initial bridge without adding external paid services or exposing ROM bytes.

## Automatic local builds while Codespace is running

After the initial successful build, run `git pull --ff-only` and then:

```bash
bash scripts/watch-private-builds.sh
```

The watcher checks `origin/mario-fireball-gun` every 90 seconds, fast-forwards only when there are no tracked local edits, and runs the private build script for new commits. A successful build is copied to `.private-build/sm64-latest.z64` and its commit ID is recorded in `.private-build/sm64-latest.commit`. ROM files remain ignored by Git; no ROM is uploaded. Stop with Ctrl+C.

**Limitations:** the terminal session and Codespace must remain running, and the watcher does not send notifications or deliver the ROM to the phone. It is an interim local automation, not an unattended cloud CI pipeline. Do not publish the resulting ROM or the base ROM as public GitHub Actions artifacts.
