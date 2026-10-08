"""OmniRoot Apparel: first persistent, customer-facing software slice.

Not a checkout, production scheduler, validated fitting tool, or public deployment.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator

BASE = Path(__file__).resolve().parent
SITE = BASE / "site"
SESSION_COOKIE = "omniroot_session"
SESSION_TTL = 7 * 24 * 3600
HASHER = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=2)
MEASUREMENT_KEYS = {"chest_cm", "waist_cm", "hip_cm", "inseam_cm"}
CATALOG = [
    {
        "id": "overshirt-v1", "name": "Everyday Overshirt", "type": "made_to_order_concept",
        "description": "Relaxed button-front overshirt. Pattern and material options require physical validation.",
        "required_measurements": ["chest_cm", "hip_cm"],
        "fabric_ids": ["cotton-twill", "linen-blend"], "status": "research_only",
    },
    {
        "id": "trouser-v1", "name": "Relaxed Trouser", "type": "made_to_order_concept",
        "description": "Easy-fitting trouser; no fit or material compatibility has been physically certified.",
        "required_measurements": ["waist_cm", "hip_cm", "inseam_cm"],
        "fabric_ids": ["cotton-twill"], "status": "research_only",
    },
]
FABRICS = [
    {"id": "cotton-twill", "name": "Cotton Twill", "composition": "Cotton (illustrative)", "status": "unverified_sample"},
    {"id": "linen-blend", "name": "Linen Blend", "composition": "Linen/cotton blend (illustrative)", "status": "unverified_sample"},
]


def now() -> int:
    return int(time.time())


def uid() -> str:
    return str(uuid.uuid4())


@contextmanager
def database(path: str):
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
 id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
 created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
 token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 csrf_token TEXT NOT NULL, expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS fit_profiles (
 user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
 measurements_json TEXT NOT NULL, method TEXT NOT NULL, preference TEXT NOT NULL,
 updated_at INTEGER NOT NULL, revision INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS design_submissions (
 id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 name TEXT NOT NULL, description TEXT NOT NULL, status TEXT NOT NULL,
 created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS order_requests (
 id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 garment_id TEXT NOT NULL, fabric_id TEXT NOT NULL, status TEXT NOT NULL,
 created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events (
 id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 action TEXT NOT NULL, created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_requests_user ON order_requests(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_designs_user ON design_submissions(user_id, created_at);
"""


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Credentials(StrictModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Enter a valid email address")
        return value


class FitInput(StrictModel):
    measurements: dict[str, float] = Field(min_length=1, max_length=4)
    method: str = Field(default="self_reported")
    preference: str = Field(default="regular")

    @field_validator("measurements")
    @classmethod
    def check_measurements(cls, measurements: dict[str, float]) -> dict[str, float]:
        for key, value in measurements.items():
            if key not in MEASUREMENT_KEYS or not (20 <= value <= 250):
                raise ValueError("Only supported centimeter measurements from 20 to 250 are accepted")
        return measurements

    @field_validator("method")
    @classmethod
    def check_method(cls, value: str) -> str:
        if value not in ("self_reported", "professional"):
            raise ValueError("Unsupported measurement method")
        return value

    @field_validator("preference")
    @classmethod
    def check_preference(cls, value: str) -> str:
        if value not in ("relaxed", "regular", "tailored"):
            raise ValueError("Unsupported fit preference")
        return value


class OrderInput(StrictModel):
    garment_id: str
    fabric_id: str


class DesignInput(StrictModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=12, max_length=1000)
    rights_confirmed: bool


class DeleteInput(StrictModel):
    password: str


def catalog_garment(garment_id: str):
    return next((g for g in CATALOG if g["id"] == garment_id), None)


def session_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def audit(conn: sqlite3.Connection, user_id: str, action: str):
    conn.execute(
        "INSERT INTO audit_events(id,user_id,action,created_at) VALUES(?,?,?,?)",
        (uid(), user_id, action, now()),
    )


def create_app(db_path: str | None = None) -> FastAPI:
    path = db_path or os.getenv("APP_DB_PATH", str(BASE / "apparel.sqlite3"))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with database(path) as conn:
        conn.executescript(SCHEMA)

    is_production = os.getenv("APP_ENV", "development") == "production"
    app_origin = os.getenv("APP_ORIGIN", "").rstrip("/")
    if is_production and (not app_origin.startswith("https://") or os.getenv("COOKIE_SECURE") != "true"):
        raise RuntimeError("Production requires APP_ORIGIN=https://... and COOKIE_SECURE=true")
    app = FastAPI(title="OmniRoot Apparel MVP", version="0.2.0", docs_url="/api/docs")
    app.state.db_path = path

    @app.middleware("http")
    async def browser_safety(request: Request, call_next):
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            origin = request.headers.get("origin")
            if origin:
                trusted = app_origin or str(request.base_url).rstrip("/")
                if origin.rstrip("/") != trusted:
                    return Response("Origin not allowed", status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; script-src 'self'; "
            "img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        )
        response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "no-cache"
        return response

    def auth(token: str | None = Cookie(default=None, alias=SESSION_COOKIE)) -> dict:
        if not token:
            raise HTTPException(401, "Sign in to continue")
        with database(path) as conn:
            row = conn.execute(
                """SELECT users.id, users.email, sessions.csrf_token
                   FROM sessions JOIN users ON users.id=sessions.user_id
                   WHERE sessions.token_hash=? AND sessions.expires_at>?""",
                (session_hash(token), now()),
            ).fetchone()
        if not row:
            raise HTTPException(401, "Session expired; sign in again")
        return dict(row)

    def protect(user: dict = Depends(auth), csrf: str | None = Header(None, alias="X-CSRF-Token")) -> dict:
        if not csrf or not hmac.compare_digest(csrf, user["csrf_token"]):
            raise HTTPException(403, "Invalid CSRF token")
        return user

    def start_session(response: Response, user_id: str, email: str) -> dict:
        token, csrf = secrets.token_urlsafe(48), secrets.token_urlsafe(32)
        expires_at = now() + SESSION_TTL
        with database(path) as conn:
            conn.execute(
                "INSERT INTO sessions(token_hash,user_id,csrf_token,expires_at) VALUES(?,?,?,?)",
                (session_hash(token), user_id, csrf, expires_at),
            )
        response.set_cookie(
            SESSION_COOKIE, token, max_age=SESSION_TTL,
            secure=is_production or os.getenv("COOKIE_SECURE") == "true",
            httponly=True, samesite="lax", path="/",
        )
        return {"id": user_id, "email": email, "csrf_token": csrf}

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "omniroot-apparel"}

    @app.get("/api/catalog")
    def catalog():
        return {"garments": CATALOG, "fabrics": FABRICS, "currency": None, "checkout_enabled": False}

    @app.post("/api/auth/register", status_code=201)
    def register(data: Credentials, response: Response):
        user_id = uid()
        with database(path) as conn:
            try:
                conn.execute(
                    "INSERT INTO users(id,email,password_hash,created_at) VALUES(?,?,?,?)",
                    (user_id, data.email, HASHER.hash(data.password), now()),
                )
                audit(conn, user_id, "account.created")
            except sqlite3.IntegrityError:
                raise HTTPException(409, "An account with this email already exists")
        return start_session(response, user_id, data.email)

    @app.post("/api/auth/login")
    def login(data: Credentials, response: Response):
        with database(path) as conn:
            row = conn.execute(
                "SELECT id,email,password_hash FROM users WHERE email=?", (data.email,)
            ).fetchone()
        if not row:
            raise HTTPException(401, "Incorrect email or password")
        try:
            HASHER.verify(row["password_hash"], data.password)
        except (VerifyMismatchError, VerificationError):
            raise HTTPException(401, "Incorrect email or password")
        return start_session(response, row["id"], row["email"])

    @app.get("/api/me")
    def me(user: dict = Depends(auth)):
        return user

    @app.post("/api/auth/logout")
    def logout(response: Response, token: str | None = Cookie(None, alias=SESSION_COOKIE),
               user: dict = Depends(protect)):
        with database(path) as conn:
            conn.execute("DELETE FROM sessions WHERE token_hash=?", (session_hash(token),))
        response.delete_cookie(SESSION_COOKIE, path="/")
        return {"signed_out": True}

    @app.get("/api/fit-profile")
    def get_fit(user: dict = Depends(auth)):
        with database(path) as conn:
            row = conn.execute(
                "SELECT * FROM fit_profiles WHERE user_id=?", (user["id"],)
            ).fetchone()
        if not row:
            return {"profile": None}
        return {"profile": {
            "measurements": json.loads(row["measurements_json"]),
            "method": row["method"], "preference": row["preference"],
            "revision": row["revision"], "updated_at": row["updated_at"]
        }}

    @app.put("/api/fit-profile")
    def save_fit(data: FitInput, user: dict = Depends(protect)):
        with database(path) as conn:
            conn.execute(
                """INSERT INTO fit_profiles(user_id,measurements_json,method,preference,updated_at,revision)
                   VALUES(?,?,?,?,?,1)
                   ON CONFLICT(user_id) DO UPDATE SET
                   measurements_json=excluded.measurements_json,
                   method=excluded.method, preference=excluded.preference,
                   updated_at=excluded.updated_at, revision=fit_profiles.revision+1""",
                (user["id"], json.dumps(data.measurements), data.method, data.preference, now()),
            )
            audit(conn, user["id"], "fit.updated")
        return {"saved": True}

    @app.delete("/api/fit-profile")
    def delete_fit(user: dict = Depends(protect)):
        with database(path) as conn:
            conn.execute("DELETE FROM fit_profiles WHERE user_id=?", (user["id"],))
            audit(conn, user["id"], "fit.deleted")
        return {"deleted": True}

    @app.post("/api/requests", status_code=201)
    def request_garment(data: OrderInput, user: dict = Depends(protect)):
        garment = catalog_garment(data.garment_id)
        if not garment:
            raise HTTPException(404, "Unknown garment")
        if data.fabric_id not in garment["fabric_ids"]:
            raise HTTPException(422, "Fabric is not compatible with this design")
        with database(path) as conn:
            profile = conn.execute(
                "SELECT measurements_json FROM fit_profiles WHERE user_id=?", (user["id"],)
            ).fetchone()
            values = json.loads(profile["measurements_json"]) if profile else {}
            missing = sorted(set(garment["required_measurements"]) - set(values))
            if missing:
                raise HTTPException(422, {"missing_measurements": missing})
            request_id = uid()
            conn.execute(
                """INSERT INTO order_requests(id,user_id,garment_id,fabric_id,status,created_at)
                   VALUES(?,?,?,?,?,?)""",
                (request_id, user["id"], data.garment_id, data.fabric_id,
                 "awaiting_human_review", now()),
            )
            audit(conn, user["id"], "request.created")
        return {"id": request_id, "status": "awaiting_human_review",
                "message": "Expression of interest only; no order, quote or payment has been placed."}

    @app.get("/api/requests")
    def list_requests(user: dict = Depends(auth)):
        with database(path) as conn:
            rows = conn.execute(
                """SELECT id,garment_id,fabric_id,status,created_at FROM order_requests
                   WHERE user_id=? ORDER BY created_at DESC,id DESC""", (user["id"],)
            ).fetchall()
        return {"requests": [dict(row) for row in rows]}

    @app.post("/api/requests/{request_id}/withdraw")
    def withdraw(request_id: str, user: dict = Depends(protect)):
        with database(path) as conn:
            row = conn.execute(
                "SELECT status FROM order_requests WHERE id=? AND user_id=?",
                (request_id, user["id"]),
            ).fetchone()
            if not row:
                raise HTTPException(404, "Request not found")
            if row["status"] != "awaiting_human_review":
                raise HTTPException(409, "Request cannot be withdrawn in this state")
            conn.execute(
                "UPDATE order_requests SET status='withdrawn' WHERE id=? AND user_id=?",
                (request_id, user["id"]),
            )
            audit(conn, user["id"], "request.withdrawn")
        return {"status": "withdrawn"}

    @app.post("/api/designs", status_code=201)
    def submit_design(data: DesignInput, user: dict = Depends(protect)):
        if not data.rights_confirmed:
            raise HTTPException(422, "You must confirm you hold the rights to submit this concept")
        design_id = uid()
        with database(path) as conn:
            conn.execute(
                """INSERT INTO design_submissions(id,user_id,name,description,status,created_at)
                   VALUES(?,?,?,?,?,?)""",
                (design_id, user["id"], data.name.strip(), data.description.strip(),
                 "awaiting_technical_review", now()),
            )
            audit(conn, user["id"], "design.submitted")
        return {"id": design_id, "status": "awaiting_technical_review"}

    @app.get("/api/designs")
    def my_designs(user: dict = Depends(auth)):
        with database(path) as conn:
            rows = conn.execute(
                """SELECT id,name,description,status,created_at FROM design_submissions
                   WHERE user_id=? ORDER BY created_at DESC,id DESC""", (user["id"],)
            ).fetchall()
        return {"designs": [dict(row) for row in rows]}

    @app.get("/api/export")
    def export_data(user: dict = Depends(auth)):
        with database(path) as conn:
            fit = conn.execute(
                "SELECT measurements_json,method,preference,revision,updated_at FROM fit_profiles WHERE user_id=?",
                (user["id"],),
            ).fetchone()
            designs = conn.execute(
                "SELECT id,name,description,status,created_at FROM design_submissions WHERE user_id=?",
                (user["id"],),
            ).fetchall()
            requests = conn.execute(
                "SELECT id,garment_id,fabric_id,status,created_at FROM order_requests WHERE user_id=?",
                (user["id"],),
            ).fetchall()
        return {"account": {"email": user["email"]},
                "fit_profile": dict(fit) | {"measurements": json.loads(fit["measurements_json"])} if fit else None,
                "designs": [dict(row) for row in designs],
                "requests": [dict(row) for row in requests]}

    @app.delete("/api/account")
    def delete_account(data: DeleteInput, response: Response, user: dict = Depends(protect)):
        with database(path) as conn:
            row = conn.execute(
                "SELECT password_hash FROM users WHERE id=?", (user["id"],)
            ).fetchone()
            try:
                HASHER.verify(row["password_hash"], data.password)
            except (VerifyMismatchError, VerificationError):
                raise HTTPException(403, "Incorrect password")
            conn.execute("DELETE FROM users WHERE id=?", (user["id"],))
        response.delete_cookie(SESSION_COOKIE, path="/")
        return {"deleted": True}

    app.mount("/assets", StaticFiles(directory=SITE), name="assets")

    @app.get("/", include_in_schema=False)
    def home():
        return FileResponse(SITE / "index.html", media_type="text/html")

    return app


app = create_app()
