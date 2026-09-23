#!/usr/bin/env python3
"""Enrich BDR TAM dialer → v2 lanes, scores, flags, fruit, seeds.
Never invents emails/phones. Reads/writes data/bdr_tam_dialer.json.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = Path("/workspace/dashboard/exec-suite")
IN = ROOT / "data" / "bdr_tam_dialer.json"
OUT = IN
AS_OF = datetime.now(ET).strftime("%Y-%m-%d %H:%M ET")

LANES = [
    "Regional Enterprise",
    "Regional Subscription",
    "Regional Violet ~50%",
    "Regional Small Biz Programmer",
    "EMBA on Call",
]

SEG_TO_LANE = {
    "Senior / IL-AL": "Regional Subscription",
    "PPEC": "Regional Subscription",
    "Adult Daycare": "Regional Subscription",
    "Existing / Customer": "Regional Subscription",
    "B2C / Violet / Inbound": "Regional Violet ~50%",
    "Brewery / Family": "Regional Small Biz Programmer",
    "Corporate HR": "Regional Enterprise",
    "Corporate QSR / Field": "Regional Enterprise",
    "Industrial / Employee Apprec": "Regional Enterprise",
    "University": "Regional Enterprise",
    "Independent School": "Regional Enterprise",
    "VPK / ELC": "Regional Enterprise",
    "Daycare / Childcare": "Regional Enterprise",
    "Goddard / Fancy School": "Regional Enterprise",
    "PTA / PTO": "Regional Enterprise",
    "Church / Faith": "Regional Enterprise",
    "Festival / Events": "Regional Enterprise",
    "Car Dealership": "Regional Enterprise",
    "Hotel / Kids Club": "Regional Enterprise",
    "Preservation / SPAR": "Regional Enterprise",
    "Nonprofit": "Regional Enterprise",
    "Hospital / Red Tape": "Regional Enterprise",
    "Municipal / B2G": "Regional Enterprise",
    "CDD / HOA": "Regional Enterprise",
    "Luxury Apartment": "Regional Enterprise",
    "Golf / Country Club": "Regional Enterprise",
}

SMALL_BIZ_RE = re.compile(
    r"\b(brew|brewery|taproom|coffee|cafe|caf[eé]|bookstore|book\s*shop|indie\s*venue|"
    r"music\s*venue|wine\s*bar|bakery|roaster|record\s*shop|gallery)\b",
    re.I,
)
EMBA_RE = re.compile(
    r"\b(founder|startup|emba|consult|sponsor|donation|goat\s*statue|homestead\s*shout|"
    r"mini\s*zoo|farm\s*tour|philanthrop|underwriter)\b",
    re.I,
)
HARD_FORM_RE = re.compile(
    r"(dealer|sales|buy.?now|schedule.?a.?tour|senior.?living.?portal|inventory|"
    r"finance.?app|credit.?app|sr\.?\s*portal)",
    re.I,
)
SOFT_FORM_RE = re.compile(
    r"(contact|community|volunteer|about|message|inquiry|enquire|connect|"
    r"get.?in.?touch|program|event|booking)",
    re.I,
)
STALE_RE = re.compile(
    r"\b(stale|bounced?|bad.?email|invalid|old.?list|messy|do.?not.?use|"
    r"undeliver|defunct|wrong.?email|outdated)\b",
    re.I,
)
CUSTOMER_PEN_RE = re.compile(
    r"\b(monthly|customer|bought|existing|quarterly|yearly|one.?off|occasional|"
    r"past|repeat)\b",
    re.I,
)
FREE_MAIL = {
    "gmail.com", "yahoo.com", "hotmail.com", "aol.com", "outlook.com",
    "icloud.com", "me.com", "live.com", "msn.com", "comcast.net",
    "att.net", "bellsouth.net", "ymail.com", "protonmail.com",
}


def org_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def clean_email(v) -> str:
    if not v:
        return ""
    s = str(v).strip().split(";")[0].split(",")[0].strip()
    if "@" not in s:
        m = re.search(r"[\w.+-]+@[\w.-]+\.\w+", s)
        return m.group(0).lower() if m else ""
    return s.lower()


def clean_phone(v) -> str:
    if not v:
        return ""
    s = str(v).strip()
    digits = re.sub(r"\D", "", s)
    if len(digits) < 7:
        return ""
    return s


def email_domain(email: str) -> str:
    e = clean_email(email)
    if not e or "@" not in e:
        return ""
    d = e.split("@", 1)[1].lower()
    return "" if d in FREE_MAIL else d


def load_customer_map() -> dict[str, dict]:
    p = Path("/workspace/bdr/lists/MICHAEL_CUSTOMER_MAP_2026-09-22.md")
    out: dict[str, dict] = {}
    if not p.exists():
        return out
    for line in p.read_text().splitlines():
        if not line.startswith("|") or line.startswith("| name") or line.startswith("|---"):
            continue
        parts = [x.strip() for x in line.strip("|").split("|")]
        if len(parts) < 3:
            continue
        name, seg, cadence = parts[0], parts[1], parts[2]
        hint = parts[3] if len(parts) > 3 else ""
        notes = parts[4] if len(parts) > 4 else ""
        if not name or name.lower() == "name":
            continue
        aliases = [a.strip() for a in re.split(r"[/|]", name) if a.strip()]
        aliases.append(name)
        for a in aliases:
            out[org_key(a)] = {
                "cadence": cadence,
                "notes": notes,
                "contact_hint": hint,
                "map_name": name,
                "segment": seg,
            }
    return out


def load_paypal_names() -> set[str]:
    p = ROOT / "data" / "paypal_customers.json"
    if not p.exists():
        return set()
    data = json.loads(p.read_text())
    names: set[str] = set()
    rows = data if isinstance(data, list) else data.get("customers") or []
    for row in rows:
        n = (row.get("Customer") or row.get("name") or "").strip().lower()
        if n:
            names.add(n)
    return names


SEED_NOTES = {
    org_key("Discovery Village at Deerwood"): (
        "SEED (disk 2026-09-22): Patricia Valenzuela · Director of Celebrations. "
        "EXISTING MONTHLY partner — keep monthly. Tasia Felix (tfelix@discoveryvillages.com) "
        "is Life Enrichment on Discovery brand; warm path for sister campuses. Likely confirming / not cold."
    ),
    org_key("Brookdale Southpoint"): (
        "SEED (disk 2026-09-22 Michael voice dump): thinks referral from Tasia; "
        "check notes/email for Tasia referral — not cold."
    ),
    org_key("Discovery Commons San Pablo"): (
        "SEED: soft-warm — ask Tasia (Deerwood / Patricia path) for warm intro; prefer not blind cold."
    ),
    org_key("Discovery Village St. Augustine"): (
        "SEED: soft-warm — ask Tasia (Deerwood / Patricia path) for warm intro; prefer not blind cold."
    ),
    org_key("Discovery St Augustine"): (
        "SEED: soft-warm — ask Tasia (Deerwood / Patricia path) for warm intro; prefer not blind cold."
    ),
}


def form_quality(url: str, segment: str) -> str:
    if not url:
        return "none"
    u = url.lower()
    if segment == "Car Dealership" or HARD_FORM_RE.search(u):
        return "hard"
    if SOFT_FORM_RE.search(u):
        return "soft"
    return "neutral"


def penetration_bucket(pen: str, notes: str, cadence: str | None) -> str:
    blob = f"{pen} {notes} {cadence or ''}".lower()
    if re.search(r"\bmonthly\b", blob):
        return "monthly"
    if re.search(r"\b(quarterly|yearly|occasional|one.?off|repeat)\b", blob):
        return "occasional"
    if re.search(r"\b(past|lapsed|former)\b", blob):
        return "past"
    if re.search(r"\b(customer|bought|existing|warm|supposed)\b", blob):
        return "bought"
    if re.search(r"\b(never_hit|needs_reply|godaddy|inbound|interest)\b", blob):
        return "inbound"
    if re.search(r"\bcold\b", blob):
        return "cold"
    return "unknown"


def extract_linkedin(row: dict) -> str:
    blob = " ".join(str(row.get(k) or "") for k in row)
    m = re.search(r"https?://(?:www\.)?linkedin\.com/[^\s|'\"<>]+", blob, re.I)
    return m.group(0).rstrip(".,);]") if m else ""


def assign_lane(row: dict) -> str:
    seg = row.get("segment") or "Other"
    blob = " ".join(
        str(row.get(k) or "")
        for k in ("account", "contact", "notes", "title", "segment", "segment_raw")
    )
    src = (row.get("source") or "").lower()
    # Subscription wins for seniors / existing / PPEC / adult daycare / customer-map hits
    if seg in {
        "Senior / IL-AL", "PPEC", "Adult Daycare", "Existing / Customer",
        "Adult Daycare", "PPEC",
    } or row.get("is_customer") or row.get("customer_match"):
        # Exception: pure B2C person-name inbound without org senior markers
        if seg == "B2C / Violet / Inbound" and not row.get("customer_match"):
            pass
        else:
            return "Regional Subscription"
    # Violet: true B2C / inbound fruit only (not senior orgs that share an inbound source tag)
    if seg == "B2C / Violet / Inbound":
        return "Regional Violet ~50%"
    if (
        ("consumer_inbound" in src or "deputy_inbound" in src or "inbound_fire" in src)
        and seg in ("Other", "B2C / Violet / Inbound", "")
    ):
        return "Regional Violet ~50%"
    lane = SEG_TO_LANE.get(seg, "Regional Enterprise")
    if SMALL_BIZ_RE.search(blob) and lane not in ("Regional Violet ~50%", "Regional Subscription"):
        lane = "Regional Small Biz Programmer"
    if EMBA_RE.search(blob) and lane not in ("Regional Violet ~50%", "Regional Subscription"):
        if lane == "Regional Small Biz Programmer" or seg in ("Other", "Nonprofit", "Festival / Events"):
            lane = "EMBA on Call"
        elif seg == "Other":
            lane = "EMBA on Call"
    if seg == "Other" and EMBA_RE.search(blob):
        lane = "EMBA on Call"
    if seg == "Other" and SMALL_BIZ_RE.search(blob):
        lane = "Regional Small Biz Programmer"
    return lane


def score_row(row: dict) -> int:
    s = 0
    if row.get("has_email") or row.get("email"):
        s += 18
    if row.get("has_phone") or row.get("phone"):
        s += 12
    if row.get("has_linkedin") or row.get("linkedin_url"):
        s += 8
    if row.get("is_tier1"):
        s += 15
    s += {
        "monthly": 20,
        "occasional": 12,
        "bought": 14,
        "past": 6,
        "inbound": 14,
        "cold": 2,
        "unknown": 0,
    }.get(row.get("pen_bucket") or "", 0)
    if row.get("is_customer") or row.get("customer_match"):
        s += 16
    fq = row.get("form_quality") or "none"
    if fq == "soft":
        s += 10
    elif fq == "neutral" and row.get("form_url"):
        s += 4
    elif fq == "hard":
        s -= 8
    if row.get("hubspot_listed"):
        s += 8
    if row.get("never_hit"):
        s += 10
    if row.get("recent_activity"):
        s += 5
    if row.get("stale_email"):
        s -= 12
    if row.get("messy_list") and not row.get("has_email"):
        s += 3
    return max(0, min(100, s))


def best_paths(row: dict) -> list[str]:
    paths = []
    if row.get("email") and not row.get("stale_email"):
        paths.append("email")
    if row.get("phone"):
        paths.append("cell")
    if row.get("linkedin_url"):
        paths.append("LinkedIn")
    fq = row.get("form_quality") or "none"
    if row.get("form_url") and fq != "hard":
        paths.append("form")
    elif row.get("form_url") and fq == "hard" and not paths:
        paths.append("form")
    return paths


def fruit_rows_from_consumer() -> list[dict]:
    p = ROOT / "data" / "consumer_inbound.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    out = []
    for r in data.get("contacts") or []:
        email = clean_email(r.get("email"))
        name = (r.get("name") or "").strip()
        if not email and not name:
            continue
        never = str(r.get("status") or "").lower() in ("interest", "needs_reply", "never_hit", "open", "")
        if str(r.get("purchase_status") or "").lower() in ("bought", "customer", "repeat"):
            never = False
        phone = clean_phone(r.get("phone"))
        out.append(
            {
                "segment": "B2C / Violet / Inbound",
                "segment_raw": r.get("bucket") or "consumer",
                "account": name or email,
                "contact": name,
                "title": "",
                "phone": phone,
                "email": email,
                "tier": "Tier 1 / Inbound" if never else "",
                "is_tier1": bool(never),
                "call_band": "Call now" if never else "Warm",
                "penetration": "never_hit" if never else (r.get("purchase_status") or r.get("status") or "inbound"),
                "next_action": r.get("next_action") or ("Reply inbound" if never else "Nurture"),
                "source": f"consumer_inbound:{r.get('bucket') or r.get('source') or 'row'}",
                "county": "",
                "city": "",
                "form_url": "",
                "notes": (r.get("detail") or "")[:200],
                "has_email": bool(email),
                "has_phone": bool(phone),
                "has_info": True,
                "hubspot_listed": bool(r.get("hubspot_listed")),
            }
        )
    return out


def fruit_rows_from_deputy() -> list[dict]:
    p = Path("/workspace/deputy-outreach/one-touch/INBOUND_QUEUE.csv")
    if not p.exists():
        return []
    out = []
    with p.open(newline="", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            email = clean_email(r.get("email"))
            contact = (r.get("contact_name") or "").strip()
            org = (r.get("org") or contact or email).strip()
            if not org:
                continue
            flag = (r.get("flag") or "").lower()
            never = flag in ("inbound", "never_hit", "")
            phone = clean_phone(r.get("phone"))
            out.append(
                {
                    "segment": "B2C / Violet / Inbound",
                    "segment_raw": r.get("type") or "deputy",
                    "account": org,
                    "contact": contact,
                    "title": (r.get("title") or "").strip(),
                    "phone": phone,
                    "email": email,
                    "tier": "Tier 1 / Inbound",
                    "is_tier1": True,
                    "call_band": "Call now" if never else "Warm",
                    "penetration": "never_hit" if never else flag,
                    "next_action": "Reply inbound" if never else "Follow up",
                    "source": f"deputy_inbound:{r.get('source') or 'INBOUND_QUEUE'}",
                    "county": "",
                    "city": "",
                    "form_url": (r.get("form_url") or "").strip(),
                    "notes": ((r.get("call_need_to_knows") or "") + " " + (r.get("draft_subject") or "")).strip()[:200],
                    "has_email": bool(email),
                    "has_phone": bool(phone),
                    "has_info": True,
                }
            )
    return out


def merge_fruit(existing: list[dict], fruit: list[dict]) -> list[dict]:
    by_email = {clean_email(r.get("email")): r for r in existing if clean_email(r.get("email"))}
    by_org: dict[str, list[dict]] = defaultdict(list)
    for r in existing:
        by_org[org_key(r.get("account") or "")].append(r)
    for fr in fruit:
        em = clean_email(fr.get("email"))
        if em and em in by_email:
            tgt = by_email[em]
            if fr.get("hubspot_listed"):
                tgt["hubspot_listed"] = True
            if fr.get("penetration") == "never_hit" and not CUSTOMER_PEN_RE.search(
                f"{tgt.get('penetration')} {tgt.get('notes')}"
            ):
                tgt["never_hit"] = True
            src = set(filter(None, (tgt.get("source") or "").split("|")))
            src.add(fr.get("source") or "")
            tgt["source"] = "|".join(sorted(src))
            continue
        ok = org_key(fr.get("account") or "")
        dup = False
        for ex in by_org.get(ok, []):
            if (ex.get("contact") or "").lower() == (fr.get("contact") or "").lower():
                if not em or not ex.get("email") or clean_email(ex.get("email")) == em:
                    dup = True
                    if fr.get("hubspot_listed"):
                        ex["hubspot_listed"] = True
                    break
        if dup:
            continue
        existing.append(fr)
        if em:
            by_email[em] = fr
        by_org[ok].append(fr)
    return existing


def enrich(contacts: list[dict], cmap: dict, paypal: set[str]) -> list[dict]:
    by_org: dict[str, list[int]] = defaultdict(list)
    by_domain: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(contacts):
        by_org[org_key(r.get("account") or "")].append(i)
        d = email_domain(r.get("email") or "")
        if d:
            by_domain[d].append(i)

    for i, r in enumerate(contacts):
        ok = org_key(r.get("account") or "")
        cm = cmap.get(ok)
        if not cm:
            for k, v in cmap.items():
                if k and len(k) > 6 and (k in ok or ok in k):
                    cm = v
                    break

        notes_blob = f"{r.get('notes') or ''} {r.get('penetration') or ''}"
        cadence = cm["cadence"] if cm else ""
        r["pen_bucket"] = penetration_bucket(r.get("penetration") or "", notes_blob, cadence)
        r["customer_match"] = bool(cm) or bool(
            CUSTOMER_PEN_RE.search(notes_blob)
            and re.search(r"\b(monthly|customer|existing|bought|quarterly|yearly)\b", notes_blob, re.I)
        )
        cname = (r.get("contact") or "").strip().lower()
        if cname and cname in paypal:
            r["customer_match"] = True
            r["paypal_match"] = True
        r["is_customer"] = bool(
            r.get("customer_match")
            or r.get("pen_bucket") in ("monthly", "occasional", "bought")
            or (r.get("segment") == "Existing / Customer")
            or (
                cm
                and cm.get("cadence")
                in ("Monthly", "Quarterly", "Yearly", "OneOff", "Past", "Supposed", "Warm")
            )
        )
        if cm:
            r["customer_cadence"] = cm.get("cadence") or ""
            r["map_notes"] = cm.get("notes") or ""

        li = extract_linkedin(r)
        r["linkedin_url"] = li
        r["has_linkedin"] = bool(li)

        r["form_quality"] = form_quality(r.get("form_url") or "", r.get("segment") or "")
        src = (r.get("source") or "").lower()
        r["hubspot_listed"] = bool(r.get("hubspot_listed")) or ("hubspot" in src)
        r["never_hit"] = bool(r.get("never_hit")) or (
            r.get("pen_bucket") == "inbound"
            or "never_hit" in (r.get("penetration") or "").lower()
            or ("inbound_fire" in src and not r.get("is_customer"))
            or ("consumer_inbound" in src and not r.get("is_customer"))
            or ("deputy_inbound" in src and not r.get("is_customer"))
        )
        stale = bool(STALE_RE.search(notes_blob)) or bool(STALE_RE.search(src))
        r["stale_email"] = bool(stale and r.get("email"))
        r["messy_list"] = bool(stale) or ("messy" in src) or ("old_list" in src)
        r["recent_activity"] = bool(re.search(r"2026-09|2026-08|today|this week", notes_blob, re.I))

        r["lane"] = assign_lane(r)
        r["seed_note"] = SEED_NOTES.get(ok) or ""
        if (
            not r["seed_note"]
            and "patricia" in (r.get("contact") or "").lower()
            and "discovery" in (r.get("account") or "").lower()
        ):
            r["seed_note"] = SEED_NOTES[org_key("Discovery Village at Deerwood")]

        related = set()
        for j in by_org.get(ok, []):
            if j != i:
                related.add(contacts[j].get("account") or "")
        d = email_domain(r.get("email") or "")
        if d:
            for j in by_domain.get(d, []):
                if j != i:
                    related.add(contacts[j].get("account") or "")
        if re.search(r"tasia|referral", notes_blob, re.I):
            r["referral_tag"] = True
            for j, other in enumerate(contacts):
                if j == i:
                    continue
                ob = f"{other.get('notes') or ''} {other.get('account') or ''}"
                if re.search(r"tasia|discovery", ob, re.I) and org_key(other.get("account") or "") != ok:
                    related.add(other.get("account") or "")
        r["related_accounts"] = sorted({a for a in related if a})[:6]
        r["likely_related"] = len(r["related_accounts"]) > 0
        r["email_domain"] = d
        r["org_key"] = ok

    for r in contacts:
        r["score"] = score_row(r)
        r["best_paths"] = best_paths(r)
        r["whitespace_email"] = bool(
            (not r.get("email") or r.get("stale_email"))
            and (r.get("is_tier1") or r.get("form_url") or r.get("is_customer"))
        )

    lane_i = {l: n for n, l in enumerate(LANES)}

    def sk(r):
        return (
            lane_i.get(r.get("lane") or "", 99),
            -(r.get("score") or 0),
            0 if r.get("is_tier1") else 1,
            0 if r.get("has_email") else 1,
            (r.get("account") or "").lower(),
        )

    contacts.sort(key=sk)
    return contacts


def main():
    data = json.loads(IN.read_text())
    # live file uses "contacts" key
    contacts = list(data.get("contacts") or data.get("rows") or [])
    for r in contacts:
        r.setdefault("has_email", bool(r.get("email")))
        r.setdefault("has_phone", bool(r.get("phone")))
        r.setdefault("is_tier1", bool(r.get("is_tier1")))
        r.setdefault("form_url", r.get("form_url") or "")
        r.setdefault("next_action", r.get("next_action") or "")

    before = len(contacts)
    contacts = merge_fruit(contacts, fruit_rows_from_consumer())
    contacts = merge_fruit(contacts, fruit_rows_from_deputy())
    fruit_added = len(contacts) - before

    cmap = load_customer_map()
    paypal = load_paypal_names()
    contacts = enrich(contacts, cmap, paypal)

    lane_counts = Counter(r.get("lane") for r in contacts)
    lanes_meta = [
        {
            "id": lane,
            "contacts": lane_counts.get(lane, 0),
            "tier1": sum(1 for r in contacts if r.get("lane") == lane and r.get("is_tier1")),
            "with_email": sum(1 for r in contacts if r.get("lane") == lane and r.get("has_email")),
            "never_hit": sum(1 for r in contacts if r.get("lane") == lane and r.get("never_hit")),
            "customers": sum(1 for r in contacts if r.get("lane") == lane and r.get("is_customer")),
        }
        for lane in LANES
    ]

    seg_counts = Counter(r.get("segment") for r in contacts)
    segments_meta = list(data.get("segments") or [])
    seg_map = {s.get("id"): s for s in segments_meta if s.get("id")}
    for s, n in seg_counts.items():
        if s in seg_map:
            seg_map[s]["contacts"] = n
            seg_map[s]["tier1"] = sum(1 for r in contacts if r.get("segment") == s and r.get("is_tier1"))
            seg_map[s]["with_email"] = sum(1 for r in contacts if r.get("segment") == s and r.get("has_email"))
        else:
            segments_meta.append(
                {
                    "id": s,
                    "contacts": n,
                    "tier1": sum(1 for r in contacts if r.get("segment") == s and r.get("is_tier1")),
                    "with_email": sum(1 for r in contacts if r.get("segment") == s and r.get("has_email")),
                }
            )

    seeded = sum(1 for r in contacts if r.get("seed_note"))
    scores = sorted((r.get("score") or 0) for r in contacts)
    kpis = {
        "segments": len([s for s in segments_meta if (s.get("contacts") or 0) > 0]),
        "segments_listed": len(segments_meta),
        "lanes": len(LANES),
        "accounts": len({org_key(r.get("account") or "") for r in contacts}),
        "contacts": len(contacts),
        "with_email": sum(1 for r in contacts if r.get("has_email")),
        "with_phone": sum(1 for r in contacts if r.get("has_phone")),
        "with_named_contact": sum(1 for r in contacts if r.get("contact")),
        "tier1": sum(1 for r in contacts if r.get("is_tier1")),
        "tier1_with_email": sum(1 for r in contacts if r.get("is_tier1") and r.get("has_email")),
        "has_info": sum(1 for r in contacts if r.get("has_info") or r.get("has_email") or r.get("has_phone")),
        "customers_matchable": sum(1 for r in contacts if r.get("is_customer") or r.get("customer_match")),
        "never_hit": sum(1 for r in contacts if r.get("never_hit")),
        "with_seed_notes": seeded,
        "with_form": sum(1 for r in contacts if r.get("form_url")),
        "soft_form": sum(1 for r in contacts if r.get("form_quality") == "soft"),
        "stale_email": sum(1 for r in contacts if r.get("stale_email")),
        "messy_list": sum(1 for r in contacts if r.get("messy_list")),
        "whitespace_email": sum(1 for r in contacts if r.get("whitespace_email")),
        "likely_related": sum(1 for r in contacts if r.get("likely_related")),
        "top20_score_floor": scores[-20:][0] if len(scores) >= 20 else (scores[0] if scores else 0),
        "fruit_added": fruit_added,
        "patricia_tasia_seed": True,
        "gaps_zero_contacts": [],
    }

    payload = {
        "as_of": AS_OF,
        "product": "Sheehan Homestead / Critters on Call — BDR TAM Dialer v2",
        "version": 2,
        "rule": "Real emails/phones only — never invented. Default sort: score desc within lane.",
        "dedupe": data.get("dedupe") or "email → phone → org+name",
        "emba_note": (
            "EMBA on Call ladder (Michael stated targets, not proven metrics): "
            "free homestead shout · small-donation goat-statue farm tour · mini-zoo sponsor-in-name · "
            "bigger donations · consulting (BDR / convert old leads) for small biz + founder types. "
            "Stated close-rate targets: 80%+ qualified software; ~100% transactional/meeting if qualified."
        ),
        "kpis": kpis,
        "lanes": lanes_meta,
        "segments": segments_meta,
        "sources": data.get("sources") or [],
        "localStorage_keys": {
            "notes": "sheehan_bdr_v2_notes",
            "customers": "sheehan_bdr_v2_customers",
            "tags": "sheehan_bdr_v2_tags",
            "done": "sheehan_bdr_v2_done",
        },
        "compose_lanes": LANES,
        "contacts": contacts,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    print(
        json.dumps(
            {
                "wrote": str(OUT),
                "bytes": OUT.stat().st_size,
                "kpis": kpis,
                "lanes": [(l["id"], l["contacts"], l["never_hit"], l["customers"]) for l in lanes_meta],
                "seeded_rows": seeded,
                "patricia_seed_accounts": list(SEED_NOTES.keys()),
                "customer_map_keys": len(cmap),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
