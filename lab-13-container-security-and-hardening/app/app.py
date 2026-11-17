from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import time


def can_write(path):
    try:
        with open(path, "w") as f:
            f.write(f"{time.time()}\n")
        return True
    except OSError:
        return False


class SecureHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_response(404)
            self.end_headers()
            return
        response = {
            "service": "hardened-demo",
            "running_uid": os.getuid(),
            "is_root": os.getuid() == 0,
            # Uygulamanın kendi veri dizini: normalde yazılabilir, --read-only ile yazılamaz
            "app_dir_writable": can_write("/app/data/write_test.txt"),
            # Geçici dizin: --read-only kullanılsa bile --tmpfs /tmp ile yazılabilir
            "tmp_writable": can_write("/tmp/last_access.log"),
        }
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())


if __name__ == "__main__":
    print("Hardened demo sunucusu 8080 portunda calisiyor", flush=True)
    HTTPServer(("0.0.0.0", 8080), SecureHandler).serve_forever()
