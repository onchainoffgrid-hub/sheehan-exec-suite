#!/usr/bin/env python3
"""Inject shared/flow-spine.js + data-flow-face/chip on suite pages."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("/workspace/dashboard/exec-suite")

# page -> (face, chip)
PAGES = {
    "index.html": ("ops", ""),
    "ann-marie-ops.html": ("ops", ""),
    "money-cfo.html": ("ops", ""),
    "bookings-dates.html": ("ops", ""),
    "actions-overdue.html": ("ops", ""),
    "bdr-tam.html": ("sales", "bdr-tam"),
    "bdr-pipeline.html": ("sales", "big-enterprise"),
    "crm-icp.html": ("sales", "subscription"),
    "consumer-inbound.html": ("sales", "violet"),
    "org-whitespace.html": ("sales", ""),
    "catalogue-close.html": ("sales", ""),
    "hail-mary.html": ("sales", "hail-mary"),
    "easy-attack.html": ("sales", "easy-attack"),
    "investor-home.html": ("investor", "home"),
    "investor-checklist.html": ("investor", "checklist"),
    "investor-capital.html": ("investor", "capital"),
    "macro-radar.html": ("investor", ""),
}

SCRIPT_TAG = '<script src="shared/flow-spine.js" defer></script>'


def patch(path: Path, face: str, chip: str) -> str:
    text = path.read_text(encoding="utf-8")
    orig = text

    # body data attributes
    def body_repl(m):
        tag = m.group(0)
        # strip existing data-flow-*
        tag = re.sub(r'\s+data-flow-face="[^"]*"', "", tag)
        tag = re.sub(r'\s+data-flow-chip="[^"]*"', "", tag)
        attrs = f' data-flow-face="{face}"'
        if chip:
            attrs += f' data-flow-chip="{chip}"'
        if tag.endswith(">"):
            return tag[:-1] + attrs + ">"
        return tag + attrs

    if re.search(r"<body\b[^>]*>", text, re.I):
        text = re.sub(r"<body\b[^>]*>", body_repl, text, count=1, flags=re.I)
    else:
        return "no-body"

    # ensure script once before </body>
    text = re.sub(
        r'\s*<script[^>]*src=["\']shared/flow-spine\.js["\'][^>]*>\s*</script>\s*',
        "\n",
        text,
        flags=re.I,
    )
    if re.search(r"</body>", text, re.I):
        text = re.sub(
            r"</body>",
            SCRIPT_TAG + "\n</body>",
            text,
            count=1,
            flags=re.I,
        )
    else:
        text += "\n" + SCRIPT_TAG + "\n"

    if text == orig:
        return "unchanged"
    path.write_text(text, encoding="utf-8")
    return "updated"


def main():
    results = []
    for name, (face, chip) in PAGES.items():
        p = ROOT / name
        if not p.exists():
            results.append((name, "missing"))
            continue
        results.append((name, patch(p, face, chip), face, chip))
    for row in results:
        print(row)


if __name__ == "__main__":
    main()
