import json
import os
import sys
import time

import requests
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

# --- Config (override via env vars) ------------------------------------------
API_KEY = os.environ.get("GEMINI_API_KEY")

# Primary + fallback models. Fallback kicks in on repeated 5xx/429 ("high demand").
# Default is the *stable* 2.5-flash: with thinking off it answers in ~1-2s and is
# not capacity-constrained like the "-preview" models (which throw 503 "high demand"
# and can take 25-75s because they "think" before answering).
# For a hard question: `GEMINI_MODEL=gemini-3-flash-preview GEMINI_THINKING=high friday ...`
PRIMARY_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
FALLBACK_MODEL = os.environ.get("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash-lite")

# Thinking mode: "off" | "low" | "high". "off" is fastest (measured ~15x faster).
THINKING = os.environ.get("GEMINI_THINKING", "off").lower()
MAX_OUTPUT_TOKENS = int(os.environ.get("GEMINI_MAX_TOKENS", "1024"))

# Retry/backoff for transient 429/503 "high demand" errors.
MAX_RETRIES = int(os.environ.get("GEMINI_MAX_RETRIES", "3"))
RETRY_STATUS = {429, 500, 502, 503, 504}

SYSTEM_INSTRUCTION = (
    "You are a terminal assistant for a senior sysadmin/DevOps engineer. "
    "Answer directly and concisely. Prefer the command(s) first, then a short "
    "explanation only if needed. Avoid long essays, headings, and repeated "
    "boilerplate. Assume the user is experienced."
)

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


def thinking_config(model):
    """Model-aware thinking config: gemini-3 uses thinkingLevel, 2.5 uses thinkingBudget."""
    if model.startswith("gemini-3"):
        # gemini-3 can't fully disable thinking; "low" is the practical minimum.
        return {"thinkingLevel": "high" if THINKING == "high" else "low"}
    # gemini-2.5 family: 0 disables thinking (fastest), -1 = dynamic/auto.
    budget = {"off": 0, "low": 0, "high": -1}.get(THINKING, 0)
    return {"thinkingBudget": budget}


def build_payload(prompt, model):
    return {
        "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "thinkingConfig": thinking_config(model),
        },
    }


def stream_model(model, prompt, console):
    """Stream one model's answer. Returns full text, or raises on HTTP error."""
    url = f"{BASE_URL}/{model}:streamGenerateContent?alt=sse&key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = build_payload(prompt, model)

    full_text = ""
    with requests.post(
        url, headers=headers, data=json.dumps(payload), stream=True, timeout=120
    ) as response:
        response.raise_for_status()
        with Live(console=console, refresh_per_second=12, vertical_overflow="visible") as live:
            for line in response.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue
                chunk = line[len("data:"):].strip()
                if chunk == "[DONE]":
                    break
                try:
                    data = json.loads(chunk)
                    part = data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError, json.JSONDecodeError):
                    continue
                full_text += part
                live.update(Markdown(full_text))
    return full_text.strip()


def ask(prompt, console):
    """Try primary model with retries/backoff, then fall back to a stable model."""
    for model in (PRIMARY_MODEL, FALLBACK_MODEL):
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return stream_model(model, prompt, console)
            except requests.exceptions.HTTPError as err:
                status = err.response.status_code if err.response is not None else None
                if status in RETRY_STATUS and attempt < MAX_RETRIES:
                    wait = 2 ** (attempt - 1)  # 1s, 2s, 4s ...
                    console.print(
                        f"[yellow]{model} busy ({status}); retry {attempt}/{MAX_RETRIES} in {wait}s...[/yellow]"
                    )
                    time.sleep(wait)
                    continue
                if status in RETRY_STATUS and model != FALLBACK_MODEL:
                    console.print(
                        f"[yellow]{model} unavailable; falling back to {FALLBACK_MODEL}...[/yellow]"
                    )
                    break  # move to fallback model
                console.print(f"[red]HTTP Error: {err}[/red]")
                return None
            except requests.exceptions.RequestException as err:
                console.print(f"[red]Request failed: {err}[/red]")
                return None
    return None


if __name__ == "__main__":
    console = Console()
    if not API_KEY:
        console.print("[red]Please set the GEMINI_API_KEY environment variable.[/red]")
        sys.exit(1)
    if len(sys.argv) < 2:
        console.print("Usage: python main.py <your prompt here>")
        sys.exit(1)

    prompt_text = " ".join(sys.argv[1:])
    answer = ask(prompt_text, console)
    if not answer:
        console.print("[red]Could not retrieve a valid answer.[/red]")
        sys.exit(1)
