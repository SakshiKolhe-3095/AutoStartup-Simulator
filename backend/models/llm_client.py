"""Shared LLM client — wraps Groq API (free tier). Every agent imports call_llm from here."""
import os
from dotenv import load_dotenv
from groq import Groq
from backend.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)
_client = None
FAST_MODEL = "openai/gpt-oss-20b"   # ~5-8x cheaper on tokens/quota, good enough for structured estimates
QUALITY_MODEL = "openai/gpt-oss-120b"  # reserved for CEO narrative + investor Q&A



def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set in .env")
        _client = Groq(api_key=api_key)
    return _client


def call_llm(prompt: str, system: str = "You are a helpful assistant.",
              model: str = QUALITY_MODEL, temperature: float = 0.7, max_tokens: int = 1024) -> str:
    """Single-turn LLM call. Returns plain text, empty string on failure.
    max_tokens=1024 by default — lower values (tried 512) truncated JSON mid-response
    on the newer gpt-oss models, causing parse failures. Token savings come from using
    FAST_MODEL for structured calls, not from starving max_tokens."""
    try:
        client = get_client()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return ""