"""LLM Provider — Gemini API (primary) with Groq fallback.

Centralised factory so every agent uses the same LLM selection logic.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature: float = 0.3, max_tokens: int = 4000):
    """Return a LangChain chat model. Uses Gemini 3.5 Flash primarily, dynamically falls back to Groq on errors.

    Returns:
        Chat model (potentially with fallbacks) | None
    """
    google_key = os.getenv("GOOGLE_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    primary_llm = None
    fallback_llm = None

    # ── Primary: Gemini 1.5 Flash ──
    if google_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            primary_llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=google_key,
                temperature=temperature,
                max_output_tokens=max_tokens,
                max_retries=0,
            )
        except Exception as e:
            print(f"[LLM] Gemini 1.5 Flash init failed ({e})")

    # ── Fallback: Groq API ──
    if groq_key:
        try:
            from langchain_groq import ChatGroq
            groq_max_tokens = min(max_tokens, 4000)
            fallback_llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=groq_key,
                temperature=temperature,
                max_tokens=groq_max_tokens,
                max_retries=0,
            )
        except Exception as e:
            print(f"[LLM] Groq init failed ({e})")

    if primary_llm and fallback_llm:
        return primary_llm.with_fallbacks([fallback_llm])
    elif primary_llm:
        return primary_llm
    elif fallback_llm:
        return fallback_llm

    print("[LLM] No API key found for Gemini or Groq.")
    return None


def get_text_content(response) -> str:
    """Safely extract text from an LLM response (works for both Gemini and Groq).

    Gemini may return response.content as a list of dicts like:
    [{'type': 'text', 'text': 'Hello world'}]
    while Groq always returns a plain string.
    """
    content = getattr(response, "content", "")
    
    if isinstance(content, str):
        return content
        
    if isinstance(content, list):
        parts_text = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                parts_text.append(part["text"])
            elif hasattr(part, "text"):
                parts_text.append(part.text)
            else:
                parts_text.append(str(part))
        return "".join(parts_text)
        
    return str(content)
