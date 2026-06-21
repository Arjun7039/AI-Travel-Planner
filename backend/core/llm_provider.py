"""LLM Provider — Gemini API (primary) with Groq fallback.

Centralised factory so every agent uses the same LLM selection logic.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature: float = 0.3, max_tokens: int = 4000):
    """Return a LangChain chat model. Tries Gemini first, falls back to Groq.

    Returns:
        ChatGoogleGenerativeAI | ChatGroq | None
    """
    google_key = os.getenv("GOOGLE_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    # ── Primary: Gemini API ──
    if google_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-3.5-flash",
                google_api_key=google_key,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        except Exception as e:
            print(f"[LLM] Gemini init failed ({e}), trying Groq fallback...")

    # ── Fallback: Groq ──
    if groq_key:
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=groq_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )

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
