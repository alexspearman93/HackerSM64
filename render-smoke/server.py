"""Render free-tier ROM build experiment; never serves ROM binaries."""
import hashlib
import json
import os
import subprocess
import threading
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer

STATE = {"status": "waiting", "rom_build": False, "rom_uploaded": False, "message": "Build not started"}
EXPECTED = "9bef1128717f958171a4afac3ed78ee2bb4e86ce"

def notify_rom_ready(download_url, expires_at):
    """Best-effort notification; never fail a successful build over push delivery."""
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if not topic:
        return
    try:
        payload = (
            "Your HackerSM64 ROM is ready! Tap to download and open in your emulator. "
            "Link expires: " + expires_at
        ).encode("utf-8")
        request = urllib.request.Request(
            "https://ntfy.sh/" + topic,
            data=payload,
            method="POST",
            headers={
                "Title": "HackerSM64 ROM ready",
                "Priority": "high",
                "Tags": "video_game,white_check_mark",
                "Click": download_url,
                "Actions": "view,Download ROM," + download_url,
                "User-Agent": "HackerSM64-Render-Builder/1.0",
            },
        )
        # Shared cloud egress IPs can hit ntfy.sh's anonymous rate limit.
        # Honor Retry-After when available, but cap delays to avoid blocking forever.
        import time
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    print("NTFY_NOTIFICATION_SENT status=" + str(response.status), flush=True)
                    break
            except urllib.error.HTTPError as exc:
                if exc.code != 429 or attempt == 3:
                    raise
                retry_after = exc.headers.get("Retry-After", "")
                try:
                    delay = min(max(int(retry_after), 2), 90)
                except ValueError:
                    delay = (10, 30, 60)[attempt]
                print("NTFY_RATE_LIMITED retry_in_seconds=" + str(delay), flush=True)
                time.sleep(delay)
    except Exception as exc:
        print("NTFY_NOTIFICATION_FAILED " + str(exc)[:200], flush=True)

def build():
    token = os.environ.get("ROM_FETCH_TOKEN")
    if not token:
        STATE.update(status="waiting", message="ROM_FETCH_TOKEN not configured")
        return
    try:
        STATE.update(status="fetching", message="Fetching private base ROM")
        req = urllib.request.Request(
            "https://hackersm64-private-upload.alexspearman93-cb2.workers.dev/private/base-rom",
            headers={"Authorization": "Bearer " + token, "User-Agent": "HackerSM64-Render-Builder/1.0"},
        )
        with urllib.request.urlopen(req, timeout=35) as response:
            data = response.read(8388609)
        if len(data) != 8388608 or hashlib.sha1(data).hexdigest() != EXPECTED:
            raise ValueError("Base ROM checksum or size mismatch")
        with open("/app/baserom.us.z64", "wb") as f:
            f.write(data)
        STATE.update(status="building", rom_uploaded=True, message="Compiling with make -j1")
        with open("/tmp/hackersm64-build.log", "w") as log:
            result = subprocess.run(
                ["make", "VERSION=us", "-j1"], cwd="/app",
                stdout=log, stderr=subprocess.STDOUT, timeout=900,
            )
        output = "/app/build/us_n64/sm64.z64"
        if result.returncode != 0 or not os.path.isfile(output):
            with open("/tmp/hackersm64-build.log", errors="replace") as log:
                tail = log.readlines()[-12:]
            raise RuntimeError("Build failed: " + "".join(tail)[-900:])
        STATE.update(status="uploading", rom_build=True, message="Uploading finished ROM to private R2")
        with open(output, "rb") as compiled:
            built_rom = compiled.read()
        if not (1048576 <= len(built_rom) <= 33554432):
            raise ValueError("Unexpected compiled ROM size")
        upload_request = urllib.request.Request(
            "https://hackersm64-private-upload.alexspearman93-cb2.workers.dev/private/build",
            data=built_rom,
            method="PUT",
            headers={
                "Authorization": "Bearer " + token,
                "User-Agent": "HackerSM64-Render-Builder/1.0",
                "Content-Type": "application/octet-stream",
            },
        )
        with urllib.request.urlopen(upload_request, timeout=90) as response:
            uploaded = json.load(response)
        if not uploaded.get("download_url"):
            raise RuntimeError("Private upload did not return a download link")
        # The link is a bearer credential: never publish it on the public /health endpoint.
        print("PRIVATE_BUILD_DOWNLOAD_URL=" + uploaded["download_url"], flush=True)
        print("PRIVATE_BUILD_EXPIRES_AT=" + uploaded["expires_at"], flush=True)
        notify_rom_ready(uploaded["download_url"], uploaded["expires_at"])
        STATE.update(status="built", rom_build=True, message="Full ROM compiled and stored privately; download link available in private Render logs")
    except urllib.error.HTTPError as exc:
        detail = exc.read(500).decode('utf-8', 'replace')
        STATE.update(status="failed", message=f"HTTP {exc.code}; server={exc.headers.get('Server')}; cf-ray={exc.headers.get('cf-ray')}; content-type={exc.headers.get('Content-Type')}; body={detail[:250]}")
    except Exception as exc:
        STATE.update(status="failed", message=str(exc)[:1200])
    finally:
        try:
            os.remove("/app/baserom.us.z64")
        except FileNotFoundError:
            pass

BUILD_LOCK = threading.Lock()

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.split("?")[0] != "/build":
            self.send_error(404)
            return
        secret = os.environ.get("ROM_FETCH_TOKEN", "")
        import hmac
        supplied = self.headers.get("Authorization", "")
        if not secret or not hmac.compare_digest(supplied, "Bearer " + secret):
            self.send_error(403)
            return
        with BUILD_LOCK:
            if STATE["status"] in ("fetching", "building", "uploading"):
                self.send_error(409, "ROM build already running")
                return
            STATE.update(status="queued", rom_build=False, message="Manual ROM build requested")
            threading.Thread(target=build, daemon=True).start()
        body = b'{"status":"queued"}'
        self.send_response(202)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_HEAD(self):
        self.respond(False)
    def do_GET(self):
        self.respond(True)
    def respond(self, send_body):
        if self.path.split("?")[0] == "/pistol-lab":
            with open("/app/tools/pistol-alignment/index.html", "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if send_body:
                self.wfile.write(body)
            return
        if self.path.split("?")[0] not in ("/", "/health"):
            self.send_error(404)
            return
        body = json.dumps(STATE).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if send_body:
            self.wfile.write(body)

if os.environ.get("ROM_AUTO_BUILD", "0") == "1":
    threading.Thread(target=build, daemon=True).start()
HTTPServer(("0.0.0.0", int(os.environ.get("PORT", "10000"))), Handler).serve_forever()
