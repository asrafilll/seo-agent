import json
import re
from collections import Counter

from agents import function_tool

from .utils import extract_headings, extract_meta_tags, fetch_page, parse_html


def _get_text_content(soup):
    """Extract visible text content from the page."""
    # Remove script and style elements
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()
    text = soup.get_text(separator=" ", strip=True)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text


def _count_words(text):
    """Count words in text."""
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    return words


def _calculate_keyword_density(words, min_count=3):
    """Calculate keyword frequency for words appearing at least min_count times."""
    counter = Counter(words)
    total = len(words)
    if total == 0:
        return {}
    # Filter stop words and short words
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "it", "as", "be", "was", "are",
        "been", "this", "that", "will", "can", "has", "have", "had", "not",
        "all", "its", "our", "we", "you", "your", "they", "them", "their",
        "what", "which", "who", "how", "when", "where", "there", "here",
        "do", "does", "did", "so", "if", "no", "up", "out", "about",
    }
    density = {}
    for word, count in counter.most_common(50):
        if count >= min_count and word not in stop_words and len(word) > 2:
            density[word] = {
                "count": count,
                "density": round(count / total * 100, 2),
            }
    return density


def _estimate_readability(words, text):
    """Simple readability estimate based on sentence and word length."""
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = max(len(sentences), 1)
    num_words = len(words)
    avg_sentence_length = num_words / num_sentences
    avg_word_length = sum(len(w) for w in words) / max(num_words, 1)

    # Simple scoring
    if avg_sentence_length > 25:
        level = "difficult"
    elif avg_sentence_length > 15:
        level = "moderate"
    else:
        level = "easy"

    return {
        "avg_sentence_length": round(avg_sentence_length, 1),
        "avg_word_length": round(avg_word_length, 1),
        "sentence_count": num_sentences,
        "word_count": num_words,
        "readability_level": level,
    }


@function_tool
def analyze_content(url: str) -> str:
    """Analyze the content of a web page for SEO optimization.

    Extracts text content and analyzes keyword density, readability,
    heading structure, and provides content optimization suggestions.

    Args:
        url: The URL to analyze (e.g. "https://example.com/blog/post")
    """
    try:
        status_code, html, final_url = fetch_page(url)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch {url}: {e}"})

    soup = parse_html(html)
    meta = extract_meta_tags(soup)
    headings = extract_headings(soup)

    # Get text content
    text_soup = parse_html(html)  # Fresh copy since _get_text_content mutates
    text = _get_text_content(text_soup)
    words = _count_words(text)

    keyword_density = _calculate_keyword_density(words)
    readability = _estimate_readability(words, text)

    # Analyze heading structure
    heading_issues = []
    h1s = headings.get("h1", [])
    h2s = headings.get("h2", [])

    if len(h1s) == 0:
        heading_issues.append("No H1 tag found")
    if len(h2s) == 0:
        heading_issues.append("No H2 tags found — consider adding subheadings")

    # Check heading hierarchy
    has_h3 = bool(headings.get("h3"))
    if has_h3 and not h2s:
        heading_issues.append("H3 used without H2 — broken heading hierarchy")

    # Content suggestions
    suggestions = []
    if readability["word_count"] < 300:
        suggestions.append("Content is thin (under 300 words). Aim for 1000+ words for better rankings.")
    elif readability["word_count"] < 1000:
        suggestions.append(f"Content has {readability['word_count']} words. Consider expanding to 1500+ for competitive topics.")

    if readability["readability_level"] == "difficult":
        suggestions.append("Sentences are long on average. Break up complex sentences for better readability.")

    if not meta["description"]:
        suggestions.append("Add a meta description that includes your target keyword.")

    top_keywords = list(keyword_density.keys())[:5]
    if top_keywords:
        suggestions.append(f"Top keywords detected: {', '.join(top_keywords)}. Ensure these align with your target topic.")

    report = {
        "url": final_url,
        "meta": meta,
        "headings": {k: v for k, v in headings.items() if v},
        "heading_issues": heading_issues,
        "readability": readability,
        "keyword_density": keyword_density,
        "suggestions": suggestions,
    }

    return json.dumps(report, indent=2)
