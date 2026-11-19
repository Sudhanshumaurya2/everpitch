#!/usr/bin/env node
/**
 * IndexNow notifier for everpitch.vercel.app
 * Run AFTER a deployment is live:  node scripts/indexnow.mjs
 *   --all     submit every sitemap URL (first run)
 *   --dry     show what would be sent, send nothing
 * Only canonical URLs from sitemap.xml are sent. Changed files are detected by content hash,
 * so unchanged URLs are not re-submitted. URLs removed from the sitemap are submitted once
 * so search engines can recrawl them and see the 404/410.
 * Docs: https://www.indexnow.org/documentation
 */
import { readFileSync, writeFileSync, existsSync, readdirSync } from "node:fs";
import { createHash } from "node:crypto";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const HOST = "everpitch.vercel.app";
const ORIGIN = `https://${HOST}`;
const KEY = readdirSync(ROOT).find(f => /^[a-f0-9]{32}\.txt$/.test(f))?.replace(".txt", "");
const STATE = join(ROOT, ".indexnow-state.json");
const args = new Set(process.argv.slice(2));

if (!KEY) { console.error("IndexNow key file not found at site root."); process.exit(1); }

const sitemap = readFileSync(join(ROOT, "sitemap.xml"), "utf8");
const urls = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1]).filter(u => u.startsWith(ORIGIN + "/"));

const fileFor = u => { const p = new URL(u).pathname; return join(ROOT, p === "/" ? "index.html" : p.slice(1)); };
const hash = f => existsSync(f) ? createHash("sha256").update(readFileSync(f)).digest("hex") : null;

const prev = existsSync(STATE) ? JSON.parse(readFileSync(STATE, "utf8")) : {};
const next = {};
const changed = [];
for (const u of urls) {
  const h = hash(fileFor(u));
  next[u] = h;
  if (args.has("--all") || prev[u] !== h) changed.push(u);
}
const removed = Object.keys(prev).filter(u => !(u in next));
const toSend = [...new Set([...changed, ...removed])];

if (!toSend.length) { console.log("Nothing changed — no IndexNow request sent."); process.exit(0); }
console.log(`Submitting ${toSend.length} URL(s):\n` + toSend.join("\n"));
if (args.has("--dry")) process.exit(0);

// Verify the key file is publicly reachable before submitting.
const keyLocation = `${ORIGIN}/${KEY}.txt`;
const kr = await fetch(keyLocation).catch(() => null);
if (!kr || !kr.ok || (await kr.text()).trim() !== KEY) {
  console.error(`Key file check failed at ${keyLocation}. Deploy first, then re-run.`); process.exit(1);
}

const body = JSON.stringify({ host: HOST, key: KEY, keyLocation, urlList: toSend });
for (let attempt = 1; attempt <= 4; attempt++) {
  const r = await fetch("https://api.indexnow.org/indexnow", {
    method: "POST", headers: { "Content-Type": "application/json; charset=utf-8" }, body
  }).catch(e => ({ ok: false, status: 0, statusText: String(e) }));
  console.log(`Attempt ${attempt}: HTTP ${r.status} ${r.statusText || ""}`);
  if (r.status === 200 || r.status === 202) {
    writeFileSync(STATE, JSON.stringify(next, null, 2));
    console.log("Accepted by IndexNow. Note: acceptance means the URLs were received, not that they are indexed.");
    process.exit(0);
  }
  if ([400, 403, 422].includes(r.status)) { console.error("Request rejected — check key, host and URLs. Not retrying."); process.exit(1); }
  await new Promise(res => setTimeout(res, 2000 * 2 ** attempt)); // 429 / 5xx / network: back off
}
console.error("IndexNow submission failed after retries."); process.exit(1);
