# SEO Agent

AI-powered SEO assistant built with Django + OpenAI Agents SDK. Performs site audits, keyword research, and content optimization through a conversational interface.

## Features

**Site Audit** — Crawl any URL and get a full SEO audit: meta tags analysis, heading structure, image alt attributes, internal/external links, and actionable recommendations.

**Keyword Research** — Discover keyword suggestions via Google Autocomplete. Get related terms, long-tail variations, and search intent insights.

**Content Optimization** — Analyze page content for keyword density, readability, heading structure, and SEO best practices. Get rewrite suggestions.

**AI Chat** — Conversational interface powered by OpenAI Agents SDK. Ask SEO questions naturally — agent picks the right tools automatically.

## Tech Stack

| Layer | Technology |
| ----- | ---------- |
| Backend | Django 5.1 + Python |
| AI Agents | OpenAI Agents SDK |
| LLM Provider | OpenAI / OpenRouter (configurable) |
| Scraping | BeautifulSoup4, lxml, requests |
| Frontend | Django Templates, custom CSS |

## Quick Start

```bash
cp .env.example .env    # add your API keys
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API Keys

Set `OPENAI_API_KEY` or use OpenRouter via `OPENROUTER_API_KEY` + `LLM_PROVIDER=openrouter` in `.env`.