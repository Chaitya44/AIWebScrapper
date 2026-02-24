"""
ai_agent.py - Thin wrapper over GeminiOrganizer.
All AI logic lives in gemini_organizer.py — this module provides
backward-compatible entry points for the API server.
"""

from gemini_organizer import GeminiOrganizer, OrganizedResult

# Singleton organizer instance
_organizer = GeminiOrganizer()


def extract_structured(html_text: str) -> OrganizedResult:
    """
    Primary entry point.  Returns an OrganizedResult with .schema, .data, .to_api_response().
    """
    return _organizer.organize(html_text)


# Legacy helpers (kept for backward compatibility with test scripts)
def extract_multi_entity(html_text: str) -> dict:
    """Returns just the data dict (no schema). Used by test2.py."""
    result = _organizer.organize(html_text)
    return result.data