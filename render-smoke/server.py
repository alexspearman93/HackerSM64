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
        STATE.update(status="built", rom_build=True, message="Full ROM compilation succeeded; private delivery not yet enabled")
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

class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.respond(False)
    def do_GET(self):
        self.respond(True)
    def respond(self, send_body):
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

threading.Thread(target=build, daemon=True).start()
HTTPServer(("0.0.0.0", int(os.environ.get("PORT", "10000"))), Handler).serve_forever()
