# Separate viewer and ROM compiler workflows

Viewer: Render auto-deploys this repository's `mario-fireball-gun` branch. GET `/pistol-lab` serves the viewer. A deployment does **not** automatically build or publish a ROM.

Compiler: explicitly start a ROM build with an authenticated `POST /build` request using the existing `ROM_FETCH_TOKEN` environment secret as a Bearer token. Example from an authorized shell (never paste the token into browser URLs or commit it):

```sh
curl -X POST -H "Authorization: Bearer $ROM_FETCH_TOKEN" https://hackersm64-compiler-smoke.onrender.com/build
```

GET `/health` reports the current in-memory build state. The build fetches the privately held base ROM, compiles, uploads the result to private R2 and notifies as before. This route is intentionally not accessible from the public viewer. On service restart, build state resets to waiting.

Compatibility escape hatch: `ROM_AUTO_BUILD=1` restores the previous start-on-deploy behavior if explicitly configured. Default is off.

**Important:** This separates triggers/workflows within one Render service, not yet two independently deployed services. A future dedicated viewer hosting target can fully isolate uptime, deployments and billing.