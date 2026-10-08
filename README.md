# OmniRoot Apparel Network — v0.1 prototype

A shareable, self-contained **concept demonstration**, plus a developer-ready product blueprint.

## Open the prototype

1. Download this folder/ZIP and extract it.
2. Open `index.html` in a modern browser, or serve it via any static file server.
3. **Overview** shows the network; **Shop + customize** shows a sample catalog; **Fit Passport** validates manual inputs; **Designer Studio** submits a local design; **Maker Hub** approves designs and moves demo orders through production; **Orders** shows the timeline.

## Try one complete journey

1. Open Fit Passport and click **Load fictional sample** (or enter your own values without using sensitive real information in a demo).
2. Open Shop + customize, choose a garment, fabric and options; click **Submit demo order**.
3. Open Maker Hub, accept the job, then advance the simulated stages.
4. Open Orders to inspect the updated timeline and export the work-order JSON.
5. In Designer Studio, submit a concept; verify it is not in Shop until **Maker Hub → Mark sample approved**.

## Files

- `index.html`: complete offline single-file browser simulation, no dependencies or external requests.
- `BLUEPRINT.md`: vision, journeys, screens, domain model, privacy, API, state machines, pilot economics, build stages, acceptance tests.
- `fit-passport.schema.json`: illustrative cross-system JSON Schema for a private fit profile.
- `production-packet.schema.json`: illustrative maker-facing production packet JSON Schema.

## Important limitations

- This is a **prototype**, not a real retailer, manufacturing service, patternmaking application, or payment gateway.
- All data are stored in JavaScript memory while the page is open. It resets when reloaded. File exports deliberately download locally; protect exported body measurements.
- Prices are **fictional examples**, not commercial quotes.
- Measurement field checks are **not** a professional measurement, accurate fit model or automated drafting system.
- No files are uploaded. The Designer Studio optional file field records a local filename only.
- Do not use the example production JSON or sample body measurements for physical garment manufacture.

## Suggested repo shape for the real build

```text
apps/web/                 # Customer, designer, maker PWA
services/api/             # Auth + Fit Vault + catalog + orders (modular monolith)
packages/domain/          # Typed models and workflows
packages/design-packets/  # Neutral, versioned garment specifications
packages/ui/              # Shared accessible components
infra/                    # Environment config and deployment
research/                 # Sample studies and maker cost interviews
standards/                # Licensed or referenced measurement definitions
```

Review `BLUEPRINT.md` before implementing APIs or collecting real user data.

## GitHub publication

See [GitHub launch checklist](docs/GITHUB_SETUP.md) for the planned repository, GitHub Pages deployment, and limitations. The project is a static prototype and should not be interpreted as a production-ready service.

## Contributing / licensing

The repository is intended to support later collaborative development. A software/content license has **not** yet been selected. Do not assume that public access grants redistribution rights; confirm ownership and licensing before accepting contributed designs, patterns, or imagery.