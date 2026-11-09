# Render free-tier compatibility test

This is an **isolated, ROM-free** proof of concept. It checks that Render can
build the HackerSM64 MIPS toolchain image and syntax-check Mario source.
It then serves a small HTTP health endpoint. It does **not** build a playable
ROM, access private ROM data, or provide downloads.

Use `render-smoke/render.yaml` as the Blueprint path and choose the **Free**
web service plan only. Auto-deploy is disabled to conserve build minutes.
Do not upgrade or attach paid storage. Check the workspace's spend limits
and existing usage before creating the service.

Success proves Render can build the toolchain and run the service, **not**
that full ROM compilation fits within Free's 512 MB RAM and 0.1 CPU.
The next experiment would need a secure, non-public method to supply
a user-owned base ROM at runtime and a safe authenticated delivery mechanism.
Never commit, embed, or publish the original or compiled ROM.
