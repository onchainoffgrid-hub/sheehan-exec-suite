# Sheehan Homestead — Executive Dashboard Suite

**Path:** `/workspace/dashboard/exec-suite/`  
**Owner dump-home:** Dashboard Bit  
**Theme:** Dark ops BI · self-contained HTML+JS+CSS · Chart.js CDN · no Power BI  
**Built:** 2026-09-19 (America/New_York)

Open `index.html` in a browser (`file://` works — data is embedded) or:

```bash
cd /workspace/dashboard/exec-suite && python3 -m http.server 8765
```

## Pages

| Page | File | Data posture |
|---|---|---|
| Executive Hub | [index.html](index.html) | KPI strip + links to all domains |
| Bookings & Dates | [bookings-dates.html](bookings-dates.html) | Fall priority **129** real rows; $ booked **PLACEHOLDER** |
| Money (CFO) | [money-cfo.html](money-cfo.html) | PayPal H2 **outside $15,408.66** · 42 customers · owner $4,254 separated |
| BDR Pipeline | [bdr-pipeline.html](bdr-pipeline.html) | **REAL** CALL_NOW 138 · Warm 81 · Needs 140 · Later 11 · Red-tape 44 + filterable dialer |
| RevOps TAM | [revops-tam.html](revops-tam.html) | Primary SAM **$572,873** · tier rollup · segment counts |
| Social & Reach | [social-reach.html](social-reach.html) | FB ~4.8k · LI ~13k · met ~500k / ~400 emails + weekly localStorage inputs |
| Investor & Capital | [investor-capital.html](investor-capital.html) | Goals $250k bookings / ~$100k AR by 2026-12-23 |
| Programming | [programming.html](programming.html) | Visit Us program types · fill vs protect stub heat |
| Team & Hire | [team-hire.html](team-hire.html) | 4 seats from HIRE_PRIORITIES (enterprise live) |
| Actions & Overdue | [actions-overdue.html](actions-overdue.html) | **84** actions from Michael_Overdue_Action_Tracker.xlsx |
| Collateral Coverage | [collateral.html](collateral.html) | Segment × asset coverage matrix (file-scan) |
| Ann-Marie Ops | [ann-marie-ops.html](ann-marie-ops.html) | Delegation scorecard **stub** |
| Platform Map | [platform-map.html](platform-map.html) | Bot / source / panel priority map |

## Data folder

JSON exports under [`data/`](data/) for offline refresh:

- `enterprise_call_now.json`, `enterprise_warm.json`, `enterprise_red_tape.json`, `enterprise_dialer.json`, `enterprise_kpis.json`
- `bdr_primary_dialer.json` (CALL_NOW + WARM + RED_TAPE for the BDR page)
- `fall_priority.json`, `fall_kpis.json`
- `paypal_*.json` (from Sheehan-Homestead-PayPal-H2-2025.xlsx)
- `overdue_actions.json`, `overdue_kpis.json`
- `revops_kpis.json`, `suite_kpis.json`

## Specs aligned

- `/workspace/dashboard/BDR-Enterprise-v1-SPEC.md`
- `/workspace/revops/dashboard_schema.md`
- `/workspace/dashboard/exec-bots/MASTER.md`
- `/workspace/bdr/HIRE_PRIORITIES.md`

## Rules

- No invented contact emails/phones — blanks stay blank.
- Red-tape accounts are hold-only (not dial targets).
- Bookings $ remains explicitly PLACEHOLDER until Michael confirms truth source.
- Detail sheets (VESTA_ROSS, GOLF, LUXURY, CORP_FIELD_HR) are subsets of CALL_NOW/WARM — not double-counted in BDR KPIs.

## Layout

See [LAYOUT_CONTRACT.md](LAYOUT_CONTRACT.md) for shared visual tokens and Money panel order.
