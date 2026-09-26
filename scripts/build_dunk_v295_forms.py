#!/usr/bin/env python3
"""Board v2.9.5 — screened FORM seats (CAPTCHA-ok) for principal dunk."""
from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path("/workspace/sheehan-exec-suite")
BOARD_PATH = ROOT / "data" / "principal_dunk_board.json"
SUMMARY_PATH = ROOT / "data" / "_dunk_v295_summary.json"
ET = ZoneInfo("America/New_York")
AS_OF = datetime.now(ET).strftime("%-I:%M %p ET").replace(" 0", " ")  # fallback below
AS_OF = datetime.now(ET).strftime("%Y-%m-%d %-I:%M %p ET")

FORM_BLURB = (
    "Hi — Michael Sheehan with Sheehan Homestead / Critters on Call (Callahan / Jax metro). "
    "We bring a small mobile petting zoo, goat yoga, and farm STEM visits for family days, "
    "fall festivals, and member or resident events.\n\n"
    "If your activities / events team still has October–December windows open, happy to share "
    "dates and a simple one-pager. No pressure — just a local option.\n\n"
    "Michael · 914-263-1311 · Callahan, FL"
)

ANTHEM_NOTE = (
    "On Anthem Lakes: set Reason = Vendor / “I offer products/services,” then paste the blurb."
)

# Well-screened forms: verified load + form fields Sep 25 2026. Exclude Primrose / Laura-ABCC / Ross-only.
SCREENED = [
    {
        "id": "form-queens-harbour-invited",
        "account": "Queen's Harbour Yacht & Country Club (Invited)",
        "city": "Jacksonville",
        "area": "Metro Jax · East Arlington",
        "persona": "other",
        "segment": "Country club / private events",
        "title": "Membership / event inquiry form",
        "form_url": "https://www.invitedclubs.com/clubs/queen-s-harbour-yacht-country-club/contact-us",
        "website": "https://www.invitedclubs.com/clubs/queen-s-harbour-yacht-country-club",
        "why": "Club events · members + non-members welcome to book · CAPTCHA · ICP private club",
        "icp": "Private club event programming (family / member events)",
    },
    {
        "id": "form-san-jose-cc-membership",
        "account": "San Jose Country Club",
        "city": "Jacksonville",
        "area": "Metro Jax · San Jose",
        "persona": "other",
        "segment": "Country club",
        "title": "Membership inquiry · Family Events / Cubs Corner",
        "form_url": "https://www.sjccjax.com/membership",
        "website": "https://www.sjccjax.com/",
        "why": "Membership form with Family Events / Cubs Corner + comments · CAPTCHA · kids/family path",
        "icp": "Country club family / kids programming",
    },
    {
        "id": "form-deerwood-cc-contact",
        "account": "Deerwood Country Club",
        "city": "Jacksonville",
        "area": "Metro Jax · Deerwood",
        "persona": "other",
        "segment": "Country club",
        "title": "Contact Us form",
        "form_url": "https://www.deerwoodclub.com/contact",
        "website": "https://www.deerwoodclub.com/",
        "why": "Public Contact Us · ask Activities / Member Events · CAPTCHA",
        "icp": "Country club member events",
    },
    {
        "id": "form-marsh-landing-cc-membership",
        "account": "Marsh Landing Country Club",
        "city": "Ponte Vedra Beach",
        "area": "St. Johns · Ponte Vedra",
        "persona": "other",
        "segment": "Country club",
        "title": "Membership inquiry form",
        "form_url": "https://www.marshlandingcc.com/Membership",
        "website": "https://www.marshlandingcc.com/",
        "why": "Membership form · Comments field · route to member/family events",
        "icp": "PVB country club family events",
    },
    {
        "id": "form-jaxgcc-membership",
        "account": "Jacksonville Golf & Country Club",
        "city": "Jacksonville",
        "area": "Metro Jax · Southside",
        "persona": "other",
        "segment": "Country club",
        "title": "Membership Information Request",
        "form_url": "https://www.jaxgcc.com/Membership-Information-Request",
        "website": "https://www.jaxgcc.com/",
        "why": "Private Events / Kids' Activities interests + Comments · CAPTCHA · screened spare→kept",
        "icp": "Country club private events / kids activities",
    },
    {
        "id": "form-dune-house-rfp",
        "account": "Dune House Hotel & Spa (ex–One Ocean)",
        "city": "Atlantic Beach",
        "area": "Beaches · Atlantic Beach",
        "persona": "other",
        "segment": "Hotel / resort events",
        "title": "Group / event RFP",
        "form_url": "https://www.dunehousehotelandspa.com/events-groups/rfp/",
        "website": "https://www.dunehousehotelandspa.com/",
        "why": "RFP Gravity Form · entertainment vendor for guest/group events · CAPTCHA",
        "icp": "Beach resort group / guest entertainment",
    },
    {
        "id": "form-ponte-vedra-resorts-rfp",
        "account": "Ponte Vedra Beach Resorts (Inn & Club / Lodge & Club)",
        "city": "Ponte Vedra Beach",
        "area": "St. Johns · Ponte Vedra",
        "persona": "other",
        "segment": "Hotel / resort events",
        "title": "Plan Your Event / RFP",
        "form_url": "https://www.pontevedra.com/events/rfp",
        "website": "https://www.pontevedra.com/",
        "why": "Official special-events RFP webform · resort ICP",
        "icp": "Resort special-events sales",
    },
    {
        "id": "form-cypress-village-contact",
        "account": "Cypress Village",
        "city": "Jacksonville",
        "area": "Metro Jax · Southside",
        "persona": "senior",
        "segment": "Senior living IL / AL / memory",
        "title": "Contact · How can we help?",
        "form_url": "https://cypressvillageretirement.com/contact/",
        "website": "https://cypressvillageretirement.com/",
        "why": "Senior Gravity Form · ask Activities / Life Enrichment · CAPTCHA / Cloudflare",
        "icp": "Senior life enrichment",
    },
    {
        "id": "form-anthem-lakes-contact",
        "account": "Anthem Lakes Senior Living",
        "city": "Jacksonville",
        "area": "Beaches · Assisi Ln",
        "persona": "senior",
        "segment": "Senior AL / memory care",
        "title": "Contact · Reason=Vendor",
        "form_url": "https://anthemlakes.com/contact-us/",
        "website": "https://anthemlakes.com/",
        "why": "Contact form with Reason=Vendor — cleanest senior vendor path · CAPTCHA",
        "icp": "Senior vendor / life enrichment",
        "blurb_extra": ANTHEM_NOTE,
    },
    {
        "id": "form-first-coast-cms-contact",
        "account": "First Coast CMS",
        "city": "St. Johns",
        "area": "St. Johns · SilverLeaf peers",
        "persona": "cdd",
        "segment": "HOA / amenity management",
        "title": "Portfolio contact form",
        "form_url": "https://www.firstcoastcms.com/contact",
        "website": "https://www.firstcoastcms.com/",
        "why": "Non-Vesta amenity mgmt form · ask who owns Lifestyle / amenity events · CAPTCHA",
        "icp": "HOA / amenity programming (non-Vesta)",
    },
    {
        "id": "form-goddard-jax-baymeadows",
        "account": "The Goddard School Jacksonville — Baymeadows/Gate Pkwy",
        "city": "Jacksonville",
        "area": "Metro Jax · Baymeadows",
        "persona": "daycare",
        "segment": "Premium daycare",
        "title": "School info / special-need form",
        "form_url": "https://www.goddardschool.com/schools/fl/jacksonville/jacksonville-baymeadows/our-school/goddard-form",
        "website": "https://www.goddardschool.com/schools/fl/jacksonville/jacksonville-baymeadows",
        "why": "Director inquiry · special need field · CAPTCHA · Primrose-peer (not Primrose)",
        "icp": "Premium daycare family event",
    },
    {
        "id": "form-goddard-jax-spartina",
        "account": "The Goddard School Jacksonville — Spartina Ct",
        "city": "Jacksonville",
        "area": "Metro Jax · Southside",
        "persona": "daycare",
        "segment": "Premium daycare",
        "title": "School info form",
        "form_url": "https://www.goddardschool.com/schools/fl/jacksonville/jacksonville/our-school/goddard-form",
        "website": "https://www.goddardschool.com/schools/fl/jacksonville/jacksonville",
        "why": "2nd Jax Goddard campus · CAPTCHA · screened spare→kept",
        "icp": "Premium daycare family event",
    },
    {
        "id": "form-goddard-oakleaf",
        "account": "The Goddard School Orange Park — OakLeaf",
        "city": "Orange Park",
        "area": "Clay · OakLeaf",
        "persona": "daycare",
        "segment": "Premium daycare",
        "title": "School info form",
        "form_url": "https://www.goddardschool.com/schools/fl/orange-park/orange-park/our-school/goddard-form",
        "website": "https://www.goddardschool.com/schools/fl/orange-park/orange-park",
        "why": "Clay Goddard · CAPTCHA · re-verified Sep 25",
        "icp": "Premium daycare Clay",
    },
    {
        "id": "form-goddard-silverleaf",
        "account": "The Goddard School Silverleaf",
        "city": "St. Augustine",
        "area": "St. Johns · Silverleaf",
        "persona": "daycare",
        "segment": "Premium daycare",
        "title": "School info form",
        "form_url": "https://www.goddardschool.com/schools/fl/st-augustine/silverleaf/our-school/goddard-form",
        "website": "https://www.goddardschool.com/schools/fl/st-augustine/silverleaf",
        "why": "St. Johns Goddard · CAPTCHA · re-verified Sep 25",
        "icp": "Premium daycare St. Johns",
    },
    {
        "id": "form-goddard-cr210",
        "account": "The Goddard School St. Augustine — CR 210",
        "city": "St. Augustine",
        "area": "St. Johns · CR 210",
        "persona": "daycare",
        "segment": "Premium daycare",
        "title": "School info form",
        "form_url": "https://www.goddardschool.com/schools/fl/st-augustine/st-augustine-county-road-210/our-school/goddard-form",
        "website": "https://www.goddardschool.com/schools/fl/st-augustine/st-augustine-county-road-210",
        "why": "CR 210 Goddard · CAPTCHA · re-verified Sep 25",
        "icp": "Premium daycare St. Johns",
    },
    {
        "id": "form-blessed-trinity-contact",
        "account": "Blessed Trinity Catholic School",
        "city": "Jacksonville",
        "area": "Metro Jax",
        "persona": "school",
        "segment": "Indie / faith school",
        "title": "School contact form",
        "form_url": "https://www.blessedtrinitycatholicschool.org/contact",
        "website": "https://www.blessedtrinitycatholicschool.org/",
        "why": "Real school contact form (Name/Email/Message) · re-verified Sep 25",
        "icp": "Faith school festival / field visit",
    },
    {
        "id": "form-cathedral-parish-contact",
        "account": "Cathedral Parish School",
        "city": "St. Augustine",
        "area": "St. Johns · St. Augustine",
        "persona": "school",
        "segment": "Indie / faith school",
        "title": "School contact form",
        "form_url": "https://www.thecathedralparishschool.org/contact",
        "website": "https://www.thecathedralparishschool.org/",
        "why": "Real school contact form · re-verified Sep 25",
        "icp": "Faith school festival / field visit",
    },
    {
        "id": "form-beach-house-senior-contact",
        "account": "Beach House Senior Living",
        "city": "Jacksonville Beach",
        "area": "Beaches · Jax Beach",
        "persona": "senior",
        "segment": "Senior living",
        "title": "Contact Us form",
        "form_url": "https://www.beachhouseseniorliving.com/contact-us/",
        "website": "https://www.beachhouseseniorliving.com/",
        "why": "Life enrichment ask · CAPTCHA · senior ICP · re-verified Sep 25",
        "icp": "Senior life enrichment / beaches",
    },
    {
        "id": "form-aging-true-contact",
        "account": "Aging True",
        "city": "Jacksonville",
        "area": "Metro Jax",
        "persona": "senior",
        "segment": "Senior services / ADC network",
        "title": "Contact form",
        "form_url": "https://agingtrue.org/contact/",
        "website": "https://agingtrue.org/",
        "why": "Senior services / ADC network contact · CAPTCHA · re-verified Sep 25",
        "icp": "Senior services / adult day network",
    },
]

SKIPPED = [
    {"org": "Palagio Senior Living", "url": "https://palagioseniorliving.com/contact-us/", "why": "Form works but email already sent/suppress + Owe card — skip form dunk"},
    {"org": "Primrose (any)", "url": "", "why": "Explicit exclude"},
    {"org": "Atlantic Beach Country Club / Laura", "url": "", "why": "Explicit exclude"},
    {"org": "Atlantic Beach Elementary PTA", "url": "http://www.duvalschools.org/abe", "why": "School homepage / bot wall — not a contact form"},
    {"org": "Callahan Elementary School PTA", "url": "https://www.nassau.k12.fl.us/", "why": "District homepage — not a contact form"},
    {"org": "Chimney Lakes Elementary School PTA", "url": "http://www.duvalschools.org/cle", "why": "School homepage / bot wall — not a contact form"},
    {"org": "Amelia Island Montessori faculty-staff", "url": "https://www.ameliaislandmontessori.com/faculty-staff", "why": "Directory page — not a working contact form"},
    {"org": "Bolles whom-to-call (3 seats)", "url": "https://www.bolles.org/about-us/whom-to-call", "why": "Staff directory — not a contact form"},
    {"org": "Almost Home DayBreak", "url": "https://almosthomeseniorservices.com/contact/", "why": "HTTP 406 — form not usable this pass"},
    {"org": "Spark Pediatrics", "url": "https://www.sparkpediatrics.com/contact", "why": "No submit form fields in fetch"},
    {"org": "Bright Horizons Harvin Rd", "url": "enterprise center page", "why": "Enterprise schedule-visit path — weaker vendor ICP vs screened clubs/seniors/Goddard"},
    {"org": "Kiddie Academy / Learning Experience chain pages", "url": "", "why": "Tour/marketing pages — prefer screened Goddard + schools"},
    {"org": "Ross / Vesta email-only amenity paths", "url": "", "why": "Explicit exclude from FORM list (mailto lanes already cover peers)"},
]


def make_row(spec: dict) -> dict:
    blurb = FORM_BLURB
    if spec.get("blurb_extra"):
        blurb = blurb + "\n\n(" + spec["blurb_extra"] + ")"
    return {
        "id": spec["id"],
        "account": spec["account"],
        "contact": "",
        "title": spec["title"],
        "email": "",  # never invent; FORM open URL only
        "phone": "",
        "city": spec["city"],
        "segment": spec["segment"],
        "lane": "local_forms",
        "tier": "A",
        "website": spec.get("website") or "",
        "linkedin": "",
        "form_url": spec["form_url"],
        "kind": "form",
        "why": spec["why"],
        "persona": spec["persona"],
        "area": spec["area"],
        "chip_tags": ["FORM"],
        "form_labeled": True,
        "quick_email": False,
        "quick_body": blurb,
        "subject": "",
        "owe_reason": "",
        "role_chip": "FORM",
        "icp_note": spec.get("icp") or "",
        "screened_as_of": "2026-09-25",
    }


def main() -> None:
    board = json.loads(BOARD_PATH.read_text())
    old_lf = next(s for s in board["sections"] if s["id"] == "local_forms")
    old_ids = [r.get("id") for r in old_lf.get("rows") or []]
    old_accounts = [r.get("account") for r in old_lf.get("rows") or []]

    rows = [make_row(s) for s in SCREENED]
    old_lf["title"] = "FORM seats (screened)"
    old_lf["hint"] = (
        "Open URL · paste draft · CAPTCHA yourself · never auto-submit. "
        "Well-screened Jax ICP (club / resort / senior / HOA amenity / school / Goddard). "
        "No Primrose · no Laura/ABCC · no Ross-only. Labeled FORM — not fake mailto."
    )
    old_lf["rows"] = rows

    board["board_version"] = "Board v2.9.5 · Sep 25 · screened FORM seats (CAPTCHA-ok)"
    board["as_of"] = AS_OF
    board["compose_note"] = (
        (board.get("compose_note") or "")
        + " | v2.9.5: local_forms rebuilt — 19 screened FORM URLs with paste draft; "
        "dropped homepage/directory junk; exclude Primrose/Laura/Ross-only/Palagio-suppress."
    ).strip(" |")

    # recount local forms
    counts = board.setdefault("counts", {})
    counts["local_forms_optional"] = len(rows)
    counts["form_seats"] = len(rows)
    # mailto_total unchanged (forms have no email)
    form_only = sum(1 for s in board["sections"] for r in s.get("rows") or [] if r.get("form_url") and not r.get("email"))
    mailto_n = sum(1 for s in board["sections"] for r in s.get("rows") or [] if r.get("email"))
    counts["mailto_total"] = mailto_n
    counts["form_only_rows"] = form_only

    board["v295"] = {
        "as_of": AS_OF,
        "change": "Screened FORM seats (CAPTCHA-ok) — clubs/resorts/senior/HOA/school/Goddard",
        "form_seats": len(rows),
        "mailto_total": mailto_n,
        "form_only_rows": form_only,
        "excluded": ["Primrose", "Atlantic Beach CC / Laura", "Ross/Vesta email-only primary", "Palagio (suppress+owe)"],
        "source": "deputy-outreach/first-touch/11_CONTACT_FORMS.md + re-verify curl Sep 25",
        "prior_local_forms_count": len(old_ids),
        "dropped_prior_ids": [i for i in old_ids if i not in {r["id"] for r in rows}],
    }

    BOARD_PATH.write_text(json.dumps(board, indent=2) + "\n")

    summary = {
        "board_version": board["board_version"],
        "as_of": AS_OF,
        "form_seats": len(rows),
        "mailto_total": mailto_n,
        "form_only_rows": form_only,
        "forms_kept_or_added": [
            {"account": r["account"], "url": r["form_url"], "icp": r.get("icp_note"), "persona": r["persona"]}
            for r in rows
        ],
        "skipped_bad_screen": SKIPPED,
        "prior_local_forms_accounts": old_accounts,
        "live_urls": [
            "https://onchainoffgrid-hub.github.io/sheehan-exec-suite/principal-dunk.html?v=295",
            "https://onchainoffgrid-hub.github.io/critters-on-call/exec/principal-dunk.html?v=295",
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"ok": True, "form_seats": len(rows), "mailto": mailto_n, "as_of": AS_OF}, indent=2))


if __name__ == "__main__":
    main()
