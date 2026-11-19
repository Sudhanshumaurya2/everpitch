import asyncio, json, re, pathlib, urllib.request, urllib.error
from playwright.async_api import async_playwright
BASE = "http://127.0.0.1:8765"; ROOT = pathlib.Path("/home/claude/everpitch")
pages = [p for p in json.loads((ROOT/"seo-pages.json").read_text())]
paths = ["/" if p["url"].endswith(".app/") else p["url"].replace("https://everpitch.vercel.app", "") for p in pages if "404" not in p["url"]]
paths = [p.replace("/order.html", "/order?package=bundle") for p in paths]
issues = []
# HTTP checks
class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NoRedir)
def status(u):
    try: r = op.open(BASE + u); return r.status, r.headers.get("Location")
    except urllib.error.HTTPError as e: return e.code, e.headers.get("Location")
print("/go/bundle ->", status("/go/bundle"))
print("/go/6 ->", status("/go/6")[0], "| /go/?url=evil ->", status("/go/?url=https://evil.com")[0])
assert status("/go/bundle") == (302, "https://www.jvzoo.com/c/1834263/461141")
# Source-level checks
banned = ["We may earn a commission", "This page contains affiliate links", "crossed-out list totals", "earn a small commission", "This is an affiliate link", "qualifying purchases", "[ADD", "[YOUR", "[INSERT", "Guide</a>" ]
for f in ROOT.rglob("*.html"):
    t = f.read_text()
    for b in banned[:-1]:
        if b in t: issues.append(f"banned phrase {b!r} in {f}")
    for m in re.finditer(r"<img\b[^>]*>", t):
        if " alt=" not in m.group(0): issues.append(f"img without alt in {f}")
    if "jvzoo.com/c/" in t: issues.append(f"raw affiliate URL in page {f}")
    if t.count("<h1") != 1: issues.append(f"{f.name}: h1 count {t.count('<h1')}")
    navs = re.findall(r'<ul class="nav-links" id="nav-links">(.*?)</ul>', t, re.S)[0]
    labels = re.findall(r'<a href="[^"]+"[^>]*>([^<]+)</a>', navs)[:7]
    if labels != ["What Is It","How It Works","Benefits","Focus Areas","Reviews","Blog","FAQ"]: issues.append(f"nav wrong {f}: {labels}")
titles = [p["title"] for p in pages]; descs = [p["description"] for p in pages]
if len(set(titles)) != len(titles): issues.append("duplicate titles")
if len(set(descs)) != len(descs): issues.append("duplicate descriptions")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        links = set()
        for vp in [(1366, 860), (390, 844)]:
            ctx = await b.new_context(viewport={"width": vp[0], "height": vp[1]})
            for path in paths:
                pg = await ctx.new_page(); errs = []
                pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                pg.on("pageerror", lambda e: errs.append(str(e)))
                r = await pg.goto(BASE + path, wait_until="load")
                if r.status != 200: issues.append(f"{path} HTTP {r.status}")
                ow = await pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                if ow > 0: issues.append(f"{path} @{vp[0]} horizontal overflow {ow}px")
                broken = await pg.evaluate("[...document.images].filter(i=>i.complete && i.naturalWidth===0).map(i=>i.src)")
                lazy = await pg.evaluate("[...document.images].filter(i=>!i.complete).length")
                if broken: issues.append(f"{path} broken images {broken}")
                for h in await pg.evaluate("[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href'))"):
                    if h.startswith("/") or h.startswith("#"): links.add(h.split("#")[0] or path)
                if errs: issues.append(f"{path} console: {errs[:2]}")
                await pg.close()
            await ctx.close()
        for l in sorted(links):
            s = status(l)[0]
            if s not in (200, 302): issues.append(f"internal link {l} -> {s}")
        print("internal links checked:", len(links))
        await b.close()
asyncio.run(main())
print("ISSUES:", len(issues)); print("\n".join(issues[:40]))
