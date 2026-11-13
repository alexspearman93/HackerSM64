# Asset Lab: isolated Mario import test

Dedicated `asset-lab` branch from HackerSM64 2.4.0 commit
`8953c07aa4592d65ffc974b596c97ae42778a221`. No pistol changes included.

## Reproduce

Use Blender 4.3.2, Fast64 checkout named `fast64` at
`b13010949567e4a2bf44ba3ccc18b06427243153`, and HailToDodongo/tiny3d
at `f2eccc3998967f1915be58d52f1c5bb6d5598a8c`.
Set FAST64_PATH and TINY3D_PATH to those absolute checkout paths.

```
for route in marker blend glb; do
  blender -b --python-exit-code 1 --python tools/asset_lab/export_assets.py -- "$route"
done
python3 tools/asset_lab/install_scene.py --stage 3
make VERSION=us -j8
```

Build requires a user-provided US baserom (SHA1
9bef1128717f958171a4afac3ed78ee2bb4e86ce) and normal HackerSM64 tools.
Never commit the ROM or extracted base-game data. CI exports only original/MIT assets.
Stage 0 is empty courtyard; 1 adds marker; 2 adds Blender crate; 3 adds GLB crate.
Only stage 3 was compiled and visually checked this session; selectable stages
are experiment scaffolding, not independent passing tests.

## Source and conversion

Crate source: https://github.com/HailToDodongo/tiny3d/tree/f2eccc3998967f1915be58d52f1c5bb6d5598a8c/examples/03_objects/assets
Files: box.blend, box.glb, crate00.ci8.png (32x32).
Repository MIT notice retained in TINY3D_LICENSE.txt; no crate-specific override
was found. This finding does not establish rights for unrelated demo assets.

The Blender source mesh is StoneFloor_F3d (8 vertices/12 triangles).
The GLB has 24 vertices/12 triangles because of seams. Both use CI8 texture,
100 game units per Blender unit, F3DEX2/LX2 exporter for f3dzex target.
Original marker has 5 positions/6 triangles. Display-list vertex counts may
increase when normals/UVs split vertices.

Initial preserved Blender material rendered black: custom fog/render mode and
subtractive combiner were incompatible with this scene. Both crate routes now
explicitly use sm64_shaded_texture. This is material adaptation, not lossless
material conversion. The .blend contains stale author-machine links; the named
crate texture is resolved explicitly and unrelated library meshes ignored.

## Verified 2026-11-13

Clean upstream US build succeeded. Stage 3 compiled and linked with GCC 14,
then cold-booted in Mupen64Plus 2.6/Rice with 8MB RAM and dummy audio. Captures
show marker and both textured crates on the checker floor. Evidence in docs/asset_lab.
Exporter JSON reports deliberately describe export-stage status only.

Initial link failed because global behavior tables reference stock BoB
collision/trajectory symbols; retained those definitions without spawning their
objects. TEST_LEVEL skipped initial menus but still opened act selection;
dedicated menu script now selects act 1 directly.

No crate collision, interaction, animation, audio verification, hardware test,
or iPhone acceptance yet. Mario/floor idle rendering is tested; movement and
camera sweeps remain manual checks. Walk/jump around each object and inspect
all faces on iPhone. The props are intentionally non-solid in this experiment.

## Next experiments

100: independently capture empty courtyard. 101: marker-only orientation check.
102/103: Blender/GLB routes (combined visual smoke passed, isolated stages pending).
104: evaluate an existing native C asset package with clear provenance.
105: add separate crate collision and interaction, check walking/jumping.
106: texture formats/transparency/material state isolation.
107: one rigged/animated asset. 108: measured object/triangle/texture limits.
109: clean rebuild, hashes, automated export/compile/emulator evidence package.

Advance by evidence: discovered -> exported -> compiled -> visually inspected ->
interactive/emulator accepted. No automatic promotion to the pistol workshop.
