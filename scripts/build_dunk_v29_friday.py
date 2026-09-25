#!/usr/bin/env python3
"""Board v2.9 — Friday weekend-programmers + Jax universities + corporate Friday.
Published emails only. Compose-only.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path("/workspace/sheehan-exec-suite")
DATA = ROOT / "data"
BOARD_PATH = DATA / "principal_dunk_board.json"
HTML_PATH = ROOT / "principal-dunk.html"
AS_OF = "2026-09-25 4:15 PM ET"
BOARD_VER = "Board v2.9 · Sep 25 4:15 ET"

LEADS = Path("/workspace/leads")
REVOPS = Path("/workspace/revops")
DEPUTY = Path("/workspace/deputy-outreach")


def slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:80] or "row"


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
        "chip_tags": list(kw.get("chip_tags") or []),
        "friday": bool(kw.get("friday")),
        "friday_class": kw.get("friday_class") or "",
    }
    for k in (
        "quick_body",
        "quick_email",
        "legacy_tier",
        "premium",
        "spend_hint",
        "bucket",
        "review_status",
        "linkedin",
        "note_gap",
    ):
        if k in kw and kw[k] is not None:
            r[k] = kw[k]
    return r


def append_unique(sec, seen: set[str], row: dict) -> bool:
    e = (row.get("email") or "").strip().lower()
    if not e or "@" not in e or " " in e:
        return False
    if e in seen:
        return False
    # also skip if same email already in this section
    for existing in sec.get("rows") or []:
        if (existing.get("email") or "").strip().lower() == e:
            return False
    seen.add(e)
    sec.setdefault("rows", []).append(row)
    return True


# ---------- Friday tagging ----------
AMENITY_RE = re.compile(
    r"amenity|lifestyle|event|program|community manager|community association|"
    r"\bcam\b|lcam|recreation|facility attendant|resident services|resident event|"
    r"community programming|operations manager|field operations",
    re.I,
)
DISTRICT_ONLY_RE = re.compile(r"^district manager$|managing partner and district", re.I)
APT_RE = re.compile(
    r"apartment|multifamily|greystar|\brise\b|air communities|leasing manager|"
    r"lifestyle coordinator|regional property manager|community manager / leasing",
    re.I,
)
CORP_FRI_RE = re.compile(
    r"mcdonald|chick-fil|burger king|royal restaurant|franchise|owner.?operator|"
    r"director of operations|operations supervisor|community affairs|"
    r"hr events|employee family|field operations|district manager|"
    r"multi.?unit|area coach|corporate operating",
    re.I,
)


def classify_friday(r: dict) -> tuple[bool, str]:
    """Return (is_friday, friday_class). University never Friday default."""
    persona = (r.get("persona") or "").lower()
    if persona == "university":
        return False, ""
    title = r.get("title") or ""
    account = r.get("account") or ""
    segment = r.get("segment") or ""
    role = r.get("role_chip") or ""
    blob = f"{title} {role} {account} {segment} {r.get('why') or ''}"
    email = (r.get("email") or "").lower()

    # Explicit corporate Friday inboxes
    if email in ("comments@mcdjax.com",) or "mcdonald" in account.lower():
        if persona in ("enterprise", "other", "consumer", "cdd") or "mcdonald" in blob.lower():
            return True, "corporate"
    if email == "inquiries@royalrg.com" or "royal restaurant" in account.lower():
        return True, "corporate"

    if persona == "church":
        return True, "church"

    if APT_RE.search(blob) or (persona == "enterprise" and APT_RE.search(blob)):
        return True, "apartment"

    if persona == "cdd" or "cdd" in segment.lower() or "hoa" in segment.lower() or r.get("premium"):
        if AMENITY_RE.search(title) or AMENITY_RE.search(role) or AMENITY_RE.search(account):
            return True, "cdd_amenity"
        if DISTRICT_ONLY_RE.search(title.strip()) or re.search(r"district manager|field operations", title, re.I):
            return True, "district"
        if re.search(r"community association|lcam|hoa manager|community manager", title, re.I):
            return True, "cdd_amenity"

    if persona == "enterprise" and CORP_FRI_RE.search(blob):
        return True, "corporate"

    # Consumer secondary Friday (rebook cards)
    if persona == "consumer":
        lane = r.get("history_lane") or r.get("consumer_lane") or ""
        if lane in ("prior_mobile", "booked_no_review", "summer_cohort", "birthday_season"):
            return True, "consumer_rebook"
        # McD consumer card
        if "mcdonald" in account.lower() or email == "comments@mcdjax.com":
            return True, "corporate"

    if r.get("friday_class") == "corporate" or "Corporate Friday" in (r.get("chip_tags") or []):
        return True, "corporate"

    return False, ""


FRIDAY_WHY = {
    "church": "Friday priority — churches program weekends (fall festival / trunk-or-treat / family night).",
    "cdd_amenity": "Friday priority — amenity / lifestyle / community managers program weekends.",
    "district": "Friday priority — district / field ops read Friday afternoon; community & employee-adjacent events.",
    "apartment": "Friday priority — multifamily lifestyle / community managers run resident weekend events.",
    "corporate": "Friday priority — corporate / franchise ops / district class; community or employee family events.",
    "consumer_rebook": "Friday secondary — consumer rebook card (weekend visit / mobile date).",
}


def apply_friday_tags(board) -> Counter:
    counts = Counter()
    for s in board["sections"]:
        for r in s.get("rows") or []:
            ok, cls = classify_friday(r)
            if not ok:
                # clear stale if we re-run? keep only if already set intentionally
                continue
            r["friday"] = True
            r["friday_class"] = cls
            tags = list(r.get("chip_tags") or [])
            if "Friday" not in tags:
                tags.append("Friday")
            if cls == "corporate" and "Corporate Friday" not in tags:
                tags.append("Corporate Friday")
            if cls == "apartment" and "Apartment" not in tags:
                tags.append("Apartment")
            r["chip_tags"] = tags
            why = (r.get("why") or "").strip()
            prefix = FRIDAY_WHY.get(cls, "Friday priority — programs weekends.")
            if "Friday priority" not in why and "Friday secondary" not in why:
                r["why"] = f"{prefix} {why}".strip()
            counts[cls] += 1
            counts["friday_total"] += 1
    return counts


# ---------- University adds (Jax-area) ----------
JU_ROWS = [
    dict(
        email="ktaylor28@ju.edu",
        contact="Kelsey Taylor",
        title="Director, Student Engagement & Leadership",
        phone="904-256-7404",
        why="EXISTING buyer · goat yoga / campus events (~$3k/yr). Primary Student Engagement seat. NOT Friday default.",
        role_chip="Buyer",
        tier="S",
        website="https://www.ju.edu/",
    ),
    dict(
        email="hgrover@ju.edu",
        contact="H. Grover",
        title="Jacksonville University (prior goat yoga)",
        phone="",
        why="EXISTING customer CRM · goat yoga scheduled historically (EM 3.9/3.10 | 4/23). Upsell / soft next campus date. NOT Friday default.",
        role_chip="Prior customer",
        tier="S",
        website="https://www.ju.edu/",
    ),
    dict(
        email="jjames20@ju.edu",
        contact="Jesse James",
        title="Director of Alumni and Family Engagement",
        phone="904-256-7201",
        why="Published alumni staff · Homecoming & Family Weekend programmer. NOT Friday default.",
        role_chip="Alumni / Family",
        tier="A",
        website="https://www.ju.edu/alumni/alumni-staff.php",
    ),
    dict(
        email="alumni@ju.edu",
        contact="",
        title="Office of Alumni & Family Engagement",
        phone="904-256-7201",
        why="Published office inbox · HCFW / family programming. NOT Friday default.",
        role_chip="Inbox",
        tier="A",
        website="https://www.ju.edu/homecoming/",
    ),
    dict(
        email="studentlife@ju.edu",
        contact="",
        title="Office of Student Life",
        phone="904-256-7067",
        why="Published Davis Student Commons inbox. NOT Friday default.",
        role_chip="Inbox",
        tier="A",
        website="https://www.ju.edu/campuslife/index.php",
    ),
    dict(
        email="housing@ju.edu",
        contact="",
        title="Residential Life",
        phone="904-256-7538",
        why="Published Res Life inbox · hall / welcome programming. NOT Friday default.",
        role_chip="Res Life",
        tier="A",
        website="https://www.ju.edu/residentiallife/",
    ),
    dict(
        email="engage@ju.edu",
        contact="",
        title="Student Engagement inbox",
        phone="904-256-7700",
        why="Published SE&L / Greek Life route inbox. NOT Friday default.",
        role_chip="Inbox",
        tier="A",
        website="https://www.ju.edu/",
    ),
    dict(
        email="kkieler@ju.edu",
        contact="Kira Kieler",
        title="Asst Dir, Student Engagement & Leadership",
        phone="904-256-7701",
        why="Published Thrive/SE&L · day-to-day programming. NOT Friday default.",
        role_chip="Programming",
        tier="A",
        website="https://www.ju.edu/studentenrichmentcenter/kira-kieler.php",
    ),
    dict(
        email="akossof@ju.edu",
        contact="Alex Kossoff Enriquez",
        title="Director, Campus Recreation & Wellness",
        phone="904-256-7548",
        why="Alex · published ju.edu/campusrecwellness/staff.php · goat yoga / wellness nights. NOT Friday default.",
        role_chip="RecWell",
        tier="A",
        website="https://www.ju.edu/campusrecwellness/staff.php",
    ),
    dict(
        email="cwells4@ju.edu",
        contact="Caroline Wells",
        title="Asst Dir, Campus Recreation & Wellness",
        phone="904-256-7548",
        why="Caroline · published RecWell staff · day-to-day wellness programming. NOT Friday default.",
        role_chip="RecWell",
        tier="A",
        website="https://www.ju.edu/campusrecwellness/staff.php",
    ),
    dict(
        email="jaxrecwell@ju.edu",
        contact="",
        title="Campus Rec & Wellness inbox",
        phone="904-256-7548",
        why="Published RecWell dept inbox. NOT Friday default.",
        role_chip="Inbox",
        tier="A",
        website="https://www.ju.edu/campusrecwellness/staff.php",
    ),
    dict(
        email="Ljames11@ju.edu",
        contact="Lauren James",
        title="Director of Residential Operations",
        phone="904-256-7213",
        why="Published Res Life staff · hall / move-in programming. NOT Friday default.",
        role_chip="Res Life",
        tier="A",
        website="https://www.ju.edu/residentiallife/contact/staff.php",
    ),
    dict(
        email="asimpso3@ju.edu",
        contact="Asha Simpson",
        title="Associate Director of Residential Life",
        phone="904-256-7099",
        why="Published Res Life staff. NOT Friday default.",
        role_chip="Res Life",
        tier="B",
        website="https://www.ju.edu/residentiallife/contact/staff.php",
    ),
    dict(
        email="Jembich@ju.edu",
        contact="Jynna Embich",
        title="Asst Dir of Residential Life",
        phone="904-256-7692",
        why="Published Res Life staff. NOT Friday default.",
        role_chip="Res Life",
        tier="B",
        website="https://www.ju.edu/residentiallife/contact/staff.php",
    ),
    dict(
        email="jparker17@ju.edu",
        contact="Jessica White",
        title="Director, Student Enrichment Center",
        phone="904-256-7190",
        why="Published · orientation / first-year programming. NOT Friday default.",
        role_chip="Orientation",
        tier="A",
        website="https://www.ju.edu/studentenrichmentcenter/jess-white.php",
    ),
    dict(
        email="enrichment@ju.edu",
        contact="",
        title="Student Enrichment office",
        phone="904-256-7694",
        why="Published enrichment inbox. NOT Friday default.",
        role_chip="Inbox",
        tier="B",
        website="https://www.ju.edu/studentenrichmentcenter/",
    ),
    dict(
        email="newtoju@ju.edu",
        contact="",
        title="New Student Orientation",
        phone="904-256-7700",
        why="Published orientation inbox. NOT Friday default.",
        role_chip="Orientation",
        tier="B",
        website="https://www.ju.edu/",
    ),
]

# Lacey / Bambi — no published personal email (phone/form note only)
JU_PHONE_GAPS = [
    dict(
        contact="Lacey Worsdell",
        title="Director of Alumni and Family Engagement (LinkedIn)",
        phone="904-256-8000",
        why="NO published personal email — use alumni@ju.edu / jjames20@ju.edu. LinkedIn title; campus main 904-256-8000. Gap card.",
        note_gap="Personal email unpublished — route via alumni@ju.edu",
    ),
    dict(
        contact="Bambi Brundage",
        title="Exec Dir Student Wellness & Engagement (LinkedIn)",
        phone="904-256-8000",
        why="NO published personal email — budget owner above RecWell/SE&L. Use engage@ju.edu / jaxrecwell@ju.edu. Campus main 904-256-8000.",
        note_gap="Personal email unpublished — route via engage@ju.edu or jaxrecwell@ju.edu",
    ),
]


def area_for_uni(company: str, city: str = "") -> str:
    c = (company or "").lower()
    if "jacksonville university" in c or re.search(r"\bju\b", c):
        return "Metro Jax · JU"
    if "north florida" in c or "unf" in c:
        return "Metro Jax · UNF"
    if "florida state college" in c or "fscj" in c:
        return "Metro Jax · FSCJ"
    if "edward waters" in c:
        return "Metro Jax · EWU"
    if "flagler" in c:
        return "St. Johns · Flagler"
    if "st. johns river" in c or "sjrstate" in c:
        return "St. Johns · SJR State"
    if "st. augustine for health" in c or "usa.edu" in c:
        return "St. Johns · USAHS"
    if "keiser" in c:
        return "Metro Jax · Keiser"
    if "embry-riddle" in c or "erau" in c:
        return "Metro Jax · ERAU"
    if "trinity college" in c:
        return "Metro Jax · Trinity"
    if "coastal georgia" in c:
        return "Farther · Brunswick"
    city = city or "Jacksonville"
    if re.search(r"st\.?\s*augustine|ponte|nocatee", city, re.I):
        return f"St. Johns · {city}"
    return f"Metro Jax · {city}"


# Programming-ish titles from uni-corporate (skip pure wellness intramurals)
UNI_KEEP_TITLE = re.compile(
    r"student (engagement|life|activities|affairs|programming|success|onboarding)|"
    r"campus (activities|events|life|recreation)|"
    r"family weekend|parent and family|alumni|orientation|residence|housing|"
    r"fraternity|sorority|greek|organizations|programming|recreation and wellness|"
    r"facility operations & events|eco adventure|student services|admissions|"
    r"campus office|sga advisor",
    re.I,
)


def add_universities(board, seen: set[str]) -> dict:
    sec = ensure_section(
        board,
        "university",
        "University / campus life",
        "Jax-area first (JU / UNF / FSCJ / EWU / Flagler / SJR State) + ASUN peers. Student life / Greek / residence. NOT Friday default — use University filter.",
    )
    added = {"ju": 0, "jax_area": 0, "gaps": 0}

    for spec in JU_ROWS:
        e = spec["email"]
        row = row_base(
            id=slug(f"{e}-ju-{spec.get('contact') or spec.get('title')}"),
            account="Jacksonville University",
            contact=spec.get("contact") or "",
            title=spec["title"],
            email=e,
            phone=spec.get("phone") or "",
            city="Jacksonville",
            segment="University",
            persona="university",
            lane="university",
            tier=spec.get("tier") or "A",
            area="Metro Jax · JU",
            role_chip=spec.get("role_chip") or "Campus",
            website=spec.get("website") or "https://www.ju.edu/",
            why=spec["why"],
            subject="Petting zoo for campus / student event?",
            friday=False,
        )
        if append_unique(sec, seen, row):
            added["ju"] += 1

    # Phone/form gap notes for Lacey / Bambi (no invented email — skip mailto rows)
    # Store as note_gap on a shared alumni inbox if present; also record in summary only.
    added["ju_phone_gaps"] = [
        f"{g['contact']}: {g['note_gap']}" for g in JU_PHONE_GAPS
    ]
    added["gaps"] = len(JU_PHONE_GAPS)

    # uni-corporate Jax-area colleges
    path = LEADS / "uni-corporate.csv"
    jax_co = re.compile(
        r"north florida|florida state college|edward waters|flagler|"
        r"st\.?\s*johns river|keiser university jacksonville|st\.?\s*augustine for health|"
        r"embry-riddle|trinity college of jacksonville|college of coastal georgia",
        re.I,
    )
    if path.exists():
        with path.open() as f:
            for raw in csv.DictReader(f):
                if (raw.get("segment") or "").lower() != "university":
                    continue
                co = raw.get("Company Name") or ""
                if "jacksonville university" in co.lower():
                    continue  # handled above
                if not jax_co.search(co):
                    continue
                e = (raw.get("Email") or "").strip()
                if not e or "@" not in e or " " in e:
                    continue
                title = raw.get("Job Title") or ""
                # keep programming seats; also keep campus inboxes
                if title and not UNI_KEEP_TITLE.search(title) and not e.lower().startswith(
                    ("family.", "parents@", "alumni@", "student", "getinvolved", "admission", "jacksonville@", "nas")
                ):
                    # still allow if email looks like programming inbox
                    if not re.search(
                        r"student|family|alumni|engage|life|activities|affair|orient|housing|admission|weekend",
                        e,
                        re.I,
                    ):
                        continue
                fn = (raw.get("First Name") or "").strip()
                ln = (raw.get("Last Name") or "").strip()
                contact = f"{fn} {ln}".strip()
                city = raw.get("City") or "Jacksonville"
                row = row_base(
                    id=slug(f"{e}-{co}-{title or contact}"),
                    account=co,
                    contact=contact,
                    title=title or "Campus programming",
                    email=e,
                    phone=raw.get("Phone Number") or "",
                    city=city,
                    segment="University",
                    persona="university",
                    lane="university",
                    tier="A" if "unf" in co.lower() or "fscj" in co.lower() or "flagler" in co.lower() else "B",
                    area=area_for_uni(co, city),
                    role_chip="Campus",
                    website=raw.get("Website URL") or "",
                    why=f"Published · {(raw.get('notes') or raw.get('event_name') or 'regional college programming')[:140]}. NOT Friday default.",
                    subject="Petting zoo for campus / student event?",
                    friday=False,
                )
                if append_unique(sec, seen, row):
                    added["jax_area"] += 1

    # Extra UNF named bookers from JU peer research (published)
    extra_unf = [
        ("ariel.lewis@unf.edu", "Ariel Lewis", "Assistant Director, Office of Student Life", "904-620-5440", "https://www.unf.edu/studentlife/"),
        ("j.thompkins@unf.edu", "Jasmine Thompkins", "Director, Fraternity & Sorority Life", "904-620-1084", "https://www.unf.edu/fraternity-sorority/staff.html"),
        ("studentlife@unf.edu", "", "Office of Student Life", "904-620-4386", "https://www.unf.edu/studentlife/"),
    ]
    for e, contact, title, phone, web in extra_unf:
        row = row_base(
            id=slug(f"{e}-unf"),
            account="University of North Florida",
            contact=contact,
            title=title,
            email=e,
            phone=phone,
            city="Jacksonville",
            segment="University",
            persona="university",
            lane="university",
            tier="A",
            area="Metro Jax · UNF",
            role_chip="Campus",
            website=web,
            why="Published UNF student-life / FSL seat (JU peer research). NOT Friday default.",
            subject="Petting zoo for campus / student event?",
            friday=False,
        )
        if append_unique(sec, seen, row):
            added["jax_area"] += 1

    # Flagler Tara Stevenson alt case from WAVE
    for e, contact, title, phone in [
        ("TStevenson@flagler.edu", "Tara Stevenson", "Vice President of Student Affairs", "904-819-6200"),
        ("RJohnson@flagler.edu", "Rick Johnson", "Director of Corporate Relations and Family Engagement", ""),
        ("jmurphy1@usa.edu", "J. Murphy", "Student Affairs (USAHS)", ""),
    ]:
        co = "Flagler College" if "flagler" in e.lower() else "University of St. Augustine for Health Sciences"
        row = row_base(
            id=slug(f"{e}-{co}"),
            account=co,
            contact=contact,
            title=title,
            email=e,
            phone=phone,
            city="St. Augustine",
            segment="University",
            persona="university",
            lane="university",
            tier="A",
            area=area_for_uni(co, "St. Augustine"),
            role_chip="Campus",
            website="",
            why="Published regional college seat. NOT Friday default.",
            friday=False,
        )
        if append_unique(sec, seen, row):
            added["jax_area"] += 1

    return added


# ---------- Apartments ----------
def add_apartments(board, seen: set[str]) -> dict:
    added = {"added": 0, "already": 0, "no_email_gaps": []}
    path = REVOPS / "b2b_expand_luxury_apartments.csv"
    # Prefer enterprise + cdd dual? Put apartments in enterprise (multifamily) and tag friday
    ent = ensure_section(
        board,
        "enterprise",
        "Regional enterprise",
        "Employee family day / wellness / country club / multifamily lifestyle.",
    )
    with path.open() as f:
        for raw in csv.DictReader(f):
            e = (raw.get("email") or "").strip()
            co = raw.get("company_name") or ""
            title = raw.get("job_title") or "Community / Lifestyle"
            if not e:
                added["no_email_gaps"].append(co)
                continue
            if e.lower() in seen:
                added["already"] += 1
                continue
            fn = (raw.get("first_name") or "").strip()
            ln = (raw.get("last_name") or "").strip()
            contact = f"{fn} {ln}".strip()
            row = row_base(
                id=slug(f"{e}-{co}"),
                account=co,
                contact=contact,
                title=title,
                email=e,
                phone=raw.get("phone") or "",
                city=raw.get("city") or "Jacksonville",
                segment="Luxury Apartment Lifestyle",
                persona="enterprise",
                lane="enterprise",
                tier="A",
                area=f"Metro Jax · {raw.get('city') or 'Jax'}",
                role_chip="Apartment",
                website=raw.get("website") or "",
                why=f"Friday priority — multifamily lifestyle / resident events. {(raw.get('notes') or '')[:120]}",
                subject="Petting zoo for resident / community event?",
                friday=True,
                friday_class="apartment",
                chip_tags=["Friday", "Apartment"],
            )
            if append_unique(ent, seen, row):
                added["added"] += 1
    # also northbeach from uni-corporate notes
    for e, co, title, phone, web in [
        ("northbeach@ram-mgt.com", "North Beach on Kernan (RAM Partners)", "Community Manager / Leasing Office", "904-997-6060", ""),
    ]:
        row = row_base(
            id=slug(f"{e}-{co}"),
            account=co,
            contact="",
            title=title,
            email=e,
            phone=phone,
            city="Jacksonville",
            segment="Luxury Apartment Lifestyle",
            persona="enterprise",
            lane="enterprise",
            tier="A",
            area="Metro Jax · Kernan",
            role_chip="Apartment",
            website=web,
            why="Friday priority — published leasing/community desk for resident events.",
            friday=True,
            friday_class="apartment",
            chip_tags=["Friday", "Apartment"],
        )
        if append_unique(ent, seen, row):
            added["added"] += 1
    return added


# ---------- Churches (published missing) ----------
def add_churches(board, seen: set[str], limit: int = 18) -> int:
    sec = ensure_section(
        board,
        "directors",
        "Directors / Pastors / Activities leads",
        "Daycare, church, senior directors. Churches = Friday weekend programmers.",
    )
    path = LEADS / "churches.csv"
    n = 0
    if not path.exists():
        return 0
    with path.open() as f:
        for raw in csv.DictReader(f):
            if n >= limit:
                break
            e = (raw.get("Email") or "").strip()
            if not e or "@" not in e or e.lower() in seen:
                continue
            co = raw.get("Company Name") or "Church"
            title = raw.get("Job Title") or "Kids / Family Ministry"
            fn = (raw.get("First Name") or "").strip()
            ln = (raw.get("Last Name") or "").strip()
            contact = f"{fn} {ln}".strip()
            city = raw.get("City") or "Jacksonville"
            row = row_base(
                id=slug(f"{e}-{co}"),
                account=co,
                contact=contact,
                title=title,
                email=e,
                phone=raw.get("Phone Number") or "",
                city=city,
                segment="Church",
                persona="church",
                lane="directors",
                tier="A",
                area=f"Metro Jax · {city}",
                role_chip="Church",
                website=raw.get("Website URL") or "",
                why=f"Friday priority — churches program weekends. {(raw.get('notes') or '')[:100]}",
                subject="Petting zoo for fall festival / family event?",
                friday=True,
                friday_class="church",
                chip_tags=["Friday"],
            )
            if append_unique(sec, seen, row):
                n += 1
    return n


# ---------- Corporate / district Friday ----------
def add_corporate_friday(board, seen: set[str]) -> dict:
    ent = ensure_section(
        board,
        "enterprise",
        "Regional enterprise",
        "Employee family day / wellness / country club / franchise ops.",
    )
    cdd = ensure_section(
        board,
        "cdd",
        "CDD / HOA amenity",
        "Community / amenity / fall festival — allow list. Friday = amenity + district/ops.",
    )
    stats = {"mcd": 0, "district": 0, "tagged_existing_mcd": 0}

    # Ensure McDonald's published inbox is an enterprise Friday card (also may live in consumer)
    mcd = row_base(
        id="comments-mcdjax-com-dcc-lee-friday-corporate",
        account="DCC LEE Enterprises (McDonald's)",
        contact="David Mullins / Ops",
        title="Owner-Operator org inbox (community events)",
        email="comments@mcdjax.com",
        phone="",
        city="Jacksonville",
        segment="Franchise / Corporate",
        persona="enterprise",
        lane="enterprise",
        tier="A",
        area="Metro Jax · McDonald's DCC LEE",
        role_chip="Corporate Friday",
        website="https://dcclee.net/",
        why="Friday priority — corporate / franchise ops. ONLY published org inbox (comments@mcdjax.com). Community / employee family events. No store emails invented.",
        subject="Petting zoo for community / employee family event?",
        friday=True,
        friday_class="corporate",
        chip_tags=["Friday", "Corporate Friday"],
    )
    # Force-add even if consumer has same email: allow duplicate across sections? Prefer update existing enterprise or add if missing in enterprise
    ent_emails = {(r.get("email") or "").lower() for r in ent.get("rows") or []}
    if "comments@mcdjax.com" not in ent_emails:
        ent.setdefault("rows", []).append(mcd)
        stats["mcd"] = 1
        seen.add("comments@mcdjax.com")
    else:
        for r in ent["rows"]:
            if (r.get("email") or "").lower() == "comments@mcdjax.com":
                r["friday"] = True
                r["friday_class"] = "corporate"
                tags = list(r.get("chip_tags") or [])
                for t in ("Friday", "Corporate Friday"):
                    if t not in tags:
                        tags.append(t)
                r["chip_tags"] = tags
                if "Friday priority" not in (r.get("why") or ""):
                    r["why"] = FRIDAY_WHY["corporate"] + " " + (r.get("why") or "")
                stats["tagged_existing_mcd"] = 1

    # Tag Royal if present
    for s in board["sections"]:
        for r in s.get("rows") or []:
            if (r.get("email") or "").lower() == "inquiries@royalrg.com":
                r["friday"] = True
                r["friday_class"] = "corporate"
                tags = list(r.get("chip_tags") or [])
                for t in ("Friday", "Corporate Friday"):
                    if t not in tags:
                        tags.append(t)
                r["chip_tags"] = tags
                if "Friday priority" not in (r.get("why") or ""):
                    r["why"] = FRIDAY_WHY["corporate"] + " " + (r.get("why") or "")

    # District / field ops from people-enterprise (published)
    path = LEADS / "people-enterprise.csv"
    if path.exists():
        with path.open() as f:
            for raw in csv.DictReader(f):
                e = (raw.get("Email") or "").strip()
                if not e or "@" not in e or e.lower() in seen:
                    continue
                title = raw.get("Job Title") or ""
                if not re.search(r"district manager|field operations|operations manager", title, re.I):
                    continue
                # skip pure university rows without email already handled
                co = raw.get("Company Name") or ""
                fn = (raw.get("First Name") or "").strip()
                ln = (raw.get("Last Name") or "").strip()
                contact = f"{fn} {ln}".strip()
                city = raw.get("City") or "Jacksonville"
                is_cdd = bool(re.search(r"cdd|hoa|vesta|gms|rizzetta|rms|inframark|firstservice|wrathell", co, re.I))
                target = cdd if is_cdd else ent
                persona = "cdd" if is_cdd else "enterprise"
                cls = "district" if is_cdd else "corporate"
                row = row_base(
                    id=slug(f"{e}-{co}-{title}"),
                    account=co,
                    contact=contact,
                    title=title,
                    email=e,
                    phone=raw.get("Phone Number") or "",
                    city=city,
                    segment="CDD / HOA" if is_cdd else "Franchise / Corporate",
                    persona=persona,
                    lane="cdd" if is_cdd else "enterprise",
                    tier="A",
                    area=f"Metro Jax · {city}",
                    role_chip="District" if is_cdd else "Corporate Friday",
                    website=raw.get("Website URL") or "",
                    why=FRIDAY_WHY[cls] + f" Published people-enterprise.csv.",
                    subject=(
                        "Petting zoo for CDD / amenity fall festival?"
                        if is_cdd
                        else "Petting zoo for community / employee family event?"
                    ),
                    friday=True,
                    friday_class=cls,
                    chip_tags=["Friday"] + (["Corporate Friday"] if cls == "corporate" else []),
                )
                if append_unique(target, seen, row):
                    stats["district"] += 1
    return stats


def recount(board, friday_counts: Counter, meta: dict):
    counts = board.get("counts") or {}
    by_persona: dict[str, int] = {}
    mailto = 0
    fri = 0
    uni_total = 0
    church = 0
    cdd_amenity = 0
    apt = 0
    corp_fri = 0
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
        for r in s.get("rows") or []:
            if r.get("email"):
                mailto += 1
            p = r.get("persona") or "other"
            by_persona[p] = by_persona.get(p, 0) + 1
            if r.get("friday"):
                fri += 1
            if p == "university" or sid == "university":
                uni_total += 1
            if r.get("friday_class") == "church" or p == "church":
                if r.get("friday"):
                    church += 1
            if r.get("friday_class") == "cdd_amenity":
                cdd_amenity += 1
            if r.get("friday_class") == "apartment":
                apt += 1
            if r.get("friday_class") == "corporate":
                corp_fri += 1
    # unique university emails
    uni_emails = set()
    for s in board["sections"]:
        for r in s.get("rows") or []:
            if (r.get("persona") or "") == "university" and r.get("email"):
                uni_emails.add(r["email"].lower())
    counts["mailto_total"] = mailto
    counts["by_persona"] = by_persona
    counts["friday"] = fri
    counts["friday_by_class"] = dict(friday_counts)
    counts["university_unique"] = len(uni_emails)
    counts["friday_church"] = friday_counts.get("church", 0)
    counts["friday_cdd_amenity"] = friday_counts.get("cdd_amenity", 0)
    counts["friday_apartment"] = friday_counts.get("apartment", 0)
    counts["friday_corporate"] = friday_counts.get("corporate", 0)
    counts["friday_district"] = friday_counts.get("district", 0)
    counts["friday_consumer_rebook"] = friday_counts.get("consumer_rebook", 0)
    board["counts"] = counts
    board["as_of"] = AS_OF
    board["board_version"] = BOARD_VER
    board["label"] = (
        "Principal dunk board v2.9 — Friday weekend programmers + Jax universities + Corporate Friday"
    )
    board["rule"] = (
        "Compose-only. Friday filter = weekend programmers (church / CDD amenity / apartments / "
        "corporate-district) + secondary consumer rebook. University = separate filter, NOT Friday default. "
        "Published emails only. Done key sheehan_principal_dunk_done_v2 · Notes sheehan_dunk_notes_v1."
    )
    board["v29"] = meta


def patch_html():
    html = HTML_PATH.read_text(encoding="utf-8")
    # version stamps
    html = re.sub(
        r"Board v2\.8 · Sep 25 [^<]+",
        BOARD_VER,
        html,
    )
    html = html.replace("Hard-refresh (?v=28)", "Hard-refresh (?v=29)")
    html = html.replace("?v=28", "?v=29")
    # banner blurb
    html = re.sub(
        r"(<div class=\"banner\"><span class=\"ver\" id=\"verstamp\">)(.*?)(</span>)",
        rf"\1{BOARD_VER}\3",
        html,
        count=1,
    )
    # Update banner body once
    old_banner_bits = [
        "Board v2.8:",
        "Board v2.9:",
    ]
    if "Friday weekend programmers" not in html:
        html = html.replace(
            "<b>Compose only — never auto-send.</b>",
            "<b>Compose only — never auto-send.</b> Board v2.9: <b>Friday</b> weekend programmers (church · CDD amenity · apartments · corporate/district) · <b>University</b> Jax-first (JU/UNF/FSCJ) — not Friday default · Bartram notes live.",
            1,
        )
        # remove duplicated old v2.8 sentence if still there after insert
        html = re.sub(
            r" Board v2\.8: <b>RCSA</b>.*?(?=</div>)",
            " ",
            html,
            count=1,
        )

    # CSS for friday chip/button
    if "friday-btn" not in html:
        html = html.replace(
            ".filters button[data-hlane].on{border-color:#fb923c88;background:#2a1a10;color:#fdba74}",
            ".filters button[data-hlane].on{border-color:#fb923c88;background:#2a1a10;color:#fdba74}\n"
            ".filters button.friday-btn.on{border-color:#fbbf2488;background:#2a2410;color:#fde68a}\n"
            ".chip.friday{border-color:#fbbf2488;color:#fde68a;font-weight:700}\n"
            ".chip.corp-fri{border-color:#f9731688;color:#fdba74}",
        )

    # Filter button after Owe / before Premium
    if 'data-sec="friday"' not in html:
        html = html.replace(
            '<button type="button" class="owe-btn" data-sec="owe">Owe / Slam</button>\n',
            '<button type="button" class="owe-btn" data-sec="owe">Owe / Slam</button>\n'
            '  <button type="button" class="friday-btn" data-sec="friday">Friday · Weekend</button>\n',
        )

    # JS: rowsForSection friday virtual lane
    if "sec==='friday'" not in html:
        html = html.replace(
            "if(sec==='fancy'){",
            "if(sec==='friday'){\n"
            "      const rows=[]; const seenE=new Set();\n"
            "      (data.sections||[]).forEach(s=>{(s.rows||[]).forEach(r=>{\n"
            "        if(!(r.friday || (r.chip_tags||[]).includes('Friday'))) return;\n"
            "        const e=String(r.email||'').toLowerCase();\n"
            "        if(e && seenE.has(e)) return; if(e) seenE.add(e);\n"
            "        rows.push(r);\n"
            "      });});\n"
            "      rows.sort((a,b)=>{\n"
            "        const order={corporate:0,cdd_amenity:1,district:2,church:3,apartment:4,consumer_rebook:5};\n"
            "        return (order[a.friday_class]??9)-(order[b.friday_class]??9);\n"
            "      });\n"
            "      return {title:'Friday · Weekend programmers', hint:'Amenity / lifestyle / church / CDD-HOA / apartments / corporate-district. Why-line explains Friday (programs weekends). University is a separate filter — not Friday default. Consumer rebook secondary. Compose only.', rows};\n"
            "    }\n"
            "    if(sec==='fancy'){",
        )

    # chip render
    if "chip friday" not in html:
        html = html.replace(
            "if(r.fancy || (r.chip_tags||[]).includes('Fancy')) html+=`<span class=\"chip fancy\">Fancy</span> `;",
            "if(r.fancy || (r.chip_tags||[]).includes('Fancy')) html+=`<span class=\"chip fancy\">Fancy</span> `;\n"
            "      if(r.friday || (r.chip_tags||[]).includes('Friday')) html+=`<span class=\"chip friday\">Friday</span> `;\n"
            "      if((r.chip_tags||[]).includes('Corporate Friday') || r.friday_class==='corporate') html+=`<span class=\"chip corp-fri\">Corp Fri</span> `;",
        )

    # KPI friday
    if "['Friday'" not in html and '["Friday"' not in html:
        html = html.replace(
            "['Fancy',counts.fancy],",
            "['Fancy',counts.fancy],\n"
            "      ['Friday',counts.friday],\n"
            "      ['Uni',counts.university_unique||counts.university||bp.university],",
        )

    # dedupe banner version mention
    html = re.sub(
        r"const ver=document.getElementById\('verstamp'\);.*?ver\.textContent=data\.board_version",
        "const ver=document.getElementById('verstamp'); if(ver&&data.board_version) ver.textContent=data.board_version",
        html,
        flags=re.S,
    )
    # softer: just ensure load sets verstamp — already does likely
    # footer note source line
    html = html.replace(
        "Source: TAM + RCSA campuses + Fancy schools + Consumer customers/warm",
        "Source: TAM + Jax universities (JU/UNF/FSCJ) + Friday weekend programmers + RCSA/Fancy + Consumer",
    )

    # v28 footer status → v29
    html = re.sub(
        r"el\.innerHTML='<b>v2\.8</b>.*?'",
        "el.innerHTML='<b>v2.9</b> · Friday '+(counts.friday||0)+' · Uni '+(counts.university_unique||counts.university||0)+' · Church fri '+(counts.friday_church||0)+' · CDD amenity '+(counts.friday_cdd_amenity||0)+' · Apt '+(counts.friday_apartment||0)+' · Corp/dist '+(counts.friday_corporate||0)+'/'+(counts.friday_district||0)+' · left <b>'+(counts.mailto_total||0)+' mailto</b>'",
        html,
        count=1,
    )

    HTML_PATH.write_text(html, encoding="utf-8")


def main():
    board = load_board()
    seen = all_emails(board)

    uni = add_universities(board, seen)
    apt = add_apartments(board, seen)
    church_n = add_churches(board, seen, limit=18)
    corp = add_corporate_friday(board, seen)
    fri_counts = apply_friday_tags(board)

    meta = {
        "as_of": AS_OF,
        "university_added_ju": uni.get("ju"),
        "university_added_jax_area": uni.get("jax_area"),
        "university_phone_gaps": uni.get("ju_phone_gaps"),
        "apartments_added": apt.get("added"),
        "apartments_already": apt.get("already"),
        "apartment_no_email_gaps": apt.get("no_email_gaps"),
        "churches_added": church_n,
        "corporate_friday": corp,
        "friday_counts": dict(fri_counts),
    }
    recount(board, fri_counts, meta)

    with BOARD_PATH.open("w") as f:
        json.dump(board, f, indent=2)
        f.write("\n")

    patch_html()

    summary = {
        "as_of": AS_OF,
        "board_version": BOARD_VER,
        "friday_total": board["counts"].get("friday"),
        "friday_by_class": dict(fri_counts),
        "university_section": board["counts"].get("university"),
        "university_unique": board["counts"].get("university_unique"),
        "meta": meta,
        "mailto_total": board["counts"].get("mailto_total"),
    }
    (DATA / "_dunk_v29_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
