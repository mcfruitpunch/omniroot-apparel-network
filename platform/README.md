# OmniRoot Apparel — real software foundation (v0.2 alpha)

This folder contains a **working persistent web application**, separate from the earlier browser-only concept at the repository root (\`index.html\`).

## What already works

- Register, sign in, sign out with Argon2-hashed passwords and server-stored sessions.
- Explore an explicitly **research-only** two-garment, two-fabric catalog.
- Create, update, view, export, or delete your **private** measurement profile, in centimeters.
- Submit feasibility-review requests only after required measurements are present and the fabric is compatible.
- See and withdraw **your own** saved requests.
- Submit designer concept metadata with an ownership/rights declaration, and see your own submissions.
- Export or delete your account data.
- API validation, customer-level authorization, CSRF protection, origin checks, HTTP-only session cookies, audit events without measurement values, and basic security headers.
- Automated API tests, including two-customer isolation and invalid requests.

The system intentionally has **no payments, quotes, real orders, maker access, or live manufacturing**. Garments are NOT validated production patterns. A request does not create a sale or promise manufacturing.

## Run locally

Python 3.11+ is recommended.

\`\`\`sh
cd platform
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
uvicorn server:app --reload
\`\`\`

Visit **http://127.0.0.1:8000** for the working storefront. An OpenAPI reference is available at **http://127.0.0.1:8000/api/docs**.

The SQLite database lives at \`platform/apparel.sqlite3\` by default, outside version control. For an alternate path, set \`APP_DB_PATH\` to the full path. Data persists across browser refreshes and server restarts.

## Test locally

\`\`\`sh
cd platform
python -m pytest -q tests/
\`\`\`

GitHub Actions uses \`.github/workflows/platform-tests.yml\`.

## Run in a container (development)

\`\`\`sh
docker build -f platform/Dockerfile -t omniroot-platform .
docker run --rm -p 8000:8000 -v omniroot-db:/data omniroot-platform
\`\`\`

The Docker image is not a substitute for an audited production environment.

## Hosting boundary — do not put real customer data into an unreviewed deployment

GitHub Pages can host the original static \`index.html\` demo but **cannot run this API**. The real platform needs a server or container host with persistent storage, HTTPS, backups and monitoring.

**Production intentionally refuses to start** unless both \`APP_ENV=production\`, \`APP_ORIGIN=https://your-domain\`, and \`COOKIE_SECURE=true\` are configured. Production readiness still requires, at minimum:

1. Move to managed PostgreSQL and versioned database migrations; provision backups and tested recovery.
2. Encrypt fit data at rest with vetted keys/KMS, implement precise retention, backup deletion strategy, and measurement-access audit.
3. Add registration/login rate limiting, email verification/password reset, anti-abuse protections, session rotation, monitoring and incident response.
4. Commission independent penetration testing and legal/privacy review; develop informed consent flows, a privacy notice and accessibility audit.
5. Implement verified maker identities, customer-authorized, field-scoped measurement grants, traceable pattern validation and rights licensing.
6. Add real, fairly priced quotes and payments only after garment samples and production partners are validated.

Use synthetic measurements for all development and early testing. This is **functional alpha software**, not a trustworthy public service for sensitive body data yet.

## Layout

\`\`\`
platform/
├── server.py           # Modular-monolith starting API and storage layer
├── site/
│   ├── index.html      # Customer-facing product experience
│   ├── style.css       # Responsive design system
│   └── app.js          # API-bound browser client
├── tests/test_api.py   # Security and request lifecycle tests
├── requirements.txt
└── Dockerfile
\`\`\`

## Next build slice

- Work with a patternmaker to define exact measurement protocols and physically validated sample patterns.
- Separate database, models, API routers and business services as the domains grow.
- Add verified maker invites/roles, quotes and customer-controlled measurement sharing.
- Migrate to Postgres, introduce encrypted measurement vault, and deploy a monitored staging environment.
