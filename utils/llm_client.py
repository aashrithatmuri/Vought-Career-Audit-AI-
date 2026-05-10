import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


load_dotenv()


MODEL_ID = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

MODEL_LIMITS = {
    "llama-3.3-70b-versatile": {
        "rpm": 30,
        "rpd": 1000,
        "tpm": 12000,
        "tpd": 100000
    },
    "llama-3.1-8b-instant": {
        "rpm": 30,
        "rpd": 14400,
        "tpm": 6000,
        "tpd": 500000
    }
}

CAP_RATIO = float(
    os.getenv(
        "GROQ_USAGE_CAP_RATIO",
        "0.75"
    )
)

REQUESTS_PER_ANALYSIS = int(
    os.getenv(
        "GROQ_REQUESTS_PER_ANALYSIS",
        "5"
    )
)

TOKENS_PER_ANALYSIS = int(
    os.getenv(
        "GROQ_TOKENS_PER_ANALYSIS",
        "12000"
    )
)

USAGE_FILE = Path(__file__).resolve().parent.parent / ".groq_usage.json"

_CLIENT = None


@dataclass
class LLMResult:
    content: str
    ok: bool
    error: str = ""
    used_fallback: bool = False


def get_groq_client():
    global _CLIENT

    if _CLIENT is not None:
        return _CLIENT

    api_key = os.getenv(
        "GROQ_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to .env before enabling Groq intelligence."
        )

    try:
        from groq import Groq

    except ImportError as error:
        raise RuntimeError(
            "The groq package is not installed. Install requirements before using Groq intelligence."
        ) from error

    _CLIENT = Groq(
        api_key=api_key
    )

    return _CLIENT


def estimate_tokens(
    text: str
) -> int:
    return max(
        1,
        len(text) // 4
    )


def _current_keys():
    now = datetime.now()

    return (
        now.strftime("%Y-%m-%d"),
        now.strftime("%Y-%m-%d %H:%M")
    )


def _read_usage() -> dict[str, Any]:
    if not USAGE_FILE.exists():
        return {
            "days": {},
            "minutes": {}
        }

    try:
        return json.loads(
            USAGE_FILE.read_text(
                encoding="utf-8"
            )
        )

    except (json.JSONDecodeError, OSError):
        return {
            "days": {},
            "minutes": {}
        }


def _write_usage(
    usage: dict[str, Any]
) -> None:
    try:
        USAGE_FILE.write_text(
            json.dumps(
                usage,
                indent=2
            ),
            encoding="utf-8"
        )

    except OSError:
        pass


def _effective_limits(
    model: str | None = None
) -> dict[str, int]:
    limits = MODEL_LIMITS.get(
        model or MODEL_ID,
        MODEL_LIMITS["llama-3.3-70b-versatile"]
    )

    return {
        key: max(
            1,
            int(value * CAP_RATIO)
        )
        for key, value in limits.items()
    }


def get_usage_status(
    model: str | None = None
) -> dict[str, Any]:
    model = model or MODEL_ID
    usage = _read_usage()
    day_key, minute_key = _current_keys()
    day_usage = usage.get(
        "days",
        {}
    ).get(
        day_key,
        {
            "requests": 0,
            "tokens": 0
        }
    )
    minute_usage = usage.get(
        "minutes",
        {}
    ).get(
        minute_key,
        {
            "requests": 0,
            "tokens": 0
        }
    )
    limits = _effective_limits(
        model
    )

    requests_left_today = max(
        0,
        limits["rpd"] - day_usage.get(
            "requests",
            0
        )
    )
    tokens_left_today = max(
        0,
        limits["tpd"] - day_usage.get(
            "tokens",
            0
        )
    )
    requests_left_minute = max(
        0,
        limits["rpm"] - minute_usage.get(
            "requests",
            0
        )
    )
    tokens_left_minute = max(
        0,
        limits["tpm"] - minute_usage.get(
            "tokens",
            0
        )
    )
    estimated_analyses_left = min(
        requests_left_today // max(
            1,
            REQUESTS_PER_ANALYSIS
        ),
        tokens_left_today // max(
            1,
            TOKENS_PER_ANALYSIS
        )
    )

    return {
        "model": model,
        "cap_ratio": CAP_RATIO,
        "daily_request_cap": limits["rpd"],
        "daily_token_cap": limits["tpd"],
        "minute_request_cap": limits["rpm"],
        "minute_token_cap": limits["tpm"],
        "requests_used_today": day_usage.get(
            "requests",
            0
        ),
        "tokens_used_today": day_usage.get(
            "tokens",
            0
        ),
        "requests_left_today": requests_left_today,
        "tokens_left_today": tokens_left_today,
        "requests_left_minute": requests_left_minute,
        "tokens_left_minute": tokens_left_minute,
        "estimated_analyses_left_today": estimated_analyses_left,
        "is_daily_cap_reached": requests_left_today <= 0 or tokens_left_today <= 0,
        "is_minute_cap_reached": requests_left_minute <= 0 or tokens_left_minute <= 0
    }


def _can_make_request(
    estimated_tokens: int,
    model: str | None = None
) -> tuple[bool, str]:
    status = get_usage_status(
        model
    )

    if status["is_daily_cap_reached"]:
        return (
            False,
            "Daily Groq safety cap reached for this project."
        )

    if status["is_minute_cap_reached"]:
        return (
            False,
            "Minute Groq safety cap reached. Try again shortly."
        )

    if estimated_tokens > status["tokens_left_today"]:
        return (
            False,
            "Not enough daily token budget remains for this analysis."
        )

    if estimated_tokens > status["tokens_left_minute"]:
        return (
            False,
            "Not enough per-minute token budget remains. Try again shortly."
        )

    return (
        True,
        ""
    )


def _record_usage(
    prompt_tokens: int,
    completion_tokens: int
) -> None:
    usage = _read_usage()
    day_key, minute_key = _current_keys()
    total_tokens = prompt_tokens + completion_tokens

    usage.setdefault(
        "days",
        {}
    )
    usage.setdefault(
        "minutes",
        {}
    )

    usage["days"].setdefault(
        day_key,
        {
            "requests": 0,
            "tokens": 0
        }
    )
    usage["minutes"].setdefault(
        minute_key,
        {
            "requests": 0,
            "tokens": 0
        }
    )

    usage["days"][day_key]["requests"] += 1
    usage["days"][day_key]["tokens"] += total_tokens
    usage["minutes"][minute_key]["requests"] += 1
    usage["minutes"][minute_key]["tokens"] += total_tokens

    _write_usage(
        usage
    )


def _extract_usage(
    response: Any,
    estimated_prompt_tokens: int,
    estimated_completion_tokens: int
) -> tuple[int, int]:
    usage = getattr(
        response,
        "usage",
        None
    )

    if usage is None:
        return (
            estimated_prompt_tokens,
            estimated_completion_tokens
        )

    prompt_tokens = getattr(
        usage,
        "prompt_tokens",
        None
    ) or estimated_prompt_tokens
    completion_tokens = getattr(
        usage,
        "completion_tokens",
        None
    ) or estimated_completion_tokens

    return (
        int(prompt_tokens),
        int(completion_tokens)
    )


def complete_chat(
    system_prompt: str,
    user_prompt: str,
    fallback: str,
    temperature: float = 0.2,
    max_completion_tokens: int = 900,
    json_mode: bool = False,
    model: str | None = None
) -> LLMResult:
    if os.getenv(
        "CAREER_AUDIT_DISABLE_LLM",
        ""
    ).lower() in [
        "1",
        "true",
        "yes"
    ]:
        return LLMResult(
            content=fallback,
            ok=False,
            error="LLM calls are disabled by CAREER_AUDIT_DISABLE_LLM.",
            used_fallback=True
        )

    model = model or MODEL_ID
    estimated_prompt_tokens = estimate_tokens(
        system_prompt
    ) + estimate_tokens(
        user_prompt
    )
    estimated_total_tokens = estimated_prompt_tokens + max_completion_tokens
    can_request, reason = _can_make_request(
        estimated_total_tokens,
        model
    )

    if not can_request:
        return LLMResult(
            content=fallback,
            ok=False,
            error=reason,
            used_fallback=True
        )

    try:
        client = get_groq_client()
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": temperature,
            "max_completion_tokens": max_completion_tokens
        }

        if json_mode:
            kwargs["response_format"] = {
                "type": "json_object"
            }

        response = client.chat.completions.create(
            **kwargs
        )

        content = (
            response.choices[0].message.content or ""
        ).strip()
        prompt_tokens, completion_tokens = _extract_usage(
            response,
            estimated_prompt_tokens,
            estimate_tokens(
                content
            )
        )

        _record_usage(
            prompt_tokens,
            completion_tokens
        )

        return LLMResult(
            content=content,
            ok=True
        )

    except Exception as error:
        return LLMResult(
            content=fallback,
            ok=False,
            error=str(error),
            used_fallback=True
        )


def _extract_json_object(
    text: str
) -> dict[str, Any]:
    try:
        return json.loads(
            text
        )

    except json.JSONDecodeError:
        pass

    start = text.find(
        "{"
    )
    end = text.rfind(
        "}"
    )

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "No JSON object found in model response."
        )

    return json.loads(
        text[start:end + 1]
    )


def complete_json(
    system_prompt: str,
    user_prompt: str,
    fallback: dict[str, Any],
    temperature: float = 0.1,
    max_completion_tokens: int = 900,
    model: str | None = None
) -> dict[str, Any]:
    result = complete_chat(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        fallback=json.dumps(
            fallback
        ),
        temperature=temperature,
        max_completion_tokens=max_completion_tokens,
        json_mode=True,
        model=model
    )

    if not result.ok:
        return fallback

    try:
        parsed = _extract_json_object(
            result.content
        )

    except (json.JSONDecodeError, ValueError, TypeError):
        return fallback

    merged = fallback.copy()
    merged.update(
        parsed
    )

    return merged
