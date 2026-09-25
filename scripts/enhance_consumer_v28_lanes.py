#!/usr/bin/env python3
"""Classify consumer dunk cards into history lanes A–G + north-star ask. No invented history."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from collections import Counter

ROOT = Path("/workspace/sheehan-exec-suite")
DATA = ROOT / "data"
BOARD = DATA / "principal_dunk_board.json"
AS_OF = "2026-09-25 4:20 PM ET"
BOARD_VER = "Board v2.8 · Sep 25 4:20 ET"
NOW = datetime(2026, 9, 25)

B2B_SUFFIXES = (
    "rivercityscience.org", "sjcds.net", "jcds.com", "esj.org", "geds.net", "prov.org",
    "duvalschools.org", "stjohns.k12.fl.us", "clay.k12.fl.us", "nassau.k12.fl.us",
    "vestapropertyservices.com", "gmsnf.com", "maymgt.com",
)


def is_b2b(email: str) -> bool:
    el = (email or "").lower()
    if el.endswith(".edu"):
        return True
    return any(el.endswith(s) for s in B2B_SUFFIXES)


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:80] or "row"


def first_name(contact: str) -> str:
    c = (contact or "").strip()
    if not c:
        return ""
    skip = re.compile(r"^(dr\.?|mr\.?|mrs\.?|ms\.?|miss)$", re.I)
    for p in c.split():
        if not skip.match(p.replace(".", "")):
            return p.rstrip(",")
    return c.split()[0]


def parse_one_touch_history() -> dict[str, dict]:
    """email -> {signals, search, evidence} from one-touch-customers.html"""
    html = (ROOT / "one-touch-customers.html").read_text(encoding="utf-8", errors="ignore")
    rows = re.findall(r'data-email="([^"]+)"[^>]*data-search="([^"]*)"', html, re.I)
    out: dict[str, dict] = {}
    for email, search in rows:
        el = email.strip().lower()
        s = search.lower()
        sig = set()
        if re.search(r"\bbirthday\b|\bbday\b", s):
            sig.add("birthday")
        if re.search(r"\bmobile\b|mini pz|mini zoo|petting zoo", s):
            sig.add("mobile")
        if re.search(r"\bsummer\b", s):
            sig.add("summer")
        if re.search(r"homeschool", s):
            sig.add("homeschool")
        if re.search(r"\bvisit\b|farm tour|farm visit", s):
            sig.add("visit")
        out[el] = {
            "signals": sorted(sig),
            "search": search[:180],
            "source": "one-touch-customers.html",
        }
    return out


def parse_inbound_history() -> dict[str, dict]:
    with (DATA / "consumer_inbound.json").open() as f:
        ci = json.load(f)
    out: dict[str, dict] = {}
    for c in ci.get("contacts") or []:
        email = (c.get("email") or "").strip()
        if not email:
            continue
        el = email.lower()
        blob = json.dumps(c).lower()
        sig = set()
        if "birthday" in blob or "bday" in blob:
            sig.add("birthday")
        if "mobile" in blob or "mini pz" in blob or "mini zoo" in blob:
            sig.add("mobile")
        if c.get("bucket") == "summer_interest" or "summer" in blob:
            sig.add("summer")
        if "homeschool" in blob:
            sig.add("homeschool")
        if "visit" in blob or "farm" in blob:
            sig.add("visit")
        amt = c.get("amount")
        if amt is not None:
            try:
                if abs(float(amt) - 300) < 1 or abs(float(amt) - 40) < 1 and "homeschool" in blob:
                    if "homeschool" in blob:
                        sig.add("homeschool")
            except Exception:
                pass
        # $300 feeder often mentioned in detail
        if re.search(r"\$ ?300\b|300 inbound|homeschool monday", blob):
            sig.add("homeschool")
            sig.add("fee_300")
        out[el] = {
            "signals": sorted(sig),
            "bucket": c.get("bucket"),
            "detail": (c.get("detail") or "")[:160],
            "purchase_status": c.get("purchase_status"),
            "last_paid_or_booked": c.get("last_paid_or_booked"),
            "amount": c.get("amount"),
            "name": c.get("name"),
            "phone": c.get("phone"),
            "date": c.get("date"),
            "evidence": c.get("evidence") or [],
            "source": "consumer_inbound.json",
        }
    return out


def month_from_date(s) -> int | None:
    if not s:
        return None
    s = str(s)
    m = re.match(r"(\d{4})-(\d{2})", s)
    if m:
        return int(m.group(2))
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", s)
    if m:
        return int(m.group(1)) if int(m.group(1)) <= 12 else int(m.group(2))
    return None


def in_birthday_season(month: int | None) -> bool:
    """Sep 25 → anniversary window roughly Aug–Nov birthday bookings."""
    if month is None:
        return False  # cannot prove season
    return month in (8, 9, 10, 11)


def classify(email: str, bought: bool, review_status: str, ot: dict, ib: dict, last_paid) -> dict:
    """Return lane, north_star, why, evidence_note. Never invent history."""
    el = email.lower()
    sig = set((ot.get("signals") or [])) | set((ib.get("signals") or []))
    evidence_bits = []
    if ot.get("signals"):
        evidence_bits.append("one-touch:" + ",".join(ot["signals"]))
    if ib.get("signals"):
        evidence_bits.append("inbound:" + ",".join(ib["signals"]))
    if ib.get("bucket"):
        evidence_bits.append("bucket:" + ib["bucket"])
    evid = "; ".join(evidence_bits) if evidence_bits else "no typed history"

    # D) Reviewers
    if review_status == "likely_reviewed":
        return {
            "history_lane": "reviewers",
            "history_lane_label": "D · Reviewers",
            "north_star": "money",
            "north_star_label": "MONEY (soft) after thanks",
            "why": f"Already reviewed — thank-you + APP FIRST; soft next date or referral. Never ask review again. [{evid}]",
            "history_proven": True,
        }

    # G) Warm never booked
    if not bought:
        if ib.get("bucket") == "summer_interest" or "summer" in sig:
            return {
                "history_lane": "warm_inbound",
                "history_lane_label": "G · Warm inbound",
                "north_star": "money",
                "north_star_label": "MONEY · book CTA only",
                "why": f"Warm never booked (summer interest) — book anything. [{evid}]",
                "history_proven": True,
            }
        return {
            "history_lane": "warm_inbound",
            "history_lane_label": "G · Warm inbound",
            "north_star": "money",
            "north_star_label": "MONEY · book CTA only",
            "why": f"Warm inbound never booked — book CTA only. [{evid}]",
            "history_proven": bool(ib or ot),
        }

    # Bought paths — priority: mobile > birthday-season > summer > homeschool > booked-no-review > unknown-past
    lp_month = month_from_date(last_paid or ib.get("last_paid_or_booked"))

    if "mobile" in sig:
        return {
            "history_lane": "prior_mobile",
            "history_lane_label": "C · Prior mobile",
            "north_star": "money",
            "north_star_label": "MONEY · mobile rebook",
            "why": f"Proven prior mobile/mini PZ — mobile rebook (best money path). [{evid}]",
            "history_proven": True,
        }

    if "birthday" in sig and in_birthday_season(lp_month):
        return {
            "history_lane": "birthday_season",
            "history_lane_label": "A · Birthday-season",
            "north_star": "money",
            "north_star_label": "MONEY · birthday rebook",
            "why": f"Birthday history in season window (last≈month {lp_month}) — rebook birthday / same-season date. [{evid}]",
            "history_proven": True,
        }

    if "birthday" in sig and lp_month is None:
        # birthday proven but season not proven → still birthday lane with honest note, OR unknown-past
        # Michael: if can't prove season, Unknown-past. Birthday alone without season → Unknown-past with birthday hint in why
        return {
            "history_lane": "unknown_past",
            "history_lane_label": "Unknown-past",
            "north_star": "money",
            "north_star_label": "MONEY · generic rebook",
            "why": f"Birthday mentioned in history but season/date not proven — generic rebook (not fake anniversary). [{evid}]",
            "history_proven": False,
            "history_hint": "birthday",
        }

    if "birthday" in sig and not in_birthday_season(lp_month):
        return {
            "history_lane": "unknown_past",
            "history_lane_label": "Unknown-past",
            "north_star": "money",
            "north_star_label": "MONEY · generic rebook",
            "why": f"Birthday history outside current season window (month {lp_month}) — generic rebook. [{evid}]",
            "history_proven": False,
            "history_hint": "birthday",
        }

    if "summer" in sig or "visit" in sig or ib.get("bucket") == "summer_interest":
        return {
            "history_lane": "summer_cohort",
            "history_lane_label": "B · Summer cohort",
            "north_star": "money",
            "north_star_label": "MONEY · fall / ToT / visit",
            "why": f"Summer/visit cohort — ask fall date / ToT / farm visit / any next date. [{evid}]",
            "history_proven": True,
        }

    if "homeschool" in sig or "fee_300" in sig:
        return {
            "history_lane": "homeschool_300",
            "history_lane_label": "F · Homeschool / $300",
            "north_star": "money",
            "north_star_label": "MONEY (+ soft referral)",
            "why": f"Homeschool / feeder — book anything; soft who-else-programs referral. [{evid}]",
            "history_proven": True,
        }

    # E) Booked, no review
    if review_status in ("no_review_seen", "unknown"):
        # prefer book; barter only if no natural season/history — use barter as north_star when unknown-past-ish
        if not sig:
            return {
                "history_lane": "booked_no_review",
                "history_lane_label": "E · Booked, no review",
                "north_star": "barter",
                "north_star_label": "BARTER · soft review (or book)",
                "why": f"Booked customer · no review seen · no typed season history — soft next-date OR soft Google review/testimonial. Prefer book. [{evid}]",
                "history_proven": False,
            }
        return {
            "history_lane": "booked_no_review",
            "history_lane_label": "E · Booked, no review",
            "north_star": "money",
            "north_star_label": "MONEY · soft next-date",
            "why": f"Booked · no review seen — soft next-date (prefer book over review ask). [{evid}]",
            "history_proven": bool(sig),
        }

    return {
        "history_lane": "unknown_past",
        "history_lane_label": "Unknown-past",
        "north_star": "money",
        "north_star_label": "MONEY · generic rebook",
        "why": f"Past customer · history type unproven — generic rebook any date/SKU. [{evid}]",
        "history_proven": False,
    }


def mailto_fields(lane: str, north: str, contact: str, review_status: str) -> tuple[str, str]:
    fn = first_name(contact) or ""
    hi = f"Hi {fn}," if fn else "Hi there,"

    play = "https://onchainoffgrid-hub.github.io/critters-play/"
    wheel = "https://onchainoffgrid-hub.github.io/critters-on-call/wheel.html"
    services = "https://www.sheehanhomestead.com/services"
    sig = ""  # Gmail auto-signature; never double

    if lane == "reviewers" or review_status == "likely_reviewed":
        subj = "kids games from Sheehan Homestead"
        body = (
            f"{hi}\n\n"
            f"Thanks again for being part of the homestead — and for the Google love. "
            f"Dropping kids games as a thank-you (play + prize wheel). High score? Text HIGH SCORE to 914-263-1311.\n\n"
            f"Play: {play}\nWheel: {wheel}\nServices: {services}\n\n"
            f"If you want another date on the books (or know a school/co-op/church that programs animals), just reply.\n\n"
            f"{sig}"
        )
        return subj, body

    if lane == "prior_mobile":
        subj = "mobile petting zoo — another date?"
        body = (
            f"{hi}\n\n"
            f"Quick one — you had us mobile before. Want another mobile date this fall (weekday or Saturday)? "
            f"Happy to hold whatever SKU fits; mobile rebook is easy on our side.\n\n"
            f"{sig}"
        )
        return subj, body

    if lane == "birthday_season":
        subj = "birthday animals — same season?"
        body = (
            f"{hi}\n\n"
            f"Birthday season check-in — want the animals again around the same time of year? "
            f"We can hold a Saturday or weekday birthday window.\n\n"
            f"{sig}"
        )
        return subj, body

    if lane == "summer_cohort":
        subj = "fall date / trunk-or-treat / farm visit?"
        body = (
            f"{hi}\n\n"
            f"You came through over summer — want a fall date? Trunk-or-treat, farm visit, or any next date works. "
            f"Happy to hold what fits.\n\n"
            f"Services: {services}\n\n"
            f"{sig}"
        )
        return subj, body

    if lane == "homeschool_300":
        subj = "homestead date + who else programs?"
        body = (
            f"{hi}\n\n"
            f"Homeschool / feeder check-in — want another homestead date (any SKU)? "
            f"Also curious who else you know that programs animals (co-op, school, church).\n\n"
            f"{sig}"
        )
        return subj, body

    if lane == "warm_inbound":
        subj = "animals / homestead visit — book a date?"
        body = (
            f"{hi}\n\n"
            f"Following up on your interest — want to book a date? Mobile, farm visit, or party — whatever fits. "
            f"I can hold a Saturday or weekday.\n\n"
            f"Services: {services}\n\n"
            f"{sig}"
        )
        return subj, body

    if lane == "booked_no_review" and north == "barter":
        subj = "quick favor + next date?"
        body = (
            f"{hi}\n\n"
            f"Two soft asks: (1) want another date on the books this fall? "
            f"(2) if you’re willing, a short Google review or testimonial helps more families find us — no pressure.\n\n"
            f"Services: {services}\n\n"
            f"{sig}"
        )
        return subj, body

    if lane == "booked_no_review":
        subj = "Next date? (Sheehan Homestead)"
        body = (
            f"{hi}\n\n"
            f"Soft check — want another date this fall? Any SKU is fine; happy to hold a Saturday or weekday.\n\n"
            f"{sig}"
        )
        return subj, body

    # unknown_past
    subj = "Next date? (Sheehan Homestead)"
    body = (
        f"{hi}\n\n"
        f"Reaching back — want another homestead date on the books? Mobile, visit, or party — whatever fits. "
        f"Happy to share open dates.\n\n"
        f"{sig}"
    )
    return subj, body


def main():
    board = json.loads(BOARD.read_text())
    ot_map = parse_one_touch_history()
    ib_map = parse_inbound_history()
    grev = json.loads((DATA / "google_reviewers.json").read_text())
    scrape_ok = grev.get("status") == "ok" and bool(grev.get("reviewers"))

    with (DATA / "customers_no_next_date.json").open() as f:
        cn = json.load(f)
    with (DATA / "consumer_inbound.json").open() as f:
        ci = json.load(f)

    # Build customer universe (personal emails)
    customers: dict[str, dict] = {}
    for r in cn.get("rows") or []:
        email = (r.get("email") or "").strip()
        if not email or "@" not in email or is_b2b(email):
            continue
        el = email.lower()
        customers[el] = {
            "email": email,
            "name": r.get("account") or r.get("brand") or "",
            "phone": r.get("phone") or "",
            "last_paid": r.get("last_paid"),
            "purchase_status": "bought",
            "source": "customers_no_next_date",
        }
    for c in ci.get("contacts") or []:
        if c.get("purchase_status") != "bought":
            continue
        email = (c.get("email") or "").strip()
        if not email or is_b2b(email):
            continue
        el = email.lower()
        if el not in customers:
            customers[el] = {
                "email": email,
                "name": c.get("name") or "",
                "phone": c.get("phone") or "",
                "last_paid": c.get("last_paid_or_booked"),
                "purchase_status": "bought",
                "source": "consumer_inbound:bought",
                "amount": c.get("amount"),
            }
        else:
            if c.get("name") and (not customers[el]["name"] or "@" in str(customers[el]["name"])):
                customers[el]["name"] = c["name"]
            if c.get("phone") and not customers[el].get("phone"):
                customers[el]["phone"] = c["phone"]
            customers[el]["last_paid"] = customers[el].get("last_paid") or c.get("last_paid_or_booked")

    warm = []
    for c in ci.get("contacts") or []:
        if c.get("purchase_status") != "not_seen":
            continue
        email = (c.get("email") or "").strip()
        if not email or is_b2b(email):
            continue
        el = email.lower()
        if el in customers:
            continue
        warm.append(c)

    def warm_score(c):
        score = 0
        if c.get("phone"):
            score += 20
        if "2026" in str(c.get("date") or ""):
            score += 10
        if c.get("bucket") in ("godaddy", "summer_interest", "critter_club"):
            score += 5
        return score

    warm.sort(key=warm_score, reverse=True)
    warm = warm[:60]

    rows = []
    lane_counts = Counter()
    north_counts = Counter()

    for el, c in sorted(customers.items(), key=lambda x: str(x[1].get("last_paid") or ""), reverse=True):
        review_status = "unknown" if not scrape_ok else "no_review_seen"
        review_conf = "none"
        ot = ot_map.get(el) or {}
        ib = ib_map.get(el) or {}
        cls = classify(el, True, review_status, ot, ib, c.get("last_paid"))
        name = c["name"]
        contact = name if name and "@" not in name else ""
        account = name or el.split("@")[0]
        subj, body = mailto_fields(cls["history_lane"], cls["north_star"], contact or account, review_status)
        # Tier
        tier = "A"
        last = str(c.get("last_paid") or "")
        if cls["history_lane"] in ("prior_mobile", "birthday_season", "reviewers") or (last.startswith("2026")):
            tier = "S"
        elif not last:
            tier = "B"
        lane_counts[cls["history_lane"]] += 1
        north_counts[cls["north_star"]] += 1
        rows.append({
            "phone": c.get("phone") or "",
            "city": "",
            "segment": "Consumer",
            "persona": "consumer",
            "kind": "mailto",
            "lane": "consumer",
            "tier": tier,
            "id": f"cons-cust-{slug(el)}",
            "account": account,
            "contact": contact,
            "title": cls["history_lane_label"],
            "email": c["email"],
            "website": "https://www.sheehanhomestead.com/services",
            "subject": subj,
            "why": cls["why"],
            "owe_reason": cls["north_star_label"],
            "form_url": "",
            "area": "Metro Jax · Consumer",
            "role_chip": "Customer",
            "fancy": False,
            "rcsa": False,
            "chip_tags": ["Consumer", cls["history_lane_label"].split("·")[-1].strip()],
            "quick_body": body,
            "quick_email": True,
            "consumer_lane": "customers",
            "purchase_status": "bought",
            "review_status": review_status,
            "review_match_confidence": review_conf,
            "history_lane": cls["history_lane"],
            "history_lane_label": cls["history_lane_label"],
            "north_star": cls["north_star"],
            "north_star_label": cls["north_star_label"],
            "history_proven": cls.get("history_proven", False),
        })

    for c in warm:
        email = c["email"].strip()
        el = email.lower()
        review_status = "unknown"
        ot = ot_map.get(el) or {}
        ib = ib_map.get(el) or {
            "signals": [],
            "bucket": c.get("bucket"),
            "detail": c.get("detail"),
            "purchase_status": "not_seen",
        }
        # ensure bucket on ib
        ib = dict(ib)
        ib.setdefault("bucket", c.get("bucket"))
        cls = classify(el, False, review_status, ot, ib, None)
        name = c.get("name") or ""
        subj, body = mailto_fields(cls["history_lane"], cls["north_star"], name, review_status)
        lane_counts[cls["history_lane"]] += 1
        north_counts[cls["north_star"]] += 1
        rows.append({
            "phone": c.get("phone") or "",
            "city": "",
            "segment": "Consumer",
            "persona": "consumer",
            "kind": "mailto",
            "lane": "consumer",
            "tier": "A" if c.get("phone") else "B",
            "id": f"cons-warm-{slug(el)}",
            "account": name or el.split("@")[0],
            "contact": name,
            "title": cls["history_lane_label"],
            "email": email,
            "website": "https://www.sheehanhomestead.com/services",
            "subject": subj,
            "why": cls["why"],
            "owe_reason": cls["north_star_label"],
            "form_url": "",
            "area": "Metro Jax · Consumer",
            "role_chip": "Warm",
            "fancy": False,
            "rcsa": False,
            "chip_tags": ["Consumer", "Warm"],
            "quick_body": body,
            "quick_email": True,
            "consumer_lane": "warm_inbound",
            "purchase_status": "not_seen",
            "review_status": review_status,
            "review_match_confidence": "none",
            "history_lane": cls["history_lane"],
            "history_lane_label": cls["history_lane_label"],
            "north_star": cls["north_star"],
            "north_star_label": cls["north_star_label"],
            "history_proven": cls.get("history_proven", False),
        })

    # replace consumer section
    for s in board["sections"]:
        if s.get("id") == "consumer":
            s["title"] = "Consumer · history lanes + one ask"
            s["hint"] = (
                "ONE primary ask per card: MONEY (rebook) · LEAD (referral) · BARTER (review/testimonial). "
                "Lanes A–G from proven history only; Unknown-past = generic rebook. "
                "Reviewers → APP FIRST thanks — never re-ask review. Google scrape gap → review_status unknown."
            )
            s["rows"] = rows
            break

    cust_n = sum(1 for r in rows if r["consumer_lane"] == "customers")
    warm_n = sum(1 for r in rows if r["consumer_lane"] == "warm_inbound")
    board["counts"]["consumer"] = len(rows)
    board["counts"]["consumer_customers"] = cust_n
    board["counts"]["consumer_warm"] = warm_n
    board["counts"]["consumer_unknown"] = sum(1 for r in rows if r.get("review_status") == "unknown")
    board["counts"]["consumer_lanes"] = dict(lane_counts)
    board["counts"]["consumer_north_star"] = dict(north_counts)
    board["counts"]["by_persona"]["consumer"] = len(rows)
    mailto = sum(1 for s in board["sections"] for r in s.get("rows") or [] if r.get("email"))
    board["counts"]["mailto_total"] = mailto

    board["as_of"] = AS_OF
    board["board_version"] = BOARD_VER
    board["label"] = "Principal dunk board v2.8 — RCSA + Fancy + Consumer history lanes"
    board["rule"] = (
        "Compose-only. B2B = v2.7 Michael school/CDD voice. "
        "Consumer = one north-star ask (MONEY / LEAD / BARTER) by history lane A–G. "
        "Reviewers = APP-FIRST thanks, never re-ask review. "
        "Unknown-past = generic rebook — never invent birthday/summer/mobile. "
        "Done key sheehan_principal_dunk_done_v2 · Notes sheehan_dunk_notes_v1."
    )
    board.setdefault("v28", {})
    board["v28"]["consumer"] = {
        "customers": cust_n,
        "warm": warm_n,
        "likely_reviewed": 0,
        "no_review": 0,
        "unknown": len(rows),
        "scrape_ok": scrape_ok,
        "lanes": dict(lane_counts),
        "north_star": dict(north_counts),
        "one_touch_history_emails": len(ot_map),
    }

    BOARD.write_text(json.dumps(board, indent=2, ensure_ascii=False) + "\n")
    summary = {
        "as_of": AS_OF,
        "board_version": BOARD_VER,
        "lanes": dict(lane_counts),
        "north_star": dict(north_counts),
        "customers": cust_n,
        "warm": warm_n,
        "one_touch_indexed": len(ot_map),
    }
    (DATA / "_dunk_v28_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
