# OmniRoot Apparel Network
## Functional Product Blueprint — v0.1 (7 October 2026)

**Status:** Concept blueprint + browser-based interactive simulation. This package is **not** a live marketplace, validated garment fitting tool, production service, or retailer partnership.

**Product thesis:** A customer-owned Fit Passport, reusable garment designs, materials catalog, independent creator licenses, skilled makers, and pickup/repair points can form an interoperable apparel network. The platform coordinates trust and production without requiring ownership of every factory or storefront.

## 1. User promise and principles

> *Your body, your fabric, your design. Made with the people and technology best suited to the work.*

**Primary user:** A customer frustrated by inconsistent sizing and generic assortments, who wants accessible customization without hiring a dedicated bespoke tailor for every item.

**Other essential users:** Independent designer/patternmaker; garment maker/workshop; quality reviewer; retail fitting-and-pickup partner; platform administrator.

**Principles:**
1. **Portable fit data.** The person owns access to their measurements and can export, edit, and request erasure.
2. **Human production accountability.** Automated recommendations never constitute pattern approval, fitted-garment guarantees, or production acceptance.
3. **Interoperability over lock-in.** Versioned design packages, explicit licenses, standard units, and API contracts allow competing makers and retailers to participate.
4. **Transparent compensation.** Quotes separate materials, making, creator license, coordination, taxes, and fulfillment rather than hiding labor in an undifferentiated total.
5. **Accessibility beyond standard sizing.** Consider seated fit, limited dexterity, texture and seam tolerances, prosthetics, asymmetry, and non-gendered navigation.
6. **Regenerative behavior must be measured.** Track scrap, repairability, expected use, freight, returned garments, actual reuse, and labor conditions; do not equate on-demand production with automatic sustainability.
7. **Consent and maker dignity.** Neither body measurements nor makers' hourly economics are data to exploit.

## 2. Product surfaces

| Surface | What user needs to accomplish | Pilot screens | Later extensions |
|---|---|---|---|
| Customer storefront | Discover, filter, price, customize, buy | Browse garments; design detail; color/fabric/cut; estimate; order timeline | Body-aware visualization; real payments; fitting appointment; multi-item cart |
| Fit Passport | Capture, correct, validate, selectively share | Manual measurements; preferences; optional accommodation notes; JSON export | Measurement tutorials; professional verification; scan import; selective encrypted sharing; permission log |
| Designer Studio | Prepare, license, revise and sell a production design | Design form; rights declaration; technical review status | Pattern-file upload; version diff; tech-pack checks; royalty ledger; collaborative commissions |
| Maker Hub | Decide what work to accept, make it safely, document quality | Incoming orders; minimal measurement packet; accept/advance; JSON work order; design concept approval | Capacity calendar; equipment/capabilities; sewing operations; cut tickets; QA photos; payment and dispute workflows |
| Retail/partner point | Support fitting, samples, pickup, repair | Modeled as pickup choice in v0.1 | Partner console; scan and measurement appointments; fitting rooms; stock/sample library; real pickup verification |
| Trust/admin | Resolve exceptions, check rights, mediate quotes, enforce controls | Product rules in this blueprint | Identity verification, moderation, audit logs, abuse reporting, recalls, removal requests |

## 3. Core experience: one garment order

### A. Fit creation
1. Person chooses `cm` or `in`, sees measurement definition and how-to guide.
2. Enters measured values, capture source (self, tailor, scan), and date; separately records fit preferences and optional accommodations.
3. System checks plausibility and missing required dimensions; it must **not** claim anatomical accuracy based on format checks.
4. Fit Passport is saved in a private store, not a maker-accessible global profile.
5. Person can export, update, remove, and inspect recent access to the record.

### B. Catalog and design
1. Customer explores **ready-to-wear retail inventory**, **made-to-order approved base patterns**, and **designer-submitted approved designs** (separate fulfillment classes).
2. Each made-to-order design has a versioned pattern, valid material families, configurable options, required body dimensions, production constraints, and license.
3. A designer submits concept assets and licensing terms to review. Concepts do not immediately become purchasable.
4. Reviewer/patternmaker validates safety, technical completeness, sample feasibility, compatible fabrics and legal/IP conditions before publishing a design version.

### C. Configuring and quoting
1. Customer chooses garment version, material SKU, colorway, compatible modifications and fulfillment preference.
2. System builds an immutable **configuration snapshot** and provisional bill of materials.
3. A *non-binding estimate* is shown until production feasibility and maker capacity are confirmed.
4. Production engine matches eligible makers by fabrication technique, equipment, minimum order, timeline, region, work conditions and price.
5. Maker confirms work scope, pricing and feasible lead time; if a change is proposed, the customer approves it before payment/production.
6. A production-specification version is locked after approval; any material changes require a revision and customer signoff.

### D. Production and handoff
1. Customer authorizes a **purpose-limited measurement grant** for the selected maker and order; only relevant fields are disclosed.
2. Work order moves through accepted → cutting → sewing → QA → pickup-ready.
3. Cutting/sewing can be performed by humans, machines or a combination; every automated stage has quality checks and a named accountable party.
4. QA records critical garment dimensions, defects, approved deviations and remake decision.
5. Pickup partner verifies the claimed garment, and the customer records fit outcome or requests an alteration/remake.
6. Consent-based order history supports later repairs or reorders without indefinitely exposing private body data to the maker.

**Exception handling:** Missing pattern asset, out-of-stock fabric, unfulfillable accommodation, capacity rejection, quote increase, failed QA, damaged garment, no-show pickup, refund, return and data deletion. Each needs a named responsible actor and an explicit state transition, not free-form notes.

## 4. State machines

### Design publication
`draft → submitted → rights_check → technical_review → sample_required → approved → published`

Branches: `changes_requested`, `rejected`, `withdrawn`, `suspended`. Each published design references an **immutable version**; an update creates a new version and cannot silently change an accepted order.

### Customer order / payment (real system)
`cart → provisional_estimate → fit_and_rights_checks → maker_quote → customer_approval → payment_authorization → production_accepted → cutting → assembly → QA → pickup_ready → collected → completed`

Branches: `quote_expired`, `maker_declined`, `customer_cancelled`, `fabric_unavailable`, `QA_failed/rework`, `alteration_requested`, `refunded`, `disputed`. Payment capture is policy-specific; never represent an unaccepted estimate as a paid order.

### Prototype simulator (`index.html`)
`submitted → accepted → cutting → sewing → quality_check → ready_for_pickup → collected`

**Deliberate simplification:** The simulator does **not** perform maker routing, sample validation, capacity scheduling, real quotes, transactions, authentication, storage, shipping, or production.

## 5. Information architecture (v0 → v1)

```text
Home
├── Shop
│   ├── Available now (future integration to traditional ready-to-wear)
│   ├── Made to order / approved patterns [v0]
│   ├── Designers [v0 form, review queue]
│   └── Garment builder [v0]
├── My Fit Passport [v0]
│   ├── Measurements / units / methods
│   ├── Fit preferences / accommodations
│   └── Grant history / export / delete
├── My Orders [v0 simulated]
│   ├── Quotes and approvals
│   ├── Making timeline
│   └── Pickup, feedback, repairs
├── Designer Studio [v0]
│   ├── Create design / submit packet
│   ├── Technical review and revisions
│   └── Catalog, licensing, payouts
├── Maker Hub [v0]
│   ├── Offered jobs and capacity
│   ├── Job specification and relevant fit data
│   ├── Production checkpoints and QA
│   └── Billing and compensation
└── Partner / Admin consoles [later]
```

## 6. Data model — entities and ownership

Every production-critical record carries `id`, `created_at`, `updated_at`, a version, actor/audit data, and immutable snapshots at approval points.

| Entity | Essential fields | Owner / access model |
|---|---|---|
| `user` | id, roles, contact preferences, locale | User and administrative subset |
| `fit_profile` | id, owner_id, label, unit, source, measured_at, revision | Private to customer; not exposed by public lookup |
| `fit_measurement` | profile_id, type, value, unit, measurement_definition_id, confidence/source | Customer; share only fields needed for accepted job |
| `fit_preferences` | ease, pressure, closures, sensory considerations, mobility needs | Customer; accommodation notes require separate consent |
| `measurement_grant` | owner, order, maker, permitted_fields, purpose, expires_at, revoked_at | Customer controls; machine-enforced access |
| `design` / `design_version` | designer, title, rights claim, license, state, allowed customization, pattern version | Designer owns IP; marketplace holds limited licensed rights |
| `pattern_asset` | file reference, hash, supported sizes/morphologies, sewing notes, validation state | Restricted creator + technical reviewers + authorized makers |
| `fabric_sku` | fiber composition, weave/knit, weight, stretch, shrinkage, colorway, supplier, lot | Supplier catalog; provenance verified before production |
| `design_fabric_rule` | design version, fabric family/SKU, compatible options, validation evidence | Technical review team; versioned |
| `maker` / `maker_capability` | operating region, equipment, techniques, compliance, capacity, minimums | Maker maintains, verified by network |
| `order` / `order_line` | buyer, design snapshot, option snapshot, quote, retail point, state | Customer; scoped access for fulfillment parties |
| `quote` | labor, material, license, network fee, tax, fulfillment, currency, expiry | Customer + maker + platform; immutable on approval |
| `work_order` | approved tech pack, relevant fit snapshot, routing decision, schedule | Assigned maker only; least-privilege view |
| `quality_event` | checkpoint, result, images/measurements, rework disposition, reviewer | Maker, authorized QA, selected customer-facing summary |
| `pickup_event` | location, code, verification, timestamp, handoff outcome | Fulfillment partner only |
| `repair_case` | garment/line, concern, repair plan, cost consent, responsible maker | Customer and assigned repair provider |

**Measurement definition notes:** The ISO 8559-1:2017 standard provides anthropometric measurement terminology. Use appropriate licensed standard references for implementation, and add tested consumer instructions for each selected measure. Do not claim to have reproduced the text of the standard.

### Fit Passport example

```json
{
  "fit_profile_id": "fit_demo_001",
  "owner_id": "demo_customer",
  "unit": "cm",
  "measurement_method": "self_reported",
  "measurement_date": "2026-10-07",
  "measurements": {
    "chest_circumference": { "value": 100, "unit": "cm", "definition_id": "chest_v1" },
    "waist_circumference": { "value": 86, "unit": "cm", "definition_id": "waist_v1" },
    "hip_circumference": { "value": 102, "unit": "cm", "definition_id": "hip_v1" },
    "inseam": { "value": 78, "unit": "cm", "definition_id": "inseam_v1" }
  },
  "preferences": { "ease": "relaxed" },
  "demo_only": true
}
```

### Maker packet example

```json
{
  "work_order_id": "work_demo_001",
  "design_version_id": "everyday_overshirt_v1",
  "fabric_sku": "cotton_twill_clay_demo",
  "cut": "relaxed",
  "relevant_fit": { "chest_circumference_cm": 100, "waist_circumference_cm": 86 },
  "authorized_fields": ["chest_circumference", "waist_circumference"],
  "customer_identity": null,
  "measurement_grant_expires_at": "2026-11-07T00:00:00Z",
  "demo_only": true
}
```

**Data policy:** The maker should not receive name, contact, optional sensory notes, or unrelated body dimensions unless a separate operational need and explicit grant exists. Real fulfillment logistics use a separate protected handoff layer.

## 7. Suggested technical architecture

```text
Customer web / mobile PWA
Designer web portal              ┌──────────────────────┐
Maker / retail portal ──────────►│ API gateway + roles  │
                                 └──────────┬───────────┘
         ┌───────────────────────────────────┼──────────────────────────┐
         ▼                                   ▼                          ▼
 Identity + permissions               Catalog + design           Orders + quoting
         │                            versions + materials             │
         ▼                                   ▼                          ▼
 Encrypted Fit Vault ◄──── scoped grants ────┴─────► Maker routing + work orders
         │                                                              │
         └──────────── Audit events / notifications / operations ────────┘
                                          │
                                QA / pickup / alterations
```

**Implementation proposal (not a commitment):**
- Front end: accessible responsive web application and installable PWA before separate mobile apps.
- Back end: modular monolith initially (clear domain boundaries), with PostgreSQL for transactional records, object storage for licensed design files, and asynchronous jobs for noncritical workflows.
- Domain modules: Auth & roles; Fit Vault & grants; Designer & rights; Catalog; Fabric & sourcing; Quotes & routing; Orders; Work orders & QA; Pickup & aftercare; Ledger & audit.
- Integration boundary: versioned REST/JSON endpoints and downloadable/exportable neutral design packages; later connect payment, logistics, POS, and manufacturing systems through adapters.
- Event bus can be introduced when real throughput justifies it; avoid premature microservices.
- Security baseline: encryption in transit/at rest, MFA for makers/admins, least privilege, time-limited grants, audit log, incident response, retention limits, and tested deletion/export.

### Initial API contract (illustrative; not implemented)

| HTTP | Resource | Why |
|---|---|---|
| `POST` | `/fit-profiles` | Create a private passport revision |
| `GET` | `/fit-profiles/{id}` | Retrieve own measurements |
| `POST` | `/measurement-grants` | Approve limited fields for a specific work order |
| `DELETE` | `/measurement-grants/{id}` | Revoke future access |
| `POST` | `/designs` | Submit design metadata for review |
| `POST` | `/designs/{id}/versions` | Submit an immutable revision |
| `GET` | `/catalog/garments?fabric=...` | Browse approved designs and compatible fabrics |
| `POST` | `/quotes` | Calculate provisional cost and send maker requests |
| `POST` | `/orders` | Create approved order snapshot following consent/payment checks |
| `GET` | `/orders/{id}/timeline` | View state/events relevant to a customer |
| `POST` | `/work-orders/{id}/transitions` | Authenticated maker stage change with conditions |
| `POST` | `/quality-events` | Record inspection, deviations, rework |
| `POST` | `/pickup-events` | Verify retail handoff |

**Critical controls:** Idempotency keys for payment/order creation; optimistic concurrency on status changes; role-scoped event views; attachment malware scans; signed download URLs; maker-specific file access; auditable overrides; no storing raw scans by default.

## 8. Production viability gates

Not every fabric works with every pattern. Before allowing checkout for a made-to-order garment, require:

- **Design:** a rights-reviewed, versioned tech pack with critical dimensions and seam/construction notes.
- **Material:** tested shrinkage, stretch, drape, needle/thread compatibility, lot availability, color and construction constraints.
- **Fit:** appropriate required body measurements and defined allowances; distinction among fitted, loose and adaptive patterns.
- **Maker:** capability and equipment match, compliant work terms, estimated cycle time, capacity, and compensation.
- **Fulfillment:** confirmed pickup location or shipping route, risk buffer, QA and remake policy.

**Exception:** If any gate is uncertain, offer **consultation/quote request**, not immediate guaranteed manufacturing.

### Example illustrative price model (USD, not market-validated)

- Pattern base labor + standard fabric: $78
- Premium linen blend: +$12
- Extended hem: +$14
- Optional licensed designer royalty: +$12
- Coordination fee: +$9
- **Example price:** $125

Taxes, scanning/fitting labor, quality rework, platform payment fees, transport and returns require real estimation. The simulator uses fictional examples; do not treat them as economically viable rates.

## 9. Phase boundaries and launch criteria

### Phase 0 — Research and feasibility (before paid orders)
- Interview 8–12 customers across different fit/accessibility needs and 5–8 independent garment makers or patternmakers.
- Physically sample **two** repeatable garment archetypes, such as overshirts and loose trousers, with 2–3 carefully validated fabric families.
- Document costed operation sequence and maker payment; build policies for alterations, remakes, and intellectual property.
- Confirm target user willingness to pay and expected fitting burden.

### Phase 1 — Concierge pilot (20–50 garments; proposed experiment size)
- Manual measurements, small catalog, human tech-pack/fit approval, partner maker, transparent quoted lead time, explicit customer approval and local pickup.
- Log quoted versus actual material/labor cost, cut-to-delivery time, alteration/remake rate, fit satisfaction and net maker earnings.
- Do not broaden design freedom until work is reproducible.

### Phase 2 — Marketplace (only if phase 1 works)
- Designer submission/review, creator payouts, multi-maker matching, fabric supplier inventory, customer permissions, retailer services and ratings that do not unfairly penalize accommodations.

### Phase 3 — Retail and automation
- Partner fitting/pickup counters → finishing workshops → regional flexible manufacturing nodes.
- Automate eligible pattern adjustments, cut nesting, workflow scheduling and suitable sewing/weaving processes; keep accountable quality oversight.

### Go / no-go gates

| Gate | What must be learned |
|---|---|
| Repeatable fit | What proportion of customers keep the garment without an avoidable alteration? |
| Positive contribution | Does sale price cover materials, fairly paid labor, licensing, returns, fees and service? |
| Reproducible lead time | Can makers consistently meet the promised date under normal disruptions? |
| Customer trust | Are measurements easy to control, correct and delete? |
| Creator value | Can designers receive useful net royalties without transferring away their IP? |
| Environmental improvement | Is scrap/use-life genuinely better than an appropriate ready-to-wear benchmark? |

Avoid setting arbitrary universal thresholds before maker consultation and baseline measurements.

## 10. Demo acceptance tests

**User-visible requirements for `index.html`:**
1. Choose a garment; the configuration panel changes.
2. Only compatible sample fabrics are shown for that garment.
3. Change the material and colorway; the illustrative SVG preview and price update.
4. Load sample Fit Passport or enter measurements; validation must be required for a demo order.
5. Toggle cm/in and verify values convert reasonably; unit switching requires revalidation.
6. Submit a demo order; inspect order timeline and scoped maker fit fields.
7. Visit Maker Hub; accept and advance the order through all simulated statuses.
8. Export order JSON and Fit Passport JSON.
9. Submit an independent designer concept; it must not appear in the customer catalog until marked approved by the Maker Hub.
10. Reload page; confirm all demo data are gone (memory-only prototype).
11. Test keyboard navigation and narrow-screen layout; audit WCAG 2.2 AA rather than claiming conformance prematurely.

### What is NOT built in this artifact

Accounts; persistent encrypted server data; licensed standards or measurement guides; real pattern CAD generation; real payment; tax computation; real inventory; automatic maker matching; delivery scheduling; verification of IP ownership; genuine maker technical signoff; accessibility certification; real retail partnership; true body-scan 3D preview; labor policy enforcement.

## 11. Next practical build decision

**First make a real physical sample with a local maker, not a full automation plant.** The key unknown is how reliably a bounded set of patterns adapts to people while providing fair compensation and acceptable cost.

A useful work package is:
- `WP-01` Fit Passport definitions, capture tutorial, privacy requirements and scoped grants.
- `WP-02` Garment v1 technical packs, fabric compatibility matrix and sample testing.
- `WP-03` Quote engine with maker-informed labor and material costs.
- `WP-04` Order lifecycle and maker approvals with exception states.
- `WP-05` Design-rights review and royalty accounting.

**Recommended near-term milestone:** an accessible end-to-end proof of concept for **two garments, two fabrics per garment, one or two makers, and one pickup site**. Validate physical fit and unit economics before expanding designer freedom.

## 12. Public reference anchors

- ISO 8559-1:2017 — `https://www.iso.org/standard/61686.html` (body measurement definitions; confirmed current by ISO in 2026).
- W3C WCAG 2.2 Quick Reference — `https://www.w3.org/WAI/WCAG22/quickref/` (accessibility success criteria and techniques).
- NIST Privacy Framework — `https://www.nist.gov/privacy-framework` (privacy-risk management).

These are design reference anchors. The prototype and blueprint have **not** been independently certified against them.