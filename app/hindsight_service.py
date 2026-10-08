"""Thin, defensive wrapper around the Hindsight SDK (retain / recall / reflect)."""
import json
import os
import re
import threading

from dotenv import load_dotenv

load_dotenv()

BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "social-audience")
PLATFORMS = ("LinkedIn", "Instagram", "YouTube", "X")


class NotConfigured(RuntimeError):
    """HINDSIGHT_BASE_URL / HINDSIGHT_API_KEY are missing."""


_client = None
_lock = threading.Lock()


def client():
    """Create the SDK client lazily so a missing key never crashes app startup."""
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                url = os.getenv("HINDSIGHT_BASE_URL")
                key = os.getenv("HINDSIGHT_API_KEY")
                if not url or not key:
                    raise NotConfigured("Hindsight credentials are not configured.")
                from hindsight_client import Hindsight

                _client = Hindsight(url, key)
    return _client


# Synchronous wrappers
def retain_audience_experience(content: str, context: str = "Social media performance"):
    return client().retain(
        BANK_ID, content, context=context, metadata={"source": "echomind"}
    )


def recall_audience_memory(query: str) -> list[str]:
    result = client().recall(BANK_ID, query, max_tokens=700, budget="low")
    seen, memories = set(), []
    for item in getattr(result, "results", None) or []:
        text = (getattr(item, "text", "") or "").strip()
        if text and text.lower() not in seen:
            seen.add(text.lower())
            memories.append(text)
    return memories


REFLECT_PROMPT = """What should this team do for its next {platform} post?

Use ONLY the audience's previous experiences stored in memory. Do not invent audience behavior.
Respond with a single JSON object and nothing else, using exactly these keys:
{{"recommendation": "one concise, practical action (max 2 sentences)",
  "why": "one or two sentences tracing the advice to specific remembered behavior",
  "avoid": "what the memory suggests NOT to do (empty string if memory says nothing)"}}"""


def generate_recommendation(platform: str) -> dict:
    """Reflect over memory and return {recommendation, why, avoid}; tolerate non-JSON output."""
    response = client().reflect(
        BANK_ID, REFLECT_PROMPT.format(platform=platform), budget="low"
    )
    return parse_reflection(getattr(response, "text", "") or "")


# Native Async wrappers for FastAPI async route handlers
async def aretain_audience_experience(content: str, context: str = "Social media performance"):
    return await client().aretain(
        BANK_ID, content, context=context, metadata={"source": "echomind"}
    )


async def arecall_audience_memory(query: str) -> list[str]:
    result = await client().arecall(BANK_ID, query, max_tokens=700, budget="low")
    seen, memories = set(), []
    for item in getattr(result, "results", None) or []:
        text = (getattr(item, "text", "") or "").strip()
        if text and text.lower() not in seen:
            seen.add(text.lower())
            memories.append(text)
    return memories


async def agenerate_recommendation(platform: str) -> dict:
    response = await client().areflect(
        BANK_ID, REFLECT_PROMPT.format(platform=platform), budget="low"
    )
    return parse_reflection(getattr(response, "text", "") or "")


def parse_reflection(raw: str) -> dict:
    raw = raw.strip()
    data = None
    match = re.search(r"\{.*\}", raw, re.DOTALL)  # tolerates ```json fences / preamble
    if match:
        try:
            data = json.loads(match.group(0))
        except ValueError:
            data = None
    if isinstance(data, dict) and str(data.get("recommendation", "")).strip():
        return {k: str(data.get(k, "") or "").strip() for k in ("recommendation", "why", "avoid")}
    if isinstance(data, dict):  # valid JSON but no usable recommendation
        return {"recommendation": "", "why": "", "avoid": ""}
    # Not JSON at all: keep the real text rather than inventing structure.
    return {"recommendation": raw, "why": "", "avoid": ""}
