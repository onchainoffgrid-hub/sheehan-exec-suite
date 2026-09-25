#!/usr/bin/env python3
"""Expand principal dunk board to v2.8 — RCSA + Fancy + Consumer. Published emails only."""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

ROOT = Path("/workspace/sheehan-exec-suite")
DATA = ROOT / "data"
BOARD_PATH = DATA / "principal_dunk_board.json"
AS_OF = "2026-09-25 4:15 PM ET"
BOARD_VER = "Board v2.8 · Sep 25 4:15 ET"


def slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:80] or "row"


def first_name(contact: str) -> str:
    c = (contact or "").strip()
    if not c:
        return ""
    skip = re.compile(r"^(dr\.?|mr\.?|mrs\.?|ms\.?|miss)$", re.I)
    for p in c.split():
        if not skip.match(p.replace(".", "")):
            return p.rstrip(",")
    return c.split()[0]


def load_board():
    with BOARD_PATH.open() as f:
        return json.load(f)


def all_emails(board) -> set[str]:
    out = set()
    for s in board["sections"]:
        for r in s.get("rows") or []:
            e = (r.get("email") or "").strip().lower()
            if e:
                out.add(e)
    return out


def section_by_id(board, sid: str):
    for s in board["sections"]:
        if s.get("id") == sid:
            return s
    return None


def ensure_section(board, sid, title, hint, after_id=None):
    s = section_by_id(board, sid)
    if s:
        s["title"] = title
        s["hint"] = hint
        return s
    new = {"id": sid, "title": title, "hint": hint, "rows": []}
    if after_id:
        ids = [x.get("id") for x in board["sections"]]
        if after_id in ids:
            i = ids.index(after_id) + 1
            board["sections"].insert(i, new)
            return new
    board["sections"].append(new)
    return new


def row_base(**kw):
    r = {
        "phone": kw.get("phone") or "",
        "city": kw.get("city") or "Jacksonville",
        "segment": kw.get("segment") or "School",
        "persona": kw.get("persona") or "school",
        "kind": kw.get("kind") or "mailto",
        "lane": kw.get("lane") or "",
        "tier": kw.get("tier") or "A",
        "id": kw["id"],
        "account": kw["account"],
        "contact": kw.get("contact") or "",
        "title": kw.get("title") or "",
        "email": kw.get("email") or "",
        "website": kw.get("website") or "",
        "subject": kw.get("subject") or "",
        "why": kw.get("why") or "",
        "owe_reason": kw.get("owe_reason") or "",
        "form_url": kw.get("form_url") or "",
        "area": kw.get("area") or "Metro Jax",
        "role_chip": kw.get("role_chip") or "",
        "fancy": bool(kw.get("fancy")),
        "rcsa": bool(kw.get("rcsa")),
        "chip_tags": kw.get("chip_tags") or [],
    }
    for k in (
        "quick_body",
        "quick_email",
        "legacy_tier",
        "premium",
        "spend_hint",
        "bucket",
        "review_status",
        "review_match_confidence",
        "purchase_status",
        "consumer_lane",
        "linkedin",
    ):
        if k in kw and kw[k] is not None:
            r[k] = kw[k]
    return r


# --------------- RCSA ---------------
RCSA_ROWS = [
    dict(
        id="rcsa-lauren-burnette",
        account="RCSA · Lauren Burnette (Owe/Slam)",
        contact="Lauren Burnette",
        title="Activities / campus booker",
        email="lburnette@rivercityscience.org",
        area="Metro Jax · Southside",
        tier="S",
        lane="owe",
        role_chip="Activities",
        rcsa=True,
        why="WAITING_YES on Oct 2 meet — push date / soft assume-the-sale. Invoice open.",
        owe_reason="Pipeline soft_yes · Oct 2 PZ / activities · invoice open",
        subject="Oct 2 petting zoo — lock details?",
        website="https://www.rivercityscience.org/",
    ),
    dict(
        id="rcsa-madelynne-beck",
        account="RCSA Intracoastal · Madelynne Beck",
        contact="Madelynne Beck",
        title="Teacher · field trip / mini zoo",
        email="mbeck@rivercityscience.org",
        area="Metro Jax · Intracoastal / San Pablo",
        city="Jacksonville",
        tier="A",
        role_chip="Teacher",
        rcsa=True,
        why="Warm Intracoastal teacher — field trip / mini zoo booked path; soft next / thank-you + open dates.",
        phone="904-489-4037",
        website="https://www.rivercityscience.org/",
    ),
    dict(
        id="rcsa-camp-elementary",
        account="RCSA Elementary (K–5)",
        contact="",
        title="Campus inbox",
        email="elementary-info@rivercityscience.org",
        area="Metro Jax · Southside",
        tier="A",
        role_chip="Campus",
        rcsa=True,
        why="Public campus inbox · 7450 Beach Blvd · slam fall festival / grandparents / STEM family night.",
        website="https://www.rivercityscience.org/",
    ),
    dict(
        id="rcsa-camp-middlehigh",
        account="RCSA Middle-High (6–12)",
        contact="",
        title="Campus inbox",
        email="middlehigh-info@rivercityscience.org",
        area="Metro Jax · Southside",
        tier="A",
        role_chip="Campus",
        rcsa=True,
        why="Public campus inbox · 7565 Beach Blvd · slam campus / family STEM events.",
        website="https://www.rivercityscience.org/",
    ),
    dict(
        id="rcsa-camp-innovation",
        account="RCSA Innovation (K–8)",
        contact="",
        title="Campus inbox",
        email="innovation-info@rivercityscience.org",
        area="Metro Jax · Baymeadows",
        tier="A",
        role_chip="Campus",
        rcsa=True,
        why="Public campus inbox · 8160 Baymeadows Way W · STEM expo campus historically.",
        website="https://www.rivercityscience.org/",
        note_gap="Prior bounce on file (Aug 2024) — website still publishes; retry or use info@.",
    ),
    dict(
        id="rcsa-camp-mandarin",
        account="RCSA Mandarin (K–8)",
        contact="",
        title="Campus inbox",
        email="mandarin@rivercityscience.org",
        area="Metro Jax · Mandarin",
        tier="A",
        role_chip="Campus",
        rcsa=True,
        why="Public campus inbox · 10911 Old St. Augustine Rd.",
        website="https://www.rivercityscience.org/",
    ),
    dict(
        id="rcsa-camp-intracoastal",
        account="RCSA Intracoastal (K–8)",
        contact="",
        title="Campus inbox",
        email="intracoastal@rivercityscience.org",
        area="Metro Jax · Intracoastal / San Pablo",
        tier="A",
        role_chip="Campus",
        rcsa=True,
        why="Public campus inbox · 2002 San Pablo Rd S · Madelynne Beck teacher warm on same campus.",
        website="https://www.rivercityscience.org/",
    ),
    dict(
        id="rcsa-camp-southeast",
        account="RCSA Southeast (K–8)",
        contact="",
        title="Campus inbox",
        email="southeast-info@rivercityscience.org",
        area="Metro Jax · Southside / Philips",
        tier="A",
        role_chip="Campus",
        rcsa=True,
        why="Public campus inbox · 12397 Philips Hwy.",
        website="https://www.rivercityscience.org/",
    ),
    dict(
        id="rcsa-org-info",
        account="RCSA · Network info",
        contact="",
        title="Org inbox",
        email="info@rivercityscience.org",
        area="Metro Jax · Southside",
        tier="B",
        role_chip="Campus",
        rcsa=True,
        why="Published network inbox — route after campus slam if needed.",
        website="https://www.rivercityscience.org/",
    ),
    dict(
        id="rcsa-dogan-tozoglu",
        account="RCSA · Executive Director",
        contact="Dr. Dogan Tozoglu",
        title="Executive Director",
        email="dtozoglu@rivercityscience.org",
        area="Metro Jax · Network",
        tier="S",
        role_chip="Director",
        rcsa=True,
        why="Published on governing board — network ED for STEM Expo / multi-campus family events.",
        website="https://www.rivercityscience.org/governing-board-rcsa",
    ),
    dict(
        id="rcsa-alisher-kuvatov",
        account="RCSA · Director of Academics",
        contact="Alisher Kuvatov",
        title="Director of Academics",
        email="akuvatov@rivercityscience.org",
        area="Metro Jax · Network",
        tier="A",
        role_chip="Curriculum",
        rcsa=True,
        why="Published email (RCSA Wellness Policy PDF on rivercityscience.org) · curriculum / academics seat.",
        website="https://www.rivercityscience.org/",
    ),
    dict(
        id="rcsa-sel-buyuksarac",
        account="RCSA Mandarin · Parent Rep",
        contact="Mr. Buyuksarac",
        title="School Board Parent Representative · Mandarin",
        email="sel@rivercityscience.org",
        area="Metro Jax · Mandarin",
        tier="A",
        role_chip="Activities",
        rcsa=True,
        why="Published parent rep (governing board) · prior STEM Expo reply thread on Gmail.",
        website="https://www.rivercityscience.org/governing-board-rcsa",
    ),
    dict(
        id="rcsa-lpalarine-stem",
        account="RCSA · STEM & Health Expo desk",
        contact="",
        title="STEM Expo / Innovation events",
        email="lpalarine@rivercityscience.org",
        area="Metro Jax · Baymeadows",
        tier="A",
        role_chip="Activities",
        rcsa=True,
        why="Real inbox — sent FL STEM & Health Expo invite (Gmail). Activities / expo seat.",
        website="https://www.rivercityscience.org/",
    ),
]


def build_rcsa(board, seen: set[str]):
    sec = ensure_section(
        board,
        "rcsa",
        "RCSA · River City Science Academy",
        "All 6 campuses + ED / academics / known seats. School voice. Lauren stays Owe/Slam S. Published emails only.",
        after_id="owe",
    )
    # Keep Lauren in owe too — update why; do not duplicate email in rcsa if already in owe? User wants RCSA section to slam all + keep Lauren as Owe. So Lauren can appear in BOTH sections (owe + rcsa) with same email — Done key is by id so different ids OK.
    rows = []
    for spec in RCSA_ROWS:
        r = row_base(**spec)
        r["lane"] = "rcsa"
        if spec.get("id") == "rcsa-lauren-burnette":
            r["lane"] = "owe"  # still owe for filter
        rows.append(r)
        if r["email"]:
            seen.add(r["email"].lower())
    sec["rows"] = rows

    # Strengthen owe Lauren why + ensure Madelynne not forcing owe unless wanted
    owe = section_by_id(board, "owe")
    if owe:
        found = False
        for r in owe["rows"]:
            if (r.get("email") or "").lower() == "lburnette@rivercityscience.org":
                r["why"] = "WAITING_YES on Oct 2 meet — push date / soft assume-the-sale. Invoice open."
                r["owe_reason"] = "Pipeline soft_yes · Oct 2 PZ / activities · invoice open"
                r["contact"] = r.get("contact") or "Lauren Burnette"
                r["title"] = r.get("title") or "Activities"
                r["role_chip"] = "Activities"
                r["rcsa"] = True
                r["tier"] = "S"
                r["area"] = "Metro Jax · Southside"
                found = True
        if not found:
            # shouldn't happen
            pass
        # Add Madelynne to owe? User said warm teacher — keep in RCSA only, not owe unless slam. Skip owe.


# --------------- Fancy / principals ---------------
FANCY_PRINCIPALS = [
    # Catholic principals (published DOSA directory) — expand beyond 3
    ("ayumul@bishopsnyder.org", "Arsenio Yumul", "Principal", "Bishop John J. Snyder High School", "Metro Jax · Westside", "Principal", True),
    ("torlando@bishopkenny.org", "Todd Orlando", "Principal", "Bishop Kenny High School", "Metro Jax · Southside", "Principal", True),
    ("deannasands@ctkschooljax.com", "Deanna Sands", "Principal", "Christ the King Catholic School", "Metro Jax · Arlington", "Principal", True),
    ("mjimenez@assumptionjax.org", "Maryann Jimenez", "Principal", "Assumption Catholic School", "Metro Jax · Riverside", "Principal", True),
    ("principal@annunciationcatholic.org", "Stephen Eiswert", "Principal", "Annunciation Interparish School", "Clay · Middleburg", "Principal", False),
    ("dartt@blessedtrinitycatholicschool.org", "Robin Dartt", "Principal & Preschool Director", "Blessed Trinity Catholic School", "Metro Jax · Beach Blvd", "Principal", False),
    ("jlord@guardiancatholic.com", "Jenn Lord", "Principal", "Guardian Catholic School", "Metro Jax · Northside", "Principal", False),
    ("fvacirca@guardiancatholic.com", "Frank Vacirca", "Head of School", "Guardian Catholic School", "Metro Jax · Northside", "Principal", False),
    ("mkavanagh@hfcatholicschool.com", "Michael Kavanagh", "Principal", "Holy Family Catholic School", "Metro Jax · Baymeadows", "Principal", True),
    ("csult@hscatholicschool.com", "Chelsea Sult", "Principal", "Holy Spirit Catholic School", "Metro Jax · Fort Caroline", "Principal", False),
    ("principal@morningstar-jax.org", "Elaine Shott", "Principal", "Morning Star High School", "Metro Jax · Arlington", "Principal", False),
    ("arainey@resurrectioncatholic.com", "Amanda Rainey", "Principal", "Resurrection Catholic School", "Metro Jax · Arlington", "Principal", False),
    ("mkennedy@sacredheartjax.com", "Melissa Kennedy", "Principal", "Sacred Heart Catholic School", "Metro Jax · Westside", "Principal", False),
    ("swain@sanjoseschool.com", "Jennifer Swain", "Principal", "San Jose Catholic School", "Metro Jax · San Jose", "Principal", True),
    ("bpeters@stjosephcs.org", "Brandi Peters", "Principal", "St. Joseph Catholic School", "Metro Jax · Mandarin", "Principal", True),
    ("mdubberly@stmatthewscs.com", "Meagan Dubberly", "Principal", "St. Matthew Catholic School", "Metro Jax · Westside", "Principal", False),
    ("cmeyer@spcsjax.org", "Chris Meyer", "Principal", "St. Patrick Catholic School", "Metro Jax · Northside", "Principal", False),
    ("kim.repper@spsjax.org", "Kim Repper", "Principal", "St. Paul Catholic School", "Metro Jax · Riverside", "Principal", False),
    ("kthompson@stpaulsbeach.com", "Krissy Thompson", "Principal", "St. Paul Catholic School (Jax Beach)", "Metro Jax · Beaches", "Principal", True),
    ("wsummer@smacad.org", "William Summer", "Principal", "St. Michael Academy", "Nassau · Fernandina", "Principal", False),
    ("bott@cpsschool.org", "Bryan Ott", "Principal", "Cathedral Parish School", "St. Johns · St. Augustine", "Principal", False),
    ("ddossantos@pcapvb.org", "Daniela DosSantos", "Principal", "Palmer Catholic Academy", "St. Johns · Ponte Vedra", "Principal", True),
    ("todd.declemente@sjaweb.org", "Todd DeClemente", "Principal", "St. Joseph Academy", "St. Johns · St. Augustine", "Principal", False),
    ("trhodes@sjdrschool.org", "Tabatha Rhodes", "Principal", "San Juan del Rio Catholic School", "St. Johns · Julington", "Principal", True),
    # Fancy independent — published emails only
    ("cjohnson@jcds.com", "Christopher Johnson", "Head of School", "Jacksonville Country Day School", "Metro Jax · Baymeadows", "Principal", True),
    ("jmurray@sjcds.net", "John Murray", "Head of School", "St. Johns Country Day School", "Clay · Orange Park", "Principal", True),
    ("owirth@sjcds.net", "Otis Wirth", "Head of Lower School", "St. Johns Country Day School", "Clay · Orange Park", "Principal", True),
    ("greenea@esj.org", "Adam Greene", "Head of School", "Episcopal School of Jacksonville", "Metro Jax · Atlantic Blvd", "Principal", True),
    ("KetchumJ@esj.org", "Jennifer Ketchum", "Head of Lower School, Beaches Campus", "ESJ Beaches Campus", "Metro Jax · Jax Beach", "Principal", True),
    ("AndersonB@esj.org", "Beville Anderson", "Head of Lower School, St. Mark's Campus", "ESJ St. Mark's Campus", "Metro Jax · Westside", "Principal", True),
    ("abast@geds.net", "Angela Bast", "Head of School", "Grace Episcopal Day School", "Clay · Orange Park", "Principal", True),
    ("info@prov.org", "Tim Anderson", "Head of School", "Providence School of Jacksonville", "Metro Jax · Southside", "Principal", True),
]

FANCY_DIRECTORS = [
    ("telstein@jcds.com", "Tonya Elstein", "Director of Education", "Jacksonville Country Day School", "Metro Jax · Baymeadows", "Curriculum", True),
    ("nrenstrom@jcds.com", "Nathan Renstrom", "Director of Auxiliary Services", "Jacksonville Country Day School", "Metro Jax · Baymeadows", "Activities", True),
    ("office@jcds.com", "", "Main office", "Jacksonville Country Day School", "Metro Jax · Baymeadows", "Campus", True),
    ("hgraham@sjcds.net", "Heather Graham", "Director of Auxiliary Services", "St. Johns Country Day School", "Clay · Orange Park", "Activities", True),
    ("rtrevett@sjcds.net", "Ryan Trevett", "Assistant Head of Lower School / ECE / Campus Rentals", "St. Johns Country Day School", "Clay · Orange Park", "Activities", True),
    ("jjacobs@sjcds.net", "Jeni Jacobs", "Director of Parent Relations", "St. Johns Country Day School", "Clay · Orange Park", "Activities", True),
    ("hodgesc@esj.org", "C. Hodges", "Dean of Student Life", "Episcopal School of Jacksonville", "Metro Jax · Atlantic Blvd", "Activities", True),
    ("goebertusk@esj.org", "", "Associate Head of School", "Episcopal School of Jacksonville", "Metro Jax · Atlantic Blvd", "Director", True),
    ("herfordn@esj.org", "", "Head of Upper School", "Episcopal School of Jacksonville", "Metro Jax · Atlantic Blvd", "Principal", True),
    ("mcgeep@esj.org", "", "Head of Middle School", "Episcopal School of Jacksonville", "Metro Jax · Atlantic Blvd", "Principal", True),
    ("gneitzke@geds.net", "Ginger Neitzke", "Campus contact (prior CC)", "Grace Episcopal Day School", "Clay · Orange Park", "Activities", True),
    ("petra@thediscoveryschool.org", "Petra Obritzberger", "School contact", "The Discovery School", "Metro Jax", "Director", True),
    ("alexis.bailey@ivybrookacademy.com", "Alexis Bailey", "Campus Contact", "Ivybrook Academy Julington Creek", "St. Johns · Julington", "Director", True),
    ("jennifer.ripkey@ivybrookacademy.com", "Jennifer Ripkey", "Campus Director", "Ivybrook Academy Valley Ridge", "St. Johns · Ponte Vedra", "Director", True),
]

# Bolles / Amelia — form/phone only (no invented email)
FANCY_FORMS = [
    dict(
        id="fancy-bolles-christy-lusk",
        account="Bolles Whitehurst Lower School",
        contact="Christy Lusk",
        title="Head of Lower School · Whitehurst",
        email="",
        phone="904-256-5256",
        area="Metro Jax · San Jose",
        tier="S",
        role_chip="Principal",
        fancy=True,
        kind="form",
        form_url="https://www.bolles.org/about-us/whom-to-call",
        website="https://www.bolles.org/",
        why="Fancy Bull School · phone published; email unpublished — use Whom to Call / office path. No invented email.",
        lane="local_forms",
    ),
    dict(
        id="fancy-bolles-suzanne-carlino",
        account="Bolles Ponte Vedra Beach Lower School",
        contact="Suzanne Carlino",
        title="Head of Lower School · PVB",
        email="",
        phone="904-732-5901",
        area="St. Johns · Ponte Vedra",
        tier="S",
        role_chip="Principal",
        fancy=True,
        kind="form",
        form_url="https://www.bolles.org/about-us/whom-to-call",
        website="https://www.bolles.org/",
        why="Fancy Bull School PVB · phone published; email unpublished — Whom to Call only.",
        lane="local_forms",
    ),
    dict(
        id="fancy-bolles-drew-upchurch",
        account="Bolles · Auxiliary / Campus Services",
        contact="Drew Upchurch",
        title="Director of Auxiliary Programs and Campus Services",
        email="",
        phone="904-256-5071",
        area="Metro Jax · San Jose",
        tier="A",
        role_chip="Activities",
        fancy=True,
        kind="form",
        form_url="https://www.bolles.org/about-us/whom-to-call",
        website="https://www.bolles.org/",
        why="Auxiliary/campus services routes family-event bookings · phone published, no personal email.",
        lane="local_forms",
    ),
    dict(
        id="fancy-amelia-montessori-lindsay",
        account="Amelia Island Montessori",
        contact="Lindsay DiBernardo",
        title="Head of School",
        email="",
        phone="904-261-6610",
        area="Nassau · Fernandina",
        tier="A",
        role_chip="Principal",
        fancy=True,
        kind="form",
        form_url="https://www.ameliaislandmontessori.com/faculty-staff",
        website="https://www.ameliaislandmontessori.com/",
        why="Named Head of School · phone published; no personal email on faculty page — do not invent.",
        lane="local_forms",
    ),
]


def build_fancy(board, seen: set[str]):
    principals = section_by_id(board, "principals")
    directors = section_by_id(board, "directors")
    local_forms = section_by_id(board, "local_forms")
    other = section_by_id(board, "other")

    # Rebuild principals list from FANCY_PRINCIPALS (dedupe by email)
    p_rows = []
    p_seen = set()
    for email, contact, title, account, area, role_chip, fancy in FANCY_PRINCIPALS:
        el = email.lower()
        if el in p_seen:
            continue
        p_seen.add(el)
        r = row_base(
            id=f"prin-{slug(email)}",
            account=account,
            contact=contact,
            title=title,
            email=email,
            area=area,
            tier="S" if fancy else "A",
            role_chip=role_chip,
            fancy=fancy,
            persona="school",
            lane="principals",
            why="Published principal / head seat — school voice. Fancy chip when independent/prep-class.",
            website="",
            chip_tags=["Fancy"] if fancy else [],
        )
        p_rows.append(r)
        seen.add(el)
    principals["rows"] = p_rows
    principals["title"] = "Principals / Heads of School"
    principals["hint"] = "Catholic + fancy independent heads with published emails. Role chip on card. Fancy filter works across board."

    # Add fancy directors — prepend new ones if email not already in directors
    dir_emails = {(r.get("email") or "").lower() for r in directors["rows"]}
    added = 0
    for email, contact, title, account, area, role_chip, fancy in FANCY_DIRECTORS:
        el = email.lower()
        if el in dir_emails:
            # tag existing
            for r in directors["rows"]:
                if (r.get("email") or "").lower() == el:
                    r["fancy"] = True
                    r["role_chip"] = r.get("role_chip") or role_chip
                    r["chip_tags"] = list(set((r.get("chip_tags") or []) + ["Fancy"]))
                    if contact and not r.get("contact"):
                        r["contact"] = contact
            continue
        if el in seen and el not in {x.lower() for x in [e[0] for e in FANCY_DIRECTORS]}:
            # already elsewhere — still add to directors for Fancy filter visibility? Prefer not duplicate mailto.
            # Move SJCDS rtrevett from other into directors if present
            pass
        r = row_base(
            id=f"dir-{slug(email)}",
            account=account,
            contact=contact,
            title=title,
            email=email,
            area=area,
            tier="A",
            role_chip=role_chip,
            fancy=True,
            persona="school",
            lane="directors",
            why="Published director / curriculum / activities / student-life seat — fancy school class.",
            chip_tags=["Fancy"],
        )
        directors["rows"].insert(0, r)
        dir_emails.add(el)
        seen.add(el)
        added += 1

    # Remove from other if now in directors/principals
    if other:
        keep = []
        for r in other["rows"]:
            el = (r.get("email") or "").lower()
            if el in dir_emails or el in p_seen:
                continue
            keep.append(r)
        other["rows"] = keep

    # Forms for Bolles / Montessori
    form_ids = {r.get("id") for r in local_forms["rows"]}
    for spec in FANCY_FORMS:
        if spec["id"] in form_ids:
            continue
        local_forms["rows"].insert(0, row_base(**spec))


# --------------- Consumer ---------------
def normalize_name(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def fuzzy_review_match(name: str, email: str, reviewers: list[str]):
    """Return (status, confidence). With empty reviewers -> unknown."""
    if not reviewers:
        return "unknown", "none"
    nn = normalize_name(name)
    local = (email or "").split("@")[0].lower()
    local = re.sub(r"[0-9._\-]+", " ", local)
    local = re.sub(r"\s+", " ", local).strip()
    parts = nn.split()
    best = ("no_review_seen", "none")
    for rev in reviewers:
        rn = normalize_name(rev)
        if not rn:
            continue
        if nn and nn == rn:
            return "likely_reviewed", "high"
        if len(parts) >= 2 and parts[0] in rn and parts[-1] in rn:
            return "likely_reviewed", "high"
        if len(parts) >= 2 and parts[-1] and parts[-1] == rn.split()[-1] and parts[0][:1] == (rn.split()[0][:1] if rn.split() else ""):
            best = ("likely_reviewed", "medium")
        if local and local in rn.replace(" ", ""):
            if best[1] == "none":
                best = ("likely_reviewed", "low")
    return best if best[0] != "no_review_seen" or best[1] != "none" else ("no_review_seen", "none")


def build_consumer(board, seen: set[str]):
    with (DATA / "google_reviewers.json").open() as f:
        grev = json.load(f)
    reviewers = [r.get("name") if isinstance(r, dict) else r for r in (grev.get("reviewers") or [])]
    scrape_ok = grev.get("status") == "ok" and bool(reviewers)

    with (DATA / "customers_no_next_date.json").open() as f:
        cn = json.load(f)
    with (DATA / "consumer_inbound.json").open() as f:
        ci = json.load(f)
    with (DATA / "paypal_customers.json").open() as f:
        pp = json.load(f)
    paypal_names = {normalize_name(p.get("Customer") or "") for p in pp}

    # Customers: prefer customers_no_next_date with real email + bought from inbound
    customers = {}
    for r in cn.get("rows") or []:
        email = (r.get("email") or "").strip()
        if not email or "@" not in email:
            continue
        el = email.lower()
        # skip org/B2B-ish school domains for consumer lane? User said customers — include all with email that look personal OR keep all from customers_no_next_date
        customers[el] = {
            "email": email,
            "name": r.get("account") or r.get("brand") or "",
            "phone": r.get("phone") or "",
            "source": "customers_no_next_date",
            "last_paid": r.get("last_paid"),
            "purchase_status": "bought",
        }
    for c in ci.get("contacts") or []:
        if c.get("purchase_status") != "bought":
            continue
        email = (c.get("email") or "").strip()
        if not email or "@" not in email:
            continue
        el = email.lower()
        if el not in customers:
            customers[el] = {
                "email": email,
                "name": c.get("name") or "",
                "phone": c.get("phone") or "",
                "source": "consumer_inbound:bought",
                "last_paid": c.get("last_paid_or_booked"),
                "purchase_status": "bought",
                "amount": c.get("amount"),
            }
        else:
            if c.get("name") and (not customers[el]["name"] or "@" in customers[el]["name"]):
                customers[el]["name"] = c["name"]
            if c.get("phone") and not customers[el].get("phone"):
                customers[el]["phone"] = c["phone"]
            customers[el]["last_paid"] = customers[el].get("last_paid") or c.get("last_paid_or_booked")

    # Cross-ref paypal by name for hint
    for el, c in customers.items():
        nn = normalize_name(c["name"])
        c["paypal_match"] = nn in paypal_names if nn else False

    # Warm inbound not_seen — cap 60 best (recent + has phone preferred)
    warm = []
    for c in ci.get("contacts") or []:
        if c.get("purchase_status") != "not_seen":
            continue
        email = (c.get("email") or "").strip()
        if not email or "@" not in email:
            continue
        el = email.lower()
        if el in customers:
            continue
        warm.append(c)

    def warm_score(c):
        score = 0
        if c.get("phone"):
            score += 20
        date = str(c.get("date") or "")
        # prefer 2026
        if "2026" in date:
            score += 10
        if c.get("bucket") in ("godaddy", "summer_interest", "critter_club"):
            score += 5
        # recent-ish month
        score += 1
        return score

    warm.sort(key=warm_score, reverse=True)
    warm = warm[:60]

    rows = []
    # Customer rows
    for el, c in sorted(customers.items(), key=lambda x: (x[1].get("last_paid") or ""), reverse=True):
        name = c["name"]
        # Prefer person-looking names
        status, conf = fuzzy_review_match(name, c["email"], reviewers)
        if not scrape_ok:
            status, conf = "unknown", "none"
        # Tier: S if likely_reviewed OR recent buyer; A solid; B old/weak
        tier = "A"
        last = str(c.get("last_paid") or "")
        if status == "likely_reviewed" or (last and last.startswith("2026")):
            tier = "S"
        elif not last:
            tier = "B"
        contact = name if name and "@" not in name else ""
        # If account looks like org, keep as account
        account = name or c["email"].split("@")[0]
        rows.append(
            row_base(
                id=f"cons-cust-{slug(el)}",
                account=account,
                contact=contact if contact != account else first_name(contact) and contact or contact,
                title="Customer",
                email=c["email"],
                phone=c.get("phone") or "",
                area="Metro Jax · Consumer",
                city="",
                segment="Consumer",
                persona="consumer",
                lane="consumer",
                tier=tier,
                role_chip="Customer",
                consumer_lane="customers",
                purchase_status="bought",
                review_status=status,
                review_match_confidence=conf,
                why=f"Customer · review={status} ({conf}) · source={c.get('source')}",
                chip_tags=["Consumer", "Reviewed" if status == "likely_reviewed" else ("Ask review later" if status == "no_review_seen" else "Review unknown")],
            )
        )

    for c in warm:
        email = c["email"].strip()
        el = email.lower()
        name = c.get("name") or ""
        status, conf = ("unknown", "none") if not scrape_ok else fuzzy_review_match(name, email, reviewers)
        if not scrape_ok:
            status, conf = "unknown", "none"
        rows.append(
            row_base(
                id=f"cons-warm-{slug(el)}",
                account=name or email.split("@")[0],
                contact=name,
                title=f"Warm inbound · {c.get('bucket') or 'interest'}",
                email=email,
                phone=c.get("phone") or "",
                area="Metro Jax · Consumer",
                segment="Consumer",
                persona="consumer",
                lane="consumer",
                tier="A" if c.get("phone") else "B",
                role_chip="Warm",
                consumer_lane="warm_inbound",
                purchase_status="not_seen",
                review_status=status,
                review_match_confidence=conf,
                why=f"Warm not-yet-customer · {c.get('bucket')} · {str(c.get('date') or '')[:12]} · review={status}",
                chip_tags=["Consumer", "Warm"],
            )
        )

    sec = ensure_section(
        board,
        "consumer",
        "Consumer · customers + warm inbound",
        "Customers (bought / no-next-date) + capped warm inbound. Review cross-ref when available — Reviewed → APP-FIRST mailto (no review ask). Compose only.",
        after_id="rcsa",
    )
    sec["rows"] = rows
    return {
        "customers": sum(1 for r in rows if r.get("consumer_lane") == "customers"),
        "warm": sum(1 for r in rows if r.get("consumer_lane") == "warm_inbound"),
        "likely_reviewed": sum(1 for r in rows if r.get("review_status") == "likely_reviewed"),
        "no_review": sum(1 for r in rows if r.get("review_status") == "no_review_seen"),
        "unknown": sum(1 for r in rows if r.get("review_status") == "unknown"),
        "scrape_ok": scrape_ok,
    }


def recount(board, consumer_stats):
    counts = board.get("counts") or {}
    by_persona = {}
    mailto = 0
    fancy_n = 0
    rcsa_n = 0
    for s in board["sections"]:
        sid = s.get("id")
        n = len(s.get("rows") or [])
        if sid == "principals":
            counts["principals"] = n
        elif sid == "directors":
            counts["directors"] = n
        elif sid == "pto":
            counts["pto_pta_presidents"] = n
        elif sid == "other":
            counts["other_decision_makers"] = n
        elif sid == "cdd":
            counts["cdd_hoa"] = n
        elif sid == "university":
            counts["university"] = n
        elif sid == "enterprise":
            counts["enterprise"] = n
        elif sid == "owe":
            counts["owe_followup"] = n
        elif sid == "local_forms":
            counts["local_forms_optional"] = n
        elif sid == "rcsa":
            counts["rcsa"] = n
        elif sid == "consumer":
            counts["consumer"] = n
            counts["consumer_customers"] = consumer_stats["customers"]
            counts["consumer_warm"] = consumer_stats["warm"]
            counts["consumer_likely_reviewed"] = consumer_stats["likely_reviewed"]
            counts["consumer_no_review"] = consumer_stats["no_review"]
            counts["consumer_unknown"] = consumer_stats["unknown"]
        for r in s.get("rows") or []:
            if r.get("email"):
                mailto += 1
            p = r.get("persona") or "other"
            by_persona[p] = by_persona.get(p, 0) + 1
            if r.get("fancy"):
                fancy_n += 1
            if r.get("rcsa") or sid == "rcsa":
                rcsa_n += 1
    counts["mailto_total"] = mailto
    counts["by_persona"] = by_persona
    counts["fancy"] = fancy_n
    counts["rcsa_cards"] = rcsa_n
    board["counts"] = counts


def main():
    board = load_board()
    seen = all_emails(board)
    build_rcsa(board, seen)
    build_fancy(board, seen)
    consumer_stats = build_consumer(board, seen)
    recount(board, consumer_stats)

    board["as_of"] = AS_OF
    board["board_version"] = BOARD_VER
    board["label"] = "Principal dunk board v2.8 — RCSA + Fancy + Consumer (review-aware)"
    board["rule"] = (
        "Compose-only mailto. B2B school/CDD = v2.7 Michael voice. "
        "Consumer Reviewed = APP-FIRST (no review ask). "
        "Consumer no_review = soft next-date. Warm = soft animals/visit. "
        f"Google reviewers scrape: {'ok' if consumer_stats['scrape_ok'] else 'FAILED — all consumer review_status=unknown'}. "
        "Done key sheehan_principal_dunk_done_v2 · Notes sheehan_dunk_notes_v1."
    )
    board["v28"] = {
        "rcsa_campuses": 6,
        "rcsa_rows": len(section_by_id(board, "rcsa")["rows"]),
        "fancy_principals": sum(1 for r in section_by_id(board, "principals")["rows"] if r.get("fancy")),
        "principals_total": len(section_by_id(board, "principals")["rows"]),
        "consumer": consumer_stats,
        "google_reviewers_file": "data/google_reviewers.json",
    }

    BOARD_PATH.write_text(json.dumps(board, indent=2, ensure_ascii=False) + "\n")
    summary = {
        "as_of": AS_OF,
        "board_version": BOARD_VER,
        "v28": board["v28"],
        "counts": board["counts"],
    }
    (DATA / "_dunk_v28_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
