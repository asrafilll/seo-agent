import json

from agents import function_tool

from .utils import (
    extract_headings,
    extract_images,
    extract_links,
    extract_meta_tags,
    fetch_page,
    parse_html,
)


@function_tool
def crawl_and_audit(url: str) -> str:
    """Crawl a URL and perform an SEO audit.

    Fetches the page, analyzes meta tags, headings, images, and links,
    then identifies SEO issues and provides recommendations.

    Args:
        url: The URL to audit (e.g. "https://example.com")
    """
    try:
        status_code, html, final_url = fetch_page(url)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch {url}: {e}"})

    soup = parse_html(html)
    meta = extract_meta_tags(soup)
    headings = extract_headings(soup)
    images = extract_images(soup)
    links = extract_links(soup, final_url)

    # Identify issues
    issues = []

    # Title checks
    if not meta["title"]:
        issues.append({"severity": "high", "issue": "Missing page title"})
    elif meta["title_length"] < 30:
        issues.append({"severity": "medium", "issue": f"Title too short ({meta['title_length']} chars, aim for 50-60)"})
    elif meta["title_length"] > 60:
        issues.append({"severity": "medium", "issue": f"Title too long ({meta['title_length']} chars, aim for 50-60)"})

    # Description checks
    if not meta["description"]:
        issues.append({"severity": "high", "issue": "Missing meta description"})
    elif meta["description_length"] < 120:
        issues.append({"severity": "medium", "issue": f"Meta description too short ({meta['description_length']} chars, aim for 150-160)"})
    elif meta["description_length"] > 160:
        issues.append({"severity": "medium", "issue": f"Meta description too long ({meta['description_length']} chars, aim for 150-160)"})

    # H1 checks
    h1_count = len(headings.get("h1", []))
    if h1_count == 0:
        issues.append({"severity": "high", "issue": "No H1 heading found"})
    elif h1_count > 1:
        issues.append({"severity": "medium", "issue": f"Multiple H1 headings found ({h1_count})"})

    # Image alt checks
    images_without_alt = [img for img in images if not img["has_alt"]]
    if images_without_alt:
        issues.append({
            "severity": "medium",
            "issue": f"{len(images_without_alt)} of {len(images)} images missing alt text",
        })

    # Canonical check
    if not meta["canonical"]:
        issues.append({"severity": "low", "issue": "No canonical URL specified"})

    # OG tags check
    if not meta["og_tags"]:
        issues.append({"severity": "low", "issue": "No Open Graph tags found"})

    report = {
        "url": final_url,
        "status_code": status_code,
        "meta": meta,
        "headings": {k: v for k, v in headings.items() if v},
        "images": {
            "total": len(images),
            "missing_alt": len(images_without_alt),
        },
        "links": {
            "internal": len(links["internal"]),
            "external": len(links["external"]),
        },
        "issues": issues,
        "score": max(0, 100 - sum(
            {"high": 20, "medium": 10, "low": 5}.get(i["severity"], 0)
            for i in issues
        )),
    }

    return json.dumps(report, indent=2)
