# api/deps_probe.py
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status = {}
        def check(name, import_name=None):
            try:
                mod = __import__(import_name or name)
                v = getattr(mod, "__version__", "OK")
                status[name] = v
            except Exception as e:
                status[name] = f"ERROR: {e}"

        # Teste de pacotes
        check("fastapi")
        check("pydantic")
        check("requests")
        check("google.auth", import_name="google.auth")
        # Se você usa Document AI:
        check("google.cloud.documentai", import_name="google.cloud.documentai")

        out = json.dumps(status, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(out)
