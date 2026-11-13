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

## LAB-105: collision and interaction (2026-11-13)

User confirmed LAB-103 display on iPhone. Stage 4 now supplies three identical
crate models: left display-only, middle solid, right solid and breakable. Run
`python3 tools/asset_lab/install_scene.py --stage 4`, then build as above.

A separate 200x200x200 collision cube has its base at Y=0. The mesh is translated
up 100 in its geolayout to match. Surface collision uses no-camera-collision
triangles, so physical body collision does not introduce camera obstacles.
The branch-local `bhvLabCrate` adapter registers dynamic collision and optionally
uses SM64's breakable interaction and coin-spawn routines (parameter byte 2 = 1).
On destruction it returns before collision registration. The source model is
never replaced by the stock box model. Each broken crate releases one coin;
restart the ROM to reset. No automatic respawn is implemented.

Measured Mupen64Plus/Rice controller-replay checks passed:
- Holding forward stops Mario at Z=150 (crate face Z=100 plus Mario radius).
- Jumping lands at Y=200, floor height 200, and remains standing there.
- Punch removes the right crate; Mario walks through its former footprint and
  collects its coin (counter 0 -> 1, never more than 1 in the replay).
- Ground pound from its top removes the platform; Mario lands at Y=0/floor=0.
  Coin collection was verified in the punch replay, not the ground-pound replay.

Initial punch attempt failed with an interaction radius of 100: collision kept
Mario outside attack overlap. Using the stock breakable-box radius of 150 fixed
this while keeping physical collision aligned to the visible cube.

`scripted_input.c` supplies controller input only. Its optional DebugMemRead32
telemetry reads Mario coordinates/action/coin count without writing emulated
memory. Replays count controller polls, not video frames. `run_replay.sh` locates
Mario's pointer from the actual ELF; never reuse an address from another build.
Provide Mupen64Plus 2.6 headers/runtime, a MIPS nm and an existing X display:

```
TOOLROOT=/path/to/toolroot DISPLAY=localhost:99 bash tools/asset_lab/run_replay.sh solid /tmp/solid
TOOLROOT=/path/to/toolroot DISPLAY=localhost:99 bash tools/asset_lab/run_replay.sh punch /tmp/punch
TOOLROOT=/path/to/toolroot DISPLAY=localhost:99 bash tools/asset_lab/run_replay.sh ground_pound /tmp/pound
```

Collect the three *-trace.csv files into one evidence directory and run
`python3 tools/asset_lab/validate_replays.py /path/to/evidence`.
Screenshots/logs/trace CSVs accompany the private test build. Audio uses dummy
output and was not listened to. New stage-4 iPhone acceptance and exhaustive
edge/camera tests remain pending. The prior export CI covers conversions,
not this private-ROM interactive harness.

## LAB-106–108: second creator, environment, rigid animation

This series extends the approved crate experiments. LAB-106 imports Kenney's
CC0 tree (408 triangles); LAB-107 imports the same pack's wooden ramp (84
triangles); LAB-108 imports UX3D/Norbert Nopper's CC0 AnimatedCube (12 triangles).
This numbering supersedes the earlier provisional ladder; skeletal animation
and stress limits remain separate future tests.

Kenney's author page https://kenney.nl/assets/platformer-kit lists CC0. Direct
archive download returned HTTP 403 here. Inputs came from Hidencod/tge-assets
commit 3ddcc695adbba9fb918cf31b7c139b3f95b76910, whose license attributes Kenney
and identifies the self-contained GLBs as CC0 derivatives. Source paths are
packs/platformer-kit/tree.glb and platform-ramp.glb; exporter verifies SHA256.
Animation inputs come from KhronosGroup/glTF-Sample-Assets commit
4995a638c96dbc94376d3d6164e70fee3ac7f7a2, Models/AnimatedCube/glTF/. The model
README credits UX3D, 2017 / Norbert Nopper under CC0. Notices retained alongside
converted sources. See export reports for hashes and target scale.

```
# KENNEY_PATH points to the pinned mirror checkout; FAST64_PATH as above.
python3 tools/asset_lab/fetch_animation.py
for route in tree ramp animated; do
  blender -b --python-exit-code 1 --python tools/asset_lab/export_expansion.py -- "$route"
done
python3 tools/asset_lab/install_expansion.py
make VERSION=us -j8
```

All three routes retain UVs and adapt base-color materials to SM64. Source
512x512 textures become 32x32 RGBA16 (2048-byte texels); metallic/roughness are
omitted. This is intentionally lossy and needs visual review, not a universal
PBR material converter. Tree height is 600 game units; its collision is absent.
Ramp width/depth is roughly 600 units. Initial render-mesh collision was tested:
Mario caught/slid between planks. Final collision is an explicit simplified
non-slippery wedge, eight vertices/twelve triangles. The 88-unit front lip
requires a jump; standable surface rises to 333 units at the back. Detail
collision is also retained in export artifacts to reproduce the failed test.
Controller replay reached and held Y/floorHeight=281.958 on the slope.

Animation is source-driven rigid object yaw, not skinning. The exporter reads
the glTF rotation sampler, applies quaternion SLERP and emits sixty samples
for a two-second loop at 30 game updates/second. Unsupported multi-channel or
non-Y rotation tracks fail. Early sampling through Blender exposed frame-rate
and interpolation differences; direct source sampling removed those ambiguities.
Static camera captures show different cube orientations; no moving collision
is attached. Skeletal rigs, blended weights and animation retargeting untested.

The expanded scene preserves all three crate stations. Assets sit behind them:
tree left, rotating cube middle, ramp right. Updated replay runner includes the
Mupen config version so requested screenshot paths survive config initialization.
Use replay `ramp` for climbing and `overview` for stationary animation captures.
No audio listening, hardware performance certification or new iPhone acceptance.
CI exports all six source routes without ROM input; full ROM/emulator runs remain
private local evidence. Do not promote to the pistol branch automatically.

## LAB-109 — two-joint skeletal skinning

User accepted LAB-108 before this experiment. Reuses Marco Hutter's CC0 Khronos
SimpleSkin at commit `4995a638c96dbc94376d3d6164e70fee3ac7f7a2`.
Ten vertices, eight triangles, two joints, 5.5-second loop sampled at 30 Hz.
Left strip is bind pose; right strip blends joint transforms at runtime. Color
indicates child-joint weight. It is decorative and has no collision.

`python3 tools/asset_lab/export_skin.py` fetches hash-checked source data and
converts hierarchy, inverse bind matrices, weights and rotation keys into C.
`python3 tools/asset_lab/test_skin.py` compiles the actual C evaluator and checks
all 165 frames against an independent analytic hinge reference. Run
`python3 tools/asset_lab/install_skin.py` to regenerate the complete courtyard.
The export workflow repeats source conversion and C parity checks without ROMs.

CPU linear blend skinning uses 15,840 bytes of sampled joint matrices, not baked
vertex frames. Frame-owned N64 vertices avoid overwriting an in-flight RSP buffer.
This is a fixture-specific adapter, not SM64 native joint animation, a universal
glTF importer, retargeting, or proof of full-character performance. Unlit vertex
colors replace source material; integer N64 positions truncate by less than one unit.

US/f3dzex ROM compiled and booted in Mupen64Plus/Rice. Four static-camera captures
show the right strip bending while the left remains straight. Read-only render-pose
telemetry covered all 165 frames (598 samples), max error 0.000043745 game units;
base anchored. Host C check max error 0.000043497. No emulator memory writes.
To repeat telemetry, pass LAB_SKIN_FRAME and LAB_SKIN_PROBE addresses from the
ELF's gLabSkinFrame/gLabSkinProbe symbols and LAB_SKIN_TRACE output path to the
replay runner; validate with `validate_skin_trace.py TRACE --output REPORT`.
Initial compile failed because gGlobalTimer was undeclared; including game_init.h
fixed it. iPhone acceptance, audio listening, larger rigs and timing budgets remain
unverified. Next: an explicitly licensed character rig and measured CPU/RSP costs.
