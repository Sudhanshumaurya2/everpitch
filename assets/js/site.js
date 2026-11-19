/* EverPitch affiliate site — interactions.
   Reusable components: mobile nav, reveal-on-scroll, 3D pointer tilt,
   promo modal (centered, 24h cooldown), info toast (bottom-left).
   Product-specific text lives in SITE_CONFIG below — edit it per product. */
(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");

  var SITE_CONFIG = {
    modal: { delayMs: 6000, cooldownHours: 24, storageKey: "ep_modal_seen" },
    toast: {
      firstMs: 5000, showMs: 6000, gapMinMs: 18000, gapMaxMs: 26000,
      // Informational messages only — no invented buyers, cities, counts or ratings.
      messages: [
        { t: "Compare the two EverPitch options", s: "EverPitch on its own, or the Bundle with four products switched on.", href: "/#compare" },
        { t: "30-day money-back guarantee", s: "The seller refunds through JVZoo if you ask within 30 days of buying.", href: "/faq.html" },
        { t: "The Bundle is a one-time payment", s: "$199.10 once, with no yearly renewal.", href: "/order?package=bundle" },
        { t: "24 ready-made webinar kits", s: "The Kit Vault in the Bundle starts you from structure, not a blank page.", href: "/benefits.html" },
        { t: "Webinars in 87 languages", s: "Translated, re-voiced copies are linked together automatically.", href: "/focus-areas/multilingual-webinars.html" }
      ]
    }
  };

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---------- Mobile navigation ---------- */
  var btn = document.querySelector(".menu-btn");
  var links = document.getElementById("nav-links");
  if (btn && links) {
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!open));
      links.classList.toggle("open", !open);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && links.classList.contains("open")) {
        btn.setAttribute("aria-expanded", "false"); links.classList.remove("open"); btn.focus();
      }
    });
  }

  /* ---------- Reveal on scroll ---------- */
  var revealEls = document.querySelectorAll(".reveal");
  if (!reduce && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- 3D pointer tilt on hero product ---------- */
  var stage = document.querySelector("[data-tilt-stage]");
  if (stage && !reduce && window.matchMedia("(pointer:fine)").matches) {
    var prod = stage.querySelector(".product");
    stage.addEventListener("pointermove", function (e) {
      var r = stage.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
      prod.style.transform = "rotateY(" + (x * 14).toFixed(2) + "deg) rotateX(" + (-y * 10).toFixed(2) + "deg) translateZ(20px)";
    });
    stage.addEventListener("pointerleave", function () { prod.style.transform = ""; });
  }

  /* ---------- Outbound purchase click tracking (no personal data) ---------- */
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[data-cta]");
    if (!a) return;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: "cta_click", cta: a.getAttribute("data-cta"), page: location.pathname });
  });

  /* ---------- Promo modal ---------- */
  var modal = document.getElementById("ep-modal");
  var modalOpen = false, lastFocus = null;
  function focusables() { return modal.querySelectorAll('a[href],button:not([disabled])'); }
  function openModal() {
    if (!modal || modalOpen) return;
    hideToast();
    modalOpen = true; lastFocus = document.activeElement;
    modal.hidden = false;
    requestAnimationFrame(function () { modal.classList.add("show"); });
    document.body.classList.add("modal-open");
    store.set(SITE_CONFIG.modal.storageKey, String(Date.now()));
    var f = focusables(); if (f.length) setTimeout(function () { f[0].focus(); }, 60);
  }
  function closeModal() {
    if (!modalOpen) return;
    modalOpen = false;
    modal.classList.remove("show");
    document.body.classList.remove("modal-open");
    setTimeout(function () { modal.hidden = true; }, reduce ? 0 : 320);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  if (modal) {
    modal.addEventListener("click", function (e) { if (e.target === modal || e.target.closest(".x")) closeModal(); });
    document.addEventListener("keydown", function (e) {
      if (!modalOpen) return;
      if (e.key === "Escape") { closeModal(); return; }
      if (e.key === "Tab") {
        var f = focusables(), first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    var seen = parseInt(store.get(SITE_CONFIG.modal.storageKey) || "0", 10);
    var cooled = !seen || (Date.now() - seen) > SITE_CONFIG.modal.cooldownHours * 3600 * 1000;
    var isOrderPage = document.body.hasAttribute("data-no-promo");
    if (cooled && !isOrderPage) {
      var start = function () { setTimeout(openModal, SITE_CONFIG.modal.delayMs); };
      if (document.readyState === "complete") start(); else window.addEventListener("load", start);
    }
  }

  /* ---------- Info toast (bottom-left) ---------- */
  var toast = document.getElementById("ep-toast");
  var tIdx = 0, tTimer = null, tDismissed = false;
  function hideToast() { if (toast) toast.classList.remove("show"); }
  function showToast() {
    if (!toast || tDismissed) return;
    if (modalOpen) { schedule(); return; }           // never overlap the modal
    var m = SITE_CONFIG.toast.messages[tIdx % SITE_CONFIG.toast.messages.length]; tIdx++;
    toast.querySelector("b").textContent = m.t;
    var s = toast.querySelector("span"); s.textContent = m.s + " ";
    var a = document.createElement("a"); a.href = m.href; a.textContent = "See details"; s.appendChild(a);
    toast.classList.add("show");
    setTimeout(function () { hideToast(); schedule(); }, SITE_CONFIG.toast.showMs);
  }
  function schedule() {
    clearTimeout(tTimer);
    var c = SITE_CONFIG.toast, gap = c.gapMinMs + Math.random() * (c.gapMaxMs - c.gapMinMs);
    tTimer = setTimeout(showToast, gap);
  }
  if (toast && !document.body.hasAttribute("data-no-promo")) {
    toast.querySelector(".tx").addEventListener("click", function () {
      tDismissed = true; clearTimeout(tTimer); hideToast();
      try { sessionStorage.setItem("ep_toast_off", "1"); } catch (e) {}
    });
    var off = false; try { off = sessionStorage.getItem("ep_toast_off") === "1"; } catch (e) {}
    if (!off) tTimer = setTimeout(showToast, SITE_CONFIG.toast.firstMs);
  }
})();
