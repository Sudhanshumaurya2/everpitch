"""Render original EverPitch illustrations (HTML/CSS scenes) to genuine WebP files.
Run: python3 render_images.py <site_dir>
"""
import sys, asyncio, io, pathlib
from PIL import Image
from playwright.async_api import async_playwright

SITE = pathlib.Path(sys.argv[1])
OUT = SITE / "assets" / "img"
FONTS = (SITE / "assets" / "fonts").resolve()

TRI = '<svg viewBox="0 0 10 12" style="width:.55em;height:.66em;margin:0 .05em;display:inline-block;vertical-align:-.02em"><path d="M0 0L10 6L0 12Z" fill="#E8704F"/></svg>'
LOGO = f'<span class="lg">ever{TRI}pitch</span>'

BASE_CSS = f"""
@font-face{{font-family:U;font-weight:500 800;src:url(file://{FONTS}/urbanist-latin-700-normal.woff2)}}
@font-face{{font-family:U8;src:url(file://{FONTS}/urbanist-latin-800-normal.woff2)}}
@font-face{{font-family:H;src:url(file://{FONTS}/hind-latin-500-normal.woff2)}}
*{{box-sizing:border-box;margin:0}}
html,body{{background:transparent}}
body{{font-family:H,sans-serif;color:#1D1512}}
.lg{{font-family:U8;letter-spacing:-.03em;color:#1D1512;display:inline-flex;align-items:center}}
.win{{background:#fff;border:3px solid #1D1512;border-radius:22px;box-shadow:0 14px 0 #1D1512;overflow:hidden}}
.bar{{height:46px;border-bottom:3px solid #1D1512;display:flex;align-items:center;gap:8px;padding:0 16px;background:#FFF6EF}}
.dot{{width:13px;height:13px;border-radius:50%;border:2px solid #1D1512}}
.url{{margin-left:14px;flex:1;height:26px;border-radius:8px;background:#FCE3D6;font:600 14px U;display:flex;align-items:center;justify-content:center;color:#7A6C66}}
.u{{font-family:U}}
.chip{{display:inline-flex;align-items:center;gap:8px;background:#fff;border:2.5px solid #1D1512;border-radius:12px;box-shadow:0 4px 0 #1D1512;padding:7px 13px;font:700 17px U;white-space:nowrap}}
.chip i{{font-style:normal;width:26px;height:26px;border-radius:8px;background:#FCEEE6;display:grid;place-items:center;font-size:15px}}
"""

def app_window(scale=1.0, slide_title="Your idea, turned into a complete webinar", sub="Script · Slides · Voice · Live Q&amp;A"):
    return f"""
<div class="win" style="width:900px">
  <div class="bar"><span class="dot" style="background:#E8704F"></span><span class="dot" style="background:#F4B860"></span><span class="dot" style="background:#9AD3B0"></span><div class="url">EverPitch · webinar room</div></div>
  <div style="display:grid;grid-template-columns:1.55fr 1fr;gap:0">
    <div style="padding:22px;border-right:3px solid #1D1512">
      <div style="position:relative;aspect-ratio:16/9;border-radius:16px;border:3px solid #1D1512;background:linear-gradient(135deg,#1D1512,#3A2A24);overflow:hidden;padding:26px 28px;color:#fff">
        <div style="position:absolute;right:-40px;top:-40px;width:200px;height:200px;border-radius:50%;background:#E8704F;opacity:.9"></div>
        <div style="position:absolute;right:40px;bottom:-60px;width:150px;height:150px;border-radius:50%;border:3px dashed rgba(255,255,255,.35)"></div>
        <div style="font:700 13px U;letter-spacing:.14em;color:#F4B860;text-transform:uppercase;position:relative">Slide 3 of 18</div>
        <div style="font:800 32px/1.1 U8;max-width:330px;margin-top:10px;position:relative">{slide_title}</div>
        <div style="font:600 16px U;color:#E9DED8;margin-top:12px;position:relative">{sub}</div>
        <div style="position:absolute;left:28px;bottom:22px;display:flex;align-items:center;gap:12px">
          <div style="width:46px;height:46px;border-radius:50%;background:#FCEEE6;border:3px solid #fff;display:grid;place-items:center">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1D1512" stroke-width="2.4" stroke-linecap="round"><path d="M12 3a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V6a3 3 0 0 1 3-3z"/><path d="M19 11a7 7 0 0 1-14 0M12 18v3"/></svg></div>
          <div style="display:flex;gap:4px;align-items:center;height:30px">{''.join(f'<span style="width:5px;border-radius:3px;background:#E8704F;height:{h}px"></span>' for h in [10,22,14,28,18,26,12,20,8,16,24,12])}</div>
        </div>
      </div>
      <div style="display:flex;gap:10px;margin-top:16px">
        {''.join(f'<div style="flex:1;height:58px;border-radius:10px;border:2.5px solid #1D1512;background:{c}"></div>' for c in ['#FCEEE6','#FFE1D2','#1D1512','#FCEEE6'])}
      </div>
    </div>
    <div style="padding:22px;background:#FFFAF6;display:flex;flex-direction:column;gap:12px">
      <div style="font:800 15px U;letter-spacing:.1em;text-transform:uppercase;color:#B8492A">Live chat</div>
      <div style="background:#fff;border:2.5px solid #1D1512;border-radius:14px;padding:10px 12px;font:600 15px/1.35 H">Viewer: How long does setup take?</div>
      <div style="background:#E8704F;border:2.5px solid #1D1512;border-radius:14px;padding:10px 12px;font:600 15px/1.35 H">Host: Great question — answered out loud from your content.</div>
      <div style="background:#fff;border:2.5px solid #1D1512;border-radius:14px;padding:10px 12px;font:600 15px/1.35 H">Viewer: Is there a replay?</div>
      <div style="margin-top:auto;display:flex;align-items:center;justify-content:space-between;border-top:2.5px dashed #EADBD2;padding-top:12px">
        <span style="font-size:30px">{LOGO}</span>
        <span style="font:800 13px U;background:#1D1512;color:#fff;border-radius:8px;padding:6px 10px">ON AIR</span>
      </div>
    </div>
  </div>
</div>"""

def page(body, w, h, bg="transparent"):
    return f"<html><head><style>{BASE_CSS} body{{width:{w}px;height:{h}px;background:{bg};overflow:hidden;position:relative}}</style></head><body>{body}</body></html>"

SCENES = {}

# 1) Main product mockup (transparent) — used like the "bottle" everywhere
SCENES["everpitch-ai-webinar-software-mockup"] = (page(
    f'<div style="position:absolute;left:30px;top:24px;transform:perspective(1600px) rotateY(-8deg) rotateX(4deg)">{app_window()}</div>', 980, 560), 980, 560, [980, 560])

# 2) Bundle: four products stacked (transparent)
def labelled(name, sub, col, front=False):
    lg = f'<div style="font-size:34px;margin-bottom:6px">{LOGO}</div>' if front else ''
    return f"""<div class="win" style="width:520px;height:300px;position:absolute;{col}">
      <div class="bar"><span class="dot" style="background:#E8704F"></span><span class="dot" style="background:#F4B860"></span><span class="dot" style="background:#9AD3B0"></span><div class="url">{name}</div></div>
      <div style="padding:{"14px" if front else "4px"} 28px">{lg}
      <div style="font:800 36px/1.05 U8;margin-top:6px">{name}</div><div style="font:600 19px/1.35 H;color:#4A3F3A;margin-top:10px">{sub}</div></div></div>"""
bundle_body = (
    labelled("Agency", "Client license · no “Powered by EverPitch”", "left:480px;top:20px;transform:rotate(5deg)")
    + labelled("Kit Vault", "24 ready-made webinar kits", "left:340px;top:118px;transform:rotate(2deg)")
    + labelled("DFY Webinars", "10 finished, voiced webinars", "left:190px;top:216px;transform:rotate(-1deg)")
    + labelled("EverPitch Commercial", "Script · slides · voice · daily hosting", "left:40px;top:316px;transform:rotate(-4deg)", True)
    + '<div class="chip" style="position:absolute;left:640px;top:560px;font-size:22px;padding:12px 18px;background:#E8704F"><i>⚡</i>8,000 credits / month</div>'
)
SCENES["everpitch-bundle-four-products"] = (page(bundle_body, 1060, 660), 1060, 660, [1060, 600])

# 3) Feature background composition (overview) — product with feature "ingredients" behind it
feat = [("¶", "AI-written scripts", 60, 70), ("▦", "73 slide layouts", 700, 60), ("◉", "30 AI voices", 40, 560), ("◍", "87 languages", 760, 590),
        ("❝", "Spoken Q&amp;A", 860, 250), ("✉", "Reminder emails", 20, 300), ("▶", "Demo insertion", 420, 30), ("◷", "Viewer timezones", 430, 650)]
chips = "".join(f'<div class="chip" style="position:absolute;left:{x}px;top:{y}px;opacity:.95"><i>{i}</i>{t}</div>' for i, t, x, y in feat)
SCENES["everpitch-features-composition"] = (page(
    f'<div style="position:absolute;inset:0;background:radial-gradient(circle at 25% 20%,#FFE3D4,transparent 55%),radial-gradient(circle at 80% 85%,#FBC9AF,transparent 50%),#FFF3EC"></div>'
    f'<div style="position:absolute;left:180px;top:80px;width:800px;height:800px;border-radius:50%;border:3px dashed rgba(29,21,18,.12)"></div>{chips}'
    f'<div style="position:absolute;left:150px;top:140px;transform:scale(.86);transform-origin:top left">{app_window()}</div>', 1200, 720, "#FFF3EC"), 1200, 720, [1200, 640])

# 4) Three-step flow
def stepbox(n, t, s):
    return f'<div class="win" style="width:330px;padding:0"><div style="padding:26px"><div style="width:58px;height:58px;border-radius:14px;background:#E8704F;border:3px solid #1D1512;display:grid;place-items:center;font:800 30px U8">{n}</div><div style="font:800 30px/1.1 U8;margin-top:18px">{t}</div><div style="font:600 19px/1.4 H;color:#4A3F3A;margin-top:10px">{s}</div></div></div>'
arrow = '<svg width="60" height="40" viewBox="0 0 60 40"><path d="M4 20h44M36 8l12 12-12 12" fill="none" stroke="#1D1512" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
SCENES["everpitch-three-step-workflow"] = (page(
    f'<div style="position:absolute;inset:0;background:#FFF3EC"></div><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:18px;padding-bottom:14px">'
    f'{stepbox(1,"Describe it","A topic, PDF, link, recording — or a kit.")}{arrow}{stepbox(2,"Review it","Script, slides and voice come back to edit.")}{arrow}{stepbox(3,"Share it","Registration page, link or join button.")}</div>',
    1200, 420, "#FFF3EC"), 1200, 420, [1200])

# 5) Focus-area visuals
def scene(bg, inner):
    return f'<div style="position:absolute;inset:0;background:{bg}"></div>{inner}'
SCENES["focus-webinar-creation"] = (page(scene("linear-gradient(135deg,#FFE9DD,#FCD3BF)",
    '<div class="win" style="position:absolute;left:70px;top:60px;width:520px;padding:26px"><div style="font:800 15px U;letter-spacing:.1em;color:#B8492A">SCRIPT</div>'
    + "".join(f'<div style="height:14px;border-radius:7px;background:{c};margin-top:14px;width:{w}%"></div>' for c, w in [("#1D1512", 90), ("#EADBD2", 100), ("#EADBD2", 84), ("#EADBD2", 94), ("#E8704F", 60), ("#EADBD2", 88)])
    + '</div><div class="win" style="position:absolute;left:470px;top:230px;width:440px;height:250px;background:#1D1512;padding:26px;color:#fff"><div style="font:800 30px/1.1 U8">Slide 6 · How it works</div><div style="display:flex;gap:12px;margin-top:22px">'
    + "".join('<div style="flex:1;height:90px;border-radius:12px;background:#3A2A24;border:2px solid #E8704F"></div>' for _ in range(3))
    + '</div></div><div class="chip" style="position:absolute;left:120px;top:440px"><i>▤</i>73 layouts · 11 styles</div>'), 1000, 560), 1000, 560, [1000])
SCENES["focus-automated-hosting-qa"] = (page(scene("linear-gradient(135deg,#1D1512,#3A2A24)",
    '<div style="position:absolute;left:70px;top:70px;font:800 54px/1.05 U8;color:#fff;max-width:440px">Today’s sessions</div>'
    + "".join(f'<div class="chip" style="position:absolute;left:70px;top:{200+i*72}px;font-size:21px"><i>◷</i>{t}</div>' for i, t in enumerate(["9:00 AM · your viewer’s time", "1:00 PM · your viewer’s time", "7:30 PM · your viewer’s time"]))
    + '<div style="position:absolute;right:70px;top:100px;width:390px;display:grid;gap:14px">'
    + '<div style="background:#fff;border:3px solid #1D1512;border-radius:16px;padding:14px 16px;font:600 20px/1.35 H">Viewer: Does it work for coaching?</div>'
    + '<div style="background:#E8704F;border:3px solid #fff;border-radius:16px;padding:14px 16px;font:600 20px/1.35 H">Host (spoken): Yes — here’s how it fits</div>'
    + '<div style="background:#fff;border:3px solid #1D1512;border-radius:16px;padding:14px 16px;font:600 20px/1.35 H">Viewer: Hello from my lunch break!</div></div>'), 1000, 560), 1000, 560, [1000])
langs = ["English", "Español", "Français", "Deutsch", "Português", "Italiano", "Nederlands", "Polski", "Türkçe", "Bahasa", "Svenska", "Română"]
SCENES["focus-multilingual-webinars"] = (page(scene("radial-gradient(circle at 50% 50%,#FFE3D4,#FCD3BF)",
    '<div style="position:absolute;left:370px;top:150px;width:260px;height:260px;border-radius:50%;background:#E8704F;border:4px solid #1D1512;box-shadow:0 10px 0 #1D1512;display:grid;place-items:center;font:800 64px U8">87</div>'
    '<div style="position:absolute;left:380px;top:420px;width:240px;text-align:center;font:800 26px U8">languages</div>'
    + "".join(f'<div class="chip" style="position:absolute;left:{[60,90,40,700,740,690,250,560,120,780,300,560][i]}px;top:{[70,200,350,80,220,370,40,40,480,480,500,500][i]}px">{t}</div>' for i, t in enumerate(langs))), 1000, 560), 1000, 560, [1000])
SCENES["focus-registration-follow-up"] = (page(scene("linear-gradient(135deg,#FFF3EC,#FCE0D2)",
    "".join(f'<div class="win" style="position:absolute;left:{40+i*235}px;top:{150+(i%2)*40}px;width:210px;padding:20px"><div style="width:44px;height:44px;border-radius:12px;background:{c};border:3px solid #1D1512;display:grid;place-items:center;font-size:22px">{ic}</div><div style="font:800 23px/1.1 U8;margin-top:14px">{t}</div><div style="font:600 16px/1.35 H;color:#4A3F3A;margin-top:8px">{s}</div></div>'
            for i, (ic, t, s, c) in enumerate([("✍", "Register", "31 page templates", "#FCEEE6"), ("✉", "Remind", "Emails + calendar invites", "#F4B860"), ("▶", "Watch", "Live room, daily", "#E8704F"), ("$", "Buy", "Offer card + checkout", "#9AD3B0")]))), 1000, 560), 1000, 560, [1000])

# 6) Blog thumbnails
def thumb(title, kicker, bg, deco):
    return page(scene(bg, deco + f'<div style="position:absolute;left:60px;bottom:60px;max-width:620px"><div class="chip" style="font-size:16px"><i>✎</i>{kicker}</div><div style="font:800 50px/1.08 U8;margin-top:22px;color:#1D1512">{title}</div></div>'
                       '<div style="position:absolute;right:50px;top:44px;font-size:34px">' + LOGO + '</div>'), 1000, 560)
SCENES["blog-evergreen-webinar-guide"] = (thumb("Live vs. evergreen webinars", "Webinar strategy", "linear-gradient(135deg,#FFE9DD,#FCD3BF)",
    '<div style="position:absolute;right:-60px;bottom:-80px;width:420px;height:420px;border-radius:50%;background:#E8704F;border:4px solid #1D1512"></div>'), 1000, 560, [1000, 600])
SCENES["blog-webinar-script-structure"] = (thumb("A webinar script that sells without pushing", "Scripting", "linear-gradient(135deg,#FFF3EC,#FDE7D9)",
    "".join(f'<div style="position:absolute;right:{60+i*30}px;top:{150+i*60}px;width:{380-i*40}px;height:22px;border-radius:11px;background:{c}"></div>' for i, c in enumerate(["#1D1512", "#E8704F", "#EADBD2", "#EADBD2", "#F4B860"]))), 1000, 560, [1000, 600])
SCENES["blog-webinar-follow-up-emails"] = (thumb("After the webinar: follow-up that respects people", "Email follow-up", "linear-gradient(135deg,#FCEEE6,#F9D9C8)",
    '<div class="win" style="position:absolute;right:70px;top:120px;width:300px;height:200px;transform:rotate(6deg);padding:22px"><div style="font:800 22px U8">✉ Here’s the replay</div><div style="height:12px;border-radius:6px;background:#EADBD2;margin-top:18px"></div><div style="height:12px;border-radius:6px;background:#EADBD2;margin-top:12px;width:80%"></div><div style="height:34px;border-radius:10px;background:#E8704F;border:2.5px solid #1D1512;margin-top:20px;width:60%"></div></div>'), 1000, 560, [1000, 600])

# 7) Reviews page graphic
SCENES["everpitch-verified-facts"] = (page(scene("linear-gradient(135deg,#1D1512,#3A2A24)",
    '<div style="position:absolute;left:70px;top:70px;font:800 52px/1.05 U8;color:#fff;max-width:520px">Facts you can check before you buy</div>'
    + "".join(f'<div class="chip" style="position:absolute;left:{70+(i%2)*330}px;top:{270+(i//2)*76}px;font-size:20px"><i>✓</i>{t}</div>' for i, t in enumerate(["$199.10 one time", "30-day guarantee", "Checkout via JVZoo", "Instant email login", "8,000 credits / mo", "No yearly renewal"]))), 1000, 560), 1000, 560, [1000])

# 8) OG image
SCENES["og-everpitch"] = (page(
    scene("linear-gradient(135deg,#FFF3EC,#FCD3BF)", '<div style="position:absolute;left:60px;top:70px;font-size:56px">' + LOGO + '</div>'
          '<div style="position:absolute;left:60px;top:170px;font:800 58px/1.06 U8;max-width:520px">AI webinars, written, voiced and hosted for you</div>'
          '<div class="chip" style="position:absolute;left:60px;top:470px;font-size:22px;background:#E8704F"><i>✓</i>Bundle: $199.10 one time</div>'
          f'<div style="position:absolute;left:560px;top:120px;transform:scale(.68);transform-origin:top left">{app_window()}</div>'), 1200, 630), 1200, 630, [1200])


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
        for name, (html, w, h, widths) in SCENES.items():
            pg = await b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
            tmp = pathlib.Path("/tmp") / f"{name}.html"
            tmp.write_text(html)
            await pg.goto(f"file://{tmp}")
            await pg.wait_for_timeout(250)
            png = await pg.screenshot(omit_background=True, full_page=False)
            await pg.close()
            im = Image.open(io.BytesIO(png)).convert("RGBA")
            for ww in widths:
                hh = round(h * ww / w)
                out = im.resize((ww, hh), Image.LANCZOS)
                suffix = "" if ww == widths[0] else f"-{ww}"
                path = OUT / f"{name}{suffix}.webp"
                out.save(path, "WEBP", quality=84, method=6)
                print(path.name, out.size, path.stat().st_size // 1024, "KB")
        await b.close()

asyncio.run(main())
