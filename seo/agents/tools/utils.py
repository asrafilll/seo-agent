import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; SEOAgent/1.0; +https://github.com/seo-agent)"
    ),
}
_TIMEOUT = 15


def fetch_page(url):
    """Fetch a URL and return (status_code, html_text) or raise on failure."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT, allow_redirects=True)
    resp.raise_for_status()
    return resp.status_code, resp.text, resp.url


def parse_html(html):
    """Parse HTML string and return a BeautifulSoup object."""
    return BeautifulSoup(html, "lxml")


def extract_meta_tags(soup):
    """Extract key meta tags from a BeautifulSoup object."""
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    meta_desc = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    description = meta_desc.get("content", "").strip() if meta_desc else None

    meta_robots = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    robots = meta_robots.get("content", "").strip() if meta_robots else None

    canonical = soup.find("link", attrs={"rel": "canonical"})
    canonical_url = canonical.get("href", "").strip() if canonical else None

    og_tags = {}
    for tag in soup.find_all("meta", attrs={"property": re.compile(r"^og:")}):
        og_tags[tag.get("property")] = tag.get("content", "")

    return {
        "title": title,
        "title_length": len(title) if title else 0,
        "description": description,
        "description_length": len(description) if description else 0,
        "robots": robots,
        "canonical": canonical_url,
        "og_tags": og_tags,
    }


def extract_headings(soup):
    """Extract all heading tags (H1-H6) with their text."""
    headings = {}
    for level in range(1, 7):
        tag_name = f"h{level}"
        found = soup.find_all(tag_name)
        headings[tag_name] = [h.get_text(strip=True) for h in found]
    return headings


def extract_images(soup):
    """Extract images with src and alt attributes."""
    images = []
    for img in soup.find_all("img"):
        images.append({
            "src": img.get("src", ""),
            "alt": img.get("alt", ""),
            "has_alt": bool(img.get("alt", "").strip()),
        })
    return images


def extract_links(soup, base_url):
    """Extract internal and external links."""
    parsed_base = urlparse(base_url)
    internal = []
    external = []

    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        link_info = {
            "url": full_url,
            "text": a.get_text(strip=True)[:100],
            "nofollow": "nofollow" in a.get("rel", []),
        }
        if parsed.netloc == parsed_base.netloc:
            internal.append(link_info)
        else:
            external.append(link_info)

    return {"internal": internal, "external": external}
