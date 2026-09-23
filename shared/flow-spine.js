/*! Sheehan Exec Suite — Ops → Sales → Investors flow spine (inject once per page).
 *  Mark the host page with: <body data-flow-face="ops|sales|investor" data-flow-chip="bdr-tam|big-enterprise|sponsor|violet|subscription|…">
 *  Or set window.__FLOW_FACE__ / window.__FLOW_CHIP__ before this script runs.
 */
(function () {
  if (window.__SHEEHAN_FLOW_SPINE__) return;
  window.__SHEEHAN_FLOW_SPINE__ = true;

  var FACE =
    (document.body && document.body.getAttribute("data-flow-face")) ||
    window.__FLOW_FACE__ ||
    "ops";
  var CHIP =
    (document.body && document.body.getAttribute("data-flow-chip")) ||
    window.__FLOW_CHIP__ ||
    "";

  // Infer face/chip from filename when not set
  try {
    var path = (location.pathname || "").split("/").pop() || "";
    if (!document.body.getAttribute("data-flow-face") && !window.__FLOW_FACE__) {
      if (/^investor-/.test(path) || path === "macro-radar.html") FACE = "investor";
      else if (
        /^(bdr-tam|bdr-pipeline|crm-icp|consumer-inbound|org-whitespace|catalogue-close|hail-mary)\.html$/.test(
          path
        )
      )
        FACE = "sales";
      else FACE = "ops";
    }
    if (!CHIP) {
      if (path === "bdr-tam.html") {
        var q = new URLSearchParams(location.search || "");
        var lane = q.get("lane") || "";
        if (lane.indexOf("Enterprise") >= 0) CHIP = "big-enterprise";
        else if (lane.indexOf("Sponsor") >= 0) CHIP = "sponsor";
        else if (lane.indexOf("Subscription") >= 0) CHIP = "subscription";
        else if (lane.indexOf("Violet") >= 0) CHIP = "violet";
        else if (lane.indexOf("Hail") >= 0) CHIP = "hail-mary";
        else CHIP = "bdr-tam";
      } else if (path === "bdr-pipeline.html") CHIP = "big-enterprise";
      else if (path === "consumer-inbound.html") CHIP = "violet";
      else if (path === "crm-icp.html") CHIP = "subscription";
      else if (path === "hail-mary.html") CHIP = "hail-mary";
      else if (path === "investor-checklist.html") CHIP = "checklist";
      else if (path === "investor-capital.html") CHIP = "capital";
      else if (path === "investor-home.html") CHIP = "home";
    }
  } catch (e) {}

  var css =
    ".flow-spine{margin:0 0 14px;padding:12px 14px;border:1px solid var(--line,#1e2a44);border-radius:14px;background:#0f1728}" +
    ".flow-spine .flow-lbl{font-size:.68rem;color:var(--muted,#93a0b8);text-transform:uppercase;letter-spacing:.07em;margin:0 0 8px}" +
    ".flow-spine .flow-faces{display:flex;flex-wrap:wrap;gap:8px;align-items:center}" +
    ".flow-spine .flow-faces a{padding:8px 16px;border-radius:999px;font-size:.84rem;font-weight:700;border:1px solid var(--line,#1e2a44);background:var(--card,#121a2b);color:var(--muted,#93a0b8);text-decoration:none}" +
    ".flow-spine .flow-faces a:hover{border-color:var(--accent,#5b8cff);color:#fff;text-decoration:none}" +
    ".flow-spine .flow-faces a.on{border-color:var(--good,#3dd68c);background:#13281d;color:#fff}" +
    ".flow-spine .flow-faces a.on.sales{border-color:#5b8cff88;background:#152238}" +
    ".flow-spine .flow-faces a.on.investor{border-color:#a78bfa88;background:#1a1530}" +
    ".flow-spine .flow-arrow{color:var(--muted,#93a0b8);font-weight:600;opacity:.7;padding:0 2px}" +
    ".flow-spine .flow-sub{display:flex;flex-wrap:wrap;gap:7px;align-items:center;margin-top:10px;padding-top:10px;border-top:1px solid #1e2a4488}" +
    ".flow-spine .flow-sub .sl{font-size:.68rem;color:var(--muted,#93a0b8);text-transform:uppercase;letter-spacing:.06em;margin-right:4px}" +
    ".flow-spine .flow-sub a{padding:5px 11px;border-radius:999px;font-size:.74rem;font-weight:600;border:1px solid var(--line,#1e2a44);background:var(--card,#121a2b);color:var(--text,#e8eefc);text-decoration:none}" +
    ".flow-spine .flow-sub a:hover{border-color:var(--accent,#5b8cff);text-decoration:none}" +
    ".flow-spine .flow-sub a.on{border-color:var(--accent,#5b8cff);background:#152238;color:#fff}" +
    ".flow-spine .flow-sub a.vio{border-color:#a78bfa55}" +
    ".flow-spine .flow-sub a.vio.on{border-color:#a78bfa99;background:#1a1530;color:#d4c4ff}" +
    ".flow-spine .flow-sub a.sp{border-color:#ffb02055}" +
    ".flow-spine .flow-sub a.sp.on{border-color:#ffb02099;background:#2a2416;color:var(--warn,#ffb020)}.flow-spine .flow-sub a.hm{border-color:#f0abfc55}.flow-spine .flow-sub a.hm.on{border-color:#f0abfc99;background:#2a1530;color:#f5d0fe}" +
    ".flow-spine .flow-hint{font-size:.72rem;color:var(--muted,#93a0b8);margin-top:8px;line-height:1.4}" +
    ".flow-spine .flow-hint a{color:var(--accent,#5b8cff)}" +
    /* hide legacy two-chip faces when spine present */
    ".faces.legacy-faces{display:none!important}";

  var style = document.createElement("style");
  style.setAttribute("data-flow-spine", "1");
  style.textContent = css;
  document.head.appendChild(style);

  function a(href, label, cls, on) {
    return (
      '<a href="' +
      href +
      '" class="' +
      (cls || "") +
      (on ? " on" : "") +
      '">' +
      label +
      "</a>"
    );
  }

  var salesSubs =
    '<div class="flow-sub" id="flow-sales-sub">' +
    '<span class="sl">Sales</span>' +
    a("bdr-tam.html", "BDR TAM", "", CHIP === "bdr-tam") +
    a(
      "bdr-tam.html?lane=" + encodeURIComponent("Regional Enterprise"),
      "Big Enterprise",
      "",
      CHIP === "big-enterprise"
    ) +
    a(
      "bdr-tam.html?lane=" + encodeURIComponent("Sponsor"),
      "Sponsor",
      "sp",
      CHIP === "sponsor"
    ) +
    a("consumer-inbound.html", "Violet", "vio", CHIP === "violet") +
    a(
      "bdr-tam.html?lane=" + encodeURIComponent("Regional Subscription"),
      "Subscription",
      "",
      CHIP === "subscription"
    ) +
    a("bdr-pipeline.html", "Pipeline", "", CHIP === "pipeline" || (CHIP === "big-enterprise" && /bdr-pipeline/.test(location.pathname || ""))) +
    a("bdr-tam.html?lane=" + encodeURIComponent("Hail Mary"), "Hail Mary", "hm", CHIP === "hail-mary") +
    "</div>";

  var investorSubs =
    '<div class="flow-sub" id="flow-investor-sub">' +
    '<span class="sl">Investors</span>' +
    a("investor-checklist.html", "Checklist", "", CHIP === "checklist" || /investor-checklist/.test(location.pathname || "")) +
    a("investor-home.html", "Home", "", CHIP === "home" || (/investor-home/.test(location.pathname || "") && CHIP !== "checklist")) +
    a("investor-capital.html", "Capital", "", CHIP === "capital" || /investor-capital/.test(location.pathname || "")) +
    a("bookings-dates.html", "Bookings (Sales proof)", "", false) +
    a("money-cfo.html", "Money (Sales proof)", "", false) +
    a("actions-overdue.html", "Ops traction", "", false) +
    "</div>";

  var html =
    '<nav class="flow-spine" aria-label="Ops Sales Investors spine" data-face="' +
    FACE +
    '">' +
    '<div class="flow-lbl">Flow spine</div>' +
    '<div class="flow-faces">' +
    a("index.html", "Operations", "ops", FACE === "ops") +
    '<span class="flow-arrow" aria-hidden="true">→</span>' +
    a("bdr-tam.html", "Sales", "sales", FACE === "sales") +
    '<span class="flow-arrow" aria-hidden="true">→</span>' +
    a("investor-home.html", "Investors", "investor", FACE === "investor") +
    "</div>" +
    (FACE === "sales" || FACE === "ops" ? salesSubs : "") +
    (FACE === "investor" ? investorSubs : "") +
    (FACE === "investor"
      ? '<div class="flow-hint">Investor face · <a href="investor-checklist.html">Seed / pre-seed checklist</a> (Assets · Proof · Founder · Co-founder · Ops) · hop to <a href="bookings-dates.html">bookings</a> / <a href="money-cfo.html">money</a> for Sales proof.</div>'
      : FACE === "sales"
      ? '<div class="flow-hint">Sales face · Big Enterprise · Sponsor · Violet · Subscription · Hail Mary (Inspired · God-connected · Local celeb · Philanthropist · Local biz-sponsor · Bazillionaires — same GTM offers).</div>'
      : '<div class="flow-hint">Operations face · Money · Bookings · Actions · Ann-Marie. Use Sales chips to dial without hunting.</div>') +
    "</nav>";

  function mount() {
    var wrap =
      document.querySelector(".wrap") ||
      document.querySelector("main") ||
      document.body;
    if (!wrap) return;
    // Prefer insert after .apps if present, else top of wrap
    var box = document.createElement("div");
    box.innerHTML = html;
    var node = box.firstChild;
    var apps = wrap.querySelector(".apps, .app-top");
    if (apps && apps.parentNode === wrap) {
      apps.insertAdjacentElement("afterend", node);
    } else if (wrap.firstChild) {
      wrap.insertBefore(node, wrap.firstChild);
    } else {
      wrap.appendChild(node);
    }
    // Mark legacy faces hidden
    wrap.querySelectorAll(".faces").forEach(function (el) {
      el.classList.add("legacy-faces");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
