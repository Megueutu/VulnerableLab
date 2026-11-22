import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import URLError
from urllib.request import urlopen
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            status, data = 200, {"status": "ok"}
        elif self.path == "/branches":
            try:
                with urlopen(os.environ["DIRECTORY_URL"], timeout=2) as upstream:
                    status, data = 200, json.load(upstream)
            except (OSError, URLError, ValueError):
                status, data = 502, {"error": "directory unavailable"}
        else:
            status, data = 404, {"error": "not found"}
        payload = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    with ThreadingHTTPServer(("0.0.0.0", 8000), Handler) as server:
        server.serve_forever()
