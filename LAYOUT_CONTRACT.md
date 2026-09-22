# Exec suite layout contract (match this)

**Hub:** `/workspace/dashboard/exec-suite/index.html`  
**Money page (live v0):** `/workspace/dashboard/exec-suite/money-cfo.html`  
**Charter:** `/workspace/dashboard/exec-bots/02-exec-money-cfo.md`  
**Dump-home:** Dashboard Bit — specs land here; App Builder renders from these files.

## Visual tokens
```css
:root{
  --bg:#0b1220; --card:#121a2b; --line:#1e2a44;
  --text:#e8eefc; --muted:#93a0b8; --accent:#5b8cff;
  --good:#3dd68c; --warn:#ffb020; --bad:#ff5d6c; --violet:#a78bfa;
}
```
- Font: Inter / system-ui
- Cards: 14px radius, 1px `--line` border, 14px padding
- KPI grid: `repeat(auto-fit,minmax(160px,1fr))`
- KPI structure: `.l` label (uppercase muted) → `.v` value → `.s` sub
- Pill nav across all 12 pages (same order as hub); Money link `active` on money page
- North-star chip in header: **bookings** (even on Money — cash supports bookings)

## Money page panel order (v1)
1. KPI strip: Outside customer gross · Owner/internal (separated) · Paying customers · (optional) Fees · Net outside
2. Monthly table (PayPal H2): All-in / Owner / Outside / Outside net
3. Top payers table (outside only; never mix owner transfers into “revenue”)
4. Later: SKU margin (mobile zoo, birthdays, goat yoga, subscription) — only when tagged; else “unlabeled”
5. Later: Bookings→cash bridge + AR aging — **placeholder until Michael confirms bookings truth** (calendar / PayPal / HubSpot)

## Data files (prefer these over re-parsing blindly)
- `data/paypal_h2.json`, `paypal_kpis.json`, `paypal_monthly.json`, `paypal_customers.json`, `paypal_invoices.json`
- Source workbook: `/workspace/Sheehan-Homestead-PayPal-H2-2025.xlsx`

## Rules
- No Power BI login dependency — self-contained HTML + JSON
- Never invent $; label modeled vs actual
- Owner transfers ≠ customer revenue
- Keep curtain closed: one home = this suite path; don’t shuttle Build↔bots
