import asyncio
import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app import hindsight_service as hs
from app.auth import get_optional_user
from app.database import Base, engine, get_db
from app.models import MemoryLog, User
from app.routers import auth as auth_router
from app.routers import users as users_router

log = logging.getLogger("echomind")
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
INDEX = STATIC_DIR / "index.html"
SIGNIN = STATIC_DIR / "signin.html"
SIGNUP = STATIC_DIR / "signup.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite tables on startup
    Base.metadata.create_all(bind=engine)
    log.info("SQLite database tables initialized successfully.")
    yield


app = FastAPI(title="EchoMind", docs_url=None, redoc_url=None, lifespan=lifespan)

# Include Routers
app.include_router(auth_router.router)
app.include_router(users_router.router)

SAMPLE_EXPERIENCES = [
    "Our LinkedIn post with a 6-line Python snippet for cleaning CSV files got 3x our usual saves and many comments asking for more code tips.",
    "A LinkedIn motivational quote graphic about 'never give up' got very few clicks and almost no comments.",
    "Followers repeatedly ask in comments for short step-by-step tutorials rather than long announcement posts.",
    "Posts published Tuesday mornings with a concrete before/after example consistently outperformed posts with generic advice.",
]
_seeded = False
_status_cache = {"at": 0.0, "value": None}
_hits = defaultdict(deque)


# ---------- errors ----------
class ApiError(Exception):
    def __init__(self, status, code, message, hint=""):
        self.status, self.code, self.message, self.hint = status, code, message, hint


def error_body(code, message, hint=""):
    return {"error": {"code": code, "message": message, "hint": hint}}


@app.exception_handler(ApiError)
async def _api_error(_, exc: ApiError):
    return JSONResponse(error_body(exc.code, exc.message, exc.hint), status_code=exc.status)


@app.exception_handler(RequestValidationError)
async def _validation_error(_, exc: RequestValidationError):
    return JSONResponse(
        error_body("invalid_input", "That input isn't valid.", "Write 3–2000 characters and try again."),
        status_code=422,
    )


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'"
    )
    return response


async def async_call_hindsight(coro_fn, *args, timeout=40):
    """Run native async Hindsight SDK calls safely in FastAPI's asyncio event loop."""
    try:
        return await asyncio.wait_for(coro_fn(*args), timeout=timeout)
    except hs.NotConfigured:
        raise ApiError(503, "not_configured", "Memory service isn't configured on this server.", "Set HINDSIGHT_API_KEY and HINDSIGHT_BASE_URL, then redeploy.")
    except asyncio.TimeoutError:
        raise ApiError(504, "upstream_timeout", "The memory service took too long to respond.", "Retry shortly.")
    except Exception as exc:
        log.exception("Hindsight async call failed")
        text = str(exc).lower()
        if "429" in text or "rate" in text:
            raise ApiError(429, "rate_limited", "The memory service is rate-limiting requests.", "Wait a moment and retry.")
        raise ApiError(502, "upstream_error", "Couldn't reach the memory service.", "Retry shortly. Your data was not changed.")


def rate_limit(request: Request, limit=30, window=60):
    ip = (request.headers.get("x-forwarded-for") or (request.client.host if request.client else "?")).split(",")[0].strip()
    now, hits = time.monotonic(), _hits[ip]
    while hits and now - hits[0] > window:
        hits.popleft()
    if len(hits) >= limit:
        raise ApiError(429, "rate_limited", "Too many requests.", "Wait a minute and try again.")
    hits.append(now)


def clean_platform(platform: str) -> str:
    match = next((p for p in hs.PLATFORMS if p.lower() == (platform or "").strip().lower()), None)
    if not match:
        raise ApiError(422, "invalid_platform", "Unknown platform.", "Choose " + ", ".join(hs.PLATFORMS) + ".")
    return match


class Experience(BaseModel):
    content: str = Field(min_length=3, max_length=2000)
    context: str = Field(default="Social media performance", max_length=120)
    platform: Optional[str] = Field(default="general", max_length=50)

    @field_validator("content", "context")
    @classmethod
    def _strip(cls, v: str) -> str:
        return v.strip()


# ---------- routes ----------
@app.get("/", include_in_schema=False)
def root():
    return FileResponse(INDEX, headers={"Cache-Control": "no-cache"})


@app.get("/signin", include_in_schema=False)
def signin_page():
    return FileResponse(SIGNIN, headers={"Cache-Control": "no-cache"})


@app.get("/signup", include_in_schema=False)
def signup_page():
    return FileResponse(SIGNUP, headers={"Cache-Control": "no-cache"})


@app.get("/health")
def health():
    return {"status": "healthy"}  # cheap liveness probe for Render


@app.get("/api/status")
async def status():
    """Real connectivity check against Hindsight (cached 30s)."""
    now = time.monotonic()
    if _status_cache["value"] and now - _status_cache["at"] < 30:
        return _status_cache["value"]
    value = {"bank": hs.BANK_ID, "configured": True, "reachable": False}
    try:
        await async_call_hindsight(hs.arecall_audience_memory, "audience preferences", timeout=15)
        value["reachable"] = True
    except ApiError as err:
        value["configured"] = err.code != "not_configured"
        value["reason"] = err.message
    _status_cache.update(at=now, value=value)
    return value


@app.get("/memory")
@app.get("/api/memory")
async def memory(q: str = "What type of content did the audience respond positively to?"):
    q = (q or "").strip()[:300] or "What type of content did the audience respond positively to?"
    memories = await async_call_hindsight(hs.arecall_audience_memory, q)
    return {"query": q, "memories": memories, "count": len(memories)}


@app.post("/learn")
@app.post("/api/learn")
async def learn(
    experience: Experience,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Store experience in Hindsight AI memory AND log to SQLite database.
    If authenticated, links to the user in SQLite memory_logs table.
    Preserves exact existing response format for backward compatibility.
    """
    rate_limit(request)
    result = await async_call_hindsight(hs.aretain_audience_experience, experience.content, experience.context)
    if getattr(result, "success", True) is False:
        raise ApiError(502, "retain_failed", "Hindsight didn't store that experience.", "Try again.")
    _status_cache["value"] = None

    # Log in SQLite application database if user is authenticated
    if current_user:
        log_entry = MemoryLog(
            user_id=current_user.id,
            content=experience.content,
            platform=experience.platform or "general",
            hindsight_bank=hs.BANK_ID,
        )
        db.add(log_entry)
        db.commit()

    return {"success": True, "message": "Experience stored in Hindsight memory."}


@app.get("/recommendation")
@app.get("/api/recommendation")
async def recommendation(request: Request, platform: str = "LinkedIn"):
    rate_limit(request, limit=15)
    platform = clean_platform(platform)
    memories = await async_call_hindsight(
        hs.arecall_audience_memory,
        f"What type of content did the {platform} audience respond positively to?",
    )
    if not memories:  # never ask the model to reason over nothing
        return {"state": "no_memory", "platform": platform, "memories": [], "based_on_memory": []}
    rec = await async_call_hindsight(hs.agenerate_recommendation, platform, timeout=60)
    if not rec["recommendation"]:
        raise ApiError(502, "empty_response", "The model returned an empty answer.", "Try again.")
    return {
        "state": "ok", "platform": platform, **rec,
        "reasoning": rec["why"], "memories": memories, "based_on_memory": memories,
    }


@app.post("/api/demo/seed")
async def seed_demo(request: Request):
    """Retain clearly-labelled sample experiences through the real retain path."""
    global _seeded
    rate_limit(request, limit=5)
    if _seeded:
        return {"success": True, "added": 0, "message": "Sample history was already loaded."}
    for text in SAMPLE_EXPERIENCES:
        await async_call_hindsight(hs.aretain_audience_experience, text, "SAMPLE DATA – EchoMind demo")
    _seeded = True
    return {"success": True, "added": len(SAMPLE_EXPERIENCES), "message": "Sample history stored."}
