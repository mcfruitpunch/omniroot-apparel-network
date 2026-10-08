# OmniRoot Apparel — Prioritized Build Backlog

**Goal:** Reach a supervised, fairly paid, physically validated small-garment pilot—not a prematurely automated factory.

## P0 · Establish physical feasibility

| ID | Work item | Definition of done | Dependency |
|---|---|---|---|
| R-01 | Customer discovery | 8–12 interviews, including varied body fits, sensory/adaptive needs, cost expectations; needs synthesized without storing unnecessary personal data | None |
| R-02 | Maker/patternmaker discovery | 5–8 consultations; capacities, tools, fair labor pricing, repair/alteration constraints captured | None |
| P-01 | Choose two garments | Select two repeatable patterns and document realistic degrees of customization | R-01, R-02 |
| P-02 | Measure/fitting protocol | Clearly defined measuring instructions, cm/in handling, fit-ease convention, source/verification fields | R-01, maker review |
| P-03 | Fabric/pattern matrix | 2–3 fabrics with technical compatibility, shrinkage and drape observations for each pattern | P-01 |
| P-04 | Produce first real samples | Physically make examples, inspect dimensions and document fit corrections, actual labor and scrap | P-01–P-03 |
| L-01 | IP and compensation agreements | Designer license template, maker terms, returns/alterations responsibilities reviewed by appropriate professionals | R-02 |

## P1 · Real software foundation (after P0 feasibility)

| ID | Work item | Definition of done | Dependency |
|---|---|---|---|
| A-01 | Domain and role model | Tested customer, designer, maker, admin access with negative permission tests | L-01 |
| A-02 | Secure Fit Vault | Encryption, export/deletion, capture metadata, optional needs separated, audit trail | A-01, P-02 |
| A-03 | Scoped measurement grants | Order-specific allowlist of fields, expiry/revocation, maker view auditing | A-02 |
| A-04 | Versioned pattern & fabric library | Published designs immutable; compatibility prevents invalid pairings | P-03 |
| A-05 | Maker-aware quoting | Fair labor + material + royalties + fees + taxes + exception allowances; expires, can be refused | P-04, L-01 |
| A-06 | Order workflow | Server-authoritative state machine, idempotent checkout, quote approval, failures, cancellation/rework | A-01, A-05 |
| A-07 | Production/QA packet | Maker accepts work, sees only relevant data, uploads QA record and exception | A-03, A-04, A-06 |
| A-08 | Customer status & pickup | Customer sees honest timeline and confirms collection; manual partner handoff initially | A-06 |
| A-09 | Accessibility and usability | Human testing and WCAG 2.2 AA audit; keyboard, zoom, screen readers, reduced motion and mobile | All interfaces |
| A-10 | Operational security | Threat modeling, incident procedure, supplier vetting, backups and retention/deletion drills | A-01–A-08 |

## P2 · First paid pilot

| ID | Work item | Definition of done | Dependency |
|---|---|---|---|
| O-01 | Recruit makers/retail partner | One or two makers and one pickup option agree on service levels, pricing and data responsibilities | P0, A-01 |
| O-02 | Limited run | 20–50 garments with customer informed consent; manual exception handling available | P0–P1 |
| O-03 | Fit/cost analysis | Actual alteration/remake rate, contribution margin, time variance, maker earnings and customer feedback measured | O-02 |
| O-04 | Go/no-go decision | Document what worked, what did not, and next limited expansion; no blanket scale claim | O-03 |

## P3 · Expansion, only after a positive pilot

- Designer portal with proper asset upload, licensing metadata, version comparisons, royalty accounts.
- Multi-maker matching with transparent capabilities, load, schedule, compensation and regional routing.
- Retail measurement appointments, swatch library, pickup and repair console.
- Optional virtual drape visualization with an explicit visual-accuracy label.
- Automated pattern grading and cut nesting only for tested and production-eligible cases.
- Structured garment passports and repair/reuse tracking.

## Most useful immediate decision

Choose **the two garments** and identify **one professional maker/patternmaker** willing to help define their measurements and build the first test samples. Everything else becomes substantially more reliable when based on real making time, fit outcomes and materials.