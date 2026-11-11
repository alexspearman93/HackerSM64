# Fire-triggered pose — 2026-11-11

Compiled locally and cold-booted Mupen64Plus/Rice. Captured before shot (369), shot (371), hold (375), release (385). Successful projectile spawn sets an 21-update timer, refreshed by another successful shot. Hold for approximately half a second, then six-update release blend; total 0.7 seconds at 30 updates/sec. User confirmed initial version worked but lowered too quickly. Increased hold to avoid bobbing between shots. Immediate raise avoids delaying projectile firing. Original animation assets restored. Renderer consumes normal channels before overriding only joints 8–11 for Mario in ACT_IDLE or ACT_WALKING; other actions remain normal.

Standing shot/release sequence exercised. Running shot needs dedicated follow-up capture and iPhone acceptance. Bullet muzzle alignment, recoil, sound and flash remain pending. Smooth pre-shot raising not implemented. Current pose blending uses shortest signed angle deltas. Scope: experimental branch, not merged.
