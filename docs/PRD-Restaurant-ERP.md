# Product Requirements Document (PRD)
# Restaurant ERP Platform — "Tavola OS" (working name)

| Field | Value |
|---|---|
| Document version | 1.0 |
| Status | Draft for review |
| Date | 2026-11-11 |
| Product type | Cloud-native, AI-first Restaurant ERP (SaaS) |
| Target segments | Single restaurants, multi-unit groups, franchises, cloud/ghost kitchens, cafés, QSR, fine dining, hotel F&B, catering |
| Audience | Founders, Product, Engineering, Design, QA, Sales, Customer Success, Investors |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Vision, Mission & Strategic Goals](#2-vision-mission--strategic-goals)
3. [Market Analysis & Competitive Positioning](#3-market-analysis--competitive-positioning)
4. [Target Users & Personas](#4-target-users--personas)
5. [Product Scope](#5-product-scope)
6. [System Overview & Module Map](#6-system-overview--module-map)
7. [Functional Requirements by Module](#7-functional-requirements-by-module)
   - 7.1 Point of Sale (POS)
   - 7.2 Order Management & Omnichannel Hub
   - 7.3 Kitchen Display System (KDS) & Production
   - 7.4 Table, Floor & Reservation Management
   - 7.5 Menu & Recipe Engineering
   - 7.6 Inventory & Warehouse Management
   - 7.7 Procurement & Supplier Management
   - 7.8 Central Kitchen & Commissary
   - 7.9 Finance & Accounting
   - 7.10 Payments & Cash Management
   - 7.11 HR, Workforce & Payroll
   - 7.12 CRM, Loyalty & Marketing
   - 7.13 Self-Service: QR, Kiosk, Web & Mobile Ordering
   - 7.14 Delivery & Logistics
   - 7.15 Multi-Location, Franchise & Head Office
   - 7.16 Business Intelligence & Analytics
   - 7.17 AI & Intelligent Automation Layer
   - 7.18 Food Safety, Quality & Compliance
   - 7.19 Maintenance & Asset Management
   - 7.20 Platform Administration, Security & Identity
   - 7.21 Integrations Marketplace & Open API
8. [Non-Functional Requirements](#8-non-functional-requirements)
9. [Technical Architecture](#9-technical-architecture)
10. [Core Data Model](#10-core-data-model)
11. [Key End-to-End Workflows](#11-key-end-to-end-workflows)
12. [UX & Design Principles](#12-ux--design-principles)
13. [Success Metrics & KPIs](#13-success-metrics--kpis)
14. [Release Plan & Roadmap](#14-release-plan--roadmap)
15. [Pricing & Packaging](#15-pricing--packaging)
16. [Go-to-Market Strategy for Market Leadership](#16-go-to-market-strategy-for-market-leadership)
17. [Risks, Assumptions & Dependencies](#17-risks-assumptions--dependencies)
18. [Acceptance Criteria & Quality Gates](#18-acceptance-criteria--quality-gates)
19. [Glossary](#19-glossary)
20. [Appendix: Requirement Traceability Conventions](#20-appendix-requirement-traceability-conventions)

---

## 1. Executive Summary

Restaurants operate on 3–10% net margins while juggling a fragmented stack: one tool for POS, another for inventory, spreadsheets for costing, a separate payroll provider, three delivery tablets on the counter, and an accountant reconciling everything at month-end. The result is food waste, labor overspend, theft, slow decisions, and no single source of truth.

**Tavola OS** is a unified, cloud-native, **AI-first Restaurant ERP** that connects front-of-house, back-of-house, and head-office in one real-time platform. It covers the full restaurant lifecycle — from the guest's first click to the supplier's last invoice — and adds an intelligence layer that **predicts demand, auto-orders stock, schedules staff, prices menus, and flags fraud** before it costs money.

**Core value proposition**

| For | Outcome |
|---|---|
| Owners / CFOs | +3–6 points of margin via lower food cost, labor cost and waste; real-time P&L per outlet |
| Operations managers | One dashboard for all outlets; automated compliance; exception-based management |
| Chefs / kitchen | Recipe-driven production, prep lists, smart KDS routing, waste tracking |
| Front-of-house | Fast offline-capable POS, table/reservation management, integrated payments |
| Guests | Seamless ordering across dine-in, QR, kiosk, app, web and delivery; personalized loyalty |
| Franchisors | Brand control, royalty automation, benchmarking across franchisees |

**Strategic differentiators to become market leader**

1. **One platform, one database** — POS + ERP + CRM + HR + Accounting natively unified (not stitched by integrations).
2. **AI Co-Pilot ("Chef Brain")** — forecasting, auto-replenishment, dynamic scheduling, menu engineering, anomaly detection, and natural-language analytics.
3. **Offline-first resilience** — POS, KDS and payments keep running with zero internet; automatic conflict-free sync.
4. **Enterprise-grade, SMB-simple** — 30-minute onboarding for a single café; scales to 5,000+ outlets.
5. **Global-ready** — multi-currency, multi-language (incl. RTL Arabic/Hebrew), multi-tax regimes, e-invoicing compliance (e.g., ZATCA, GST, VAT, fiscal printers).
6. **Open ecosystem** — public API, webhooks, and an app marketplace.

---

## 2. Vision, Mission & Strategic Goals

### 2.1 Vision
To be the **operating system for every restaurant in the world** — the platform that makes running a profitable food business predictable.

### 2.2 Mission
Give every restaurant, from a single food truck to a global chain, enterprise-grade intelligence and control with consumer-grade simplicity.

### 2.3 Strategic Goals (36 months)

| # | Goal | Measure |
|---|---|---|
| G1 | Market leadership in target regions | #1 or #2 by active outlets in 3 launch markets |
| G2 | Proven customer ROI | Average customer improves food-cost % by ≥2 pts and labor % by ≥1.5 pts within 6 months |
| G3 | Best-in-class reliability | 99.95% cloud uptime; 100% POS availability via offline mode |
| G4 | Fastest time-to-value | Median time from sign-up to first live sale < 1 day (SMB), < 30 days (enterprise) |
| G5 | Customer love | NPS ≥ 60, logo churn < 1% per month (SMB), < 5% per year (enterprise) |
| G6 | Platform ecosystem | 150+ integrations, 50+ third-party marketplace apps |
| G7 | Sustainable growth | Net Revenue Retention ≥ 120% |

---

## 3. Market Analysis & Competitive Positioning

### 3.1 Market Problems

| Problem | Impact |
|---|---|
| Fragmented tools (POS ≠ inventory ≠ accounting ≠ HR) | Duplicate data entry, reconciliation errors, no real-time profitability |
| Food cost leakage (waste, over-portioning, theft, price creep) | 4–10% of revenue lost |
| Labor scheduling by gut feel | Over/under-staffing; labor typically 25–35% of revenue |
| Delivery aggregator chaos | Multiple tablets, missed orders, manual menu updates, opaque commissions |
| Poor visibility for multi-unit operators | Decisions made on week-old spreadsheets |
| Legacy on-premise systems | Expensive hardware, no remote access, painful upgrades |
| Compliance burden | Tax e-invoicing, food safety (HACCP), labor laws vary by country |

### 3.2 Competitive Landscape (category level)

| Category | Typical strengths | Typical gaps we exploit |
|---|---|---|
| Cloud POS-first vendors | Great POS UX, payments | Shallow inventory/recipe costing, weak accounting, limited AI |
| Back-office / inventory specialists | Deep costing & procurement | Requires separate POS; integration lag |
| Generic ERPs adapted for F&B | Strong finance | Poor FOH UX, slow, expensive implementation |
| Legacy on-prem hospitality systems | Enterprise footprint | Outdated UX, no cloud/mobile, costly upgrades |
| Local/regional POS players | Local tax compliance, price | Limited scalability, no multi-country, weak analytics |

### 3.3 Positioning Statement
> For restaurant operators who need to grow profitably, **Tavola OS** is the AI-first restaurant ERP that unifies every operation — POS to P&L — in one real-time platform. Unlike POS-first systems or generic ERPs, Tavola OS is built natively for food businesses and **tells you what to do next**, not just what happened.

### 3.4 Winning Differentiators (Moats)

| Moat | Description |
|---|---|
| Data network effect | Anonymized cross-customer benchmarks ("your burger cost is 12% above peers in your city") |
| AI depth | Forecasts trained on POS + weather + events + holidays + local trends |
| Switching cost via unification | Once POS, inventory, HR and accounting are in one system, replacing it is hard |
| Ecosystem | Marketplace apps and supplier network embedded in procurement |
| Embedded fintech | Payments, instant payouts, working-capital loans, supplier financing |

---

## 4. Target Users & Personas

| Persona | Role | Goals | Pain points | Key modules |
|---|---|---|---|---|
| **Omar — Owner/Operator** | Owns 1–3 outlets | Profit, control, less admin | No time, unclear numbers | Dashboard, P&L, AI insights, mobile app |
| **Sara — Multi-unit Ops Director** | Runs 20–200 outlets | Consistency, efficiency, growth | Inconsistent execution, slow reporting | Head office, benchmarking, audits, BI |
| **Chef Marco — Executive Chef** | Kitchen leader | Quality, consistency, cost control | Recipe drift, waste, stock-outs | Recipes, KDS, prep, inventory, waste |
| **Lina — Restaurant Manager** | Daily operations | Smooth service, staff coverage | Scheduling, cash discrepancies | Scheduling, POS admin, cash, tasks |
| **Ali — Cashier/Server** | FOH staff | Fast service, tips | Slow POS, split bills, payment failures | POS, handheld, payments |
| **Nadia — Purchasing Manager** | Procurement | Best price, on-time delivery | Manual POs, price creep | Procurement, supplier portal, 3-way match |
| **Karim — Finance Controller / CFO** | Accounting | Accurate close, compliance | Manual reconciliation, delayed close | GL, AP/AR, reconciliation, tax |
| **Hana — HR Manager** | People | Compliance, retention | Attendance disputes, payroll errors | HR, time & attendance, payroll |
| **Franchisor HQ** | Brand owner | Brand standards, royalties | Visibility into franchisees | Franchise portal, royalty engine |
| **Guest** | Customer | Easy ordering, rewards | Waiting, wrong orders | QR/kiosk/app, loyalty, feedback |
| **Supplier** | Vendor | Timely orders & payment | Phone/WhatsApp orders, late payments | Supplier portal, e-invoicing |
| **Driver** | Delivery staff | Efficient routes | Poor dispatch | Driver app, routing |

---

## 5. Product Scope

### 5.1 In Scope (overall product)
All modules listed in Section 6, delivered in phases (Section 14), across web (admin/back office), iOS/Android (POS, manager, driver, guest apps), Windows/Android POS terminals, kiosks, and KDS screens.

### 5.2 Out of Scope (v1.0)
- Hotel PMS room management (integration only)
- Manufacturing-grade MRP for packaged-food factories (lightweight central kitchen only)
- Own banking license (partner-based embedded finance)
- Hardware manufacturing (certified third-party hardware program instead)

### 5.3 Priority Definitions

| Priority | Meaning | Phase |
|---|---|---|
| **P0** | Must-have for MVP / launch | Phase 1 |
| **P1** | Required for competitive parity & mid-market | Phase 2 |
| **P2** | Differentiator / enterprise / leadership features | Phase 3+ |

---

## 6. System Overview & Module Map

```
                         ┌──────────────────────────────────────────┐
                         │        AI & Intelligence Layer           │
                         │ Forecasting · Recommendations · Copilot  │
                         │ Anomaly/Fraud · Dynamic Pricing · NLQ    │
                         └───────────────────▲──────────────────────┘
                                             │
 ┌──────────────── FRONT OF HOUSE ───────────┼──────────── BACK OF HOUSE ───────────────┐
 │ POS · Handheld · Tables · Reservations    │  KDS · Recipes · Inventory · Procurement │
 │ QR / Kiosk / Web / App ordering           │  Central Kitchen · Waste · Food Safety   │
 │ Delivery Hub (aggregators + own fleet)    │  Maintenance & Assets                    │
 └───────────────────────────────────────────┼──────────────────────────────────────────┘
                                             │
 ┌──────────────── HEAD OFFICE ──────────────┼──────────── PEOPLE & CUSTOMERS ──────────┐
 │ Finance & Accounting · Payments · Cash    │  HR · Scheduling · Time & Attendance     │
 │ Multi-location · Franchise · BI           │  Payroll · CRM · Loyalty · Marketing     │
 └───────────────────────────────────────────┴──────────────────────────────────────────┘
                                             │
                ┌────────────────────────────▼─────────────────────────────┐
                │ Platform: Identity · RBAC · Audit · Workflow Engine ·    │
                │ Notifications · Open API · Webhooks · Marketplace        │
                └──────────────────────────────────────────────────────────┘
```

---

## 7. Functional Requirements by Module

> Requirement ID format: `FR-<MODULE>-<NNN>`. Each requirement has a priority (P0/P1/P2). "The system shall…" is implied for each line.

### 7.1 Point of Sale (POS)

**Objective:** The fastest, most reliable POS in the market — works offline, supports every service style, and takes < 3 taps for a typical item.

| ID | Requirement | Priority |
|---|---|---|
| FR-POS-001 | Support service modes: dine-in, takeaway, delivery, drive-thru, counter/QSR, bar tabs, room service, catering | P0 |
| FR-POS-002 | Configurable menu grid with categories, colors, images, favorites, and search (by name, PLU, barcode) | P0 |
| FR-POS-003 | Item modifiers: forced/optional, nested modifiers, min/max selections, price-affecting modifiers, combos and meal deals | P0 |
| FR-POS-004 | Open items, custom price items (with permission), weighed items via integrated scale | P0 |
| FR-POS-005 | Course management (fire/hold courses), seat numbers, guest count, special instructions, allergen flags | P0 |
| FR-POS-006 | Split bill by item, seat, equal parts, or custom amount; merge and transfer tables/checks | P0 |
| FR-POS-007 | Multiple tenders per check: cash, card, wallet, gift card, loyalty points, voucher, house account, room charge | P0 |
| FR-POS-008 | Discounts & promotions: % / fixed, item / check level, happy hour, BOGO, coupon codes, auto-applied rules, manager approval thresholds | P0 |
| FR-POS-009 | Voids, refunds and comps with mandatory reason codes and role-based approval (PIN/biometric/NFC card) | P0 |
| FR-POS-010 | Full **offline mode**: take orders, send to KDS, accept card payments (store-and-forward per processor rules), print receipts; auto-sync on reconnect with conflict resolution | P0 |
| FR-POS-011 | Receipt printing, e-receipts (SMS/email/WhatsApp), QR-code receipts, fiscal printer and e-invoicing compliance per country | P0 |
| FR-POS-012 | Shift/till management: open/close shift, float, cash drops, paid-in/paid-out, blind close, X/Z reports | P0 |
| FR-POS-013 | Tips: on-screen tipping, tip pooling/sharing rules, tip declaration, tip-out reports | P1 |
| FR-POS-014 | Service charges, auto-gratuity by party size, tax-inclusive/exclusive pricing, multiple tax rates per item | P0 |
| FR-POS-015 | Customer lookup & attach to order (phone/QR/loyalty card), view history and preferences | P1 |
| FR-POS-016 | Handheld/mobile POS (tablet/phone) for tableside ordering & payment; pay-at-table | P1 |
| FR-POS-017 | Multi-language UI per user, RTL support, large-font/high-contrast accessibility mode | P0 |
| FR-POS-018 | Quick-service features: order number display, pager integration, customer-facing display with upsell suggestions | P1 |
| FR-POS-019 | Bar features: open tabs with card pre-auth, bottle/pour tracking, age-verification prompt | P1 |
| FR-POS-020 | **AI upsell prompts** at order entry based on basket, time of day, weather and guest profile | P2 |
| FR-POS-021 | Voice ordering assistant for staff (hands-free item entry) | P2 |
| FR-POS-022 | Real-time stock awareness: 86'd items auto-disabled across all channels when stock hits zero | P0 |
| FR-POS-023 | Hardware support: thermal/kitchen printers, cash drawers, scales, barcode scanners, card terminals, customer displays, MSR/NFC | P0 |
| FR-POS-024 | Training mode (sandbox transactions excluded from reporting) | P1 |

### 7.2 Order Management & Omnichannel Hub

**Objective:** Every order from every channel lands in one queue, one menu, one stock pool.

| ID | Requirement | Priority |
|---|---|---|
| FR-OMS-001 | Unified order inbox for POS, QR, kiosk, web, app, phone, and third-party aggregators | P0 |
| FR-OMS-002 | Native integrations with major delivery aggregators (order injection, status sync, menu sync, store open/close, item availability) | P0 |
| FR-OMS-003 | Single master menu with per-channel overrides (price, availability, images, descriptions) | P0 |
| FR-OMS-004 | Order lifecycle states: received → accepted → in-prep → ready → picked-up/served → completed / cancelled / refunded, with timestamps | P0 |
| FR-OMS-005 | Auto-accept rules and auto-throttling (pause channels or extend prep time when kitchen load exceeds threshold) | P1 |
| FR-OMS-006 | Scheduled / pre-orders and catering orders with deposits | P1 |
| FR-OMS-007 | Aggregator commission & payout reconciliation per order | P1 |
| FR-OMS-008 | Order-ahead capacity slots per outlet (orders per 15-min window) | P1 |
| FR-OMS-009 | Smart order batching for kitchen efficiency (group identical items across orders) | P2 |
| FR-OMS-010 | Customer notifications (SMS/WhatsApp/push) at each status change | P1 |

### 7.3 Kitchen Display System (KDS) & Production

| ID | Requirement | Priority |
|---|---|---|
| FR-KDS-001 | Route items to stations (grill, fry, cold, bar, pastry, expo) by configurable rules | P0 |
| FR-KDS-002 | Ticket views: tile, list, all-day (aggregated counts), with color-coded aging timers | P0 |
| FR-KDS-003 | Bump, recall, prioritize (rush/VIP), and partial-bump by item | P0 |
| FR-KDS-004 | Course pacing and "fire" synchronization so all items of a course finish together | P1 |
| FR-KDS-005 | Expo screen consolidating all stations with ready-status per item | P0 |
| FR-KDS-006 | Display modifiers, allergens (highlighted), notes, seat numbers and order source | P0 |
| FR-KDS-007 | Recipe/plating card on tap (image, steps, portion size) | P1 |
| FR-KDS-008 | Prep time tracking per item/station; KPI: ticket times, late tickets | P0 |
| FR-KDS-009 | Bump bar and touch support; works offline over LAN | P0 |
| FR-KDS-010 | **AI prep-time prediction** used to quote accurate wait times to guests and aggregators | P2 |
| FR-KDS-011 | Prep lists: daily prep quantities generated from forecast and par levels | P1 |
| FR-KDS-012 | Kitchen load balancing across stations and smart cook-start times ("start fries in 3 min") | P2 |

### 7.4 Table, Floor & Reservation Management

| ID | Requirement | Priority |
|---|---|---|
| FR-TBL-001 | Visual drag-and-drop floor plan designer with multiple areas (indoor, terrace, bar, VIP) | P0 |
| FR-TBL-002 | Live table status: available, seated, ordered, mains served, dessert, bill requested, paid, dirty | P0 |
| FR-TBL-003 | Server section assignment and table turn-time tracking | P1 |
| FR-TBL-004 | Reservations: online booking widget, phone entry, deposits/no-show fees, confirmations & reminders | P1 |
| FR-TBL-005 | Waitlist with SMS "table ready" notification and quoted wait-time estimates | P1 |
| FR-TBL-006 | Table combining/splitting for large parties | P1 |
| FR-TBL-007 | Guest profile in reservation (allergies, preferences, visit history, VIP tags) | P1 |
| FR-TBL-008 | **AI table optimization**: auto-assign tables to maximize covers & minimize wait | P2 |
| FR-TBL-009 | Integration with external reservation networks | P1 |

### 7.5 Menu & Recipe Engineering

| ID | Requirement | Priority |
|---|---|---|
| FR-MNU-001 | Central menu builder: items, categories, modifiers, combos, availability schedules (daypart), channel visibility | P0 |
| FR-MNU-002 | Multi-level recipes (BOM): raw ingredient → sub-recipe (sauce, dough) → menu item, with yields and units | P0 |
| FR-MNU-003 | Unit of measure conversions (purchase unit → storage unit → recipe unit) per ingredient | P0 |
| FR-MNU-004 | Yield / waste factors (trim loss, cooking loss) applied to theoretical cost | P0 |
| FR-MNU-005 | Real-time theoretical food cost and margin per item, updated automatically when purchase prices change | P0 |
| FR-MNU-006 | Modifier-level recipe impact (e.g., "extra cheese" deducts 30 g cheese) | P0 |
| FR-MNU-007 | Allergen (14+ major allergens) and dietary tagging (vegan, halal, gluten-free) auto-derived from ingredients | P0 |
| FR-MNU-008 | Nutritional information calculation (calories, macros) from ingredient database | P1 |
| FR-MNU-009 | **Menu engineering matrix** (Stars, Plowhorses, Puzzles, Dogs) by popularity and contribution margin | P1 |
| FR-MNU-010 | Recipe versioning with effective dates and approval workflow | P1 |
| FR-MNU-011 | Price management: price levels by outlet, region, channel, daypart; scheduled price changes | P0 |
| FR-MNU-012 | **AI price optimization** suggestions based on elasticity, competitor data, and target margin | P2 |
| FR-MNU-013 | Recipe scaling for batch production and catering | P1 |
| FR-MNU-014 | Digital recipe book with photos/videos, steps, and plating standards | P1 |
| FR-MNU-015 | Menu import from CSV/Excel and from existing POS | P0 |

### 7.6 Inventory & Warehouse Management

| ID | Requirement | Priority |
|---|---|---|
| FR-INV-001 | Item master: SKU, categories, storage location, units, par levels, reorder points, shelf life, allergen data | P0 |
| FR-INV-002 | Real-time stock depletion from sales via recipes (backflush) | P0 |
| FR-INV-003 | Multi-location stock: outlets, warehouses, central kitchen, storage zones (dry, chiller, freezer, bar) | P0 |
| FR-INV-004 | Stock counts: full, partial, cycle counts; mobile counting app with barcode scanning, offline support, count sheets ordered by shelf | P0 |
| FR-INV-005 | **Actual vs. Theoretical (AvT) variance** report by item, category, outlet, and period with root-cause hints | P0 |
| FR-INV-006 | Waste logging (spoilage, prep waste, plate waste, staff meals, comps) with reasons and photos | P0 |
| FR-INV-007 | Inter-store transfers with request → approve → dispatch → receive flow and in-transit tracking | P0 |
| FR-INV-008 | Batch/lot and expiry tracking; FEFO/FIFO picking suggestions; expiry alerts | P1 |
| FR-INV-009 | Costing methods: weighted average (default), FIFO, latest purchase price | P0 |
| FR-INV-010 | Stock adjustments with reason codes and approval | P0 |
| FR-INV-011 | Low-stock and over-stock alerts | P0 |
| FR-INV-012 | **AI demand-driven replenishment**: suggested order quantities per item per supplier based on forecast, lead times, and pars | P1 |
| FR-INV-013 | IoT integration: smart scales, temperature sensors, RFID for high-value items (spirits, meat) | P2 |
| FR-INV-014 | **Computer-vision waste tracking** (camera over waste bin auto-classifies and weighs waste) | P2 |
| FR-INV-015 | Bar inventory: bottle weighing, pour-cost reports, keg monitoring | P1 |
| FR-INV-016 | Inventory valuation report and period-end closing | P0 |

### 7.7 Procurement & Supplier Management

| ID | Requirement | Priority |
|---|---|---|
| FR-PRC-001 | Supplier master: contacts, payment terms, lead times, delivery days, minimum order value, catalogs, contract prices | P0 |
| FR-PRC-002 | Purchase requisitions → approval workflow (configurable by amount, category, outlet) → purchase orders | P0 |
| FR-PRC-003 | Send POs via email, supplier portal, EDI, or WhatsApp | P0 |
| FR-PRC-004 | Goods Received Notes (GRN) with partial receipts, quantity/quality checks, temperature capture, photo evidence, rejection reasons | P0 |
| FR-PRC-005 | **3-way match**: PO ↔ GRN ↔ supplier invoice; auto-flag price/quantity discrepancies | P0 |
| FR-PRC-006 | Invoice capture via **OCR/AI** (photo or email inbox) with automatic line-item extraction and mapping | P1 |
| FR-PRC-007 | Price-change tracking and alerts; contract price compliance | P1 |
| FR-PRC-008 | Supplier scorecards: on-time %, fill rate, quality rejections, price variance | P1 |
| FR-PRC-009 | Supplier portal: view POs, confirm, propose substitutions, upload invoices, view payment status | P1 |
| FR-PRC-010 | Credit notes / returns to vendor (RTV) | P0 |
| FR-PRC-011 | Order guides / templates and recurring standing orders | P0 |
| FR-PRC-012 | Multi-supplier price comparison & **AI best-buy recommendation** | P2 |
| FR-PRC-013 | Budget control: block or warn when POs exceed category budget | P1 |
| FR-PRC-014 | Marketplace: discover new suppliers and request quotes (RFQ) | P2 |

### 7.8 Central Kitchen & Commissary

| ID | Requirement | Priority |
|---|---|---|
| FR-CK-001 | Outlet orders to central kitchen (internal requisitions) with cut-off times | P1 |
| FR-CK-002 | Production planning: aggregate outlet demand → production orders by recipe and batch | P1 |
| FR-CK-003 | Production execution: issue raw materials, record output, yield variance, labor time | P1 |
| FR-CK-004 | Batch labeling (product, batch, production date, expiry, allergens) with printable barcodes | P1 |
| FR-CK-005 | Internal transfer pricing (cost, cost-plus, fixed) and inter-company invoicing | P1 |
| FR-CK-006 | Dispatch planning and delivery routes to outlets | P2 |
| FR-CK-007 | Traceability: forward/backward lot tracing for recalls | P1 |

### 7.9 Finance & Accounting

| ID | Requirement | Priority |
|---|---|---|
| FR-FIN-001 | Multi-entity, multi-currency general ledger with configurable chart of accounts (restaurant templates included) | P0 |
| FR-FIN-002 | Automatic journal postings from sales, payments, COGS, inventory movements, payroll, and purchases | P0 |
| FR-FIN-003 | Accounts Payable: supplier invoices, aging, payment runs, partial payments, withholding tax | P0 |
| FR-FIN-004 | Accounts Receivable: corporate/house accounts, catering invoices, credit limits, dunning | P1 |
| FR-FIN-005 | Bank feeds and **AI-assisted bank reconciliation** | P1 |
| FR-FIN-006 | Daily sales reconciliation: POS vs. payments vs. bank deposits vs. aggregator payouts | P0 |
| FR-FIN-007 | Real-time **P&L per outlet, brand, region, and consolidated**; prime cost (COGS + labor) daily | P0 |
| FR-FIN-008 | Budgeting & forecasting by outlet and account, with variance analysis | P1 |
| FR-FIN-009 | Tax engine: VAT/GST/sales tax, multiple rates, tax-inclusive pricing, tax returns reports | P0 |
| FR-FIN-010 | **E-invoicing compliance** per jurisdiction (e.g., ZATCA Phase 2, GST e-invoice, EU e-invoicing, fiscal devices) | P0 (per launch market) |
| FR-FIN-011 | Fixed assets register with depreciation schedules | P1 |
| FR-FIN-012 | Period close checklist, locking, and adjustments; month-end close in < 3 days | P1 |
| FR-FIN-013 | Inter-company transactions and eliminations for consolidation | P2 |
| FR-FIN-014 | Cash-flow forecast powered by sales forecast and AP schedule | P2 |
| FR-FIN-015 | Export / sync to external accounting systems for customers who keep their ledger elsewhere | P0 |
| FR-FIN-016 | Financial statements: P&L, balance sheet, cash flow, trial balance, GL detail | P0 |

### 7.10 Payments & Cash Management

| ID | Requirement | Priority |
|---|---|---|
| FR-PAY-001 | Integrated card-present payments (chip, contactless, mobile wallets) via certified terminals | P0 |
| FR-PAY-002 | Card-not-present payments for online, QR and app orders; tokenization; 3-D Secure | P0 |
| FR-PAY-003 | Local payment methods per market (e.g., local debit schemes, QR wallets, BNPL) | P1 |
| FR-PAY-004 | Gift cards (physical & digital), store credit, and vouchers | P1 |
| FR-PAY-005 | Pre-authorization and incremental auth for tabs; tip adjustment | P1 |
| FR-PAY-006 | Automated settlement reconciliation and fee reporting | P0 |
| FR-PAY-007 | Cash management: safe counts, bank deposit tracking, over/short alerts | P0 |
| FR-PAY-008 | Embedded finance: instant payouts, revenue-based working-capital financing (partner-based) | P2 |
| FR-PAY-009 | Payment-processor agnostic architecture (pluggable gateways) | P0 |
| FR-PAY-010 | Chargeback management workflow | P1 |

### 7.11 HR, Workforce & Payroll

| ID | Requirement | Priority |
|---|---|---|
| FR-HR-001 | Employee master: personal info, documents, contracts, roles, wage rates, multiple positions, outlets | P0 |
| FR-HR-002 | Hiring & onboarding: job posts, applicant tracking, digital onboarding forms, e-signature | P1 |
| FR-HR-003 | Time & attendance: clock-in/out on POS, mobile with geofencing, **facial recognition** to prevent buddy punching; breaks | P0 |
| FR-HR-004 | Scheduling: drag-and-drop rota, templates, availability, shift swaps, open shifts, manager approvals | P0 |
| FR-HR-005 | **AI labor scheduling**: auto-generate schedules from sales forecast and labor standards (covers per labor hour) | P1 |
| FR-HR-006 | Labor law compliance engine: overtime, max hours, minors' rules, mandatory breaks, predictive scheduling laws | P1 |
| FR-HR-007 | Real-time labor cost % vs. sales on dashboard; alerts when exceeding target | P0 |
| FR-HR-008 | Leave management: requests, approvals, balances, public holidays per country | P1 |
| FR-HR-009 | Payroll: gross-to-net, overtime, tips, service charge distribution, deductions, payslips; or export to payroll providers | P1 |
| FR-HR-010 | Training & certification tracking (food handler cards, alcohol service) with expiry alerts | P1 |
| FR-HR-011 | Performance: sales per server, upsell rates, reviews, KPIs, goals | P2 |
| FR-HR-012 | Employee self-service app: schedule, swaps, payslips, leave, announcements, earned wage access | P1 |
| FR-HR-013 | Task management & digital checklists (opening/closing/cleaning) with photo proof | P1 |

### 7.12 CRM, Loyalty & Marketing

| ID | Requirement | Priority |
|---|---|---|
| FR-CRM-001 | Unified guest profile across all channels (orders, visits, spend, preferences, allergies, feedback) | P1 |
| FR-CRM-002 | Loyalty programs: points, tiers, stamps, cashback, birthday rewards, referral rewards | P1 |
| FR-CRM-003 | Segmentation: RFM, lapsed guests, VIPs, channel preferences, custom filters | P1 |
| FR-CRM-004 | Campaigns via SMS, email, WhatsApp, push with templates and A/B testing | P1 |
| FR-CRM-005 | Automated journeys: welcome, win-back, birthday, post-visit feedback, abandoned cart | P1 |
| FR-CRM-006 | Feedback & reviews: post-order surveys, NPS, review aggregation from public platforms, AI sentiment analysis | P1 |
| FR-CRM-007 | Promotions engine shared with POS & online (single rule set) | P0 |
| FR-CRM-008 | **AI next-best-offer** and churn prediction per guest | P2 |
| FR-CRM-009 | Consent management (opt-in/opt-out) compliant with GDPR/PDPL etc. | P0 |
| FR-CRM-010 | Campaign ROI attribution (redemptions → revenue) | P1 |

### 7.13 Self-Service: QR, Kiosk, Web & Mobile Ordering

| ID | Requirement | Priority |
|---|---|---|
| FR-SS-001 | QR table ordering & pay-at-table (no app download), with group ordering on one bill | P0 |
| FR-SS-002 | Self-order kiosk app with upsell flows, combo builder, loyalty login, card/cash payment | P1 |
| FR-SS-003 | Branded online ordering website (no-code builder, custom domain, SEO-friendly) | P1 |
| FR-SS-004 | White-label branded mobile app (iOS/Android) for chains | P2 |
| FR-SS-005 | Real-time menu & stock sync; item images, allergens, nutrition | P0 |
| FR-SS-006 | Pickup, curbside, dine-in and delivery options; scheduled orders | P1 |
| FR-SS-007 | Multi-language menus with auto-translation | P1 |
| FR-SS-008 | **AI personalized recommendations** and conversational ordering (chat/voice) | P2 |
| FR-SS-009 | Accessibility conformance (WCAG 2.2 AA) for all guest-facing UIs | P0 |

### 7.14 Delivery & Logistics

| ID | Requirement | Priority |
|---|---|---|
| FR-DLV-001 | Own-fleet dispatch: assign drivers manually or automatically | P1 |
| FR-DLV-002 | Driver app: order details, navigation, proof of delivery (photo/signature/OTP), cash collection | P1 |
| FR-DLV-003 | Live tracking link for guests | P1 |
| FR-DLV-004 | Delivery zones (polygon), zone-based fees and minimum orders | P1 |
| FR-DLV-005 | Route optimization for multi-drop deliveries | P2 |
| FR-DLV-006 | Third-party last-mile courier integration (on-demand dispatch) | P1 |
| FR-DLV-007 | Driver performance & cash reconciliation | P1 |

### 7.15 Multi-Location, Franchise & Head Office

| ID | Requirement | Priority |
|---|---|---|
| FR-HQ-001 | Hierarchy: Organization → Brand → Region → Outlet (and Legal Entity), with inheritance of settings | P0 |
| FR-HQ-002 | Central menu/price/promo publishing with outlet-level override permissions | P0 |
| FR-HQ-003 | Cross-outlet dashboards, leaderboards, and benchmarking | P1 |
| FR-HQ-004 | Franchise management: franchisee onboarding, royalty & marketing-fee calculation, automated invoicing | P1 |
| FR-HQ-005 | Brand-standard audits (mobile checklists, scoring, photo evidence, corrective actions) | P1 |
| FR-HQ-006 | Multi-brand / virtual brand support from one kitchen (cloud kitchens) | P1 |
| FR-HQ-007 | New-outlet cloning (copy configuration, menus, users in minutes) | P0 |
| FR-HQ-008 | Communication hub: announcements, policy acknowledgement, document library | P2 |

### 7.16 Business Intelligence & Analytics

| ID | Requirement | Priority |
|---|---|---|
| FR-BI-001 | Real-time executive dashboard: sales, covers, average check, food cost %, labor %, prime cost, top items, channel mix | P0 |
| FR-BI-002 | 150+ standard reports (sales, product mix, hourly, discount/void, payments, inventory, procurement, labor, CRM) | P0 |
| FR-BI-003 | Custom report builder (drag-and-drop dimensions/measures), saved views, scheduled email/WhatsApp delivery | P1 |
| FR-BI-004 | Drill-down from consolidated → outlet → day → check → item | P0 |
| FR-BI-005 | Comparisons: vs. last week/year, vs. budget, vs. forecast, same-store sales | P0 |
| FR-BI-006 | Mobile owner app with push alerts and KPI widgets | P0 |
| FR-BI-007 | **Natural-language analytics** ("What was my food cost at the downtown branch last month vs. budget?") | P2 |
| FR-BI-008 | Data warehouse export / connectors to external BI tools; read-only SQL access for enterprise | P1 |
| FR-BI-009 | Anonymized peer benchmarking by cuisine, city, and format | P2 |
| FR-BI-010 | Export to Excel/CSV/PDF for all reports | P0 |

### 7.17 AI & Intelligent Automation Layer ("Chef Brain")

**Objective:** Shift the product from "system of record" to "system of decisions." Every AI feature must be explainable, overridable, and measured for ROI.

| ID | Capability | Description | Priority |
|---|---|---|---|
| FR-AI-001 | Demand forecasting | Item- and ingredient-level forecasts per outlet per 15-min interval using sales history, seasonality, holidays, weather, local events, promotions; accuracy (WAPE) shown to users | P1 |
| FR-AI-002 | Auto-replenishment | Suggested/auto-generated POs from forecast, stock, lead times, and shelf life | P1 |
| FR-AI-003 | Smart scheduling | Labor schedules optimized for forecasted demand, labor laws, skills and employee preferences | P1 |
| FR-AI-004 | Prep planning | Daily prep lists with quantities and timing | P1 |
| FR-AI-005 | Menu & price intelligence | Engineering matrix plus price elasticity and recommendations | P2 |
| FR-AI-006 | Anomaly & fraud detection | Detect suspicious voids, discounts, refunds, no-sales, cash shortages, sweethearting, inventory shrinkage; ranked alerts with evidence | P1 |
| FR-AI-007 | AI Copilot | Conversational assistant for owners/managers: query data, generate reports, draft supplier emails, create promotions, explain variances, execute actions with confirmation | P2 |
| FR-AI-008 | Invoice OCR | Extract supplier invoice data and auto-map to items | P1 |
| FR-AI-009 | Review & sentiment analysis | Summarize guest feedback themes per outlet and dish | P2 |
| FR-AI-010 | Computer vision | Waste-bin recognition, plating-quality checks, drive-thru vehicle counting | P2 |
| FR-AI-011 | Dynamic pricing (optional) | Time/demand-based pricing for delivery channels with guardrails | P2 |
| FR-AI-012 | Proactive insights feed | Daily "3 things to do today" recommendations with estimated $ impact | P1 |
| FR-AI-013 | Governance | Explanations for every recommendation, human-in-the-loop approval, audit log, opt-out per feature, and ROI tracking | P0 (for any AI feature shipped) |

### 7.18 Food Safety, Quality & Compliance

| ID | Requirement | Priority |
|---|---|---|
| FR-FS-001 | HACCP plans: critical control points, digital logs, corrective actions | P1 |
| FR-FS-002 | Temperature monitoring: manual logs and wireless IoT probes for fridges/freezers with alerts | P1 |
| FR-FS-003 | Food labeling: prep/expiry labels with allergen info printed from mobile/KDS | P1 |
| FR-FS-004 | Allergen matrix per outlet, auto-generated from recipes | P0 |
| FR-FS-005 | Cleaning schedules and sanitation checklists | P1 |
| FR-FS-006 | Inspection readiness reports and audit trail | P1 |
| FR-FS-007 | Product recall workflow using lot traceability | P2 |

### 7.19 Maintenance & Asset Management

| ID | Requirement | Priority |
|---|---|---|
| FR-MNT-001 | Asset register (equipment, serial, warranty, vendor, location) | P1 |
| FR-MNT-002 | Preventive maintenance schedules and work orders | P1 |
| FR-MNT-003 | Issue reporting with photos from mobile; assign to technician/vendor | P1 |
| FR-MNT-004 | Maintenance cost tracking per asset/outlet | P2 |
| FR-MNT-005 | Energy monitoring integration (IoT) for sustainability reporting | P2 |

### 7.20 Platform Administration, Security & Identity

| ID | Requirement | Priority |
|---|---|---|
| FR-ADM-001 | Role-based access control (RBAC) with granular permissions per module/action/outlet; custom roles | P0 |
| FR-ADM-002 | SSO (SAML/OIDC), MFA, password policies; staff PIN/NFC/biometric for POS | P0 |
| FR-ADM-003 | Complete immutable audit log (who, what, when, where, before/after values) | P0 |
| FR-ADM-004 | Configurable approval workflow engine (multi-level, conditional) used across modules | P1 |
| FR-ADM-005 | Notification center: in-app, email, SMS, WhatsApp, push; per-user preferences | P0 |
| FR-ADM-006 | Device management: register/lock/wipe POS devices, remote configuration, software updates | P0 |
| FR-ADM-007 | Data import/export tools and migration wizards from common legacy systems | P0 |
| FR-ADM-008 | Localization: languages, RTL, date/number formats, currencies, time zones, fiscal calendars (incl. 4-4-5) | P0 |
| FR-ADM-009 | Subscription & billing self-service for customers | P0 |
| FR-ADM-010 | Sandbox/test environment for enterprise customers | P2 |
| FR-ADM-011 | Custom fields and custom objects on key entities | P1 |

### 7.21 Integrations Marketplace & Open API

| ID | Requirement | Priority |
|---|---|---|
| FR-INT-001 | Public REST + GraphQL APIs covering all core entities, with OAuth 2.0 and scoped API keys | P1 |
| FR-INT-002 | Webhooks for key events (order created, payment captured, stock low, shift closed…) with retries and signing | P1 |
| FR-INT-003 | Developer portal: docs, sandbox, SDKs, API status page | P1 |
| FR-INT-004 | App marketplace with partner onboarding, review process, and revenue share | P2 |
| FR-INT-005 | Pre-built connectors: delivery aggregators, accounting, payroll, payment gateways, reservations, e-invoicing authorities, BI tools, messaging (WhatsApp/SMS/email) | P0–P1 |
| FR-INT-006 | Rate limiting, API usage analytics, and versioning policy (≥ 12 months deprecation notice) | P1 |

---

## 8. Non-Functional Requirements

### 8.1 Performance

| ID | Requirement | Target |
|---|---|---|
| NFR-PERF-001 | POS item add / screen response | < 100 ms (p95) local |
| NFR-PERF-002 | Order sent to KDS (LAN) | < 1 s (p95) |
| NFR-PERF-003 | Card payment authorization end-to-end | < 3 s (p95, processor-dependent) |
| NFR-PERF-004 | Back-office page load | < 2 s (p95) |
| NFR-PERF-005 | Standard report generation (1 outlet, 1 month) | < 3 s; consolidated 500 outlets < 15 s |
| NFR-PERF-006 | Stock depletion after sale | Real-time (< 5 s) |
| NFR-PERF-007 | Dashboard data freshness | < 60 s |

### 8.2 Availability & Resilience

| ID | Requirement | Target |
|---|---|---|
| NFR-AV-001 | Cloud platform uptime SLA | 99.95% (enterprise 99.99% option) |
| NFR-AV-002 | POS/KDS operation without internet | Unlimited duration for core flows |
| NFR-AV-003 | RPO / RTO | RPO ≤ 5 min, RTO ≤ 1 h |
| NFR-AV-004 | Multi-AZ deployment; multi-region DR | Required |
| NFR-AV-005 | Zero-downtime deployments | Blue/green or canary |
| NFR-AV-006 | Local LAN failover (POS-to-POS peer sync when cloud down) | Required |

### 8.3 Scalability

| ID | Requirement | Target |
|---|---|---|
| NFR-SC-001 | Tenants | 100,000+ outlets |
| NFR-SC-002 | Peak throughput | 5,000 orders/sec platform-wide |
| NFR-SC-003 | Single enterprise tenant | 5,000 outlets, 100,000 employees |
| NFR-SC-004 | Horizontal scaling | Stateless services, auto-scaling |

### 8.4 Security & Privacy

| ID | Requirement |
|---|---|
| NFR-SEC-001 | PCI DSS Level 1 compliance for payments; P2PE terminals; no raw PAN stored |
| NFR-SEC-002 | SOC 2 Type II and ISO 27001 certification (within 18 months of GA) |
| NFR-SEC-003 | Encryption: TLS 1.2+ in transit; AES-256 at rest; tenant-level key management for enterprise |
| NFR-SEC-004 | Privacy: GDPR, local data-protection laws (e.g., PDPL); data residency options per region; right to erasure/export |
| NFR-SEC-005 | Tenant isolation enforced at data layer (row-level security + tenant-scoped keys) |
| NFR-SEC-006 | OWASP ASVS L2; annual third-party penetration tests; bug bounty program |
| NFR-SEC-007 | Secrets management, least privilege, security logging & SIEM |
| NFR-SEC-008 | Session timeouts, device binding for POS, anomaly-based login protection |

### 8.5 Usability & Accessibility

| ID | Requirement |
|---|---|
| NFR-UX-001 | New cashier productive after ≤ 15 minutes of training |
| NFR-UX-002 | Single-outlet self-onboarding ≤ 30 minutes with guided setup wizard and templates |
| NFR-UX-003 | WCAG 2.2 AA for web/mobile; touch targets ≥ 44 px on POS |
| NFR-UX-004 | Full RTL support and localization for launch languages (e.g., English, Arabic, French, Spanish) |
| NFR-UX-005 | Consistent design system across all apps; dark mode for KDS/POS |

### 8.6 Maintainability & Quality

| ID | Requirement |
|---|---|
| NFR-MQ-001 | Automated test coverage ≥ 80% on core domain services; contract tests for all integrations |
| NFR-MQ-002 | CI/CD with automated security scanning (SAST, DAST, dependency, container) |
| NFR-MQ-003 | Observability: distributed tracing, structured logs, metrics, SLO dashboards, alerting |
| NFR-MQ-004 | Feature flags for progressive rollout per tenant/region |
| NFR-MQ-005 | Backward-compatible APIs; database migrations without downtime |

### 8.7 Compliance (market-dependent)

- Fiscal/e-invoicing regulations of each launch country (certification before launch in that market)
- Labor law rules engine per jurisdiction
- Food safety record retention requirements
- Accessibility regulations for public kiosks
- Tax audit-ready immutable transaction journal

---

## 9. Technical Architecture

### 9.1 Architectural Principles
1. **Cloud-native, multi-tenant SaaS** with optional dedicated tenancy for enterprise.
2. **Domain-driven, modular services** (bounded contexts per module) communicating via events.
3. **Event-driven core**: every business action emits an event (e.g., `OrderPlaced`, `PaymentCaptured`, `StockDepleted`) → enables real-time analytics, AI, webhooks, and auditability.
4. **Offline-first edge**: POS/KDS run a local engine with an embedded database and sync via CRDT/operation log with idempotent server APIs.
5. **API-first**: every UI uses the same public APIs available to partners.
6. **Security & privacy by design**.

### 9.2 Logical Architecture

```
┌──────────────── Clients ─────────────────────────────────────────────────────┐
│ POS (Win/Android/iPad) · KDS · Kiosk · Handheld · Back-office Web · Owner App │
│ Guest Web/App · Driver App · Supplier Portal · Partner Apps                   │
└───────────────▲───────────────────────────────▲──────────────────────────────┘
                │ (local LAN sync, edge engine) │ HTTPS / WebSocket
┌───────────────┴──────────┐        ┌───────────┴───────────────────────────────┐
│ Edge Store Hub (optional │        │ API Gateway · Auth (OIDC) · Rate limiting  │
│ local server per outlet) │        └───────────▲───────────────────────────────┘
└──────────────────────────┘                    │
               ┌────────────────────────────────┴───────────────────────────────┐
               │ Domain Services: Orders · Menu · Payments · Inventory ·         │
               │ Procurement · Finance · HR · CRM · Delivery · Franchise · ...   │
               └───────────────▲────────────────────────────────▲───────────────┘
                               │ Event Bus (streaming)          │
         ┌─────────────────────┴──────┐            ┌────────────┴────────────────┐
         │ OLTP DBs (per domain,      │            │ Analytics Lakehouse +        │
         │ relational, RLS)           │            │ Feature Store + ML Platform  │
         └────────────────────────────┘            └─────────────────────────────┘
```

### 9.3 Suggested Technology Stack (non-binding)

| Layer | Options |
|---|---|
| Frontend web | React/Next.js + TypeScript, design system, i18n with RTL |
| Mobile / POS | React Native or Flutter; native modules for hardware/payments; Windows POS via Electron/.NET where needed |
| Backend | TypeScript (Node.js) / Go / Kotlin microservices; gRPC internal, REST/GraphQL external |
| Data | PostgreSQL (OLTP, row-level security), Redis (cache), event streaming (Kafka-compatible), object storage |
| Analytics | Lakehouse/columnar warehouse, dbt-style transformations, semantic layer |
| AI/ML | Feature store, model registry, batch + real-time inference; LLM integration for Copilot with retrieval over tenant data and strict permission filtering |
| Edge | Embedded SQLite + sync engine; local message broker for POS↔KDS |
| Infra | Kubernetes, IaC, multi-region cloud, CDN, WAF |
| Observability | OpenTelemetry, centralized logging, metrics & tracing |

### 9.4 Integration Patterns
- Outbound webhooks (signed, retried with exponential backoff, dead-letter queue)
- Inbound adapters per partner with canonical order/menu models
- Idempotency keys on all write APIs
- Scheduled sync jobs for accounting/payroll exports

---

## 10. Core Data Model

| Entity | Key attributes | Relationships |
|---|---|---|
| Organization | id, name, plan, settings | has Brands, LegalEntities |
| Brand | id, name, logo, menu sets | belongs to Organization; has Outlets |
| Outlet | id, address, timezone, currency, tax profile, hours | belongs to Brand, Region, LegalEntity |
| User / Employee | id, roles, outlets, wage rates, PIN | has Shifts, TimeEntries |
| MenuItem | id, name, category, prices[], modifiers[], allergens, channels | has Recipe |
| Recipe (BOM) | id, version, yield, lines[] (ingredient/sub-recipe, qty, uom) | belongs to MenuItem / SubRecipe |
| Ingredient (InventoryItem) | id, SKU, uoms, par, reorder point, cost, shelf life | stocked at Locations; supplied by Suppliers |
| StockLedger | item, location, qty, cost, movement type, reference | immutable movement journal |
| Order | id, channel, type, status, outlet, table, guest, lines[], taxes, discounts, timestamps | has Payments, KDS tickets |
| Payment | id, order, tender, amount, tip, processor ref, status | belongs to Order, Shift |
| Shift / Till | id, user, device, float, cash counts, X/Z | has Payments, CashMovements |
| Supplier | id, terms, lead time, catalog | has PurchaseOrders, Invoices |
| PurchaseOrder | id, supplier, outlet, lines, status | has GRNs, Invoices |
| JournalEntry | id, date, entity, lines (account, debit, credit, dimensions) | generated from business events |
| Guest | id, contact, consents, loyalty balance, preferences | has Orders, Reservations |
| Reservation | id, guest, party size, time, table, deposit | belongs to Outlet |
| Forecast | outlet, item, interval, predicted qty, confidence | used by Replenishment, Scheduling |
| AuditEvent | actor, action, entity, before, after, timestamp, device | all entities |

**Data principles:** immutable ledgers for stock, cash and accounting; soft deletes; every record carries tenant id, outlet id, and created/updated audit metadata; dimensions (outlet, brand, channel, daypart) on all financial postings.

---

## 11. Key End-to-End Workflows

### 11.1 Dine-in Order-to-Cash
1. Host seats party (table status → seated, guest linked if known).
2. Server enters order on handheld; AI suggests upsell; allergens flagged.
3. Items routed to stations on KDS; course pacing applied.
4. Each sale depletes inventory via recipes in real time.
5. Guest pays at table (card/QR/split); tip captured; e-receipt sent.
6. Revenue, tax, tips, COGS journal entries posted automatically.
7. Feedback request sent post-visit; loyalty points credited.

### 11.2 Procure-to-Pay
1. AI generates suggested order from forecast & stock → manager reviews/edits.
2. PO approved via workflow and sent to supplier.
3. Delivery received on mobile: quantities, temperatures, photos; GRN posted, stock increased.
4. Supplier invoice captured via OCR → 3-way match → discrepancies flagged.
5. Approved invoice posted to AP; scheduled in payment run; bank reconciliation closes the loop.

### 11.3 Forecast-to-Schedule
1. Nightly forecast per outlet per 15-min interval.
2. Labor standards convert demand to required staff per role.
3. Auto-schedule generated respecting availability, skills, labor laws, budget.
4. Manager adjusts and publishes; staff notified via app; swaps handled in-app.
5. Real-time labor % monitored; alerts suggest sending staff home or calling in.

### 11.4 Daily Close
1. Shifts closed with blind cash counts; over/short recorded.
2. POS vs. payments vs. aggregator reconciliation auto-run.
3. Daily flash report (sales, prime cost, variances, anomalies) pushed to owner by 7:00 AM.

### 11.5 Month-End Close
1. Inventory count via mobile → valuation and AvT variance.
2. Accruals, depreciation, and allocations posted.
3. Bank reconciliations completed; period locked.
4. Consolidated P&L and balance sheet generated per entity/brand.

---

## 12. UX & Design Principles

1. **Speed over everything at the point of service** — minimal taps, no blocking dialogs, predictable layouts.
2. **Exception-based management** — show what needs attention, not every number.
3. **Mobile-first for managers & owners** — every critical action possible from a phone.
4. **Progressive disclosure** — simple defaults for a café; advanced settings for enterprises.
5. **Guided setup** — templates by cuisine/format (QSR, café, fine dining, cloud kitchen).
6. **Explainable AI** — every recommendation shows "why" and expected impact, with one-tap accept/edit/reject.
7. **Consistent design system** with light/dark themes, RTL mirroring, and accessible color contrast.
8. **In-product help** — contextual tips, video guides, and AI help assistant.

---

## 13. Success Metrics & KPIs

### 13.1 Customer Outcome Metrics (proof of value)

| Metric | Target |
|---|---|
| Food cost % reduction | ≥ 2 pts within 6 months |
| Labor cost % reduction | ≥ 1.5 pts within 6 months |
| Waste reduction | ≥ 20% within 6 months |
| Ticket time reduction | ≥ 15% |
| Month-end close time | ≤ 3 days |
| Forecast accuracy (WAPE, daily item level) | ≤ 25% |

### 13.2 Product Metrics

| Metric | Target |
|---|---|
| Time to first sale (SMB) | < 24 h |
| Module adoption (≥ 3 modules active) | ≥ 70% of customers |
| AI recommendation acceptance rate | ≥ 50% |
| Weekly active managers / outlet | ≥ 2 |
| Crash-free POS sessions | ≥ 99.9% |

### 13.3 Business Metrics

| Metric | Target |
|---|---|
| Net Revenue Retention | ≥ 120% |
| Gross margin (software) | ≥ 75% |
| CAC payback | < 18 months |
| NPS | ≥ 60 |
| Payment attach rate | ≥ 60% of outlets |

---

## 14. Release Plan & Roadmap

### Phase 1 — MVP / Launch (Months 0–6): "Run the restaurant"
- POS (incl. offline), KDS, table management, basic QR ordering
- Menu & recipe management, real-time theoretical costing
- Core inventory (counts, transfers, waste, AvT), basic procurement (PO, GRN)
- Integrated payments, cash management, daily reconciliation
- Basic HR: employees, time clock, scheduling
- Core reports & owner mobile dashboard
- Multi-outlet hierarchy, RBAC, audit log, localization, e-invoicing for launch market
- Accounting export connectors
- **Exit criteria:** 50 pilot outlets live, POS crash-free ≥ 99.9%, NPS ≥ 40

### Phase 2 — Growth (Months 7–12): "Control the business"
- Full procurement (3-way match, OCR invoices, supplier portal)
- Native accounting (GL, AP/AR, P&L, bank reconciliation)
- Delivery aggregator hub, own-fleet delivery, online ordering website, kiosk
- CRM, loyalty, campaigns, feedback
- AI: demand forecasting, auto-replenishment, smart scheduling, anomaly detection, insights feed
- Central kitchen, food safety, task checklists
- Public API & webhooks
- **Exit criteria:** 1,000 outlets, first enterprise customer (50+ outlets), NRR ≥ 110%

### Phase 3 — Leadership (Months 13–24): "Predict and optimize"
- AI Copilot (natural language analytics & actions), menu price optimization
- Franchise management & royalty engine, brand audits
- Payroll (selected markets), employee app with earned wage access
- Computer vision waste tracking, IoT sensors, energy monitoring
- White-label guest apps, marketplace & partner ecosystem
- Peer benchmarking, embedded finance
- SOC 2 Type II, ISO 27001
- **Exit criteria:** 10,000 outlets, top-2 position in launch markets, 50+ marketplace apps

### Phase 4 — Expansion (Months 25–36)
- New country rollouts with local compliance packs
- Advanced enterprise: data residency, dedicated tenancy, custom SLAs
- Supplier network marketplace and procurement financing
- Autonomous operations: AI auto-executes approved policies (auto-order, auto-schedule within guardrails)

---

## 15. Pricing & Packaging

| Plan | Target | Includes | Indicative pricing model |
|---|---|---|---|
| **Starter** | Single café / food truck | POS, KDS, basic menu, payments, basic reports | Low monthly fee per outlet + payment processing |
| **Professional** | Independent restaurants (1–5 outlets) | Starter + inventory, recipes, procurement, scheduling, QR ordering, CRM basics | Per outlet / month |
| **Business** | Multi-unit groups (5–50 outlets) | Pro + accounting, delivery hub, loyalty, central kitchen, AI forecasting & replenishment, API | Per outlet / month |
| **Enterprise** | Chains & franchises (50+ outlets) | Everything + franchise, AI Copilot, advanced BI, SSO, data residency, dedicated CSM, SLA | Custom annual contract |

**Add-ons:** additional POS terminals, kiosks, KDS screens, payroll, white-label app, IoT/vision, premium support.
**Monetization levers:** SaaS subscription, payments revenue share, marketplace revenue share, embedded finance, hardware bundles.

---

## 16. Go-to-Market Strategy for Market Leadership

1. **Land with POS + payments, expand to ERP** — the POS wins the outlet; inventory, accounting and AI drive expansion revenue.
2. **Vertical focus first** — dominate 1–2 segments (e.g., multi-unit casual dining and cloud kitchens) in launch markets before broadening.
3. **ROI guarantee** — publish a measurable promise (e.g., "reduce food cost by 2 points in 6 months or get 3 months free").
4. **Frictionless migration** — free data migration from legacy systems, hardware trade-in, parallel-run support.
5. **Partner channels** — hardware resellers, accountants, payment processors, F&B consultants, suppliers.
6. **Community & content** — benchmarks reports, academy/certification for restaurant managers, industry events.
7. **Customer success at scale** — onboarding specialists, in-app guidance, 24/7 support in local languages, health scores.
8. **Product-led growth** — free tools (recipe costing calculator, menu engineering analyzer) that funnel to trials.
9. **Local compliance as a wedge** — be first-to-certify for new e-invoicing/fiscal regulations in each market.

---

## 17. Risks, Assumptions & Dependencies

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Scope too broad; slow time-to-market | High | High | Strict phasing; MVP focused on POS + inventory core; modular architecture |
| R2 | Offline sync conflicts cause data errors | Medium | High | Operation-log/CRDT sync, idempotent APIs, extensive chaos testing |
| R3 | Payment / fiscal certifications delay launch | Medium | High | Start certification early; partner with certified processors |
| R4 | AI recommendations not trusted | Medium | Medium | Explainability, human-in-the-loop, show measured ROI |
| R5 | Aggregator API changes | High | Medium | Adapter layer, contract tests, partner relationships |
| R6 | Data security breach | Low | Critical | Security program, PCI scope reduction, pen tests, bug bounty |
| R7 | High implementation cost for enterprise | Medium | Medium | Templates, migration tools, partner implementation network |
| R8 | Hardware fragmentation | Medium | Medium | Certified hardware list; hardware abstraction layer |
| R9 | Strong incumbent competition / price wars | High | Medium | Differentiate on AI ROI & unification; bundle payments |

**Assumptions:** Stable internet in most outlets (with offline fallback); customers willing to adopt cloud; payment partners available in launch markets.

**Dependencies:** Payment processors, delivery aggregators' APIs, tax-authority e-invoicing APIs, cloud provider, messaging providers, LLM/AI providers.

---

## 18. Acceptance Criteria & Quality Gates

### 18.1 Sample Acceptance Criteria (Gherkin)

**FR-POS-010 Offline mode**
```gherkin
Given the POS has lost internet connectivity
When a cashier creates an order with 3 items and takes a card payment
Then the order is saved locally, sent to KDS over LAN, and a receipt is printed
And when connectivity is restored, the order, payment and stock movements sync to the cloud within 60 seconds
And no duplicate orders or payments are created
```

**FR-INV-005 Actual vs. Theoretical variance**
```gherkin
Given recipes are defined for all sold menu items
And an opening and closing stock count exist for the period
When the manager opens the AvT report for the period
Then each ingredient shows theoretical usage, actual usage, variance quantity, variance value, and variance %
And items exceeding the configured variance threshold are highlighted
```

**FR-PRC-005 3-way match**
```gherkin
Given a PO for 10 kg of tomatoes at 2.00/kg
And a GRN receiving 9 kg
When a supplier invoice for 10 kg at 2.20/kg is captured
Then the invoice is flagged with a quantity variance of 1 kg and a price variance of 0.20/kg
And the invoice cannot be approved for payment without a user with "AP Approver" permission resolving it
```

**FR-AI-001 Demand forecasting**
```gherkin
Given an outlet with at least 8 weeks of sales history
When the nightly forecast job runs
Then a forecast exists for each active menu item for each 15-minute interval of the next 14 days
And the forecast accuracy (WAPE) for the previous week is displayed on the forecast screen
```

### 18.2 Release Quality Gates
- All P0 requirements for the phase implemented and passing acceptance tests
- No open Critical/High severity bugs; security scan clean of High/Critical findings
- Performance tests meet Section 8.1 targets
- Offline/chaos tests pass (network drop, device crash, clock skew)
- Localization & RTL QA complete for launch languages
- Compliance certifications obtained for launch market (payments, fiscal/e-invoicing)
- Documentation, training material, and support runbooks published

---

## 19. Glossary

| Term | Definition |
|---|---|
| AvT | Actual vs. Theoretical — comparison of actual ingredient usage (from counts) vs. expected usage (from recipes × sales) |
| BOM | Bill of Materials — the recipe structure of a menu item |
| COGS | Cost of Goods Sold |
| Prime cost | COGS + total labor cost; key restaurant profitability metric |
| KDS | Kitchen Display System |
| GRN | Goods Received Note |
| 3-way match | Matching purchase order, goods receipt, and invoice before payment |
| Par level | Target stock quantity to hold between deliveries |
| 86'd | Item out of stock / unavailable |
| WAPE | Weighted Absolute Percentage Error — forecast accuracy metric |
| FEFO / FIFO | First-Expired-First-Out / First-In-First-Out |
| HACCP | Hazard Analysis and Critical Control Points — food safety system |
| RLS | Row-Level Security |
| NRR | Net Revenue Retention |
| CRDT | Conflict-free Replicated Data Type — technique for offline sync |

---

## 20. Appendix: Requirement Traceability Conventions

| Prefix | Module |
|---|---|
| FR-POS | Point of Sale |
| FR-OMS | Order Management & Omnichannel |
| FR-KDS | Kitchen Display & Production |
| FR-TBL | Tables & Reservations |
| FR-MNU | Menu & Recipes |
| FR-INV | Inventory |
| FR-PRC | Procurement |
| FR-CK | Central Kitchen |
| FR-FIN | Finance & Accounting |
| FR-PAY | Payments & Cash |
| FR-HR | HR & Workforce |
| FR-CRM | CRM, Loyalty & Marketing |
| FR-SS | Self-Service Ordering |
| FR-DLV | Delivery & Logistics |
| FR-HQ | Multi-location & Franchise |
| FR-BI | Business Intelligence |
| FR-AI | AI & Automation |
| FR-FS | Food Safety & Compliance |
| FR-MNT | Maintenance & Assets |
| FR-ADM | Administration & Security |
| FR-INT | Integrations & API |
| NFR-* | Non-functional requirements |

Each requirement should be tracked in the backlog as an epic/story linked to its ID, with acceptance criteria, test cases, and release phase.

---

*End of document.*
