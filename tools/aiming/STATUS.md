# Fixed aiming arm — 2026-11-11

Local GCC 14 source build succeeded; Mupen64Plus/Rice cold boot succeeded. Corrected pose inspected idle at frame 400 and running at frame 345. Pistol is forward and right arm extended; legs and free arm animate. Matrix parity tests pass (600 joint/frame matrices).

Root cause of failed prototypes: pose.py passed degrees to scipy Rotation.from_euler without degrees=True. Earlier hardcoded parent hierarchy also omitted torso ancestry; corrected. Successful screenshots: clean__3 frame 400, clean__-3 frames 330/345/400 in local emulator harness.

Changed channels for right shoulder/upper arm/forearm/wrist in idle C3/C4/C5, walk 48 and run 72/73. Hand orientation retains the original calibrated idle transform. Body sway remains. Animation reuse also affects other actions using these animations; swimming, cutscenes, transitions, jumping and full-speed variants are not exhaustively tested. iPhone acceptance pending. Bullet muzzle alignment, sound and flash unchanged.

Pistol transform: position (15,-5,-14), rotation (11,112,-116), scale 2.25; three LOD layouts. Source patch's missing comma corrected.

Next: iPhone test; scope aiming to intended actions, then align projectile spawn to muzzle. Original aligned ROM retained as rollback. This branch is experimental, not merged.
