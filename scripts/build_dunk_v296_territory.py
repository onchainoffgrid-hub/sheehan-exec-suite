#!/usr/bin/env python3
"""Board v2.9.6 — PM territory / Ross-type cluster notes on principal dunk."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path("/workspace/sheehan-exec-suite")
BOARD_PATH = ROOT / "data" / "principal_dunk_board.json"
SUMMARY_PATH = ROOT / "data" / "_dunk_v296_summary.json"
HTML_PATH = ROOT / "principal-dunk.html"
ET = ZoneInfo("America/New_York")
AS_OF = datetime.now(ET).strftime("%Y-%m-%d %-I:%M %p ET")
VERSION = "Board v2.9.6 · Sep 25 · PM territory / Ross-type clusters"

TERRITORY_HELP = {
    "title": "PM territory · Ross vs site booker",
    "source": "PM_TERRITORY_MAP_2026-09-25.md (Talk-Deputy lock)",
    "bullets": [
        "Vesta ≠ all Ross: Mindy DeAngelis = HQ Lunch&Learn / pizza door · Ross Ruben = list intro · Winslow Wheeler = NE Amenity Ops boss · site bookers (Kate / Kaylie / Kimberly…) book the money separately.",
        "First Coast CMS / SilverLeaf = second Vesta: Tony Shiver (owner / Ross via service@) + Liz Giacobbi (engagement win-back).",
        "MAY = ask customerservice@maymgt.com for portfolio Lifestyle Ross (Jane / Kelly are CAMs, not full Ross).",
        "GMS = multi-CDD amenity phones (Bartram / Greyhawk / Amelia…), not one pizza day.",
        "FSR Shearwater / Nocatee / Wildlight = own trees — do not file under Vesta.",
        "Wallet: A big amenity (~$1–3k+) · B mid (~$1–2k) · C small/light · Club/independent = one-off.",
    ],
}

# Explicit annotations keyed by email (lower) or id. Prefer enhance, no fake emails.
# management_company chips: Vesta | First Coast CMS | MAY | GMS | FSR | Independent | Nocatee | Wildlight
ANNOTATIONS = {
    # --- Vesta Ross-types / HQ ---
    "rruben@vestapropertyservices.com": {
        "management_company": "Vesta",
        "ross_type": "Ross-type",
        "wallet_class": "A",
        "board_note": "List intro — not every Vesta buy. Pair with site bookers for money. Mindy = HQ L&L/pizza door; Winslow = NE Amenity Ops.",
    },
    "wwheeler@vestapropertyservices.com": {
        "management_company": "Vesta",
        "ross_type": "Ross-type",
        "wallet_class": "A",
        "board_note": "NE Region Amenity Ops boss — above Glen St. Johns-class. Regional, not a Saturday booker.",
    },
    # --- Vesta site bookers (A) ---
    "klsmith@vestapropertyservices.com": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "A",
        "board_note": "Durbin site booker — money lands here; converts without Ross/Mindy on thread.",
    },
    "kfatuch@vestapropertyservices.com": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "A",
        "board_note": "RiverTown events / AGM — site money, not Ross.",
    },
    "kcouncil@vestapropertyservices.com": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "A",
        "board_note": "RiverTown amenity manager — site desk.",
    },
    "kfitzhugh@vestapropertyservices.com": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "A",
        "board_note": "Tamaya events / AA — site booker.",
    },
    "oingram@vestapropertyservices.com": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "A",
        "board_note": "Tamaya amenity manager — site desk.",
    },
    "staylor@vestapropertyservices.com": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "A",
        "board_note": "Sampson / SJG amenities GM — site booker.",
    },
    "mdorsey@jcpcdd.org": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "A",
        "board_note": "JCP / Vesta site path — CDD amenity desk books money.",
    },
    "dkincaid@jcpcdd.org": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "A",
        "board_note": "JCP CDD (Vesta) — site / district path.",
    },
    "recharge@etownjax.com": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "B",
        "board_note": "eTown / Cypress Bluff Vesta lifestyle inbox — site desk.",
    },
    # --- Vesta site bookers (B/C) ---
    "dpowers@vestapropertyservices.com": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "B",
        "board_note": "Palencia amenities — site booker (B-class).",
    },
    "jmoore@vestapropertyservices.com": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "B",
        "board_note": "Palencia GM — site desk, not Ross.",
    },
    "dmcinnes@vestapropertyservices.com": {
        "management_company": "Vesta",
        "ross_type": "Ops / district",
        "wallet_class": "B",
        "board_note": "Palencia district (Vesta) — map amenity desk; rarely the entertainment buyer.",
    },
    "hila.stalcup@marshallcreekcdd.com": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "B",
        "board_note": "Marshall Creek / Palencia Vesta path — site desk.",
    },
    "ghamilton@vestapropertyservices.com": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "C",
        "board_note": "Johns Creek — light/C-class site desk.",
    },
    "campheritage@heritagelanding.comcastbiz.net": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "B",
        "board_note": "Heritage Landing Vesta camp / amenity — site desk.",
    },
    "wynnfieldlakesmanager@gmail.com": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "C",
        "board_note": "Wynnfield Lakes (Vesta) — C/light asks only.",
    },
    "jamorrow@vestapropertyservices.com": {
        "management_company": "Vesta",
        "ross_type": "Site booker",
        "wallet_class": "A",
        "board_note": "Durbin amenity manager — site desk next to Kate.",
    },
    "jarias@vestapropertyservices.com": {
        "management_company": "Vesta",
        "ross_type": "CAM",
        "wallet_class": "B",
        "board_note": "Bartram Springs HOA CAM (Vesta) — HOA path; amenity may sit with GMS phones.",
    },
    # --- First Coast CMS / SilverLeaf ---
    "desk@silverleafamenities.com": {
        "management_company": "First Coast CMS",
        "ross_type": "Ross-peer",
        "wallet_class": "A",
        "board_note": "Liz · Engagement win-back for SilverLeaf. Closest Ross-peer booker under Tony/FCCMS.",
    },
    "liz@firstcoastcms.com": {
        "management_company": "First Coast CMS",
        "ross_type": "Ross-peer",
        "wallet_class": "A",
        "board_note": "Liz Giacobbi · SilverLeaf / FCCMS — engagement win-back (same tree as desk@).",
    },
    "service@firstcoastcms.com": {
        "management_company": "First Coast CMS",
        "ross_type": "Ross-type",
        "wallet_class": "A",
        "board_note": "Tony Shiver owner inbox — THE Ross outside Vesta. Opens lifestyle/amenity managers across FCCMS.",
    },
    "form-first-coast-cms-contact": {
        "management_company": "First Coast CMS",
        "ross_type": "Ross-type",
        "wallet_class": "A",
        "board_note": "FCCMS portfolio form · ask who owns Lifestyle / amenity events (Tony tree). Second Vesta.",
    },
    # --- MAY ---
    "jsapere@maymgt.com": {
        "management_company": "MAY",
        "ross_type": "CAM",
        "wallet_class": "C",
        "board_note": "Jane = CAM (Stonehaven-class) — not full Ross. Ask customerservice for portfolio Lifestyle Ross.",
    },
    "kfrick@maymgt.com": {
        "management_company": "MAY",
        "ross_type": "CAM",
        "wallet_class": "C",
        "board_note": "Kelly = CAM — not full Ross. Route Lifestyle ask via customerservice@maymgt.com.",
    },
    "customerservice@maymgt.com": {
        "management_company": "MAY",
        "ross_type": "Ross-gap",
        "wallet_class": "B",
        "board_note": "Ask for named portfolio Lifestyle / Resident Experience Ross across MAY HOAs.",
    },
    "sales@maymgt.com": {
        "management_company": "MAY",
        "ross_type": "Ross-gap",
        "wallet_class": "B",
        "board_note": "MAY sales inbox — ask who owns Lifestyle across portfolio.",
    },
    # --- GMS ---
    "ddemarco@gmsnf.com": {
        "management_company": "GMS",
        "ross_type": "Ops phone",
        "wallet_class": "A",
        "board_note": "GMS amenity phone cluster — dial by CDD, not one pizza day. Bartram Springs amenity.",
    },
    "joliver@gmsnf.com": {
        "management_company": "GMS",
        "ross_type": "Ops / district",
        "wallet_class": "A",
        "board_note": "GMS district — infrastructure-heavy; amenity events may sit with HOA/amenity phones.",
    },
    "mbiagetti@gmsnf.com": {
        "management_company": "GMS",
        "ross_type": "Ops / district",
        "wallet_class": "A",
        "board_note": "GMS district · amenity phones 904-880-5156 cluster — multi-CDD, not one Ross lunch.",
    },
    "kmullins@gmsnf.com": {
        "management_company": "GMS",
        "ross_type": "Ops phone",
        "wallet_class": "B",
        "board_note": "GMS amenity/ops — dial this CDD phone; no single pizza Ross.",
    },
    "ameliawalkmanager@gmsnf.com": {
        "management_company": "GMS",
        "ross_type": "Ops phone",
        "wallet_class": "B",
        "board_note": "GMS amenity phone (Chip) — multi-CDD cluster.",
    },
    "greyhawkmanager@gmsnf.com": {
        "management_company": "GMS",
        "ross_type": "Ops phone",
        "wallet_class": "B",
        "board_note": "GMS Greyhawk amenity — dial by CDD.",
    },
    # --- FSR / Shearwater ---
    "belynda.tharpe@fsresidential.com": {
        "management_company": "FSR",
        "ross_type": "Site + brand",
        "wallet_class": "A",
        "board_note": "Shearwater / Trout Creek FSR GM — own tree, not Vesta. Pair Marcia/Lifestyle if needed.",
    },
    "jessica.knutelsky@fsresidential.com": {
        "management_company": "FSR",
        "ross_type": "Site booker",
        "wallet_class": "A",
        "board_note": "Shearwater FSR amenity path — own tree.",
    },
    "canopyclub@fsresidential.com": {
        "management_company": "FSR",
        "ross_type": "Site booker",
        "wallet_class": "A",
        "board_note": "Del Webb Nocatee Lifestyle (FSR) — own canopy, not Vesta.",
    },
    # --- Nocatee / Wildlight own trees ---
    "help@nocatee.com": {
        "management_company": "Nocatee",
        "ross_type": "Own tree",
        "wallet_class": "A",
        "board_note": "Nocatee / Tolomato mega-community — own ecosystem, not Vesta.",
    },
    "welcomecenter@nocatee.com": {
        "management_company": "Nocatee",
        "ross_type": "Own tree",
        "wallet_class": "A",
        "board_note": "Nocatee Welcome Center — own tree.",
    },
    "wes.hinton@wildlight.com": {
        "management_company": "Wildlight",
        "ross_type": "Own tree",
        "wallet_class": "B",
        "board_note": "Wildlight developer lifestyle — own tree (Nassau), not Vesta.",
    },
    "info@eastnassausd.net": {
        "management_company": "Wildlight",
        "ross_type": "Own tree",
        "wallet_class": "B",
        "board_note": "ENSD / Wildlight district inbox — pair Wes; own tree.",
    },
    # --- Independent club ---
    "jmorgan@jaxgcc.com": {
        "management_company": "Independent",
        "ross_type": "Club wallet",
        "wallet_class": "Club",
        "board_note": "Jax GCC Director of Fun — independent club wallet (Ross warm-intro possible).",
    },
}

# Heuristic fallbacks when email/id not in ANNOTATIONS
DOMAIN_MGMT = [
    (r"@vestapropertyservices\.com$", "Vesta", None, None),
    (r"@gmsnf\.com$", "GMS", "Ops phone", None),
    (r"@fsresidential\.com$", "FSR", None, None),
    (r"@maymgt\.com$", "MAY", "CAM", None),
    (r"@firstcoastcms\.com$", "First Coast CMS", None, None),
    (r"@silverleafamenities\.com$", "First Coast CMS", "Ross-peer", "A"),
    (r"@nocatee\.com$", "Nocatee", "Own tree", "A"),
    (r"@wildlight\.com$", "Wildlight", "Own tree", "B"),
    (r"@eastnassausd\.net$", "Wildlight", "Own tree", "B"),
    (r"@jaxgcc\.com$", "Independent", "Club wallet", "Club"),
]

ACCOUNT_HINTS = [
    (r"\bvesta\b", "Vesta"),
    (r"first coast cms|silverleaf|silver leaf", "First Coast CMS"),
    (r"\bmay\b|may management|maymgt", "MAY"),
    (r"\bgms\b", "GMS"),
    (r"firstservice|fsr\b|shearwater|del webb", "FSR"),
    (r"nocatee|tolomato", "Nocatee"),
    (r"wildlight|east nassau", "Wildlight"),
]

# Published seats to ADD only if missing (no invented emails).
NEW_SEATS = [
    {
        "id": "wwheeler-vesta-ne-amenity-ops",
        "account": "Vesta Property Services (NE Amenity Ops)",
        "contact": "Winslow Wheeler",
        "title": "Dir. Amenity Operations, N.E. Region",
        "email": "wwheeler@vestapropertyservices.com",
        "phone": "904-318-0796",
        "city": "Jacksonville",
        "area": "Metro Jax · Vesta HQ / NE region",
        "segment": "CDD / HOA",
        "persona": "cdd",
        "kind": "mailto",
        "lane": "premium",
        "tier": "S",
        "premium": True,
        "friday": True,
        "friday_class": "cdd_amenity",
        "website": "https://www.vestapropertyservices.com/",
        "subject": "NE amenity programming — Critters on Call",
        "why": "Friday priority — regional amenity ops boss. Vesta NE Amenity Ops above Glen St. Johns-class. Ross-type regional, not Saturday booker.",
        "spend_hint": "Wallet A — regional amenity boss (opens site desks)",
        "management_company": "Vesta",
        "ross_type": "Ross-type",
        "wallet_class": "A",
        "board_note": "NE Region Amenity Ops boss — above Glen St. Johns-class. Regional, not a Saturday booker.",
        "chip_tags": ["Friday", "Vesta", "Ross-type"],
        "role_chip": "Ross-type",
        "sections": ["premium", "cdd"],
    },
    {
        "id": "service-firstcoastcms-tony-shiver",
        "account": "First Coast CMS (Tony Shiver / owner)",
        "contact": "Tony Shiver",
        "title": "Owner / President",
        "email": "service@firstcoastcms.com",
        "phone": "904-537-9034",
        "city": "St. Augustine",
        "area": "St. Johns · SilverLeaf / FCCMS portfolio",
        "segment": "CDD / HOA",
        "persona": "cdd",
        "kind": "mailto",
        "lane": "premium",
        "tier": "S",
        "premium": True,
        "friday": True,
        "friday_class": "cdd_amenity",
        "website": "https://www.firstcoastcms.com/",
        "form_url": "https://www.firstcoastcms.com/contact",
        "subject": "Lifestyle / amenity programming — Critters on Call",
        "why": "Friday priority — THE Ross outside Vesta. Owner inbox opens lifestyle/amenity managers (SilverLeaf + FCCMS portfolio).",
        "spend_hint": "Wallet A — second Vesta (FCCMS / SilverLeaf)",
        "management_company": "First Coast CMS",
        "ross_type": "Ross-type",
        "wallet_class": "A",
        "board_note": "Tony Shiver owner inbox — THE Ross outside Vesta. Opens lifestyle/amenity managers across FCCMS.",
        "chip_tags": ["Friday", "First Coast CMS", "Ross-type"],
        "role_chip": "Ross-type",
        "sections": ["premium", "cdd"],
    },
    {
        "id": "customerservice-maymgt-lifestyle-ross-ask",
        "account": "MAY Management (portfolio Lifestyle ask)",
        "contact": "MAY Customer Service",
        "title": "Ask for Lifestyle / Resident Experience Ross",
        "email": "customerservice@maymgt.com",
        "phone": "904-461-9708",
        "city": "St. Augustine",
        "area": "St. Augustine / PVB / WGV / JC / Palm Coast",
        "segment": "CDD / HOA",
        "persona": "cdd",
        "kind": "mailto",
        "lane": "premium",
        "tier": "A",
        "premium": True,
        "friday": True,
        "friday_class": "cdd_amenity",
        "website": "https://www.maymgt.com/",
        "subject": "Who owns Lifestyle across MAY? — Critters on Call",
        "why": "Friday priority — named portfolio Lifestyle Ross is a gap. Jane/Kelly are CAMs. Ask customerservice who owns Lifestyle.",
        "spend_hint": "Wallet B — portfolio Lifestyle path (Ross gap)",
        "management_company": "MAY",
        "ross_type": "Ross-gap",
        "wallet_class": "B",
        "board_note": "Ask for named portfolio Lifestyle / Resident Experience Ross across MAY HOAs. Jane/Kelly = CAMs only.",
        "chip_tags": ["Friday", "MAY", "Ross-gap"],
        "role_chip": "Ross-gap",
        "quick_body": (
            "Hi MAY team,\n\n"
            "Michael Sheehan with Sheehan Homestead / Critters on Call (Callahan / Jax metro). "
            "We bring a small mobile petting zoo for HOA/amenity family days.\n\n"
            "Who on your side owns Lifestyle / Resident Experience across the MAY portfolio "
            "(the person who can intro amenity desks the way a Ross-type would)? "
            "Happy to keep it short — just looking for the right name.\n\n"
            "Michael · 914-263-1311 · Callahan, FL"
        ),
        "sections": ["premium", "cdd"],
    },
]


def annotate_row(r: dict) -> bool:
    """Apply management_company / ross_type / board_note. Return True if changed."""
    before = json.dumps(
        {k: r.get(k) for k in ("management_company", "ross_type", "wallet_class", "board_note", "chip_tags", "role_chip")},
        sort_keys=True,
    )
    em = (r.get("email") or "").strip().lower()
    rid = (r.get("id") or "").strip()
    ann = ANNOTATIONS.get(em) or ANNOTATIONS.get(rid)

    if not ann:
        # domain / account heuristics — lighter touch
        mgmt = None
        ross = None
        wallet = None
        for pat, m, rt, w in DOMAIN_MGMT:
            if em and re.search(pat, em, re.I):
                mgmt, ross, wallet = m, rt, w
                break
        if not mgmt:
            blob = f"{r.get('account') or ''} {r.get('segment') or ''}"
            for pat, m in ACCOUNT_HINTS:
                if re.search(pat, blob, re.I):
                    mgmt = m
                    break
        # Form First Coast
        if rid == "form-first-coast-cms-contact" or (
            (r.get("form_url") or "").find("firstcoastcms.com") >= 0 and (r.get("account") or "").lower().find("first coast") >= 0
        ):
            ann = ANNOTATIONS["form-first-coast-cms-contact"]
        elif mgmt:
            ann = {"management_company": mgmt}
            if ross:
                ann["ross_type"] = ross
            if wallet:
                ann["wallet_class"] = wallet

    if not ann:
        return False

    for k in ("management_company", "ross_type", "wallet_class", "board_note"):
        if ann.get(k):
            r[k] = ann[k]

    # chips
    tags = list(r.get("chip_tags") or [])
    for label in (r.get("management_company"), r.get("ross_type")):
        if label and label not in tags:
            tags.append(label)
    r["chip_tags"] = tags

    # role_chip: prefer ross_type when set and role empty / generic
    if r.get("ross_type") and (not r.get("role_chip") or r.get("role_chip") in ("Enterprise", "FORM", "Daycare")):
        if r.get("kind") == "form" or (r.get("form_url") and not r.get("email")):
            # keep FORM visible via chip; still set role to ross_type for clarity
            r["role_chip"] = r["ross_type"]
        elif r.get("role_chip") != "FORM":
            r["role_chip"] = r["ross_type"]

    # spend_hint one-liner from wallet when missing/generic
    wc = r.get("wallet_class")
    if wc and (not r.get("spend_hint") or "premium wallet / $20k" in (r.get("spend_hint") or "")):
        hints = {
            "A": "Wallet A — big amenity (~$1–3k+ multi-date possible)",
            "B": "Wallet B — mid amenity (~$1–2k)",
            "C": "Wallet C — small / thin (light asks only)",
            "Club": "Club / independent — one-off wallet, not a cluster",
        }
        if wc in hints:
            r["spend_hint"] = hints[wc]

    after = json.dumps(
        {k: r.get(k) for k in ("management_company", "ross_type", "wallet_class", "board_note", "chip_tags", "role_chip")},
        sort_keys=True,
    )
    return before != after


def patch_html(html: str) -> str:
    # CSS for territory strip + cluster chips
    css_inject = """
.territory-help{margin:0 0 12px;padding:12px 14px;border:1px solid #67e8f966;border-radius:14px;background:#0c1f2a;font-size:.78rem;color:#c5d0e6}
.territory-help h4{margin:0 0 8px;font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;color:#67e8f9}
.territory-help ul{margin:0;padding:0 0 0 1.1em}
.territory-help li{margin:0 0 5px}
.territory-help .src{font-size:.68rem;color:#93a0b8;margin-top:8px}
.chip.mgmt{border-color:#67e8f988;color:#a5f3fc;font-weight:700}
.chip.ross{border-color:#fbbf2488;color:#fde68a;font-weight:700}
.chip.ross-gap{border-color:#fb923c88;color:#fdba74}
.chip.site-booker{border-color:#86efac88;color:#bbf7d0}
.board-note{font-size:.74rem;color:#a5f3fc;grid-column:1/-1;padding:6px 8px;border-radius:8px;background:#0c1f2a88;border:1px solid #67e8f944;margin-top:2px}
.board-note b{color:#e8eefc}
.filters button.cluster-btn.on{border-color:#67e8f988;background:#0c1f2a;color:#a5f3fc}
"""
    if ".territory-help{" not in html:
        html = html.replace(
            ".premium-map b{color:#e8eefc}",
            ".premium-map b{color:#e8eefc}\n" + css_inject,
        )

    # Insert territory help container after banner (before dedupe)
    if 'id="territory-help"' not in html:
        html = html.replace(
            '<div class="banner" id="dedupe"',
            '<div class="territory-help" id="territory-help" hidden></div>\n<div class="banner" id="dedupe"',
        )

    # Hard-refresh version crumbs
    html = html.replace("?v=295", "?v=296")
    html = html.replace("Board v2.9.5 · Sep 25 · screened FORM seats", "Board v2.9.6 · Sep 25 · PM territory / Ross clusters")
    # Banner blurb — prepend v2.9.6 note
    if "v2.9.6:" not in html:
        html = html.replace(
            "Board v2.9.5: <b>FORM</b>",
            "Board v2.9.6: <b>PM territory</b> strip + management/Ross chips · v2.9.5: <b>FORM</b>",
        )

    # Update dedupe KPI line version string in JS
    html = html.replace("'<b>v2.9.5</b> · FORM '", "'<b>v2.9.6</b> · PM clusters · FORM '")

    # Render territory help after data load
    if "renderTerritoryHelp" not in html:
        inject_fn = """
  function renderTerritoryHelp(d){
    const el=document.getElementById('territory-help');
    if(!el) return;
    const th=d.territory_help;
    if(!th || !(th.bullets||[]).length){ el.hidden=true; return; }
    let h='<h4>'+esc(th.title||'PM territory')+'</h4><ul>';
    (th.bullets||[]).forEach(b=>{ h+='<li>'+esc(b)+'</li>'; });
    h+='</ul>';
    if(th.source) h+='<div class="src">Source: '+esc(th.source)+'</div>';
    el.innerHTML=h; el.hidden=false;
  }
"""
        html = html.replace(
            "  let data=null, done=loadDone()",
            inject_fn + "  let data=null, done=loadDone()",
        )
        html = html.replace(
            "    if(ver)ver.textContent=d.board_version||'Board v2';",
            "    if(ver)ver.textContent=d.board_version||'Board v2';\n    renderTerritoryHelp(d);",
        )

    # Card chips + board_note in render loop
    if "r.management_company" not in html:
        chip_block = """      if(r.management_company) html+=`<span class="chip mgmt" title="Management / cluster">${esc(r.management_company)}</span> `;
      if(r.ross_type){
        const rt=String(r.ross_type);
        const cls=/gap/i.test(rt)?'ross-gap':(/site booker|club wallet|own tree|ops/i.test(rt)?'site-booker':'ross');
        html+=`<span class="chip ${cls}" title="Ross-type vs site booker">${esc(rt)}</span> `;
      }
      if(r.wallet_class) html+=`<span class="chip" title="Wallet class">W-${esc(r.wallet_class)}</span> `;
"""
        html = html.replace(
            "      if(r.role_chip) html+=`<span class=\"chip role\">${esc(r.role_chip)}</span> `;",
            chip_block + "      if(r.role_chip) html+=`<span class=\"chip role\">${esc(r.role_chip)}</span> `;",
        )

    if "r.board_note" not in html:
        html = html.replace(
            "      if(r.spend_hint){\n        html+=`<div class=\"spend\"><b>Wallet:</b> ${esc(r.spend_hint)}</div>`;\n      }",
            "      if(r.board_note){\n        html+=`<div class=\"board-note\"><b>Cluster:</b> ${esc(r.board_note)}</div>`;\n      }\n"
            "      if(r.spend_hint){\n        html+=`<div class=\"spend\"><b>Wallet:</b> ${esc(r.spend_hint)}</div>`;\n      }",
        )

    # Include cluster fields in filter blob
    if "r.management_company" not in html.split("const blob=")[1][:400] if "const blob=" in html else True:
        html = html.replace(
            "r.lead_source,r.lead_source_detail,r.premium?'premium':'',noteTxt]",
            "r.lead_source,r.lead_source_detail,r.management_company,r.ross_type,r.wallet_class,r.board_note,r.premium?'premium':'',noteTxt]",
        )

    # Search placeholder
    html = html.replace(
        'placeholder="Filter email / city / area / note…"',
        'placeholder="Filter email / city / Vesta / GMS / Ross / note…"',
    )

    # Footer hard-refresh
    html = re.sub(
        r"Hard-refresh \(\?v=\d+\)",
        "Hard-refresh (?v=296)",
        html,
    )

    return html


def email_on_board(board: dict, email: str) -> bool:
    e = email.lower()
    for s in board.get("sections") or []:
        for r in s.get("rows") or []:
            if (r.get("email") or "").lower() == e:
                return True
    return False


def main() -> None:
    board = json.loads(BOARD_PATH.read_text())
    annotated = 0
    by_mgmt: dict[str, int] = {}
    touched_ids: list[str] = []

    for s in board.get("sections") or []:
        for r in s.get("rows") or []:
            if annotate_row(r):
                annotated += 1
                touched_ids.append(r.get("id") or r.get("email") or "")
            mg = r.get("management_company")
            if mg:
                by_mgmt[mg] = by_mgmt.get(mg, 0) + 1

    # Add published missing seats
    added = []
    sec_by_id = {s.get("id"): s for s in board.get("sections") or []}
    for seat in NEW_SEATS:
        em = seat["email"]
        if email_on_board(board, em):
            continue
        row = {k: v for k, v in seat.items() if k != "sections"}
        for sid in seat["sections"]:
            sec = sec_by_id.get(sid)
            if not sec:
                continue
            # avoid dup id in same section
            if any(x.get("id") == row["id"] for x in (sec.get("rows") or [])):
                continue
            sec.setdefault("rows", []).insert(0, dict(row))
        added.append({"id": row["id"], "email": em, "account": row["account"]})
        annotated += 1
        mg = row.get("management_company")
        if mg:
            by_mgmt[mg] = by_mgmt.get(mg, 0) + 1

    board["as_of"] = AS_OF
    board["board_version"] = VERSION
    board["territory_help"] = TERRITORY_HELP
    board["compose_note"] = (
        (board.get("compose_note") or "")
        + " | v2.9.6: PM territory help strip + management_company/ross_type/board_note chips "
        "(Vesta≠all Ross; FCCMS=second Vesta; MAY Ross-gap; GMS phones; FSR/Nocatee/Wildlight own trees). "
        "No invented emails."
    ).strip(" |")

    # recount
    counts = board.setdefault("counts", {})
    mailto_n = sum(1 for s in board["sections"] for r in s.get("rows") or [] if r.get("email"))
    form_only = sum(
        1 for s in board["sections"] for r in s.get("rows") or [] if r.get("form_url") and not r.get("email")
    )
    counts["mailto_total"] = mailto_n
    counts["form_only_rows"] = form_only
    counts["territory_annotated"] = annotated
    counts["by_management_company"] = by_mgmt

    # premium / cdd row counts may have grown
    for sid in ("premium", "cdd"):
        sec = sec_by_id.get(sid)
        if sec:
            key = "premium" if sid == "premium" else "cdd_hoa"
            counts[key] = len(sec.get("rows") or [])

    board["v296"] = {
        "as_of": AS_OF,
        "change": "PM territory / Ross-type cluster notes + chips; published Winslow/Tony/MAY seats if missing",
        "annotated_rows": annotated,
        "added_seats": added,
        "by_management_company": by_mgmt,
        "source": "assets/PM_TERRITORY_MAP_2026-09-25.md",
        "no_fake_emails": True,
        "mindy_note": (
            "Mindy DeAngelis covered in territory help strip (HQ L&L/pizza door). "
            "Map lists mdeangelis@vestapropertyservices.com · 904-747-0181 x625 — "
            "no new dunk mailto added (account-vesta caution: verify before compose)."
        ),
    }

    BOARD_PATH.write_text(json.dumps(board, indent=2) + "\n")

    html = HTML_PATH.read_text()
    HTML_PATH.write_text(patch_html(html))

    summary = {
        "board_version": VERSION,
        "as_of": AS_OF,
        "annotated_rows": annotated,
        "added_seats": added,
        "by_management_company": by_mgmt,
        "mailto_total": mailto_n,
        "touched_sample": [t for t in touched_ids if t][:40],
        "ui": [
            "territory-help strip (6 bullets)",
            "management_company chips (Vesta / First Coast CMS / MAY / GMS / FSR / Nocatee / Wildlight / Independent)",
            "ross_type chips (Ross-type / Site booker / CAM / Ops phone / Own tree / Ross-gap / …)",
            "board_note Cluster line on annotated cards",
            "wallet_class W-A/B/C chips + spend_hint one-liner",
        ],
        "live_urls": [
            "https://onchainoffgrid-hub.github.io/sheehan-exec-suite/principal-dunk.html?v=296",
            "https://onchainoffgrid-hub.github.io/critters-on-call/exec/principal-dunk.html?v=296",
        ],
        "mindy": board["v296"]["mindy_note"],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"ok": True, "annotated": annotated, "added": added, "by_mgmt": by_mgmt, "as_of": AS_OF}, indent=2))


if __name__ == "__main__":
    main()
