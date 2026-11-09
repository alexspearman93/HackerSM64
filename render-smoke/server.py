"""ROM-free Render compatibility smoke test. No build/download endpoint."""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.respond(send_body=False)

    def do_GET(self):
        self.respond(send_body=True)

    def respond(self, send_body):
        if urlsplit(self.path).path not in ("/", "/health"):
            self.send_error(404)
            return
        body = json.dumps({
            "status": "ok",
            "test": "mips-cross-compiler-syntax-check",
            "rom_build": False,
            "rom_uploaded": False
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if send_body:
            self.wfile.write(body)

HTTPServer(("0.0.0.0", int(os.environ.get("PORT", "10000"))), Handler).serve_forever()
