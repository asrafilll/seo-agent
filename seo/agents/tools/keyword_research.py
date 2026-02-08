import json
import string

import requests

from agents import function_tool

_AUTOCOMPLETE_URL = "https://suggestqueries.google.com/complete/search"
_TIMEOUT = 10


def _get_suggestions(query):
    """Fetch Google Autocomplete suggestions for a query."""
    params = {
        "client": "firefox",
        "q": query,
    }
    try:
        resp = requests.get(_AUTOCOMPLETE_URL, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        # Response format: [query, [suggestion1, suggestion2, ...]]
        if isinstance(data, list) and len(data) > 1:
            return data[1]
    except Exception:
        pass
    return []


@function_tool
def research_keywords(seed_keyword: str) -> str:
    """Research keyword ideas using Google Autocomplete.

    Expands a seed keyword by appending a-z prefixes and question modifiers
    to discover related search queries and long-tail keywords.

    Args:
        seed_keyword: The base keyword to research (e.g. "best running shoes")
    """
    results = {
        "seed_keyword": seed_keyword,
        "base_suggestions": [],
        "alphabetical": {},
        "questions": [],
    }

    # Base suggestions
    results["base_suggestions"] = _get_suggestions(seed_keyword)

    # Alphabetical expansion (a-z)
    for letter in string.ascii_lowercase:
        query = f"{seed_keyword} {letter}"
        suggestions = _get_suggestions(query)
        if suggestions:
            results["alphabetical"][letter] = suggestions

    # Question modifiers
    question_words = ["how", "what", "why", "when", "where", "which", "who", "is", "can", "does"]
    for word in question_words:
        query = f"{word} {seed_keyword}"
        suggestions = _get_suggestions(query)
        if suggestions:
            results["questions"].extend(suggestions)

    # Deduplicate questions
    results["questions"] = list(dict.fromkeys(results["questions"]))

    # Summary stats
    all_keywords = set(results["base_suggestions"])
    for suggestions in results["alphabetical"].values():
        all_keywords.update(suggestions)
    all_keywords.update(results["questions"])

    results["total_unique_keywords"] = len(all_keywords)

    return json.dumps(results, indent=2)
