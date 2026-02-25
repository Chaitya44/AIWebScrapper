"""
ai_agent.py - Thin wrapper over GeminiOrganizer.
All AI logic lives in gemini_organizer.py — this module provides
backward-compatible entry points for the API server.
"""

from gemini_organizer import GeminiOrganizer, OrganizedResult

# Singleton organizer instance
_organizer = GeminiOrganizer()


def extract_structured(html_text: str, api_key: str = None, source_url: str = "") -> OrganizedResult:
    """
    Primary entry point. Returns an OrganizedResult with .schema, .data, .to_api_response().
    api_key: optional user-provided Gemini key (BYOK).
    source_url: the URL that was scraped (used to resolve relative URLs).
    """
    return _organizer.organize(html_text, api_key=api_key, source_url=source_url)


# Legacy helpers (kept for backward compatibility with test scripts)
def extract_multi_entity(html_text: str) -> dict:
    """Returns just the data dict (no schema). Used by test2.py."""
    result = _organizer.organize(html_text)
    return result.data