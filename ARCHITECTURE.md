# Architecture

## Overview

brengel.com is a static site generated from data that lives in Sieve's SQLite database. The core architectural principle is the same one that governs Sieve itself: **the data stays with you.** The site is a *view* into your local intelligence, not a pipeline that sends your data somewhere else.

Nothing runs in the cloud. No API calls at build time. No external dependencies at runtime. The site generator reads markdown files committed to this repository, produces HTML, and that HTML gets served. The complexity lives in the export pipeline — the script that transforms Sieve's internal data into publishable content.

## Data Flow

```
                         ┌─────────────────────────────────────────┐
                         │            YOUR MACHINE                 │
                         │                                         │
  RSS Feeds ──────────▶  │  ┌─────────┐    ┌──────────────────┐   │
  (300+ articles/day)    │  │  Sieve   │───▶│  SQLite Database  │   │
                         │  │ Pipeline │    │                  │   │
                         │  └─────────┘    │  - articles      │   │
                         │                 │  - scores         │   │
                         │                 │  - digests        │   │
                         │                 │  - threads        │   │
                         │                 └────────┬─────────┘   │
                         │                          │              │
                         │                 ┌────────▼─────────┐   │
                         │                 │  export.py        │   │
                         │                 │  (human triggers) │   │
                         │                 └────────┬─────────┘   │
                         │                          │              │
                         │                 ┌────────▼─────────┐   │
                         │                 │  content/         │   │
                         │                 │  (markdown files) │   │
                         │                 └────────┬─────────┘   │
                         │                          │              │
                         │                 ┌────────▼─────────┐   │
                         │                 │  Static Site Gen  │   │
                         │                 │  (Hugo/Zola)      │   │
                         │                 └────────┬─────────┘   │
                         │                          │              │
                         │                 ┌────────▼─────────┐   │
                         │                 │  public/          │   │
                         │                 │  (HTML/CSS)       │   │
                         └─────────────────┴────────┬─────────┴───┘
                                                    │
                                           rsync / scp / git push
                                                    │
                                           ┌────────▼─────────┐
                                           │  VPS / Server     │
                                           │  (nginx/caddy)    │
                                           │  brengel.com      │
                                           └──────────────────┘
```

## Key Architectural Decisions

### Why Static

The site has no server-side logic, no database at runtime, no session state. This is a deliberate choice, not a limitation.

Static means: no attack surface beyond the web server itself. No SQL injection because there's no SQL. No auth bypass because there's no auth. No data breach because there's no data — just HTML files. The site loads in milliseconds because there's nothing to compute. It works without JavaScript because it doesn't need any.

This is also the thesis made physical. If the argument is that sovereignty means owning your infrastructure, the site should demonstrate infrastructure so simple that anyone could replicate it. `nginx` serving a directory of HTML files is the most sovereign possible web architecture.

### Why the Human Stays in the Loop

Sieve's export pipeline does not auto-publish. It generates markdown files and commits them to the repo (or stages them for review). You look at them. You edit if needed. You push to trigger a build. You deploy.

This is not inefficiency — it's the design. Two reasons:

1. **Sieve serves your attention.** The digests, scores, and thread analysis are calibrated for you. What's interesting to you may need framing for a public audience. The export step is where private intelligence becomes public communication.

2. **Automated publishing from an AI pipeline would violate the architecture's own principles.** The site argues that attention is sacred labor. Auto-publishing content without human review treats the audience's attention as something to be filled rather than earned.

### Separation of Concerns

| Concern | Where It Lives |
|---|---|
| Article ingestion, scoring, storage | Sieve (separate repo) |
| Digest generation, thread detection | Sieve (separate repo) |
| Content export and formatting | `scripts/export.py` (this repo) |
| Site structure, templates, styling | `templates/`, `static/` (this repo) |
| Content (digests, articles, about) | `content/` (this repo, generated) |
| Hosting configuration | Server config (not in this repo) |

The site repo contains no intelligence logic. It doesn't know how articles are scored or how digests are generated. It only knows how to render markdown into HTML. If Sieve's scoring rubric changes, this repo doesn't need to change. If the site redesign happens, Sieve doesn't need to change.

## Database Schema (Sieve Side)

The export pipeline reads from Sieve's SQLite database. Key tables it accesses:

```sql
-- Articles: every article Sieve has ingested and scored
articles (
    id              INTEGER PRIMARY KEY,
    title           TEXT,
    source          TEXT,        -- RSS feed / publication name
    url             TEXT,        -- Original article URL
    published_date  TEXT,        -- ISO 8601
    ingested_date   TEXT,        -- When Sieve processed it
    content         TEXT,        -- Full text or summary
    overall_score   REAL,        -- Composite rubric score
    -- Individual axiom scores (columns per axiom)
    -- See ABEND.md for rubric documentation
)

-- Digests: generated daily summaries
digests (
    id              INTEGER PRIMARY KEY,
    date            TEXT,        -- YYYY-MM-DD
    summary         TEXT,        -- Big picture / headline synthesis
    full_content    TEXT,        -- Complete digest markdown
    article_count   INTEGER,     -- How many articles contributed
)

-- Threads: detected patterns across articles
threads (
    id              INTEGER PRIMARY KEY,
    label           TEXT,        -- Thread name/description
    first_seen      TEXT,        -- When thread first appeared
    last_seen       TEXT,        -- Most recent article in thread
    article_ids     TEXT,        -- JSON array of article IDs
    convergence     REAL,        -- How strongly articles cluster
)
```

*Note: Actual schema may differ as Sieve evolves. The export pipeline should be resilient to schema changes and fail loudly when assumptions break.*

## Content Format

All content in `content/` is markdown with YAML frontmatter. The static site generator reads frontmatter for metadata and renders the markdown body.

### Digest Format

```yaml
---
date: "2026-02-15"
title: "The Signal — February 15, 2026"
summary: "One-paragraph big picture for the landing page card"
article_count: 47
top_threads:
  - "regulatory capture AI safety boards"
  - "semiconductor export controls expansion"
sources_represented: 23
---

Full digest content in Abend's voice...
```

### Article Format

```yaml
---
title: "Article Title as Published"
source: "Publication Name"
url: "https://original-article-url.com/..."
published: "2026-02-15"
ingested: "2026-02-15T08:30:00Z"
overall_score: 7.8
axiom_scores:
  # Individual axiom scores — see ABEND.md for rubric
threads:
  - "thread-slug"
---
```

## Deployment

The site can be deployed anywhere that serves static files. Recommended approaches, in order of sovereignty:

1. **Own hardware** — A Raspberry Pi, old laptop, or home server running nginx. Most sovereign. Requires a static IP or dynamic DNS.
2. **Simple VPS** — A $5/month VPS (Hetzner, Vultr, etc.) running nginx or Caddy. Nearly as sovereign, more reliable uptime.
3. **Static hosting** — Netlify, Cloudflare Pages, GitHub Pages. Least sovereign but zero maintenance. Acceptable tradeoff if you need it.

Deployment is a `rsync` or `scp` of the `public/` directory, or a `git push` if using a CI/CD pipeline.

```bash
# Example: rsync to VPS
hugo && rsync -avz --delete public/ user@yourserver:/var/www/brengel.com/

# Example: with Caddy auto-HTTPS
# On server: Caddyfile
# brengel.com {
#     root * /var/www/brengel.com
#     file_server
# }
```
