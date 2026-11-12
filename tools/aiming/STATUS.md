# Fire-triggered pose — 2026-11-11

Compiled locally and cold-booted Mupen64Plus/Rice. Captured before shot (369), shot (371), hold (375), release (385). Successful projectile spawn sets an 21-update timer, refreshed by another successful shot. Hold for approximately half a second, then six-update release blend; total 0.7 seconds at 30 updates/sec. User confirmed initial version worked but lowered too quickly. Increased hold to avoid bobbing between shots. Immediate raise avoids delaying projectile firing. Original animation assets restored. Renderer consumes normal channels before overriding only joints 8–11 for Mario in ACT_IDLE or ACT_WALKING; other actions remain normal.

Standing shot/release sequence exercised. Running shot needs dedicated follow-up capture and iPhone acceptance. Bullet muzzle alignment, recoil, sound and flash remain pending. Smooth pre-shot raising not implemented. Current pose blending uses shortest signed angle deltas. Scope: experimental branch, not merged.

## Combined effects prototype
Added animation-derived muzzle position for idle/walking, including pistol transform and Mario quarter-scale. Other actions retain prior spawn fallback. Auto-aim yaw correction limited to 0x600 (~8.4 degrees). Bullet stays at spawn for first update. Two-update sparkle muzzle flash and existing SOUND_GENERAL_RACE_GUN_SHOT triggered only after successful bullet allocation. Compiled and cold-boot firing tested; audio not listened to (dummy audio harness). Running torso tilt, animation frame timing and exact muzzle parity need further validation. First visual trial caught missing quarter-scale; corrected before delivery. Flash is a short world-space particle, not continuously attached.

## Custom arcade sound
Original deterministic 0.18-second mono 22050 Hz sample: filtered noise crack plus descending bass thump. Added bank-5 instrument 16 and repurposed unused general sound slot 0x31; race-start sound remains unchanged. Generation script and lossless base64 materializer included; Makefile restores sample before discovering sound assets. ADPCM encoding and ROM compilation passed. Boot/firing smoke test uses dummy audio: subjective loudness and timbre await iPhone feedback.

## Running muzzle fix — 2026-11-12

HackerSM64 experimental branch `fixed-aim-idle-running`, gameplay commit `e812afc41e79967bc26c1571df88f4cf9144caaf`. User accepted fire-triggered arm pose, longer hold, effects and latest supplied 9mm sound; reported running muzzle mismatch.

Shot creation now runs after Mario movement/action updates. Muzzle reconstruction uses the upcoming rendered animation frame, translation flags/multiplier, torso lean and rendered object position/rotation. Local GCC US ROM build succeeded; three existing matrix tests passed (these test idle math, not running muzzle parity). Mupen64Plus/Rice cold-boot test with analog X held through firing captured the bullet at the barrel then travelling away while Mario continued running. Standing-fire smoke test also exited normally. Exact parity across all speeds, turns and slopes and iPhone acceptance remain pending. Other actions retain fallback muzzle positioning; audio was not listened to in the dummy-audio harness.

Delivered `sm64_running_muzzle_fix.z64`, SHA256 `cd6451fa38ff63b7aaa355519cf4247da8557cd70e117d7362fecce81b871f6f`, Library `libfile_891108cd1554819190b3684422481856`. Local build retains user-supplied 9mm sample; GitHub still contains earlier attributed CZ52 sample, so repository alone does not reproduce this sound variant. No ROM committed; branch not merged or promoted. Next: user tests straight running, turning while firing, and idle on iPhone.
