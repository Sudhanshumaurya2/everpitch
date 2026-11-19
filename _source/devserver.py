"""Local server that emulates vercel.json rewrites/redirects/404 for testing."""
import http.server, json, pathlib, sys, urllib.parse
ROOT = pathlib.Path(sys.argv[1]); PORT = int(sys.argv[2])
cfg = json.loads((ROOT / "vercel.json").read_text())
RED = {r["source"]: r for r in cfg["redirects"]}; REW = {r["source"]: r["destination"] for r in cfg["rewrites"]}
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s, *a, **k): super().__init__(*a, directory=str(ROOT), **k)
    def log_message(s, *a): pass
    def do_GET(s):
        u = urllib.parse.urlsplit(s.path); p = u.path
        if p in RED:
            s.send_response(RED[p]["statusCode"]); s.send_header("Location", RED[p]["destination"]); s.end_headers(); return
        if p in REW: s.path = REW[p] + (("?" + u.query) if u.query else "")
        f = ROOT / urllib.parse.unquote(s.path.split("?")[0]).lstrip("/")
        if s.path.split("?")[0] != "/" and not f.exists():
            body = (ROOT / "404.html").read_bytes(); s.send_response(404); s.send_header("Content-Type", "text/html"); s.end_headers(); s.wfile.write(body); return
        super().do_GET()
http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
