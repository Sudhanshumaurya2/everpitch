"""Static site generator for the EverPitch affiliate website.
Run: python3 build.py /home/claude/everpitch
All product facts come from the seller page https://everpitch.co/epbundle (researched 2026-11-19).
"""
import sys, json, pathlib, html, re, secrets

OUT = pathlib.Path(sys.argv[1])
DOMAIN = "https://everpitch.vercel.app"
AFFILIATE_URL = "https://www.jvzoo.com/c/1834263/461141"   # exact, unmodified
ORDER = "/order?package=bundle"
LASTMOD = "2026-11-19"
PRODUCT = "EverPitch"

NAV = [("What Is It", "/product-overview.html"), ("How It Works", "/how-it-works.html"), ("Benefits", "/benefits.html"),
       ("Focus Areas", "/focus-areas/index.html"), ("Reviews", "/reviews.html"), ("Blog", "/blog/index.html"), ("FAQ", "/faq.html")]

PAGES = []  # (path, title, desc, indexable)

# ---------------------------------------------------------------- icons
def ic(name):
    p = {
        "script": '<path d="M6 3h9l3 3v15H6z"/><path d="M9 9h6M9 13h6M9 17h4"/>',
        "slides": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M12 16v4M8 20h8"/>',
        "voice": '<path d="M12 3a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V6a3 3 0 0 1 3-3z"/><path d="M19 11a7 7 0 0 1-14 0M12 18v3"/>',
        "host": '<circle cx="12" cy="12" r="9"/><path d="M10 8.5l5 3.5-5 3.5z"/>',
        "chat": '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9h8M8 12h5"/>',
        "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/>',
        "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
        "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        "edit": '<path d="M4 20h4l11-11-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>',
        "kit": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18"/>',
        "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V4h6v3"/>',
        "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
        "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
        "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
        "upload": '<path d="M12 16V4M7 9l5-5 5 5"/><path d="M4 16v4h16v-4"/>',
        "video": '<rect x="3" y="6" width="13" height="12" rx="2"/><path d="M16 10l5-3v10l-5-3z"/>',
        "layers": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
        "gov": '<path d="M3 21h18M4 10h16M12 3l9 5H3z"/><path d="M6 10v8M10 10v8M14 10v8M18 10v8"/>',
        "doc": '<path d="M6 3h9l3 3v15H6z"/><path d="M9 12h6M9 16h6"/>',
        "ext": '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v6H4V6h6"/>',
        "x": '<path d="M6 6l12 12M18 6L6 18"/>',
        "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>',
        "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-3.6 3.4-5.5 6.5-5.5s5.7 1.9 6.5 5.5"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14.8c1.8.7 3 2.4 3.5 5.2"/>',
        "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
        "refresh": '<path d="M20 11a8 8 0 0 0-14.3-4.9L4 8M4 4v4h4M4 13a8 8 0 0 0 14.3 4.9L20 16M20 20v-4h-4"/>',
    }[name]
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{p}</svg>'

TRI = '<svg viewBox="0 0 10 12" aria-hidden="true"><path d="M0 0L10 6L0 12Z" fill="#E8704F"/></svg>'
LOGO = f'<a class="logo" href="/" aria-label="{PRODUCT} home">ever{TRI}pitch</a>'

def cta(label="Get the EverPitch Bundle", cls="btn-primary", name="generic", extra=""):
    return f'<a class="btn {cls}{extra}" href="{ORDER}" data-cta="{name}">{label} <span class="arrow" aria-hidden="true">→</span></a>'

def img(name, alt, w, h, cls="", lazy=True, sizes=None, small=None, priority=False):
    srcset = ""
    if small:
        srcset = f' srcset="/assets/img/{name}-{small}.webp {small}w, /assets/img/{name}.webp {w}w" sizes="{sizes or "(max-width: 700px) 92vw, 560px"}"'
    load = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high" decoding="async"'
    return f'<img src="/assets/img/{name}.webp"{srcset} width="{w}" height="{h}" alt="{html.escape(alt, quote=True)}"{load}{(" class=" + chr(34) + cls + chr(34)) if cls else ""}>'

# ---------------------------------------------------------------- shared chrome
def header(active):
    items = "".join(f'<li><a href="{u}"{" aria-current=" + chr(34) + "page" + chr(34) if u == active else ""}>{t}</a></li>' for t, u in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="container nav">{LOGO}
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav-links" aria-label="Open menu"><span></span></button>
<nav aria-label="Main"><ul class="nav-links" id="nav-links">{items}<li class="mobile-cta">{cta("Order Now", "btn-dark btn-sm btn-block", "nav-mobile")}</li></ul></nav>
<div class="nav-cta">{cta("Order Now", "btn-dark btn-sm", "nav")}</div></div></header>'''

def footer():
    return f'''<footer class="site-footer"><div class="container">
<div class="foot-grid">
<div>{LOGO.replace('class="logo"', 'class="logo"')}<p>An independent guide to EverPitch, the AI tool that writes, designs, voices and hosts webinars. We explain what the product does using the seller’s published details.</p></div>
<div><h3>Explore</h3><ul>{"".join(f'<li><a href="{u}">{t}</a></li>' for t, u in NAV)}</ul></div>
<div><h3>Guides</h3><ul>
<li><a href="/focus-areas/webinar-creation.html">AI script &amp; slide creation</a></li>
<li><a href="/focus-areas/automated-hosting-qa.html">Hosting &amp; spoken Q&amp;A</a></li>
<li><a href="/focus-areas/multilingual-webinars.html">Multilingual webinars</a></li>
<li><a href="/focus-areas/registration-follow-up.html">Registration &amp; follow-up</a></li>
<li><a href="/product-review.html">EverPitch review</a></li>
<li><a href="/blog/live-vs-evergreen-webinars.html">Live vs. evergreen webinars</a></li></ul></div>
<div><h3>Legal</h3><ul>
<li><a href="/affiliate-disclosure.html">Affiliate Disclosure</a></li>
<li><a href="/disclaimer.html">Disclaimer</a></li>
<li><a href="/privacy-policy.html">Privacy Policy</a></li>
<li><a href="/terms.html">Terms of Use</a></li>
<li><a href="/sitemap.xml">Sitemap</a></li></ul></div>
</div>
<div class="foot-legal">
<p>Independent affiliate website. This site is not owned or operated by EverPitch or JVZoo. If you buy through links on this site, the seller may pay us a commission. Read the <a href="/affiliate-disclosure.html">Affiliate Disclosure</a> for details.</p>
<p>Product names and trademarks belong to their owners. Results from any marketing tool depend on your offer, audience and effort. Prices and terms are set by the seller and can change.</p>
<p>© 2026 everpitch.vercel.app</p>
</div></div></footer>'''

MODAL = f'''<div class="ep-modal" id="ep-modal" role="dialog" aria-modal="true" aria-labelledby="ep-modal-title" hidden>
<div class="box">
<button class="x" type="button" aria-label="Close">{ic("x")}</button>
{img("everpitch-bundle-four-products", "EverPitch Bundle illustration showing Commercial, DFY Webinars, Kit Vault and Agency", 1060, 660, small=600, sizes="360px")}
<div class="kicker">The EverPitch Bundle</div>
<h2 id="ep-modal-title">Four products, switched on from day one</h2>
<p>EverPitch Commercial, DFY Webinars, Kit Vault and Agency, plus 8,000 credits every month.</p>
<div class="mprice">$199.10 <small>one-time payment</small></div>
<ul class="mini"><li>30-day money-back guarantee</li><li>No yearly renewal</li><li>Instant email login</li></ul>
<a class="btn btn-primary btn-block" href="{ORDER}" data-cta="modal">View the Bundle Offer <span class="arrow" aria-hidden="true">→</span></a>
</div></div>
<div class="ep-toast" id="ep-toast" role="status" aria-live="polite">
<div class="ok">{ic("check")}</div><div><b>EverPitch</b><span></span></div>
<button class="tx" type="button" aria-label="Dismiss notification">{ic("x")}</button></div>'''

def crumbs(trail):
    lis = "".join((f'<li><a href="{u}">{t}</a></li>' if u else f'<li aria-current="page">{t}</li>') for t, u in trail)
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{lis}</ol></nav>'

def breadcrumb_ld(trail, path):
    items = []
    for i, (t, u) in enumerate(trail, 1):
        items.append({"@type": "ListItem", "position": i, "name": t, "item": DOMAIN + (u if u else path)})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}

def write(path, title, desc, body, active=None, ld=None, index=True, og_img="og-everpitch", preload=None, no_promo=False, og_type="website"):
    assert len(title) <= 55, f"title too long ({len(title)}): {title}"
    assert len(desc) <= 155, f"description too long ({len(desc)}): {desc}"
    PAGES.append((path, title, desc, index))
    canonical = DOMAIN + ("/" if path == "/index.html" else path)
    robots = "index, follow, max-image-preview:large" if index else "noindex, follow"
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    pre = f'<link rel="preload" as="image" href="/assets/img/{preload}.webp" type="image/webp" fetchpriority="high">' if preload else ""
    doc = f'''<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{PRODUCT}">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{DOMAIN}/assets/img/{og_img}.webp">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FFFAF6">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/urbanist-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/hind-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
{pre}
<link rel="stylesheet" href="/assets/css/site.css">
{ld_html}
</head>
<body{" data-no-promo" if no_promo else ""}>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
{MODAL}
<script src="/assets/js/site.js" defer></script>
</body>
</html>'''
    f = OUT / path.lstrip("/")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(doc)

def final_cta(headline="Ready to let your best pitch run every day?", text="One payment of $199.10 switches on EverPitch Commercial, DFY Webinars, Kit Vault and Agency, with 8,000 credits a month and a 30-day money-back guarantee from the seller."):
    return f'''<section class="section"><div class="container"><div class="cta-band reveal">
<div><span class="eyebrow">The Bundle</span><h2>{headline}</h2><p>{text}</p>
<div class="price-line">$199.10 one time · no yearly renewal</div>
<div class="cta-row">{cta("Order Now", "btn-primary", "final")}<a class="btn btn-ghost" href="/faq.html">Read the FAQ</a></div></div>
<div>{img("everpitch-bundle-four-products", "Illustration of the four EverPitch Bundle products stacked: Commercial, DFY Webinars, Kit Vault and Agency", 1060, 660, small=600)}</div>
</div></div></section>'''

def page_hero(trail, eyebrow, h1, lead, image=None, alt="", w=1000, h=560, small=None, extra=""):
    right = f'<div class="media plain">{img(image, alt, w, h, lazy=False, small=small)}</div>' if image else ""
    return f'''<section class="page-hero"><div class="container">{crumbs(trail)}
<div class="split"><div><span class="eyebrow">{eyebrow}</span><h1>{h1}</h1><p class="lead">{lead}</p>{extra}<div class="cta-row">{cta("Get the EverPitch Bundle", "btn-primary", "page-hero")}</div></div>
<div>{right}</div></div></div></section>'''

def card(icon, title, text, cls="card tilt reveal"):
    return f'<div class="{cls}"><div class="icon">{ic(icon)}</div><h3>{title}</h3><p>{text}</p></div>'

SOFTWARE_LD = {
    "@context": "https://schema.org", "@type": "SoftwareApplication", "name": "EverPitch Bundle",
    "applicationCategory": "BusinessApplication", "operatingSystem": "Web browser",
    "description": "AI webinar software that writes the script, designs the slides, adds natural AI narration, then presents the webinar daily and answers viewer questions out loud.",
    "image": DOMAIN + "/assets/img/everpitch-bundle-four-products.webp",
    "offers": {"@type": "Offer", "price": "199.10", "priceCurrency": "USD", "url": DOMAIN + "/order?package=bundle", "availability": "https://schema.org/InStock"},
}

# ---------------------------------------------------------------- data (verified from seller page)
FEATURES = [
    ("script", "AI-written webinar scripts", "A structured talk with an opening, the teaching and a natural move to your offer, drafted from your topic or material."),
    ("slides", "AI-designed slides", "73 slide layouts and 11 visual styles, with AI slide images, your logo and brand colours, and PDF deck import."),
    ("voice", "Natural AI narration", "30 AI voices across 87 languages, so you never need to record yourself or appear on camera."),
    ("host", "Automated daily hosting", "The webinar runs on flexible schedules, shown in each viewer’s local timezone, on a shared clock."),
    ("chat", "Spoken AI Q&amp;A", "Questions get answered out loud from your webinar’s own content, up to 20 free spoken answers per session."),
    ("mail", "Pages and emails included", "Registration pages, reminder and follow-up emails, and replay sales pages are created around each webinar."),
]

FAQS = [
    ("The Bundle", [
        ("What is EverPitch?", "EverPitch is AI webinar software. You give it a topic, a document, a link or a recording, and it creates the script, the slides and the voice-over. Once you have reviewed it, EverPitch presents the webinar on a schedule and answers viewers’ questions out loud. See the <a href=\"/product-overview.html\">product overview</a>."),
        ("What is included in the EverPitch Bundle?", "EverPitch Commercial, DFY Webinars, Kit Vault and Agency, with 8,000 credits a month and three bonuses: The First 7 Days Playbook, The Webinar Title &amp; Hook Bank and The After-Webinar Email Pack."),
        ("How much does the Bundle cost?", "The seller lists the Bundle at $199.10 as a one-time payment, with no yearly renewal. Bought separately, the seller lists the first-year total at $307.10. Always check the final price at checkout."),
        ("Is Ultra included?", "No. According to the seller, Ultra (streaming, MP4 export, host on camera and voice calls) is sold separately. Done-for-you webinars are already part of the Bundle."),
        ("Can I buy EverPitch on its own?", "Yes. The seller offers EverPitch on its own as a one-time payment, with upgrades available after checkout. This site links to the Bundle offer."),
    ]),
    ("Getting started", [
        ("Do I need technical skills?", "No. You describe your webinar in plain words, pick a kit, or upload something you already have. There is nothing to install. The <a href=\"/how-it-works.html\">How It Works</a> page walks through the three steps."),
        ("How do I get my login after buying?", "Right after checkout the seller emails you a link to set up your EverPitch account. You choose a password and everything in the Bundle is already switched on."),
        ("Do I have to appear on camera?", "No. EverPitch writes, designs and voices the whole webinar, so you never have to record yourself. If you want to, you can add on-camera clips of yourself made from one photo."),
    ]),
    ("Credits", [
        ("What are credits used for?", "Credits pay for building webinars, at 40 credits per finished minute. A 15-minute webinar uses about 600. Extra languages and extra AI images use a few more."),
        ("How many credits does the Bundle include?", "8,000 credits a month (about 200 finished minutes), compared with 3,000 for EverPitch on its own. Credits refresh every month."),
        ("What happens if I run out of credits?", "Webinars you have already built keep running. New builds wait until your credits refresh the next month."),
        ("Do viewer questions cost credits?", "No. Spoken answers during a session are included, up to 20 answers per session."),
    ]),
    ("Using it for your business", [
        ("Is an EverPitch webinar really live?", "The talk is prepared in advance and played on a shared clock, so everyone in a session sees the same moment. Questions are answered on the spot from your content. A simulated audience is optional, and when it is switched on, your registration page says so."),
        ("What if the AI host gets a fact wrong?", "Answers come only from what is in your webinar, and you can read and edit every line of the script before going live. Spam and abuse in the chat are screened before anything is read out."),
        ("Can I use EverPitch for client work?", "Every account can add its own logo, name and colour. Agency, included in the Bundle, adds the licence to make and run webinars for clients and removes “Powered by EverPitch” from the pages. Read more in <a href=\"/benefits.html\">Benefits</a>."),
        ("Can I clone someone’s voice?", "Only with their consent. When you clone a voice from a recording, you confirm that the speaker has agreed. Answers are then spoken in that voice."),
    ]),
    ("Ordering and refunds", [
        ("Is there a money-back guarantee?", "Yes. The seller offers a 30-day money-back guarantee. If the Bundle is not right for you, email support within 30 days of buying and the refund goes back through JVZoo. No reason is required."),
        ("Where does the purchase happen?", "Checkout is handled securely by JVZoo, the seller’s payment platform. This website does not process payments. The Order Now buttons take you to our <a href=\"/order?package=bundle\">order page</a>, which forwards you to the official checkout."),
        ("Who is this website?", "This is an independent affiliate website, not the EverPitch team. If you buy through our links, the seller may pay us a commission. See our <a href=\"/affiliate-disclosure.html\">Affiliate Disclosure</a>."),
    ]),
]

def faq_html(groups, limit=None):
    out = []
    n = 0
    for g, items in groups:
        block = []
        for q, a in items:
            if limit and n >= limit: break
            block.append(f'<details><summary>{q}</summary><div class="a"><p>{a}</p></div></details>')
            n += 1
        if block:
            out.append(("" if limit else f'<h3 class="faq-group">{g}</h3>') + "".join(block))
    return f'<div class="faq">{"".join(out)}</div>'

def faq_ld(groups):
    qs = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for _, items in groups for q, a in items]
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": qs}

REFS = [
    ("FTC", "FTC’s Endorsement Guides: What People Are Asking", "https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking",
     "Plain-language FTC answers on disclosing material connections in endorsements and testimonials. Relevant if you feature customer stories in a webinar.", "US Government Guidance"),
    ("FTC", "The Consumer Reviews and Testimonials Rule: Questions and Answers", "https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers",
     "Explains the rule, in effect since October 21, 2024, that prohibits fake reviews and testimonials, including AI-generated ones.", "US Government Guidance"),
    ("FTC", "Disclosures 101 for Social Media Influencers", "https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers",
     "FTC basics on when and how to disclose a paid relationship. Useful if affiliates or partners promote your webinars.", "US Government Guidance"),
    ("FTC", "CAN-SPAM Act: A Compliance Guide for Business", "https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business",
     "The rules for commercial email, including accurate headers and an opt-out. Relevant to webinar reminder and follow-up emails.", "US Government Guidance"),
    ("FTC Business Blog", "Keep your AI claims in check", "https://www.ftc.gov/business-guidance/blog/2023/02/keep-your-ai-claims-check",
     "FTC staff guidance on making truthful, evidence-backed claims about AI products, for anyone selling with or about AI.", "US Government Guidance"),
    ("FTC Office of Technology", "Preventing the Harms of AI-enabled Voice Cloning", "https://www.ftc.gov/policy/advocacy-research/tech-at-ftc/2023/11/preventing-harms-ai-enabled-voice-cloning",
     "Background on the risks of voice cloning and the FTC’s Voice Cloning Challenge. Relevant to consent-based AI voice features.", "US Government Research"),
    ("FTC", "Protecting Personal Information: A Guide for Business", "https://www.ftc.gov/business-guidance/resources/protecting-personal-information-guide-business",
     "Five principles for handling personal data: take stock, scale down, lock it, pitch it, plan ahead. Useful when you collect registrations.", "US Government Guidance"),
    ("U.S. Small Business Administration", "Marketing and sales", "https://www.sba.gov/business-guide/manage-your-business/marketing-sales",
     "SBA guidance on writing a marketing plan: target market, competitive advantage, sales plan, budget and measuring results.", "US Government Resource"),
    ("NIST", "AI Risk Management Framework", "https://www.nist.gov/itl/ai-risk-management-framework",
     "NIST’s voluntary framework for managing risks in the design, development and use of AI systems.", "Government Scientific Publication"),
    ("NIST", "AI RMF: Generative Artificial Intelligence Profile (NIST AI 600-1)", "https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence",
     "A companion profile to the AI RMF that addresses generative AI, the category of tool that writes scripts and synthesises voices.", "Government Scientific Publication"),
]

def refs_html():
    cards = "".join(f'''<article class="card ref reveal"><div class="src">{ic("gov" if "Publication" not in t else "doc")}<span>{s}</span></div>
<span class="tag">{t}</span><h3 class="mt-2">{ti}</h3><p>{d}</p>
<a class="ext" href="{u}" target="_blank" rel="noopener noreferrer" aria-label="View source: {html.escape(ti, quote=True)} (opens in a new tab)">View Source {ic("ext")}</a></article>''' for s, ti, u, d, t in REFS)
    return f'''<section class="section section-soft" id="references"><div class="container">
<div class="section-head"><span class="eyebrow">Further reading</span><h2>References &amp; Research</h2>
<p>Government guidance and research related to the topics on this site: AI tools, voice cloning, testimonials, marketing email and customer data.</p></div>
<div class="grid g3">{cards}</div>
<p class="note">These references are provided for educational purposes only. They do not represent an endorsement or approval of this product by any government agency. Guidance on a topic does not establish how well any specific product performs.</p>
</div></section>'''

# ================================================================ HOME
def home():
    body = f'''
<section class="hero"><div class="container hero-grid">
<div>
<span class="eyebrow">AI webinar software · one-time payment</span>
<h1>EverPitch: AI Webinars <span class="hl">Written, Voiced and Hosted for You</span></h1>
<p class="lead">Give EverPitch a topic, a document, a link or an old recording. It drafts the script, designs the slides and adds a natural voice. Then it runs your webinar every day and answers viewers’ questions out loud.</p>
<dl class="spec">
<div><dt>Format</dt><dd>Web app, nothing to install</dd></div>
<div><dt>Starts from</dt><dd>An idea, document, URL, PDF deck or recording</dd></div>
<div><dt>Creates</dt><dd>Script, slides, AI narration, pages and emails</dd></div>
<div><dt>Bundle price</dt><dd>$199.10 one time · no yearly renewal</dd></div>
<div><dt>Guarantee</dt><dd>30-day money-back, refunded through JVZoo</dd></div>
</dl>
<div class="cta-row">{cta("Get the EverPitch Bundle", "btn-primary", "hero")}<a class="btn btn-ghost" href="/product-overview.html">What is EverPitch?</a></div>
<div class="trust"><span>{ic("shield")} 30-day guarantee</span><span>{ic("lock")} Secure checkout via JVZoo</span><span>{ic("bolt")} Instant email login</span></div>
</div>
<div class="stage" data-tilt-stage>
<div class="stage-bg" aria-hidden="true"></div>
<span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
<div class="chip back c5" aria-hidden="true"><i>¶</i>AI scripts</div>
<div class="chip c1" aria-hidden="true"><i>▦</i>73 slide layouts</div>
<div class="chip c2" aria-hidden="true"><i>◍</i>87 languages</div>
<div class="chip c3" aria-hidden="true"><i>◉</i>30 AI voices</div>
<div class="chip c4" aria-hidden="true"><i>❝</i>Spoken Q&amp;A</div>
<div class="product">{img("everpitch-ai-webinar-software-mockup", "EverPitch webinar room illustration: AI-designed slide, narration waveform and live chat answered by the AI host", 980, 560, lazy=False, small=560)}</div>
<div class="stage-badge">4 products · $199.10 once</div>
</div>
</div></section>

<section class="section"><div class="container split">
<div class="reveal"><div class="media plain">{img("everpitch-features-composition", "EverPitch webinar room surrounded by its core features: AI scripts, slide layouts, voices, languages, Q&A, emails, demos and timezones", 1200, 720, small=640)}</div></div>
<div class="reveal"><span class="eyebrow">EverPitch in about a minute</span>
<h2>One tool for the whole webinar, not just one piece of it</h2>
<p>Most webinar tools handle one job. One writes, one designs slides, one streams the session, and you still have to rehearse, present and handle questions yourself. EverPitch puts those jobs in one place.</p>
<p>You bring the expertise and the offer. EverPitch turns them into a finished presentation you can read and edit line by line, then presents it on a schedule in each viewer’s timezone. Registration pages, reminder emails and a replay sales page are built for each webinar.</p>
<ul class="checks"><li>No scriptwriting, slide design or recording needed</li><li>Edit any slide just by asking</li><li>Drop in a product demo video at the right moment</li></ul>
<div class="cta-row"><a class="btn btn-ghost" href="/product-overview.html">Read the full overview <span class="arrow" aria-hidden="true">→</span></a><a class="btn btn-ghost" href="/product-review.html">Read our EverPitch review</a></div></div>
</div></section>

<section class="section section-soft"><div class="container">
<div class="section-head"><span class="eyebrow">How it fits your week</span><h2>From an idea to a webinar that runs every day</h2>
<p>EverPitch splits the work into four simple stages. You keep control of the message; the tool does the production.</p></div>
<div class="grid g4">
{card("edit", "Created for you", "Describe the webinar, attach a PDF or upload a recording. The talk, slides and voice come back as a first draft.")}
{card("layers", "Customised by you", "Read every line, change any slide by asking, add your logo and colours, and insert a demo video.")}
{card("host", "Presented for you", "EverPitch hosts the session on your schedule and answers questions out loud from your content.")}
{card("mail", "Marketing included", "Each webinar gets a registration page, reminder and follow-up emails, and a replay sales page.")}
</div></div></section>

<section class="section"><div class="container">
<div class="section-head"><span class="eyebrow">Focus areas</span><h2>Four areas where EverPitch does the heavy lifting</h2>
<p>Each guide explains one part of the product in detail, using the seller’s published specifications.</p></div>
<div class="grid g4">
{"".join(f'<a class="card tilt reveal card-link" href="/focus-areas/{s}.html"><div class="icon">{ic(i)}</div><h3>{t}</h3><p>{d}</p><span class="more">Read the guide →</span></a>' for s, i, t, d in [
 ("webinar-creation", "script", "Script &amp; slide creation", "How EverPitch drafts the talk and designs the deck from an idea, a document or a recording."),
 ("automated-hosting-qa", "chat", "Hosting &amp; spoken Q&amp;A", "Daily sessions on a shared clock, viewer-local times, and a host that answers out loud."),
 ("multilingual-webinars", "globe", "Multilingual webinars", "Translated, re-voiced copies in 87 languages, linked together with combined analytics."),
 ("registration-follow-up", "mail", "Registration &amp; follow-up", "Pages, reminders, calendar invites and replay pages that surround each webinar.")])}
</div></div></section>

<section class="section section-soft" id="compare"><div class="container">
<div class="section-head"><span class="eyebrow">Product details</span><h2>EverPitch on its own vs. the Bundle</h2>
<p>Both are one-time payments. The Bundle switches on three more products and raises your monthly credits. Figures are as published by the seller.</p></div>
<div class="table-wrap reveal"><table>
<caption class="sr-only">Comparison of EverPitch on its own and the EverPitch Bundle</caption>
<thead><tr><th scope="col">Feature</th><th scope="col">EverPitch on its own</th><th scope="col" class="bundle-col">The Bundle</th></tr></thead>
<tbody>
<tr><th scope="row">Credits every month</th><td>3,000</td><td class="bundle-col">8,000</td></tr>
<tr><th scope="row">Finished minutes, about</th><td>75</td><td class="bundle-col">200</td></tr>
<tr><th scope="row">Done-for-you webinars</th><td class="no">Not included</td><td class="yes bundle-col">10</td></tr>
<tr><th scope="row">Ready-made webinar kits</th><td class="no">Not included</td><td class="yes bundle-col">24</td></tr>
<tr><th scope="row">Your own logo, name and colour</th><td class="yes">Included</td><td class="yes bundle-col">Included</td></tr>
<tr><th scope="row">Client licence</th><td class="no">Not included</td><td class="yes bundle-col">Included</td></tr>
<tr><th scope="row">Remove “Powered by EverPitch”</th><td class="no">Not included</td><td class="yes bundle-col">Included</td></tr>
</tbody></table></div>
<p class="small center mt-2">Ultra (streaming, MP4 export, host on camera and voice calls) is sold separately and is not part of the Bundle.</p>
</div></section>

<section class="section"><div class="container">
<div class="section-head"><span class="eyebrow">Benefits</span><h2>What EverPitch takes off your plate</h2>
<p>The features below are listed on the seller’s page. What you get out of them depends on your offer and your audience.</p></div>
<div class="grid g3">{"".join(card(i, t, d) for i, t, d in FEATURES)}</div>
<div class="center mt-4"><a class="btn btn-ghost" href="/benefits.html">See every benefit <span class="arrow" aria-hidden="true">→</span></a></div>
</div></section>

<section class="section section-soft"><div class="container">
<div class="section-head"><span class="eyebrow">How to use it</span><h2>Up and running in three steps</h2></div>
<div class="steps">
<div class="card step reveal"><h3>Describe it, or pick a kit</h3><p>Type what the webinar is about, attach a PDF, upload a recording, or start from one of 24 ready-made kits.</p></div>
<div class="card step reveal"><h3>Review it</h3><p>The talk, slides and voice come back. Change any slide by asking, and add on-camera clips of yourself made from one photo.</p></div>
<div class="card step reveal"><h3>Share it everywhere</h3><p>Pick a registration page and share the link, or embed a join button on your website.</p></div>
</div>
<div class="center mt-4"><a class="btn btn-ghost" href="/how-it-works.html">See how it works <span class="arrow" aria-hidden="true">→</span></a></div>
</div></section>

<section class="section"><div class="container split rev">
<div class="reveal"><div class="grid g2">
{card("target", "A clear offer", "EverPitch presents your offer; it cannot invent one. Know who it is for and what it costs.", "card reveal")}
{card("users", "A real audience", "Webinars need visitors. Plan where registrations will come from: your list, content or ads.", "card reveal")}
{card("shield", "Honest claims", "Every line in your script is yours to check. Keep results claims accurate and disclosures clear.", "card reveal")}
{card("refresh", "Steady iteration", "Watch the numbers, change one thing at a time, and let the next week’s sessions show what worked.", "card reveal")}
</div></div>
<div class="reveal"><span class="eyebrow">Good habits</span><h2>What still depends on you</h2>
<p>EverPitch removes the production work: scripting, slide design, recording and presenting. It does not replace the fundamentals of selling. The best results come when the tool is paired with a well-defined offer, honest messaging and a steady source of visitors.</p>
<p>The <a href="/blog/index.html">EverPitch blog</a> covers these habits in more depth, from structuring a script to writing respectful follow-up emails.</p></div>
</div></section>

<section class="section section-ink"><div class="container">
<div class="section-head"><span class="eyebrow">At a glance</span><h2>The numbers behind the Bundle</h2><p>Specifications published by the seller. These are product facts, not customer ratings.</p></div>
<div class="grid g4 center">
{"".join(f'<div class="reveal"><div class="stat" style="color:#fff">{n}</div><div class="stat-label" style="color:#D9CCC5">{l}</div></div>' for n, l in [("73", "slide layouts"), ("11", "visual styles"), ("30", "AI voices"), ("87", "languages"), ("24", "webinar kits"), ("10", "done-for-you webinars"), ("8,000", "credits a month"), ("20", "free spoken answers per session")])}
</div>
<p class="center mt-4" style="color:#D9CCC5">Want an independent take? <a href="/product-review.html" style="color:#F4B860">Read our EverPitch review</a> or see <a href="/reviews.html" style="color:#F4B860">what we found on customer reviews</a>.</p>
</div></section>

<section class="section" id="pricing"><div class="container">
<div class="section-head"><span class="eyebrow">Pricing</span><h2>Everything in one payment</h2><p>The seller offers the Bundle as a single, one-time purchase through JVZoo.</p></div>
<div class="pricing-grid">
<div class="reveal">{img("everpitch-bundle-four-products", "EverPitch Bundle illustration: four stacked product windows labelled Commercial, DFY Webinars, Kit Vault and Agency, with 8,000 credits a month", 1060, 660, small=600)}</div>
<div class="price-card tilt reveal"><span class="ribbon">Best value</span>
<h3>The EverPitch Bundle</h3>
<p class="small">Commercial + DFY Webinars + Kit Vault + Agency + three bonuses</p>
<div><span class="was">$307.10</span> <span class="save">Save $108.00</span></div>
<div class="price mt-0">$199.10<small>one time</small></div>
<ul class="breakdown">
<li><span>EverPitch Commercial</span><span>$39.10</span></li>
<li><span>DFY Webinars</span><span>$67.00</span></li>
<li><span>Webinar Kit Vault</span><span>$47.00</span></li>
<li><span>Agency</span><span>$77.00</span></li>
<li><span>Credit Boost (8,000)</span><span>$77.00</span></li>
<li class="total"><span>First-year total if bought separately</span><span>$307.10</span></li>
</ul>
<ul class="checks mt-2"><li>Instant access, login by email</li><li>30-day money-back guarantee</li><li>One payment, no renewal</li></ul>
{cta("Order the Bundle", "btn-primary btn-block", "pricing")}
</div></div></div></section>

<section class="section section-soft"><div class="container">
<div class="guarantee reveal"><div class="seal"><div><b>30</b><span>Day money-back</span></div></div>
<div><h2>Use all of it for 30 days, then decide</h2>
<p>Build a webinar, try a done-for-you one, open a kit and watch the room work. If the Bundle isn’t right for you, the seller asks you to email support within 30 days of buying, and your money goes back through JVZoo.</p>
<ul class="checks"><li>No reason needed</li><li>A full 30 days to try everything</li><li>Refunded the way you paid, through JVZoo</li></ul></div></div>
</div></section>

<section class="section"><div class="container">
<div class="section-head"><span class="eyebrow">From the blog</span><h2>Short reads for better webinars</h2></div>
<div class="grid g3">{blog_cards()}</div>
</div></section>

<section class="section section-soft"><div class="container narrow">
<div class="section-head"><span class="eyebrow">FAQ</span><h2>Questions before you order</h2></div>
{faq_html(FAQS, limit=8)}
<div class="center mt-4 cta-row" style="justify-content:center"><a class="btn btn-ghost" href="/faq.html">All questions <span class="arrow" aria-hidden="true">→</span></a><a class="btn btn-ghost" href="/product-review.html">Read our EverPitch review</a></div>
</div></section>

{refs_html()}
{final_cta("Start your first EverPitch webinar this week")}
'''
    website = {"@context": "https://schema.org", "@type": "WebSite", "name": PRODUCT, "url": DOMAIN + "/"}
    write("/index.html", "EverPitch | AI Webinar Software Bundle",
          "EverPitch writes, designs, voices and hosts your webinar, then answers questions out loud. See features, the $199.10 Bundle and the 30-day guarantee.",
          body, active=None, ld=[website, SOFTWARE_LD], preload="everpitch-ai-webinar-software-mockup")

# ================================================================ BLOG
POSTS = [
    ("live-vs-evergreen-webinars", "Live vs. Evergreen Webinars: Which Fits Your Business?", "blog-evergreen-webinar-guide",
     "Live vs Evergreen Webinars | EverPitch", "Live or evergreen webinar? Compare effort, scheduling, Q&A and honesty rules to choose the format that suits your offer and your week.",
     "Webinar strategy", "Illustrated cover for the article comparing live and evergreen webinars"),
    ("webinar-script-structure", "How to Structure a Webinar Script That Sells Without Pushing", "blog-webinar-script-structure",
     "Webinar Script Structure That Sells | EverPitch", "A practical webinar script outline: hook, promise, teaching, proof, offer and Q&A, with tips for keeping claims honest and the pitch natural.",
     "Scripting", "Illustrated cover for the article on structuring a webinar script"),
    ("webinar-follow-up-emails", "After the Webinar: A Follow-Up Email Plan That Respects People", "blog-webinar-follow-up-emails",
     "Webinar Follow-Up Emails Plan | EverPitch", "Plan webinar follow-up emails for attendees, early leavers and no-shows, with timing ideas and the CAN-SPAM basics to keep in mind.",
     "Email follow-up", "Illustrated cover for the article on webinar follow-up emails"),
]

def blog_cards():
    return "".join(f'''<a class="card tilt reveal card-link post-card" href="/blog/{s}.html">{img(im, alt, 1000, 560, small=600, sizes="(max-width:640px) 92vw, 360px")}
<div class="body"><div class="meta">{k}</div><h3>{h}</h3><span class="more">Read article →</span></div></a>''' for s, h, im, _, _, k, alt in POSTS)

ARTICLES = {
"live-vs-evergreen-webinars": '''
<p>A webinar is one of the few marketing formats that holds someone’s full attention for twenty minutes or more. That is long enough to explain a service, show a product and answer doubts before you ask for a decision. The question most businesses get stuck on is not <em>whether</em> to run webinars but <em>how</em>: live each time, or recorded once and replayed on a schedule.</p>
<h2>What a live webinar gives you</h2>
<p>Live sessions feel immediate. You can read the room, react to questions and adjust the pitch in real time. For a product launch, a one-off announcement or a small, high-value audience, that flexibility is worth a lot.</p>
<p>The cost is your calendar. Every session needs preparation, rehearsal and a presenter at a fixed time, which usually suits one timezone better than the others. When the session ends, anyone who missed it gets a replay that can’t answer them back.</p>
<h2>What an evergreen webinar gives you</h2>
<p>An evergreen webinar is prepared once and shown repeatedly, often daily. People can join at a time that suits them, and your best version of the pitch runs every time. The trade-off has traditionally been interaction: a plain recording cannot respond to a question.</p>
<p>Tools such as <a href="/focus-areas/automated-hosting-qa.html">EverPitch’s automated hosting</a> try to close that gap. The talk plays on a shared clock so everyone in a session sees the same moment, and an AI host answers questions out loud from the webinar’s own content.</p>
<h2>A simple way to choose</h2>
<ul>
<li><strong>Choose live</strong> when the content changes every time, when the audience is small and valuable, or when the event itself is the news.</li>
<li><strong>Choose evergreen</strong> when you explain the same offer again and again, when your audience spans timezones, or when you can’t present every day.</li>
<li><strong>Combine them</strong> by running one live session, then turning the recording into an evergreen webinar. EverPitch can import a recording of up to 2 GB and either keep the full video or cut a shorter version.</li>
</ul>
<div class="callout"><h3>Be upfront about the format</h3><p>Viewers deserve to know what they are watching. Avoid implying that a pre-recorded session is happening live for the first time. If you use features such as a simulated audience, say so. EverPitch adds a note to the registration page when that option is on. The FTC’s guidance on endorsements and reviews, listed in our <a href="/#references">references</a>, is a useful read for anyone selling through webinars.</p></div>
<h2>Where to start</h2>
<p>If you already have a pitch you repeat on sales calls, that is the best candidate for an evergreen webinar. Write down the questions prospects ask most often; they become the content the host draws on when answering. Then decide how often sessions should run and where your registrations will come from.</p>
''',
"webinar-script-structure": '''
<p>A good webinar script is a teaching session with a clear destination. People sign up to learn something. If you give them that, the offer at the end feels like a natural next step rather than a bait-and-switch. Here is an outline you can adapt to almost any topic.</p>
<h2>1. The hook (first two minutes)</h2>
<p>Name the problem in the audience’s own words and say what they will leave with. Keep it specific: “three changes to your booking page” is more convincing than “grow your business.”</p>
<h2>2. Why you, and why now</h2>
<p>Briefly explain your experience with the problem. Keep it short and factual. Don’t claim results you can’t back up.</p>
<h2>3. The teaching (the core)</h2>
<p>Deliver two to four genuinely useful ideas. Each should stand on its own, so someone who never buys still leaves better off. That generosity builds the trust the offer relies on.</p>
<h2>4. Proof that is honest</h2>
<p>Examples, demos and case studies help, but they must be real and typical, or clearly labelled when they are not. Since October 2024 the FTC’s rule on consumer reviews and testimonials has prohibited fake testimonials, including AI-generated ones. Use real customer words, with permission, or none at all.</p>
<h2>5. The bridge to the offer</h2>
<p>Connect the last teaching point to what you sell: “You can do all of this yourself, or here is how we help.” If you have a product demo, this is the moment for it. EverPitch can <a href="/focus-areas/webinar-creation.html">insert a demo video</a> with a short spoken lead-in at the point in the talk where it fits.</p>
<h2>6. The offer, plainly stated</h2>
<p>Say what it is, who it is for, what it costs and what happens after purchase. Mention the guarantee if there is one. Clarity converts better than pressure, and invented deadlines erode trust.</p>
<h2>7. Questions</h2>
<p>Leave time for questions, and prepare answers to the common ones in advance. In an evergreen format, the host can only answer from what is in your content, so writing a short FAQ into the webinar improves those answers.</p>
<div class="callout"><h3>Using AI to draft the script</h3><p>AI tools can produce a solid first draft quickly, but you are still responsible for every claim in it. Read the whole script, cut anything you can’t stand behind, and add your real examples. EverPitch lets you edit every line before you share the webinar. See the <a href="/how-it-works.html">How It Works</a> page.</p></div>
''',
"webinar-follow-up-emails": '''
<p>Most webinar sign-ups don’t buy during the session, and many don’t attend at all. Follow-up emails are where a lot of the value is recovered, but only if they are useful, well-timed and easy to opt out of.</p>
<h2>Segment by what people actually did</h2>
<ul>
<li><strong>Stayed to the end:</strong> they heard the offer. Send a short recap, answer the main objection, and include the link.</li>
<li><strong>Left early:</strong> they missed the most important part. Point them to the moment they missed rather than the whole replay.</li>
<li><strong>Registered but didn’t attend:</strong> a simple “here’s the replay” works better than a guilt trip.</li>
<li><strong>Asked a question:</strong> answer it personally if you can. It is often the highest-intent group.</li>
</ul>
<h2>Timing that feels helpful</h2>
<p>A reasonable rhythm is a replay or recap within a day, a useful follow-up a couple of days later, and a final reminder before any real deadline. If there is no genuine deadline, don’t invent one.</p>
<h2>Keep it legal and respectful</h2>
<p>In the US, the CAN-SPAM Act applies to commercial email. Among other things, it requires accurate “From” and subject lines, a valid physical postal address, and a clear way to opt out that you honour promptly. The FTC’s compliance guide is in our <a href="/#references">references</a>. Other countries have their own rules, so check the ones that apply to your list.</p>
<h2>What EverPitch provides</h2>
<p>Each EverPitch webinar comes with reminder and follow-up emails written for its topic, plus a replay sales page. The Bundle also includes a bonus called <em>The After-Webinar Email Pack</em>: seven ready-to-edit follow-ups for people who stayed, left early, missed the session or still have a question. Leads go to your own list. Learn more in <a href="/focus-areas/registration-follow-up.html">Registration &amp; Follow-Up</a>.</p>
<div class="callout"><h3>One rule of thumb</h3><p>Write every follow-up as if the reader will reply. If an email would be awkward to send to one person you know, it is probably wrong for your whole list too.</p></div>
''',
}

def blog():
    trail = [("Home", "/"), ("Blog", None)]
    body = f'''<section class="page-hero"><div class="container">{crumbs(trail)}
<div class="section-head" style="margin-bottom:0"><span class="eyebrow">EverPitch blog</span><h1>Practical guides to webinars that sell</h1>
<p class="lead">Original, plain-English articles on webinar strategy, scripting and follow-up, written for coaches, consultants, course creators, agencies and software teams.</p></div></div></section>
<section class="section"><div class="container"><div class="grid g3">{blog_cards()}</div></div></section>
{final_cta()}'''
    ld = [breadcrumb_ld(trail, "/blog/index.html"),
          {"@context": "https://schema.org", "@type": "Blog", "name": "EverPitch blog", "url": DOMAIN + "/blog/index.html",
           "blogPost": [{"@type": "BlogPosting", "headline": h, "url": f"{DOMAIN}/blog/{s}.html"} for s, h, *_ in POSTS]}]
    write("/blog/index.html", "EverPitch Blog | Webinar Marketing Guides",
          "Practical webinar marketing guides: live vs evergreen webinars, script structure and follow-up emails, written to help you sell with clarity.",
          body, active="/blog/index.html", ld=ld)
    for s, h, im, title, desc, k, alt in POSTS:
        path = f"/blog/{s}.html"
        trail = [("Home", "/"), ("Blog", "/blog/index.html"), (h, None)]
        others = "".join(f'<li><a href="/blog/{s2}.html">{h2}</a></li>' for s2, h2, *_ in POSTS if s2 != s)
        body = f'''<section class="page-hero"><div class="container narrow">{crumbs(trail)}
<span class="eyebrow">{k}</span><h1>{h}</h1>
<div class="article-meta"><span>Published November 19, 2026</span><span>By the everpitch.vercel.app editorial team</span></div></div></section>
<section class="section-sm"><div class="container narrow">
<div class="media plain">{img(im, alt, 1000, 560, lazy=False, small=600, sizes="(max-width:860px) 92vw, 780px")}</div>
<article class="prose mt-4">{ARTICLES[s]}
<h2>Keep reading</h2><ul>{others}<li><a href="/product-review.html">Our EverPitch review: pros, cons and verdict</a></li><li><a href="/product-overview.html">What is EverPitch?</a></li><li><a href="/faq.html">EverPitch FAQ</a></li></ul>
</article>
<div class="callout"><h3>Try it with your own topic</h3><p>The EverPitch Bundle is a one-time $199.10 payment with a 30-day money-back guarantee from the seller.</p>{cta("See the Bundle offer", "btn-primary", "article")}</div>
</div></section>'''
        ld = [breadcrumb_ld(trail, path), {"@context": "https://schema.org", "@type": "Article", "headline": h, "datePublished": LASTMOD, "dateModified": LASTMOD,
               "image": f"{DOMAIN}/assets/img/{im}.webp", "author": {"@type": "Organization", "name": "everpitch.vercel.app editorial team", "url": DOMAIN + "/"},
               "publisher": {"@type": "Organization", "name": "everpitch.vercel.app", "url": DOMAIN + "/"}, "mainEntityOfPage": DOMAIN + path}]
        write(path, title, desc, body, active="/blog/index.html", ld=ld, og_img=im, og_type="article")

# ================================================================ OVERVIEW
def overview():
    trail = [("Home", "/"), ("What Is It", None)]
    body = page_hero(trail, "Product overview", "What Is EverPitch? The AI Webinar Builder Explained",
        "EverPitch is cloud software that turns your knowledge and your offer into a complete webinar, then presents it for you every day. Here is what it is, what it makes, and what the Bundle adds.",
        "everpitch-features-composition", "EverPitch webinar room illustration surrounded by its features: scripts, slide layouts, voices, languages, Q&A and reminder emails", 1200, 720, small=640) + f'''
<section class="section"><div class="container split">
<div class="reveal"><h2>The short version</h2>
<p>Creating a webinar normally means a stack of jobs: planning the pitch, writing the script, building slides, preparing demos, rehearsing, presenting, handling questions and preparing the replay. EverPitch is built to take on each of those jobs.</p>
<p>You start from whatever you have: a one-line idea, a document, a web page, a PDF deck or an old Zoom recording. EverPitch drafts the talk, designs the slides and narrates them in a natural AI voice. You review and edit everything. Then EverPitch hosts it on a schedule and answers viewers’ questions out loud, using only your content.</p>
<p>Want to see the stages in order? Read <a href="/how-it-works.html">How It Works</a>, or jump to the <a href="/benefits.html">benefits</a>.</p></div>
<div class="reveal"><div class="card"><h3>Product specifications</h3><p class="small">Want the analysis behind these numbers? <a href="/product-review.html#features">See our detailed feature analysis</a>.</p>
<dl class="spec mt-0">
<div><dt>Product</dt><dd>EverPitch (AI webinar software)</dd></div>
<div><dt>Format</dt><dd>Web app, nothing to install</dd></div>
<div><dt>Inputs</dt><dd>Idea, document, URL, PDF deck, video (up to 2 GB)</dd></div>
<div><dt>Slides</dt><dd>73 layouts, 11 visual styles, AI images</dd></div>
<div><dt>Voices</dt><dd>30 AI voices, 87 languages</dd></div>
<div><dt>Hosting</dt><dd>Automated sessions, viewer-local timezones</dd></div>
<div><dt>Q&amp;A</dt><dd>Spoken answers, up to 20 free per session</dd></div>
<div><dt>Checkout</dt><dd>JVZoo · instant email login</dd></div>
</dl></div></div>
</div></section>

<section class="section section-soft"><div class="container">
<div class="section-head"><span class="eyebrow">Core features</span><h2>What every EverPitch account includes</h2></div>
<div class="grid g3">{"".join(card(i, t, d) for i, t, d in FEATURES)}</div></div></section>

<section class="section"><div class="container">
<div class="section-head"><span class="eyebrow">The Bundle</span><h2>Four products, already switched on</h2>
<p>The EverPitch Bundle adds more credits, done-for-you webinars, ready-made kits and client rights, all active from your first login.</p></div>
<div class="grid g2">
{card("bolt", "More credits: 8,000 a month", "Up from 3,000, or about 200 finished minutes. That is enough for roughly 13 fifteen-minute webinars a month. Credits refresh monthly.")}
{card("kit", "Kit Vault: 24 webinar kits", "Ready-made kits for coaching, courses, SaaS, agencies and local services. Each sets the structure, length and style; you fill in the marked blanks and build.")}
{card("briefcase", "Agency: a client licence", "Make, run and charge for webinars for clients, with their logo, name and colour, and no “Powered by EverPitch” on registration, live room or replay pages.")}
{card("video", "DFY Webinars: 10 finished webinars", "About 15 minutes each, designed and voiced, each with its registration page, emails, poll and offer card. They are neutral so your offer fits, and copying them uses no credits.")}
</div>
<div class="callout mt-4"><h3>Three bonuses included with the Bundle</h3><ul class="checks mt-0"><li><strong>The First 7 Days Playbook:</strong> one small job a day, from first login to a live, promoted webinar.</li><li><strong>The Webinar Title &amp; Hook Bank:</strong> 100 fill-in-the-blank titles and opening lines for 10 kinds of business.</li><li><strong>The After-Webinar Email Pack:</strong> seven ready-to-edit follow-up emails.</li></ul></div>
</div></section>

<section class="section section-soft"><div class="container split rev">
<div class="reveal">{img("everpitch-ai-webinar-software-mockup", "Illustration of an EverPitch webinar room with a narrated slide and the AI host answering chat questions", 980, 560, small=560)}</div>
<div class="reveal"><span class="eyebrow">Who it suits</span><h2>Built for experts who don’t want to become producers</h2>
<p>The seller positions EverPitch for people who know their subject and their offer but don’t have time to script, design, record and present: coaches, consultants, course creators, local service businesses, SaaS teams and agencies.</p>
<ul class="checks"><li>You explain the same offer repeatedly on calls</li><li>You sell something that needs explaining, like a service, software or a new idea</li><li>You’d rather not appear on camera</li><li>You build marketing assets for clients</li></ul>
<p>It suits you less if you need live streaming, MP4 export or an on-camera host in real time. Those are part of Ultra, which is sold separately.</p></div>
</div></section>
{final_cta()}'''
    write("/product-overview.html", "What Is EverPitch? | AI Webinar Builder",
          "What EverPitch is and what it creates: AI scripts, slides, voices, daily hosting and spoken Q&A, plus what the four-product Bundle adds.",
          body, active="/product-overview.html", ld=[breadcrumb_ld(trail, "/product-overview.html"), SOFTWARE_LD], preload="everpitch-features-composition")

# ================================================================ HOW IT WORKS
def how():
    trail = [("Home", "/"), ("How It Works", None)]
    body = page_hero(trail, "How it works", "How EverPitch Works, From Prompt to Daily Webinar",
        "Three steps take you from an idea to a hosted webinar: describe it, review it, share it. Here is what happens at each stage and what you control.",
        "everpitch-three-step-workflow", "Three-step EverPitch workflow diagram: describe, review, share", 1200, 420) + f'''
<section class="section"><div class="container">
<div class="steps">
<div class="card step reveal"><h3>Describe it, or pick a kit</h3><p>Type what the webinar is about in plain words, attach a PDF, paste a link, or upload a recording. You can also start from one of 24 ready-made kits in the Bundle’s Kit Vault.</p></div>
<div class="card step reveal"><h3>Review and customise</h3><p>The script, slides and voice come back as a draft. Read every line, change any slide by asking, apply your logo and colours, and add on-camera clips of yourself made from one photo.</p></div>
<div class="card step reveal"><h3>Share and let it run</h3><p>Choose a registration page and share the link, or embed a join button on your site. EverPitch presents the webinar on your schedule in each viewer’s timezone.</p></div>
</div></div></section>

<section class="section section-soft"><div class="container split">
<div class="reveal"><span class="eyebrow">Inputs</span><h2>Four ways to start</h2>
<p>EverPitch is designed so you never face a blank page. Whatever you already have can become the starting point.</p>
<ul class="checks"><li><strong>An idea:</strong> describe the topic and the offer in a sentence or two.</li><li><strong>A document or URL:</strong> turn an existing article, sales page or brief into a talk.</li><li><strong>A PDF deck:</strong> import slides you already use.</li><li><strong>A recording:</strong> upload a past Zoom call (up to 2 GB). Slides are read from the video so names and prices come out right.</li></ul></div>
<div class="reveal"><div class="grid g2">
{card("edit", "Idea", "A short prompt is enough to get a first draft.", "card")}
{card("doc", "Document", "Reuse material you already wrote.", "card")}
{card("upload", "PDF deck", "Import an existing presentation.", "card")}
{card("video", "Recording", "Turn an old call into an evergreen webinar.", "card")}
</div></div>
</div></section>

<section class="section"><div class="container">
<div class="section-head"><span class="eyebrow">During the session</span><h2>What happens when viewers join</h2>
<p>The talk is prepared ahead of time and played on a shared clock, so everyone in a session sees the same moment.</p></div>
<div class="grid g3">
{card("clock", "Viewer-local times", "Session times are shown in each visitor’s timezone, with reminders and calendar invites.")}
{card("chat", "Spoken answers", "Greetings get a welcome, comments don’t interrupt, and questions get a spoken answer from your content, at a minute you choose or right away.")}
{card("video", "Your demo, in place", "Paste a video link and EverPitch finds where it belongs, plays it full screen with a spoken lead-in, then picks the talk back up.")}
</div>
<div class="notice mt-4 reveal"><h3>About credits</h3><p>Building a webinar uses credits at 40 per finished minute, so a 15-minute webinar uses about 600. Extra languages and extra AI images use a few more. Spoken answers during sessions don’t use credits (up to 20 per session). If you run out, finished webinars keep running and new builds wait for next month’s refresh.</p></div>
<p class="center mt-4">Next, explore the <a href="/focus-areas/index.html">focus areas</a> for a closer look at each part of the product.</p>
</div></section>
{final_cta()}'''
    write("/how-it-works.html", "How EverPitch Works | AI Webinar Tool Steps",
          "How EverPitch works in three steps: describe your webinar, review the AI script and slides, then share it. Covers inputs, live sessions and credits.",
          body, active="/how-it-works.html", ld=[breadcrumb_ld(trail, "/how-it-works.html"),
          {"@context": "https://schema.org", "@type": "HowTo", "name": "Create a webinar with EverPitch",
           "step": [{"@type": "HowToStep", "name": n, "text": t} for n, t in [("Describe it, or pick a kit", "Type the topic, attach a PDF, paste a link, upload a recording or choose a kit."), ("Review and customise", "Edit the script, slides and voice; apply your branding."), ("Share and let it run", "Share the registration page or embed a join button; EverPitch presents on schedule.")]]}],
          preload="everpitch-three-step-workflow")

# ================================================================ BENEFITS
def benefits():
    trail = [("Home", "/"), ("Benefits", None)]
    items = [
        ("script", "No blank-page scripting", "Get a structured first draft of the whole talk, with an opening, the teaching and a natural move to your offer, then edit it to sound like you.", "/focus-areas/webinar-creation.html"),
        ("slides", "Professional slides without a designer", "Choose from 73 layouts and 11 visual styles, add AI images and your brand colours, or import your PDF deck.", "/focus-areas/webinar-creation.html"),
        ("voice", "Off-camera presenting", "30 natural AI voices narrate the talk, so recording equipment and on-camera nerves are no longer a barrier.", "/focus-areas/webinar-creation.html"),
        ("host", "Your pitch runs every day", "Automated sessions on flexible schedules mean your best presentation keeps working without you in the room.", "/focus-areas/automated-hosting-qa.html"),
        ("chat", "Questions answered out loud", "The host answers questions from your webinar’s content, with up to 20 free spoken answers per session.", "/focus-areas/automated-hosting-qa.html"),
        ("globe", "Reach more languages", "Create translated, re-voiced copies in 87 languages. Visitors see their own language and analytics add the versions together.", "/focus-areas/multilingual-webinars.html"),
        ("mail", "Funnel pages included", "31 registration templates, 20 replay sales page templates, a join button in 10 styles, reminders and follow-ups.", "/focus-areas/registration-follow-up.html"),
        ("kit", "Faster starts with kits", "The Bundle’s 24 kits and 10 done-for-you webinars give you a working structure before you write a word.", "/product-overview.html"),
        ("briefcase", "Client-ready with Agency", "Build and run webinars for paying clients under their brand, without EverPitch branding on the pages.", "/product-overview.html"),
    ]
    body = page_hero(trail, "Benefits", "EverPitch Benefits: What Changes When Webinars Run Themselves",
        "The practical advantages of letting EverPitch handle scripting, design, narration, hosting and follow-up, based on the features the seller lists.",
        "focus-automated-hosting-qa", "Illustration of EverPitch daily sessions in viewer-local times next to chat questions answered by the AI host", 1000, 560) + f'''
<section class="section"><div class="container">
<div class="grid g3">{"".join(f'<a class="card tilt reveal card-link" href="{u}"><div class="icon">{ic(i)}</div><h3>{t}</h3><p>{d}</p><span class="more">Learn more →</span></a>' for i, t, d, u in items)}</div>
</div></section>

<section class="section section-soft"><div class="container split">
<div class="reveal"><span class="eyebrow">Why webinars</span><h2>Why a focused presentation still works</h2>
<p>A sales page gets a quick scan. A webinar gets attention for long enough to explain what you do and why it matters. That is especially useful for services, software and new ideas, which are hard to sell in bullet points.</p>
<p>Webinars also build trust before the ask: viewers hear the reasoning, see the demo and get their questions answered. The difficulty has always been the production work. That is the part EverPitch is designed to remove.</p>
<p>Want the strategy side? Read <a href="/blog/live-vs-evergreen-webinars.html">Live vs. Evergreen Webinars</a>. Weighing it up? <a href="/product-review.html#pros-cons">Explore the product’s pros and cons</a>.</p></div>
<div class="reveal">{img("everpitch-features-composition", "EverPitch feature composition showing scripts, slides, voices, languages and Q&A around the webinar room", 1200, 720, small=640, cls="media plain")}</div>
</div></section>

<section class="section"><div class="container narrow">
<div class="notice reveal"><h3>A note on results</h3><p>EverPitch is a production and hosting tool. How many people register, attend or buy depends on your offer, your audience, your traffic and your message. This site makes no promise of sales, income or conversion rates. Treat any such claims elsewhere with caution.</p></div>
</div></section>
{final_cta()}'''
    write("/benefits.html", "EverPitch Benefits | Automated AI Webinars",
          "The benefits of EverPitch: no blank-page scripting, designer-quality slides, AI narration, daily hosting, spoken Q&A, 87 languages and funnel pages.",
          body, active="/benefits.html", ld=[breadcrumb_ld(trail, "/benefits.html")], preload="focus-automated-hosting-qa")

# ================================================================ FOCUS AREAS
FOCUS = [
    ("webinar-creation", "script", "Script &amp; Slide Creation", "AI Script &amp; Slide Creation",
     "EverPitch | AI Webinar Script & Slide Creation", "How EverPitch drafts a webinar script and designs slides from an idea, document, PDF or recording, with 73 layouts, 11 styles and 30 voices.",
     "focus-webinar-creation", "Illustration of an EverPitch script draft beside a designed slide deck with 73 layouts and 11 styles",
     [("What it does", "EverPitch writes a structured talk with a clear opening, useful teaching and a natural transition to your offer. It then builds the slides and narrates them. You can start from a prompt, a document, a URL, a PDF deck or a recording."),
      ("Design options", "73 slide layouts and 11 visual styles, AI-generated slide images, and your own logo and brand colours. Change any slide by describing the change you want."),
      ("Voice and presence", "30 AI voices in 87 languages narrate the talk. If you want a personal touch, add on-camera clips of yourself generated from one photo. Voice cloning is available only with the speaker’s consent."),
      ("Demos and recordings", "Paste a demo link and EverPitch places it where it fits, with a spoken lead-in. Upload a past recording (up to 2 GB) to keep the full video in a live room or cut a shorter version.")],
     ["Coaches and consultants with a repeatable pitch", "Course creators turning lessons into a sales webinar", "SaaS teams that need a product demo inside the talk"],
     "/blog/webinar-script-structure.html", "How to structure a webinar script that sells"),
    ("automated-hosting-qa", "chat", "Hosting &amp; Spoken Q&amp;A", "Evergreen Hosting &amp; Spoken Q&amp;A",
     "EverPitch | Evergreen Webinar Hosting & Live Q&A", "EverPitch hosts webinars daily on a shared clock in each viewer's timezone, and an AI host answers questions out loud from your content.",
     "focus-automated-hosting-qa", "Illustration of EverPitch session times in viewer-local time and chat questions answered aloud by the AI host",
     [("Daily, scheduled sessions", "EverPitch presents your webinar on flexible schedules. Times appear in each visitor’s own timezone, and everyone in a session shares one clock, so they see the same moment together."),
      ("A host who answers out loud", "Greetings get a welcome, comments don’t interrupt, and every question gets a spoken answer drawn from your webinar’s own content, at a minute you choose or right away. Up to 20 spoken answers per session are free."),
      ("Accuracy controls", "Answers come only from what is in your webinar, and you can add extra host knowledge and FAQs. You can read every line of the script before going live, and spam or abuse is screened before anything is read out."),
      ("Transparency", "The session is prepared in advance and played on a schedule. A simulated audience is optional, and when it is on, the registration page says so.")],
     ["Businesses whose prospects are spread across timezones", "Anyone sending paid traffic to a webinar", "Sellers who answer the same questions repeatedly"],
     "/blog/live-vs-evergreen-webinars.html", "Live vs. evergreen webinars"),
    ("multilingual-webinars", "globe", "Multilingual Webinars", "Multilingual Webinars in 87 Languages",
     "EverPitch | Multilingual Webinars in 87 Languages", "Create translated, re-voiced copies of one EverPitch webinar in 87 languages. Visitors get their own language and analytics are combined.",
     "focus-multilingual-webinars", "Illustration of EverPitch's 87 supported languages surrounding a central badge",
     [("One webinar, many languages", "EverPitch creates translated and re-voiced copies of a webinar and links them together. It supports 87 languages and 30 AI voices."),
      ("Automatic language matching", "Each visitor gets their own language automatically, so you share one link instead of managing separate funnels."),
      ("Combined analytics", "Analytics add every language version together, so you see the whole picture of a webinar’s performance."),
      ("Credit use", "Extra languages use a few more credits than a single-language build. The Bundle’s 8,000 monthly credits give more room for translated versions.")],
     ["Businesses selling into more than one market", "Course creators with international students", "Agencies serving multilingual clients"],
     "/blog/live-vs-evergreen-webinars.html", "Choosing the right webinar format"),
    ("registration-follow-up", "mail", "Registration &amp; Follow-Up", "Registration Pages &amp; Follow-Up",
     "EverPitch | Webinar Registration & Follow-Up", "EverPitch builds registration pages, reminders, calendar invites, replay sales pages and follow-up emails around every webinar.",
     "focus-registration-follow-up", "Illustration of the EverPitch funnel: register, remind, watch and buy",
     [("Pages that fill the room", "31 registration templates, or import a page you already have. Every page is written for the webinar’s topic and is editable word by word."),
      ("Reminders that bring people back", "Session times in each visitor’s timezone, with reminders and calendar invites, plus follow-up emails after the session."),
      ("From replay to sale", "A replay sales page from 20 templates, an offer card in the live room, and checkout. Payments go to your own account and leads go to your own list."),
      ("Embed anywhere", "A join button for any website in 10 styles. With Agency (in the Bundle), none of the pages say “Powered by EverPitch”.")],
     ["Marketers who want the full funnel in one place", "Agencies delivering webinar funnels to clients", "Anyone who needs a replay page and follow-ups fast"],
     "/blog/webinar-follow-up-emails.html", "A follow-up email plan that respects people"),
]

def focus():
    trail = [("Home", "/"), ("Focus Areas", None)]
    body = f'''<section class="page-hero"><div class="container">{crumbs(trail)}
<div class="section-head" style="margin-bottom:0"><span class="eyebrow">Focus areas</span><h1>EverPitch Focus Areas: Four Parts of One Webinar System</h1>
<p class="lead">EverPitch covers four connected areas of webinar work. Pick one to see exactly what the product does there and who it suits.</p></div></div></section>
<section class="section"><div class="container"><div class="grid g2">
{"".join(f'<a class="card tilt reveal card-link post-card" href="/focus-areas/{s}.html">{img(im, alt, 1000, 560)}<div class="body"><div class="icon">{ic(i)}</div><h2 style="font-size:1.5rem">{short}</h2><p>{facts[0][1]}</p><span class="more">Read the guide →</span></div></a>' for s, i, short, h1, t, d, im, alt, facts, *_ in FOCUS)}
</div>
<p class="center mt-4">New to EverPitch? Start with the <a href="/product-overview.html">product overview</a> or see <a href="/how-it-works.html">how it works</a>.</p>
</div></section>
{final_cta()}'''
    write("/focus-areas/index.html", "EverPitch Focus Areas | AI Webinar Features",
          "Explore EverPitch's four focus areas: AI script and slide creation, automated hosting with spoken Q&A, multilingual webinars, and registration pages.",
          body, active="/focus-areas/index.html", ld=[breadcrumb_ld(trail, "/focus-areas/index.html")])
    for idx, (s, i, short, h1, title, desc, im, alt, facts, who, blog_u, blog_t) in enumerate(FOCUS):
        path = f"/focus-areas/{s}.html"
        trail = [("Home", "/"), ("Focus Areas", "/focus-areas/index.html"), (re.sub("&amp;", "&", short), None)]
        nxt = FOCUS[(idx + 1) % len(FOCUS)]
        body = page_hero(trail, "Focus area", f"EverPitch {h1}", facts[0][1], im, alt) + f'''
<section class="section"><div class="container"><div class="grid g2">
{"".join(f'<div class="card reveal"><h2 style="font-size:1.45rem">{t}</h2><p>{d}</p></div>' for t, d in facts)}
</div></div></section>
<section class="section section-soft"><div class="container split">
<div class="reveal"><span class="eyebrow">Who it suits</span><h2>Where this matters most</h2><ul class="checks">{"".join(f"<li>{w}</li>" for w in who)}</ul></div>
<div class="reveal card"><h3>Related reading</h3><ul class="checks mt-0">
<li><a href="{blog_u}">{blog_t}</a></li><li><a href="/how-it-works.html">How EverPitch works</a></li><li><a href="/benefits.html">All EverPitch benefits</a></li>
<li>Next focus area: <a href="/focus-areas/{nxt[0]}.html">{nxt[2]}</a></li></ul></div>
</div></section>
{final_cta()}'''
        write(path, title, desc, body, active="/focus-areas/index.html", ld=[breadcrumb_ld(trail, path)], og_img=im, preload=im)

# ================================================================ REVIEWS
def reviews():
    trail = [("Home", "/"), ("Reviews", None)]
    body = page_hero(trail, "Reviews", "EverPitch Customer Reviews and Complaints: What We Found",
        "We only publish customer reviews and complaints we can verify. Here is the current state of EverPitch feedback, plus facts you can check yourself. For our own analysis, read our <a href=\"/product-review.html\">full EverPitch review</a>.",
        "everpitch-verified-facts", "Graphic listing verifiable EverPitch Bundle facts: $199.10 one time, 30-day guarantee, JVZoo checkout and 8,000 credits a month") + f'''
<section class="section"><div class="container narrow">
<div class="notice reveal"><h2 style="font-size:1.6rem">Verified customer reviews and complaints: none found yet</h2>
<p>When we researched this page on November 19, 2026, the seller’s Bundle page did not publish customer testimonials, star ratings or review counts. Searches for EverPitch reviews and complaints found no independent reviews and no published complaints, and we did not find an authorised, verifiable review source to quote. We won’t fill the gap with invented testimonials or scores. If genuine, attributable reviews become available, we will add them here with their source.</p></div>
</div></section>

<section class="section section-soft"><div class="container">
<div class="section-head"><span class="eyebrow">Verified facts</span><h2>What you can check for yourself</h2><p>Each point below comes directly from the seller’s published offer.</p></div>
<div class="grid g3">
{card("bolt", "One-time price", "The Bundle is listed at $199.10, paid once, with no yearly renewal. Ultra is sold separately.")}
{card("shield", "30-day guarantee", "Email support within 30 days of buying for a refund through JVZoo. No reason is required.")}
{card("lock", "Checkout via JVZoo", "Payment runs through JVZoo’s secure checkout, followed by an account set-up email for instant access.")}
{card("layers", "What’s included", "Commercial, DFY Webinars, Kit Vault and Agency, plus 8,000 credits a month and three bonuses.")}
{card("chat", "Q&amp;A limits", "Up to 20 free spoken answers per session; spoken answers don’t use credits.")}
{card("refresh", "Credit rules", "40 credits per finished minute. Finished webinars keep running if you run out of credits.")}
</div></div></section>

<section class="section"><div class="container split">
<div class="reveal"><span class="eyebrow">Reading reviews elsewhere</span><h2>How to judge an EverPitch review</h2>
<ul class="checks"><li>Look for a clear disclosure if the reviewer earns a commission</li><li>Prefer reviews that show the actual app and a real webinar they built</li><li>Be wary of income claims or “guaranteed” results</li><li>Check that prices and inclusions match the seller’s current page</li></ul>
<p>The FTC’s rules on endorsements and on fake reviews explain what honest reviews should look like. Both are linked in our <a href="/#references">references</a>.</p></div>
<div class="reveal card"><h3>Still deciding?</h3><p>The guarantee lets you use the whole Bundle for 30 days and ask for a refund if it isn’t right for you. Read the full terms on the seller’s checkout before paying.</p>
<p><a href="/product-review.html">Explore the product’s pros and cons</a> · <a href="/faq.html">Read the FAQ</a></p>{cta("View the Bundle offer", "btn-primary", "reviews")}</div>
</div></section>
{final_cta()}'''
    write("/reviews.html", "EverPitch Customer Reviews & Complaints Check",
          "EverPitch customer reviews and complaints: what we found, with no invented testimonials, plus verifiable facts on price, refunds and credits.",
          body, active="/reviews.html", ld=[breadcrumb_ld(trail, "/reviews.html")], preload="everpitch-verified-facts")

# ================================================================ PRODUCT REVIEW (editorial)
def product_review():
    path = "/product-review.html"
    trail = [("Home", "/"), ("Reviews", "/reviews.html"), ("EverPitch Review", None)]
    toc = [("what-is", "What is EverPitch?"), ("how-it-works", "How EverPitch claims to work"), ("features", "Complete feature breakdown"),
           ("evidence", "What independent sources say"), ("benefits-limits", "Potential benefits and limitations"), ("risks", "Risks and possible downsides"),
           ("pros-cons", "EverPitch pros and cons"), ("price", "EverPitch price and packages"), ("refund", "Refund policy"), ("who-for", "Who EverPitch may suit"),
           ("check-first", "Who should get advice first"), ("worth-it", "Is EverPitch worth it? Is it legit?"), ("faq", "EverPitch review FAQ"), ("verdict", "Final verdict")]
    feats = [
        ("script", "AI webinar scripts", "Writes a structured talk with an opening, teaching and a move to your offer, from an idea, document, URL or recording.",
         "Quality depends on your input and on how much you edit. Generative AI can state things confidently that are wrong, so every line needs a human check. EverPitch does let you edit the whole script."),
        ("slides", "AI-designed slides", "73 layouts, 11 visual styles, AI slide images, your logo and colours, PDF deck import, and changes made by asking.",
         "Plenty of layout choice for a webinar tool. We could not assess design quality ourselves. AI images use extra credits."),
        ("voice", "AI narration and voice cloning", "30 AI voices in 87 languages; voice cloning from a recording only with the speaker’s consent.",
         "Removes the need to record. Whether a synthetic voice suits your audience is a judgement call. The consent step matters, given the FTC’s concerns about voice cloning misuse."),
        ("host", "Automated daily hosting", "Sessions run on flexible schedules, in each viewer’s timezone, on a shared clock so everyone sees the same moment.",
         "This is an evergreen (pre-prepared) format, not a live presenter. The seller says so in its FAQ. Present it honestly to your viewers."),
        ("chat", "Spoken AI Q&amp;A", "Answers questions out loud from your webinar’s own content, up to 20 free spoken answers per session; spam is screened first.",
         "A real differentiator against silent replays, but the 20-answer limit and content-only answers mean you should add an FAQ to your webinar’s host knowledge."),
        ("mail", "Pages, emails and checkout", "31 registration templates, 20 replay-page templates, reminders, calendar invites, follow-ups, a join button and an offer card; payments and leads go to your own accounts.",
         "Covers the funnel around the webinar. You remain responsible for email-law compliance (such as CAN-SPAM) and for handling registrants’ data."),
        ("video", "Recording and demo import", "Turns a past recording (up to 2 GB) into an evergreen webinar; inserts a demo video with a spoken lead-in where it fits.",
         "Useful if you already have a strong recorded pitch. We could not test how well slides are read from video."),
        ("kit", "Bundle extras", "8,000 credits a month, 24 webinar kits, 10 done-for-you webinars, Agency client licence and three bonuses.",
         "Good value only if you will use the extras. If you run one webinar a month for yourself, EverPitch on its own may be enough."),
    ]
    feat_cards = "".join(f'''<article class="card reveal"><div class="icon">{ic(i)}</div><h3>{t}</h3>
<p><span class="label label-claim">Seller says</span> {claim}</p><p><span class="label label-ours">Our analysis</span> {ours}</p></article>''' for i, t, claim, ours in feats)
    pros = ["One tool covers script, slides, voice, hosting, Q&amp;A, pages and follow-up", "One-time payment ($199.10 for the Bundle), no yearly renewal stated",
            "30-day money-back guarantee, refunded through JVZoo", "You can read and edit every line before anything goes live",
            "87 languages with linked, re-voiced versions and combined analytics", "Transparent about format: simulated audience is optional and disclosed on the page",
            "Client licence and white-labelled pages included in the Bundle"]
    cons = ["No independent customer reviews or ratings found as of November 2026", "Credits cap how many minutes you can build each month (about 200 with the Bundle)",
            "Ultra (live streaming, MP4 export, on-camera host, voice calls) costs extra", "AI-written content still needs careful human review",
            "Spoken answers are limited to 20 per session and only cover your content", "A one-time price for a hosted service: long-term service terms are not stated on the sales page",
            "It does not bring you an audience; traffic is still your job"]
    review_faqs = [
        ("Does EverPitch work?", "Based on the seller’s published information, EverPitch creates a script, slides and AI narration from your input, hosts the webinar on a schedule and answers questions out loud. We have not tested it ourselves, so we can’t confirm output quality. The 30-day guarantee gives you a window to test it on your own topic."),
        ("Is EverPitch legit?", "EverPitch is sold through JVZoo’s checkout with a stated 30-day money-back guarantee, and the sales page explains its limits plainly. JVZoo is the payment platform, not the seller, so support and refunds are handled by the EverPitch team through JVZoo. We found no independent reviews yet, which is common for a newly launched product."),
        ("Are there EverPitch complaints?", "We searched for EverPitch complaints and reviews on November 19, 2026 and did not find any published customer complaints or independent reviews. That is not proof there are none. Check again before buying, and see our <a href=\"/reviews.html\">customer reviews page</a> for updates."),
        ("Does EverPitch have side effects or risks?", "As software it has no physical side effects. The practical risks are AI mistakes in scripts or answers, misrepresenting a pre-recorded webinar as live, using someone’s voice without consent, and handling registrants’ data carelessly. Each is covered in the <a href=\"#risks\">risks section</a>."),
        ("How much does EverPitch cost?", "The Bundle is listed at $199.10 as a one-time payment. The seller lists EverPitch Commercial on its own at $39.10 within its separate-purchase breakdown. Prices can change, so confirm at checkout."),
        ("Is EverPitch worth it?", "It is worth considering if you repeatedly explain the same offer and want a webinar running daily without presenting it yourself. It is harder to justify if you need true live streaming, or if you won’t use the extra credits, kits and client rights in the Bundle."),
    ]
    rfaq = "".join(f'<details><summary>{q}</summary><div class="a"><p>{a}</p></div></details>' for q, a in review_faqs)
    body = f'''<section class="page-hero"><div class="container">{crumbs(trail)}
<div class="split"><div><span class="eyebrow">Independent review · Updated November 19, 2026</span>
<h1>EverPitch Review: Features, Benefits, Pros and Cons</h1>
<p class="lead">EverPitch promises to turn an idea, a document or an old recording into a complete webinar, then present it every day and answer questions out loud. This EverPitch review separates what the seller claims from what we could verify, and covers the price, the refund policy, the risks and who it suits.</p>
<div class="method"><h2 class="h4">How this review was made</h2>
<p>We have <strong>not</strong> used EverPitch ourselves. This review is based on the seller’s public Bundle page (researched November 19, 2026), searches for independent reviews and complaints, and government guidance on the underlying technology. No testing, ratings or customer stories have been invented. This is an independent affiliate site: if you buy through our links, the seller may pay us a commission. That does not change the pros, cons or verdict below.</p>
<p class="small">By the everpitch.vercel.app editorial team · <a href="/affiliate-disclosure.html">Affiliate Disclosure</a></p></div>
</div>
<div><div class="media plain">{img("everpitch-ai-webinar-software-mockup", "EverPitch review illustration: an EverPitch webinar room with AI-designed slide, narration and live chat answered by the AI host", 980, 560, lazy=False, small=560)}</div>
<div class="verdict-box mt-2"><h2 class="h4">The short verdict</h2><p>A capable all-in-one idea for evergreen webinars at a one-time price, with a fair 30-day refund window. The catches: no independent reviews yet, credit limits, and AI output you must check yourself.</p>
<a class="small" href="#verdict">Jump to the full verdict ↓</a></div></div>
</div></div></section>

<section class="section-sm"><div class="container review-layout">
<aside class="toc" aria-label="Table of contents"><h2 class="h4">In this review</h2><ol>{"".join(f'<li><a href="#{a}">{t}</a></li>' for a, t in toc)}</ol></aside>
<article class="prose review-body">

<h2 id="what-is">What is EverPitch?</h2>
<p>EverPitch is browser-based AI webinar software. You give it a topic, a document, a link, a PDF deck or a recording, and it produces a webinar script, a slide deck and an AI voice-over. Once you have reviewed and edited the result, EverPitch hosts the webinar on a schedule, builds the registration and replay pages, sends reminders and follow-ups, and answers viewers’ questions out loud using your content.</p>
<p>It is sold through JVZoo in two main forms: EverPitch on its own, and the EverPitch Bundle, which adds more credits, done-for-you webinars, ready-made kits and a client licence. This review focuses on the Bundle, since that is the offer this site links to. For a plain product summary without the analysis, see <a href="/product-overview.html">What Is It</a>.</p>

<h2 id="how-it-works">How does EverPitch claim to work?</h2>
<p>According to the seller, the process has three steps:</p>
<ol><li><strong>Describe it, or pick a kit.</strong> Type the topic, attach a PDF, upload a recording or start from one of 24 kits.</li>
<li><strong>Review it.</strong> The talk, slides and voice come back; change any slide by asking and add on-camera clips made from one photo.</li>
<li><strong>Share it.</strong> Publish a registration page or embed a join button; EverPitch presents on schedule.</li></ol>
<p>During a session, the talk plays on a shared clock so everyone sees the same moment, and the host answers questions out loud from the webinar’s content. These are the seller’s descriptions. We explain each step in more depth on <a href="/how-it-works.html">How It Works</a>.</p>

<h2 id="features">Complete EverPitch feature breakdown</h2>
<p>A webinar tool’s features are its “ingredients”. Each card below separates the <strong>seller’s claim</strong> from <strong>our analysis</strong>, including what we could not verify.</p>
</article></div>
<div class="container review-layout"><div class="grid g2 mt-2">{feat_cards}</div></div>

<div class="container review-layout"><div aria-hidden="true"></div><article class="prose review-body">
<h2 id="evidence">What independent sources say about the technology</h2>
<p>No independent study has tested EverPitch itself. What does exist is government guidance on the technologies it relies on. This guidance describes general risks; it says nothing about EverPitch specifically.</p>
<div class="evidence">
<div class="ev"><span class="label label-ind">Independent · NIST</span><h3>Generative AI can produce confident errors</h3><p>NIST’s Generative AI Profile (AI 600-1) lists confabulation, meaning confidently stated false content, among the risks of generative AI. Practical takeaway: read every line of an AI-written script before it goes live.</p><a href="https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence" target="_blank" rel="noopener noreferrer">View source</a></div>
<div class="ev"><span class="label label-ind">Independent · FTC</span><h3>Voice cloning carries real misuse risks</h3><p>The FTC has highlighted fraud and misuse of people’s voices as harms of AI voice cloning. EverPitch’s consent confirmation is the right design; it is still your responsibility to get genuine permission.</p><a href="https://www.ftc.gov/policy/advocacy-research/tech-at-ftc/2023/11/preventing-harms-ai-enabled-voice-cloning" target="_blank" rel="noopener noreferrer">View source</a></div>
<div class="ev"><span class="label label-ind">Independent · FTC</span><h3>Fake reviews and testimonials are prohibited</h3><p>The FTC’s rule on consumer reviews and testimonials, in effect since October 21, 2024, bans fake testimonials, including AI-generated ones. This matters if you add social proof to an automated webinar.</p><a href="https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers" target="_blank" rel="noopener noreferrer">View source</a></div>
<div class="ev"><span class="label label-ind">Independent · FTC</span><h3>AI marketing claims need evidence</h3><p>FTC staff guidance warns businesses to keep claims about AI products truthful and supported. Apply the same scepticism to any review, including this one, that promises results.</p><a href="https://www.ftc.gov/business-guidance/blog/2023/02/keep-your-ai-claims-check" target="_blank" rel="noopener noreferrer">View source</a></div>
</div>
<p class="small">More sources are listed under <a href="/#references">References &amp; Research</a>. None of these agencies reviews, approves or endorses EverPitch.</p>

<h2 id="benefits-limits">Potential benefits and limitations</h2>
<div class="grid g2">
<div class="card"><h3>Potential benefits</h3><ul class="checks mt-0"><li>Removes scripting, slide design, recording and presenting from your workload</li><li>A webinar that runs daily in viewers’ own timezones</li><li>Spoken answers to questions instead of a silent replay</li><li>Reach into other languages without separate funnels</li></ul></div>
<div class="card"><h3>Limitations</h3><ul class="xs mt-0"><li>It produces and hosts; it does not create demand or traffic</li><li>Output quality depends on your input and editing</li><li>Monthly credits limit how much you can build</li><li>Not a live-streaming tool unless you buy Ultra</li></ul></div>
</div>
<p>For a fuller list of what each feature does for you, see <a href="/benefits.html">EverPitch benefits</a>.</p>

<h2 id="risks">Risks and possible downsides</h2>
<p>Software has no physical side effects, but there are practical risks to manage:</p>
<ul>
<li><strong>Accuracy.</strong> AI-written scripts and spoken answers can be wrong. Edit the script and add your own FAQ to the host’s knowledge.</li>
<li><strong>Honesty about the format.</strong> An evergreen webinar is prepared in advance. Don’t imply it is a one-off live event, and keep the simulated-audience option disclosed if you use it.</li>
<li><strong>Consent.</strong> Only clone a voice, or feature a person, with clear permission.</li>
<li><strong>Data and email.</strong> You collect registrants’ details and send them email, so privacy and anti-spam rules apply to you.</li>
<li><strong>Vendor dependency.</strong> Your webinars run on EverPitch’s service. The sales page does not state long-term service or uptime terms, so read the terms of service before relying on it.</li>
<li><strong>Upsells.</strong> Ultra is sold separately; the Bundle itself is the complete package for everything else listed.</li>
</ul>

<h2 id="pros-cons">EverPitch pros and cons</h2>
</article></div>
<div class="container review-layout"><div class="proscons reveal">
<div class="pc pro"><h3>Pros</h3><ul>{"".join(f"<li>{p}</li>" for p in pros)}</ul></div>
<div class="pc con"><h3>Cons</h3><ul>{"".join(f"<li>{c}</li>" for c in cons)}</ul></div>
</div></div>

<div class="container review-layout"><div aria-hidden="true"></div><article class="prose review-body">
<h2 id="price">EverPitch price and available packages</h2>
<p>Prices below are as listed by the seller on November 19, 2026. Confirm them at checkout.</p>
<div class="table-wrap"><table><caption class="sr-only">EverPitch prices</caption>
<thead><tr><th scope="col">Item</th><th scope="col">Seller’s price</th><th scope="col">Payment</th></tr></thead><tbody>
<tr><th scope="row">EverPitch Bundle (all four products + bonuses)</th><td><strong>$199.10</strong></td><td>One time</td></tr>
<tr><th scope="row">EverPitch Commercial</th><td>$39.10</td><td>One time</td></tr>
<tr><th scope="row">DFY Webinars</th><td>$67.00</td><td>Listed in separate-purchase total</td></tr>
<tr><th scope="row">Webinar Kit Vault</th><td>$47.00</td><td>Listed in separate-purchase total</td></tr>
<tr><th scope="row">Agency</th><td>$77.00</td><td>Listed in separate-purchase total</td></tr>
<tr><th scope="row">Credit Boost (8,000 credits)</th><td>$77.00</td><td>Listed in separate-purchase total</td></tr>
<tr><th scope="row">Separate first-year total</th><td>$307.10</td><td>Seller’s figure</td></tr>
<tr><th scope="row">Ultra</th><td>Not listed on the Bundle page</td><td>Sold separately</td></tr>
</tbody></table></div>
<p>The Bundle’s $108.00 saving is the difference between the seller’s separate first-year total and the Bundle price. There is no shipping: access is digital, with a login email sent after checkout.</p>

<h2 id="refund">Refund policy and money-back guarantee</h2>
<p>The seller offers a <strong>30-day money-back guarantee</strong>. If the Bundle isn’t right for you, email support within 30 days of buying and the refund is processed through JVZoo. The seller says no reason is required. Keep your purchase email, and test the product early in the window rather than on day 29.</p>

<h2 id="who-for">Who may find EverPitch relevant?</h2>
<ul><li>Coaches, consultants and course creators who repeat the same pitch on calls</li><li>Service businesses and SaaS teams selling something that needs explaining</li><li>People who don’t want to appear on camera or present live</li><li>Agencies building webinar funnels for clients (Agency licence in the Bundle)</li><li>Sellers reaching audiences in several languages</li></ul>
<p>It is a weaker fit if you need real-time live streaming, run very long webinars every week (credits), or have no plan for getting visitors to register.</p>

<h2 id="check-first">Who should get professional advice first?</h2>
<p>EverPitch isn’t a health product, so medical advice doesn’t apply. Some users should still check with a qualified professional before relying on it:</p>
<ul><li>Businesses in <strong>regulated fields</strong> such as finance, health, legal or insurance, where presentations and claims are subject to specific rules</li>
<li>Agencies signing <strong>client contracts</strong> that cover branding, data and ownership of content</li>
<li>Anyone planning to <strong>clone a voice</strong> or use another person’s likeness</li>
<li>Sellers emailing audiences in the EU, UK or other regions with strict <strong>privacy and marketing-consent laws</strong></li></ul>

<h2 id="worth-it">Is EverPitch worth it? Is it legit?</h2>
<p><strong>Legitimacy.</strong> EverPitch sells through JVZoo’s checkout with a stated 30-day refund, publishes detailed limits (credit costs, the 20-answer cap, what Ultra excludes) and tells buyers that simulated audiences are disclosed. Those are good signs. JVZoo processes the payment but is not the seller.</p>
<p><strong>Complaints.</strong> As of November 19, 2026 we found no published EverPitch complaints and no independent reviews. That may simply reflect a recent launch, so check again before buying.</p>
<p><strong>Value.</strong> Producing a webinar normally takes a writer, a designer, a voice or presenter, a hosting platform and a page builder. EverPitch replaces that stack with one tool for a one-time payment. It is worth considering if you will actually run webinars regularly; it is poor value if the extras sit unused.</p>
<div class="table-wrap"><table><caption class="sr-only">EverPitch compared with a typical do-it-yourself webinar setup</caption>
<thead><tr><th scope="col">Task</th><th scope="col">Typical DIY setup</th><th scope="col">EverPitch</th></tr></thead><tbody>
<tr><th scope="row">Script and slides</th><td>You write and design, or hire help</td><td>AI first draft you edit</td></tr>
<tr><th scope="row">Narration</th><td>You record yourself</td><td>30 AI voices, 87 languages</td></tr>
<tr><th scope="row">Hosting</th><td>Separate webinar platform</td><td>Included, daily schedules</td></tr>
<tr><th scope="row">Questions</th><td>You answer live, or a replay can’t</td><td>Spoken answers from your content</td></tr>
<tr><th scope="row">Pages and emails</th><td>Separate page builder and email tool</td><td>Included per webinar</td></tr>
</tbody></table></div>

<h2 id="faq">EverPitch review FAQ</h2>
<div class="faq not-prose">{rfaq}</div>
<p>More questions are answered on the <a href="/faq.html">EverPitch FAQ</a> page.</p>

<h2 id="verdict">Final verdict</h2>
<div class="verdict-box"><p><strong>EverPitch is worth considering if you sell something that needs explaining and you want a webinar working for you every day without scripting, designing or presenting it yourself.</strong> On paper the Bundle is strong value at $199.10 one time, and the 30-day refund lowers the risk of trying it.</p>
<p>Hold back if you need live streaming (Ultra costs extra), if you won’t use the extra credits and kits, or if you would rather wait for independent customer reviews, which don’t exist yet. Whatever you decide, edit the AI’s script carefully and be honest with viewers that the webinar is prepared in advance.</p>
<p class="small">We give no star rating, because we have not tested EverPitch ourselves.</p>
<div class="cta-row">{cta("See the EverPitch Bundle offer", "btn-primary", "review-verdict")}<a class="btn btn-ghost" href="/reviews.html">Customer reviews &amp; complaints check</a></div></div>
</article></div></section>
{final_cta("Want to test EverPitch on your own topic?")}'''
    ld = [breadcrumb_ld(trail, path), {"@context": "https://schema.org", "@type": "Article",
           "headline": "EverPitch Review: Features, Benefits, Pros and Cons", "datePublished": LASTMOD, "dateModified": LASTMOD,
           "image": DOMAIN + "/assets/img/everpitch-ai-webinar-software-mockup.webp", "about": {"@type": "SoftwareApplication", "name": "EverPitch", "applicationCategory": "BusinessApplication", "operatingSystem": "Web browser"},
           "author": {"@type": "Organization", "name": "everpitch.vercel.app editorial team", "url": DOMAIN + "/"},
           "publisher": {"@type": "Organization", "name": "everpitch.vercel.app", "url": DOMAIN + "/"}, "mainEntityOfPage": DOMAIN + path}]
    write(path, "EverPitch Review: Features, Benefits & Pros and Cons",
          "Our EverPitch review: what the AI webinar tool does, does it work, is it legit, risks, pros and cons, the $199.10 price, refund policy and our verdict.",
          body, active="/reviews.html", ld=ld, og_type="article", preload="everpitch-ai-webinar-software-mockup")

# ================================================================ FAQ
def faq():
    trail = [("Home", "/"), ("FAQ", None)]
    body = f'''<section class="page-hero"><div class="container narrow">{crumbs(trail)}
<span class="eyebrow">FAQ</span><h1>EverPitch FAQ: Pricing, Credits, Refunds and Setup</h1>
<p class="lead">Answers to the questions people ask most about EverPitch and the Bundle, based on the seller’s published information.</p></div></section>
<section class="section"><div class="container narrow">{faq_html(FAQS)}
<div class="callout mt-4"><h3>Didn’t find your answer?</h3><p>For account or refund help after you buy, contact EverPitch support through the details in your purchase email. For an independent assessment, <a href="/product-review.html">read our EverPitch review</a>. For background on the product, see <a href="/product-overview.html">What Is It</a>, <a href="/how-it-works.html">How It Works</a> and the <a href="/blog/index.html">blog</a>.</p></div>
</div></section>
{final_cta()}'''
    write("/faq.html", "EverPitch FAQ | Pricing, Credits & Refunds",
          "EverPitch FAQ: what the $199.10 Bundle includes, how credits work, spoken Q&A limits, client use, voice cloning consent and the 30-day refund policy.",
          body, active="/faq.html", ld=[breadcrumb_ld(trail, "/faq.html"), faq_ld(FAQS)])

# ================================================================ ORDER (first-party routing page)
def order():
    body = f'''<section class="page-hero"><div class="container">
<div class="order-card">
<div>{img("everpitch-bundle-four-products", "EverPitch Bundle illustration with the four included products: Commercial, DFY Webinars, Kit Vault and Agency", 1060, 660, lazy=False, small=600)}</div>
<div><span class="eyebrow">Your package</span><h1>EverPitch Bundle</h1>
<p class="lead">Four products switched on from your first login, plus three bonuses.</p>
<ul class="pkg-list">
<li>{ic("check")}<span><b>EverPitch Commercial:</b> every core feature, with commercial rights</span></li>
<li>{ic("check")}<span><b>8,000 credits a month:</b> about 200 finished minutes</span></li>
<li>{ic("check")}<span><b>DFY Webinars:</b> 10 finished, voiced webinars to rebrand</span></li>
<li>{ic("check")}<span><b>Kit Vault:</b> 24 ready-made webinar kits</span></li>
<li>{ic("check")}<span><b>Agency:</b> client licence, no “Powered by EverPitch”</span></li>
<li>{ic("check")}<span><b>Bonuses:</b> 7-Day Playbook, Title &amp; Hook Bank, After-Webinar Email Pack</span></li>
</ul>
<div><span class="was">$307.10</span> <span class="save">Save $108.00</span></div>
<div class="price">$199.10<small>one time</small></div>
<p class="small">Seller’s first-year total if each item is bought separately: $307.10.</p>
<a class="btn btn-primary btn-block" href="/go/bundle" rel="sponsored nofollow noopener" data-cta="order-buy">BUY NOW <span class="arrow" aria-hidden="true">→</span></a>
<div class="trust"><span>{ic("shield")} 30-day money-back guarantee</span><span>{ic("lock")} Secure checkout on JVZoo</span><span>{ic("bolt")} Instant email login</span></div>
<p class="small mt-2">You’ll continue to the seller’s official checkout on JVZoo. This website doesn’t process payments or store card details.</p>
</div></div></div></section>'''
    write("/order.html", "Order EverPitch Bundle | $199.10 One Time",
          "Continue to the official EverPitch Bundle checkout on JVZoo: four products, 8,000 monthly credits and a 30-day money-back guarantee.",
          body, index=False, no_promo=True, preload="everpitch-bundle-four-products")

# ================================================================ LEGAL
def legal(path, title, desc, h1, content, active=None):
    trail = [("Home", "/"), (h1, None)]
    body = f'''<section class="page-hero"><div class="container narrow">{crumbs(trail)}<h1>{h1}</h1><p class="small">Last updated: November 19, 2026</p></div></section>
<section class="section"><div class="container narrow prose">{content}</div></section>'''
    write(path, title, desc, body, ld=[breadcrumb_ld(trail, path)])

def legal_pages():
    legal("/affiliate-disclosure.html", "Affiliate Disclosure | EverPitch", "How this independent EverPitch website earns money: affiliate links to the seller's JVZoo checkout, and how that affects our content.",
          "Affiliate Disclosure", '''
<p>everpitch.vercel.app is an independent website. It is not owned, operated or endorsed by EverPitch, its creators or JVZoo.</p>
<h2>How we earn money</h2><p>Purchase buttons on this site lead to our order page, which forwards you to the seller’s official checkout on JVZoo using our affiliate link. If you buy, the seller may pay us a commission. The price you pay is set by the seller and is not increased by our link.</p>
<h2>How this affects our content</h2><p>We describe EverPitch using the seller’s published information, and we aim to be accurate and balanced. We don’t publish invented reviews, ratings or results. Where information isn’t available, we say so.</p>
<h2>Your choice</h2><p>You are free to buy directly from the seller without using our links. Always check the final price, inclusions and refund terms at checkout.</p>''')
    legal("/disclaimer.html", "Disclaimer | EverPitch", "Important information about using this independent EverPitch website: accuracy, results, trademarks and third-party links.",
          "Disclaimer", '''
<h2>Information only</h2><p>Content on this website is for general information. It is based on the seller’s published product page as of the date shown above. Features, prices and terms can change, so check the seller’s current offer before buying.</p>
<h2>No guarantee of results</h2><p>EverPitch is software for creating and hosting webinars. Registrations, attendance and sales depend on many factors outside the software, including your offer, audience, traffic and messaging. Nothing on this site is a promise of income or business results.</p>
<h2>Not professional advice</h2><p>Mentions of laws and regulations, such as rules on email marketing, endorsements or data protection, are general pointers, not legal advice. Consult a qualified professional about your situation.</p>
<h2>Trademarks</h2><p>EverPitch, JVZoo and other names are trademarks of their respective owners and are used here only to identify the products discussed.</p>
<h2>External links</h2><p>We link to third-party websites, including government sources. We aren’t responsible for their content or availability.</p>''')
    legal("/privacy-policy.html", "Privacy Policy | EverPitch", "How this independent EverPitch website handles data: no accounts or forms, minimal browser storage, hosting logs and third-party checkout.",
          "Privacy Policy", '''
<h2>What we collect</h2><p>This website has no user accounts, contact forms or newsletter sign-up, and it does not ask for personal information.</p>
<h2>Browser storage</h2><p>To avoid showing the promotional pop-up repeatedly, the site stores a timestamp in your browser’s local storage, and remembers for the current session if you dismiss the notification card. This data stays on your device and is not sent to us.</p>
<h2>Hosting logs</h2><p>Our hosting provider (Vercel) may process technical data such as IP addresses and request logs to deliver and secure the website, under its own privacy policy.</p>
<h2>Purchases</h2><p>When you click a purchase button, you are forwarded to the seller’s checkout on JVZoo. Any information you enter there is handled by the seller and JVZoo under their policies, not by this website.</p>
<h2>Changes</h2><p>If we add analytics or other data collection, we will update this page first.</p>''')
    legal("/terms.html", "Terms of Use | EverPitch", "Terms for using this independent EverPitch information website, including accuracy, third-party purchases and limitation of liability.",
          "Terms of Use", '''
<h2>Using this site</h2><p>By using everpitch.vercel.app you agree to these terms. The site provides information about a third-party product, EverPitch.</p>
<h2>Purchases are with the seller</h2><p>We do not sell EverPitch. Purchases, access, support and refunds are handled by the seller and JVZoo under their terms. The 30-day money-back guarantee described on this site is the seller’s guarantee.</p>
<h2>Accuracy</h2><p>We work to keep information accurate but can’t guarantee it is complete or current. The seller’s checkout page is the final authority on price and inclusions.</p>
<h2>Limitation of liability</h2><p>To the extent permitted by law, this website is not liable for losses arising from your use of the site or of any third-party product.</p>
<h2>Content</h2><p>Text and illustrations on this site are original works of the site owner unless stated otherwise. Product names belong to their owners.</p>''')

# ================================================================ 404, favicon, SEO files
def extras():
    body = f'''<section class="section"><div class="container narrow center"><span class="eyebrow">404</span><h1>That page isn’t here</h1>
<p class="lead">The link may be old or mistyped. Try one of these instead:</p>
<div class="cta-row" style="justify-content:center"><a class="btn btn-ghost" href="/">Home</a><a class="btn btn-ghost" href="/product-overview.html">What Is It</a><a class="btn btn-ghost" href="/faq.html">FAQ</a></div></div></section>'''
    write("/404.html", "Page Not Found | EverPitch", "The page you were looking for could not be found. Return to the EverPitch homepage or browse the guides.", body, index=False, no_promo=True)
    (OUT / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#1D1512"/><path d="M11 8l13 8-13 8z" fill="#E8704F"/></svg>')

    idx = [(p, t, d) for p, t, d, i in PAGES if i]
    def loc(p): return DOMAIN + ("/" if p == "/index.html" else p)
    urls = "\n".join(f"  <url><loc>{loc(p)}</loc><lastmod>{LASTMOD}</lastmod></url>" for p, _, _ in idx)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /go/\n\nSitemap: {DOMAIN}/sitemap.xml\n")

    existing = [f for f in OUT.glob("*.txt") if re.fullmatch(r"[a-f0-9]{32}\.txt", f.name)]
    key = existing[0].stem if existing else secrets.token_hex(16)   # keep the published key stable
    (OUT / f"{key}.txt").write_text(key)

    vercel = {
        "cleanUrls": False, "trailingSlash": False,
        "rewrites": [{"source": "/order", "destination": "/order.html"}],
        "redirects": [
            {"source": "/go/bundle", "destination": AFFILIATE_URL, "statusCode": 302},
            {"source": "/order.html", "destination": "/order", "statusCode": 301},
            {"source": "/index.html", "destination": "/", "statusCode": 301},
        ],
        "headers": [
            {"source": "/go/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}, {"key": "Cache-Control", "value": "no-store"}]},
            {"source": "/order", "headers": [{"key": "X-Robots-Tag", "value": "noindex, follow"}]},
            {"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
            {"source": "/(.*)", "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"}, {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}, {"key": "Strict-Transport-Security", "value": "max-age=63072000"}]},
        ],
    }
    (OUT / "vercel.json").write_text(json.dumps(vercel, indent=2))
    (OUT / "seo-pages.json").write_text(json.dumps([{"url": loc(p), "title": t, "title_len": len(t), "description": d, "description_len": len(d), "indexable": i} for p, t, d, i in PAGES], indent=2))
    return key

home(); overview(); how(); benefits(); focus(); reviews(); product_review(); blog(); faq(); order(); legal_pages()
key = extras()
print(f"Built {len(PAGES)} pages. IndexNow key: {key}")
