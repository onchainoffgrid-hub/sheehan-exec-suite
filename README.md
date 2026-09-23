# Sheehan Homestead — Executive Dashboard Suite

**Path:** `/workspace/dashboard/exec-suite/`  
**Owner dump-home:** Dashboard Bit  
**Theme:** Dark ops BI · self-contained HTML+JS+CSS · Chart.js CDN · no Power BI  
**Built:** 2026-09-22 (America/New_York) · BDR TAM all-segment dialer live

Open `index.html` in a browser (`file://` works — data is embedded) or:

```bash
cd /workspace/dashboard/exec-suite && python3 -m http.server 8765
```

## Pages

| Page | File | Data posture |
|---|---|---|
| Executive Hub | [index.html](index.html) | KPI strip + links to all domains |
| Consumer Inbound (Violet/B2C) | [consumer-inbound.html](consumer-inbound.html) | Interest **34** · GoDaddy pass **27** · waivers **GAP** · **4** forms missing sheets |
| Bookings & Dates | [bookings-dates.html](bookings-dates.html) | Fall priority **129** real rows; $ booked **PLACEHOLDER** |
| Money (CFO) | [money-cfo.html](money-cfo.html) | PayPal H2 **outside $15,408.66** · 42 customers · owner $4,254 separated |
| BDR TAM Dialer v2 | [bdr-tam.html](bdr-tam.html) | **Enterprise · Sponsor · Subscription · Violet · Small Biz · EMBA · Hail Mary** · Hail filters: Inspired · God-connected · Local celeb · Philanthropist · Local biz-sponsor · Bazillionaires · same GTM offers · `data/hail_mary.json` |
| BDR Enterprise v1 | [bdr-pipeline.html](bdr-pipeline.html) | **REAL** CALL_NOW 138 · Warm 81 · Needs 140 · Later 11 · Red-tape 44 + filterable dialer |
| RevOps TAM | [revops-tam.html](revops-tam.html) | Primary SAM **$572,873** · tier rollup · segment counts |
| Social & Reach | [social-reach.html](social-reach.html) |
| Jax Local Buzz | [jax-local-buzz.html](jax-local-buzz.html) | BDR table **24** outlets · sortable email/outlet · preloaded pitches · `data/jax_local_buzz.json` |
| Investor Home | [investor-home.html](investor-home.html) | Frame spine + traction / capital / GTM tiles |
| Investor Checklist | [investor-checklist.html](investor-checklist.html) | **Seed / pre-seed readiness** — Assets · Proof · Founder · Co-founder · Ops · Have/Need localStorage |
| Investor & Capital | [investor-capital.html](investor-capital.html) | Goals $250k bookings / ~$100k AR by 2026-12-23 · nested under checklist |
| Programming | [programming.html](programming.html) | Visit Us program types · fill vs protect stub heat |
| Team & Hire | [team-hire.html](team-hire.html) | 4 seats from HIRE_PRIORITIES (enterprise live) |
| Actions & Overdue | [actions-overdue.html](actions-overdue.html) | **84** actions from Michael_Overdue_Action_Tracker.xlsx |
| Collateral Coverage | [collateral.html](collateral.html) | Segment × asset coverage matrix (file-scan) |
| Ann-Marie Ops | [ann-marie-ops.html](ann-marie-ops.html) | Delegation scorecard **stub** |
| Platform Map | [platform-map.html](platform-map.html) | Bot / source / panel priority map |

## Data folder

JSON exports under [`data/`](data/) for offline refresh:

- `enterprise_call_now.json`, `enterprise_warm.json`, `enterprise_red_tape.json`, `enterprise_dialer.json`, `enterprise_kpis.json`
- `bdr_tam_dialer.json` (unified all-segment dialer — Tier1 + email sort)
- `bdr_primary_dialer.json` (CALL_NOW + WARM + RED_TAPE for the BDR page)
- `fall_priority.json`, `fall_kpis.json`
- `paypal_*.json` (from Sheehan-Homestead-PayPal-H2-2025.xlsx)
- `overdue_actions.json`, `overdue_kpis.json`
- `revops_kpis.json`, `suite_kpis.json`
- `consumer_inbound.json` (Summer Scholars · GoDaddy · waivers GAP · forms missing sheets)

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

## Flow spine (Ops → Sales → Investors)

Shared top rail: `shared/flow-spine.js` on Operator, Sales, and Investor pages.

- **Operations** → `index.html` (money / bookings / actions / Ann-Marie)
- **Sales** subchips: BDR TAM · Big Enterprise · Sponsor · Violet · Subscription · Hail Mary
- **Investors** → `investor-checklist.html` (Seed / pre-seed: Assets · Proof · Founder · Co-founder · Ops) · `investor-home.html` · capital nested · Sales proof (bookings/money)

Inject/refresh: `python3 scripts/inject_flow_spine.py`

## Layout

See [LAYOUT_CONTRACT.md](LAYOUT_CONTRACT.md) for shared visual tokens and Money panel order.

## Public

- GitHub: https://github.com/onchainoffgrid-hub/sheehan-exec-suite
- Pages: https://onchainoffgrid-hub.github.io/sheehan-exec-suite/
- Consumer: https://onchainoffgrid-hub.github.io/sheehan-exec-suite/consumer-inbound.html
- BDR TAM: https://onchainoffgrid-hub.github.io/sheehan-exec-suite/bdr-tam.html
- Hail Mary (TAM lane): https://onchainoffgrid-hub.github.io/sheehan-exec-suite/bdr-tam.html?lane=Hail%20Mary
- Bazillionaires filter: https://onchainoffgrid-hub.github.io/sheehan-exec-suite/bdr-tam.html?lane=Hail%20Mary&hail=Bazillionaires
- Easy Attack (mass-touch): https://onchainoffgrid-hub.github.io/sheehan-exec-suite/easy-attack.html
- Sell catalog: Franchise + Consulting LIVE; gray = not ready · `data/sell_catalog.json` · mass plays `data/mass_touch_ideas.json` (no HubSpot)
- Jax Buzz: https://onchainoffgrid-hub.github.io/sheehan-exec-suite/jax-local-buzz.html


### BDR TAM v2 rebuild

```bash
cd /workspace/dashboard/exec-suite && python3 scripts/build_bdr_tam_dialer.py && python3 scripts/enrich_bdr_tam_v2.py
```

localStorage keys: `sheehan_bdr_v2_notes`, `sheehan_bdr_v2_customers`, `sheehan_bdr_v2_tags`, `sheehan_bdr_v2_done`.

## Investor readiness

- Checklist: https://onchainoffgrid-hub.github.io/sheehan-exec-suite/investor-checklist.html
- Data: `data/investor_readiness.json` · localStorage `sheehan_investor_readiness`
- Critters mirror: https://onchainoffgrid-hub.github.io/critters-on-call/exec/investor-checklist.html
