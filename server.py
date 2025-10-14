#!/usr/bin/env python3
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
PORT = int(os.environ.get("PORT", "5050"))


class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_POST(self):
        if self.path != "/ai":
            self._set_headers(404)
            self.wfile.write(b"{}")
            return

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "OPENAI_API_KEY manquant"}).encode("utf-8"))
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length or 0)
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
            prompt = payload.get("prompt", "").strip()
            if not prompt:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "prompt requis"}).encode("utf-8"))
                return
        except Exception as e:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": f"JSON invalide: {e}"}).encode("utf-8"))
            return

        req_body = json.dumps({
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Tu es un assistant expert en design de processus et delivery produit."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 900
        }).encode("utf-8")

        req = Request(OPENAI_API_URL, data=req_body, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        })

        try:
            with urlopen(req, timeout=60) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
                text = (
                    data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                        .strip()
                )
                self._set_headers(200)
                self.wfile.write(json.dumps({"text": text}).encode("utf-8"))
        except HTTPError as e:
            try:
                err = e.read().decode("utf-8")
            except Exception:
                err = str(e)
            self._set_headers(e.code or 500)
            self.wfile.write(json.dumps({"error": err}).encode("utf-8"))
        except URLError as e:
            self._set_headers(502)
            self.wfile.write(json.dumps({"error": f"URLError: {e}"}).encode("utf-8"))
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": f"Exception: {e}"}).encode("utf-8"))


def main():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"AI proxy running on http://localhost:{PORT}/ai  (model={MODEL})")
    server.serve_forever()


if __name__ == "__main__":
    main()


