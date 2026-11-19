# EverPitch affiliate website — project notes & reports

Static, multi-page site for **https://everpitch.vercel.app**. It's plain HTML, CSS and JS with no build step, and every page ships its full content in the initial HTML (SSG). Hosting config is in `vercel.json`.

## Important: EverPitch is software, not a supplement
The sales page (https://everpitch.co/epbundle) sells **AI webinar software**, so the supplement-specific parts of the brief were adapted:

| Brief item | What was built instead |
|---|---|
| Original bottle image / bundle bottles | The seller page has no product photo or box shot (its only image is not a product image). I made **original illustrations** in EverPitch's colours (an app-window "webinar room" and a four-product Bundle stack) and rendered them to WebP. Swap in official product images if the vendor provides an affiliate media kit. |
| Ingredients behind the bottle | Verified **features** (scripts, 73 layouts, 30 voices, 87 languages, Q&A…) float behind the hero product, with a subtle animated 3D background. |
| Supplement Facts / dosage | Product specifications and credit rules from the seller page. |
| 1/2/3/6-bottle packages | One verified package: **the Bundle, $199.10 one time**. You supplied one affiliate URL, so there is one route, `/go/bundle`. |
| Lifestyle photos of models holding the product | **Not created.** No image-generation tool was available, and a person "holding" software isn't meaningful. |
| "Scientific References & Research" (8+ US gov sources) | Section titled **"References & Research"** with **10 verified US-government sources relevant to webinar marketing** (FTC, SBA, NIST). Health sources would be unrelated, and the brief forbids unrelated links. |
| Customer reviews / ratings | The seller page publishes **no testimonials, ratings or review counts**. The Reviews page says so and lists verifiable facts instead. Nothing was invented. |
| Supplement disclaimer | Replaced by a software/results **Disclaimer** page. |

## Verified product facts used (from everpitch.co/epbundle, 19 Nov 2026)
- Bundle: **$199.10 one-time**, no yearly renewal. Includes EverPitch Commercial, DFY Webinars (10), Kit Vault (24 kits), Agency (client licence, removes "Powered by EverPitch"), 8,000 credits/month (vs 3,000), three bonuses.
- Bought separately (seller's figures): Commercial $39.10, DFY $67, Kit Vault $47, Agency $77, Credit Boost $77 → **first-year total $307.10**. "Save $108.00" is that difference.
- **30-day money-back guarantee**: email support within 30 days, refunded through JVZoo, no reason needed.
- Ultra (streaming, MP4 export, host on camera, voice calls) is **not** included.
- Credits: 40 per finished minute (~600 for 15 min); up to 20 free spoken answers per session; finished webinars keep running if credits run out.
- No shipping (digital product; instant email login).

## Deploy to Vercel
1. Push this folder to a Git repo (or use `vercel deploy` from the folder). In Vercel, set Framework Preset to **Other**, leave Build Command empty, and set Output Directory to `.` (root).
2. Assign the domain **everpitch.vercel.app**. ⚠️ Vercel subdomains are first-come, first-served. If `everpitch` is taken you'll get a different `*.vercel.app` name; then replace `https://everpitch.vercel.app` everywhere (`grep -rl everpitch.vercel.app . | xargs sed -i 's#everpitch.vercel.app#NEW-HOST#g'`) and redeploy.
3. `.vercelignore` keeps `README.md`, `scripts/`, `.github/` and `seo-pages.json` off the public site.

## Affiliate routing
- Every purchase CTA → `/order?package=bundle` (first-party order page, `noindex, follow`).
- The order page's **BUY NOW** → `/go/bundle` → **HTTP 302** → `https://www.jvzoo.com/c/1834263/461141` (exact, unmodified). It's configured server-side in `vercel.json` with `Cache-Control: no-store` and `X-Robots-Tag: noindex`.
- No open redirect: only `/go/bundle` exists, and any other `/go/...` path or `?url=` returns 404. There's no JS redirect.
- To add package links later, add another entry to `redirects` in `vercel.json` (e.g. `/go/commercial`) and point a button at it.

## Popups
- **Centered modal**: appears about 6 s after load, has a dark overlay, uses the Bundle image, the $199.10 price and a CTA to the order page. It closes via ×, Esc or outside click; it locks scroll, traps focus and has a 24-hour cooldown (localStorage). There's no countdown, because the seller shows no real deadline. It doesn't appear on `/order`.
- **Bottom-left toast**: first at 5 s, shows for 6 s, repeats every 18–26 s. It shows informational messages only, never fake buyers. It never overlaps the modal and can be dismissed for the session. Messages are in `SITE_CONFIG` at the top of `assets/js/site.js`.

## Bing Webmaster Tools & IndexNow checklist
- Homepage (canonical): https://everpitch.vercel.app/
- Sitemap: https://everpitch.vercel.app/sitemap.xml (20 indexable URLs, lastmod 2026-11-19)
- Robots: https://everpitch.vercel.app/robots.txt
- IndexNow key file: https://everpitch.vercel.app/f156399836a2899222f51e9bba5e5e76.txt

1. In Bing Webmaster Tools, add the site. The quickest route is **Import from Google Search Console**. Otherwise choose **HTML meta tag** verification, paste the tag into `<head>` of `index.html` (or add it in `build.py` and rebuild) and redeploy.
2. **Sitemaps** → submit `https://everpitch.vercel.app/sitemap.xml`.
3. **URL Submission** → submit the homepage, `/product-review.html` and the main pages (list below).
4. **URL Inspection** → check that the homepage and one blog article are crawlable and indexable.
5. **IndexNow**: after each deploy, run `node scripts/indexnow.mjs` (first time: `--all`). It checks the live key file, sends only changed sitemap URLs, retries on 429/5xx, and prints the HTTP result. A 200/202 means the URLs were *received*, not indexed. There's an optional GitHub Action in `.github/workflows/indexnow.yml`.
6. Watch **Crawl & Indexing** reports for errors.

Nothing has been submitted, verified or indexed yet. The IndexNow integration hasn't been run against the live API because the site isn't deployed.

## Tests run (local server emulating vercel.json)
- All 21 public routes return 200; `/go/bundle` returns 302 with the exact affiliate URL; `/go/6` and `/go/?url=…` return 404.
- At 1366 px and 390 px: no horizontal overflow, no broken images, no console errors.
- 23 unique internal links resolve. Each page has exactly one H1, and all pages have the 7 nav items in order.
- No banned disclosure/commission sentences, no placeholder text, no raw affiliate URL anywhere in page HTML.
- Modal: hidden at 4 s, shown by 7 s, overlay and price present, fits the mobile viewport; Esc, × and outside click all close it; 24 h cooldown works; it doesn't show on /order. Toast: shows at about 5 s and hides after about 6 s. Reduced motion disables animations.
- All 19 image files are genuine WebP (RIFF/WEBP header); no PNG or JPG is shipped. All JSON-LD blocks parse.

## Final SEO report
| Page URL | SEO title | Chars | Meta description | Chars | Primary keyword | Indexed |
|---|---|---|---|---|---|---|
| https://everpitch.vercel.app/ | EverPitch | AI Webinar Software Bundle | 38 | EverPitch writes, designs, voices and hosts your webinar, then answers questions out loud. See features, the $199.10 Bundle and the 30-day guarantee. | 149 | AI webinar software | yes |
| https://everpitch.vercel.app/product-overview.html | What Is EverPitch? | AI Webinar Builder | 39 | What EverPitch is and what it creates: AI scripts, slides, voices, daily hosting and spoken Q&A, plus what the four-product Bundle adds. | 136 | what is EverPitch / EverPitch features | yes |
| https://everpitch.vercel.app/how-it-works.html | How EverPitch Works | AI Webinar Tool Steps | 43 | How EverPitch works in three steps: describe your webinar, review the AI script and slides, then share it. Covers inputs, live sessions and credits. | 148 | how EverPitch works | yes |
| https://everpitch.vercel.app/benefits.html | EverPitch Benefits | Automated AI Webinars | 42 | The benefits of EverPitch: no blank-page scripting, designer-quality slides, AI narration, daily hosting, spoken Q&A, 87 languages and funnel pages. | 148 | EverPitch benefits | yes |
| https://everpitch.vercel.app/focus-areas/index.html | EverPitch Focus Areas | AI Webinar Features | 43 | Explore EverPitch's four focus areas: AI script and slide creation, automated hosting with spoken Q&A, multilingual webinars, and registration pages. | 149 | AI webinar features | yes |
| https://everpitch.vercel.app/focus-areas/webinar-creation.html | EverPitch | AI Webinar Script & Slide Creation | 46 | How EverPitch drafts a webinar script and designs slides from an idea, document, PDF or recording, with 73 layouts, 11 styles and 30 voices. | 140 | AI webinar script and slides | yes |
| https://everpitch.vercel.app/focus-areas/automated-hosting-qa.html | EverPitch | Evergreen Webinar Hosting & Live Q&A | 48 | EverPitch hosts webinars daily on a shared clock in each viewer's timezone, and an AI host answers questions out loud from your content. | 136 | evergreen webinar hosting | yes |
| https://everpitch.vercel.app/focus-areas/multilingual-webinars.html | EverPitch | Multilingual Webinars in 87 Languages | 49 | Create translated, re-voiced copies of one EverPitch webinar in 87 languages. Visitors get their own language and analytics are combined. | 137 | multilingual webinars | yes |
| https://everpitch.vercel.app/focus-areas/registration-follow-up.html | EverPitch | Webinar Registration & Follow-Up | 44 | EverPitch builds registration pages, reminders, calendar invites, replay sales pages and follow-up emails around every webinar. | 127 | webinar registration page | yes |
| https://everpitch.vercel.app/reviews.html | EverPitch Customer Reviews & Complaints Check | 45 | EverPitch customer reviews and complaints: what we found, with no invented testimonials, plus verifiable facts on price, refunds and credits. | 141 | EverPitch customer reviews / complaints | yes |
| https://everpitch.vercel.app/product-review.html | EverPitch Review: Features, Benefits & Pros and Cons | 52 | Our EverPitch review: what the AI webinar tool does, does it work, is it legit, risks, pros and cons, the $199.10 price, refund policy and our verdict. | 151 | EverPitch review | yes |
| https://everpitch.vercel.app/blog/index.html | EverPitch Blog | Webinar Marketing Guides | 41 | Practical webinar marketing guides: live vs evergreen webinars, script structure and follow-up emails, written to help you sell with clarity. | 141 | webinar marketing guides | yes |
| https://everpitch.vercel.app/blog/live-vs-evergreen-webinars.html | Live vs Evergreen Webinars | EverPitch | 38 | Live or evergreen webinar? Compare effort, scheduling, Q&A and honesty rules to choose the format that suits your offer and your week. | 134 | live vs evergreen webinars | yes |
| https://everpitch.vercel.app/blog/webinar-script-structure.html | Webinar Script Structure That Sells | EverPitch | 47 | A practical webinar script outline: hook, promise, teaching, proof, offer and Q&A, with tips for keeping claims honest and the pitch natural. | 141 | webinar script structure | yes |
| https://everpitch.vercel.app/blog/webinar-follow-up-emails.html | Webinar Follow-Up Emails Plan | EverPitch | 41 | Plan webinar follow-up emails for attendees, early leavers and no-shows, with timing ideas and the CAN-SPAM basics to keep in mind. | 131 | webinar follow-up emails | yes |
| https://everpitch.vercel.app/faq.html | EverPitch FAQ | Pricing, Credits & Refunds | 42 | EverPitch FAQ: what the $199.10 Bundle includes, how credits work, spoken Q&A limits, client use, voice cloning consent and the 30-day refund policy. | 149 | EverPitch FAQ | yes |
| https://everpitch.vercel.app/order.html | Order EverPitch Bundle | $199.10 One Time | 41 | Continue to the official EverPitch Bundle checkout on JVZoo: four products, 8,000 monthly credits and a 30-day money-back guarantee. | 132 | order EverPitch Bundle | noindex |
| https://everpitch.vercel.app/affiliate-disclosure.html | Affiliate Disclosure | EverPitch | 32 | How this independent EverPitch website earns money: affiliate links to the seller's JVZoo checkout, and how that affects our content. | 133 | affiliate disclosure | yes |
| https://everpitch.vercel.app/disclaimer.html | Disclaimer | EverPitch | 22 | Important information about using this independent EverPitch website: accuracy, results, trademarks and third-party links. | 122 | disclaimer | yes |
| https://everpitch.vercel.app/privacy-policy.html | Privacy Policy | EverPitch | 26 | How this independent EverPitch website handles data: no accounts or forms, minimal browser storage, hosting logs and third-party checkout. | 138 | privacy policy | yes |
| https://everpitch.vercel.app/terms.html | Terms of Use | EverPitch | 24 | Terms for using this independent EverPitch information website, including accuracy, third-party purchases and limitation of liability. | 134 | terms of use | yes |
| https://everpitch.vercel.app/404.html | Page Not Found | EverPitch | 26 | The page you were looking for could not be found. Return to the EverPitch homepage or browse the guides. | 104 | — | noindex |

| Image (WebP, verified) | ALT text used |
|---|---|
| blog-evergreen-webinar-guide.webp | Illustrated cover for the article comparing live and evergreen webinars |
| blog-webinar-follow-up-emails.webp | Illustrated cover for the article on webinar follow-up emails |
| blog-webinar-script-structure.webp | Illustrated cover for the article on structuring a webinar script |
| everpitch-ai-webinar-software-mockup.webp | EverPitch review illustration: an EverPitch webinar room with AI-designed slide, narration and live chat answered by the AI host / EverPitch webinar room illustration: AI-designed slide, narration waveform and live chat answered by the AI host / Illustration of an EverPitch webinar room with a narrated slide and the AI host answering chat questions |
| everpitch-bundle-four-products.webp | EverPitch Bundle illustration showing Commercial, DFY Webinars, Kit Vault and Agency / EverPitch Bundle illustration with the four included products: Commercial, DFY Webinars, Kit Vault and Agency / EverPitch Bundle illustration: four stacked product windows labelled Commercial, DFY Webinars, Kit Vault and Agency, with 8,000 credits a month / Illustration of the four EverPitch Bundle products stacked: Commercial, DFY Webinars, Kit Vault and Agency |
| everpitch-features-composition.webp | EverPitch feature composition showing scripts, slides, voices, languages and Q&amp;A around the webinar room / EverPitch webinar room illustration surrounded by its features: scripts, slide layouts, voices, languages, Q&amp;A and reminder emails / EverPitch webinar room surrounded by its core features: AI scripts, slide layouts, voices, languages, Q&amp;A, emails, demos and timezones |
| everpitch-three-step-workflow.webp | Three-step EverPitch workflow diagram: describe, review, share |
| everpitch-verified-facts.webp | Graphic listing verifiable EverPitch Bundle facts: $199.10 one time, 30-day guarantee, JVZoo checkout and 8,000 credits a month |
| focus-automated-hosting-qa.webp | Illustration of EverPitch daily sessions in viewer-local times next to chat questions answered by the AI host / Illustration of EverPitch session times in viewer-local time and chat questions answered aloud by the AI host |
| focus-multilingual-webinars.webp | Illustration of EverPitch&#x27;s 87 supported languages surrounding a central badge |
| focus-registration-follow-up.webp | Illustration of the EverPitch funnel: register, remind, watch and buy |
| focus-webinar-creation.webp | Illustration of an EverPitch script draft beside a designed slide deck with 73 layouts and 11 styles |

## Review-keyword SEO strategy (added 19 Nov 2026)

**SERP research.** Searches for EverPitch review, legit, complaints and price queries on 19 Nov 2026 found **no EverPitch-specific reviews, complaints or forum threads**. Results for "EverPitch review" showed unrelated "Pitch" products. Similar JVZoo webinar tools are usually covered by affiliate pages titled "review", "legit or scam", "complaints", "OTO" and "pricing". No search-volume or difficulty data was available, so none is claimed.

**Keyword → page map** (one page per search intent, no duplicates):

| Search intent | Target page |
|---|---|
| EverPitch review · does it work · is it legit · pros and cons · is it worth it · side effects (→ risks) | `/product-review.html` |
| EverPitch reviews (customer) · EverPitch complaints | `/reviews.html` (retitled "Customer Reviews & Complaints Check"; links to the review) |
| EverPitch price | `/product-review.html#price`, plus the homepage pricing section and the FAQ |
| EverPitch ingredients (→ features) | `/product-overview.html` and `/product-review.html#features` |
| EverPitch benefits | `/benefits.html` |
| EverPitch refund / FAQ | `/faq.html` |

**Review page** (`/product-review.html`): title "EverPitch Review: Features, Benefits & Pros and Cons" (52 characters), self-canonical, `index, follow`, in the sitemap, with BreadcrumbList and Article JSON-LD. There is deliberately **no Product/Review rating schema**, because there's no genuine rating. It's linked from 21 pages: the footer, the homepage, What Is It, Benefits, Reviews, FAQ and every blog article. A "How this review was made" box states plainly that EverPitch was **not** personally tested.

Adapted for software: "ingredients" became a feature breakdown with **Seller says / Our analysis** labels, "scientific evidence" became independent NIST/FTC sources on the underlying technology, "side effects" became practical risks, and "consult a healthcare professional" became "who should get professional advice first".

**Not done: Google Search Console / Bing URL Inspection.** The site isn't deployed and I have no access to your accounts. After deploying, inspect `https://everpitch.vercel.app/product-review.html` in both tools, request indexing, and confirm the canonical shown there matches. Ranking and indexing aren't guaranteed.

## References & Research (all opened in a new tab; URLs found via search on 19 Nov 2026)
| Source | Title | URL | Type | Relevance |
|---|---|---|---|---|
| FTC | FTC's Endorsement Guides: What People Are Asking | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking | US Government Guidance | Testimonials and disclosures in webinars |
| FTC | The Consumer Reviews and Testimonials Rule: Q&A | https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers | US Government Guidance | Ban on fake (incl. AI) reviews |
| FTC | Disclosures 101 for Social Media Influencers | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | US Government Guidance | Affiliates promoting webinars |
| FTC | CAN-SPAM Act: A Compliance Guide for Business | https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business | US Government Guidance | Reminder and follow-up emails |
| FTC Business Blog | Keep your AI claims in check | https://www.ftc.gov/business-guidance/blog/2023/02/keep-your-ai-claims-check | US Government Guidance | Marketing AI products honestly |
| FTC Office of Technology | Preventing the Harms of AI-enabled Voice Cloning | https://www.ftc.gov/policy/advocacy-research/tech-at-ftc/2023/11/preventing-harms-ai-enabled-voice-cloning | US Government Research | Consent-based voice cloning |
| FTC | Protecting Personal Information: A Guide for Business | https://www.ftc.gov/business-guidance/resources/protecting-personal-information-guide-business | US Government Guidance | Handling registration data |
| SBA | Marketing and sales | https://www.sba.gov/business-guide/manage-your-business/marketing-sales | US Government Resource | Marketing plan basics |
| NIST | AI Risk Management Framework | https://www.nist.gov/itl/ai-risk-management-framework | Government Scientific Publication | Responsible use of AI tools |
| NIST | AI RMF: Generative AI Profile (NIST AI 600-1) | https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence | Government Scientific Publication | Generative AI (scripts and voices) |

## Rebuilding / reusing for the next product
`_source/` holds the generator (it's excluded from deployment):
- `render_images.py <site_dir>` renders the illustrations to WebP (needs Playwright + Chrome, Pillow).
- `build.py <site_dir>` writes every page, the sitemap, robots.txt, vercel.json and the IndexNow key file. It fails the build if any title is over 55 characters or any description is over 155.
- `devserver.py <site_dir> 8765` plus `qa.py` and `popup_test.py` run the local test suite.
Product facts, the affiliate URL, the domain, page copy, FAQs and references are all at the top of `build.py`.
