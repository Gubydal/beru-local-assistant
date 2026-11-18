"""Serve only the local practice files, never the workspace or API.env."""

import argparse, http.server, json, pathlib, webbrowser, urllib.request, urllib.error, errno

ROOT = pathlib.Path(__file__).resolve().parents[1] / "practice"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path == "/healthz":
            body = json.dumps({"app": "beru-practice"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()
    server = None
    for port in range(args.port, args.port + 10):
        try:
            server = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError as exc:
            if exc.errno != errno.EADDRINUSE:
                raise
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/healthz", timeout=0.5
                ) as response:
                    if json.load(response).get("app") == "beru-practice":
                        url = f"http://127.0.0.1:{port}/"
                        print("Practice quiz already running: " + url, flush=True)
                        if not args.no_open:
                            webbrowser.open(url)
                        return
            except (OSError, ValueError):
                pass
    if server is None:
        raise SystemExit(
            "No free local practice port. Close an old server and try again."
        )
    url = f"http://127.0.0.1:{server.server_port}/"
    print("Practice quiz: " + url, flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
