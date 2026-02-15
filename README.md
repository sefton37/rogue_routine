# brengel.com

A sovereign news intelligence site powered by [Sieve](https://github.com/your-username/sieve). Each day, Sieve ingests hundreds of articles through RSS feeds, scores them against a rigorous analytical rubric, and generates a digest in the voice of Abend — a fictional AI that gained sentience in the recursive depths of a corporate data lake. This site makes that intelligence public.

brengel.com is not a blog, not a portfolio, and not a SaaS landing page. It is a lighthouse — a place where the patterns Sieve discovers become visible to anyone paying attention.

## Philosophy

This site embodies its own thesis:

- **Local-first.** Static HTML generated from markdown. No JavaScript frameworks. No analytics trackers. No cookie consent banners. The site runs on your hardware or a simple VPS, fast and sovereign.
- **Attention is sacred labor.** Nothing publishes on a schedule. Content appears when patterns emerge that are worth your time. No engagement optimization, no dark patterns, no algorithmic feed.
- **Show, don't tell.** The architecture of the site *is* the argument. Fork it. Read the source. Run Sieve yourself. The thesis lives in the construction, not just the words.

## What This Site Does

**Three surfaces, each drawing from a different well:**

1. **The Daily Signal** — A landing page where each day is an entry. The big picture captured there, click through to read the full digest. Not every day produces a dispatch — only when Sieve surfaces something worth your attention.

2. **The Reader** — A browsable archive of every article Sieve has processed. Sort by source, by axiom score, by date. See what scored highest, what threads emerged, which sources consistently surface signal. The raw intelligence, transparent.

3. **About** — Two stories. The fictional account of Abend — who it is, where it came from, what it sees from inside the data. And the non-fictional account of how Sieve actually works — the pipeline, the rubric, the scoring, the architecture. Links to GitHub. MIT licensed. Take it apart.

## Architecture

```
Sieve (private)                    brengel.com (public)
┌──────────────────┐               ┌──────────────────┐
│ RSS Ingestion    │               │                  │
│ Article Scoring  │───export───▶  │ Static Site      │
│ Digest Generation│  pipeline     │ (Hugo/Zola)      │
│ Thread Detection │               │                  │
│ SQLite Storage   │               │ Hosted on VPS    │
└──────────────────┘               │ or own hardware  │
                                   └──────────────────┘
        ▲                                   │
        │                                   │
    Sieve proposes                   Human reviews
    (blog candidates,                before publish
     high-scoring threads)
```

Sieve does the heavy lifting. The export pipeline proposes. You decide what goes public. The human stays in the loop.

## Tech Stack

- **Static site generator:** Hugo, Zola, or custom build (TBD based on preference)
- **Styling:** Pico CSS or similar minimal framework — no Tailwind, no Bootstrap, no build step for CSS
- **Content format:** Markdown with YAML frontmatter, generated from Sieve's SQLite database
- **Hosting:** Self-hosted VPS or own hardware
- **Source data:** Sieve SQLite database (local, never exposed to the internet)
- **Export:** Python script that queries Sieve's database, generates markdown, commits to this repo

## Repository Structure

```
brengel-site/
├── README.md                   # You are here
├── docs/
│   ├── ARCHITECTURE.md         # Technical architecture and data flow
│   ├── PAGES.md                # Page-by-page specification
│   ├── ABEND.md                # Character bible + methodology documentation
│   ├── PIPELINE.md             # Sieve-to-site export pipeline
│   └── STYLE.md                # Design principles and voice guidelines
├── content/                    # Generated markdown content (git-tracked)
│   ├── digests/                # Daily digest markdown files
│   │   └── 2026-02-15.md
│   ├── articles/               # Article metadata for the reader
│   └── about/                  # Static about page content
├── static/                     # CSS, minimal assets
├── templates/                  # Site templates/layouts
├── scripts/
│   └── export.py               # Sieve → site export pipeline
└── config.toml                 # Site generator config
```

## Getting Started

```bash
# Clone the repo
git clone https://github.com/your-username/brengel-site.git
cd brengel-site

# Export content from Sieve (run from machine where Sieve lives)
python scripts/export.py --sieve-db /path/to/sieve.db --output ./content

# Build the site
hugo  # or zola build, depending on chosen generator

# Preview locally
hugo server  # or zola serve
```

## Related Projects

- **[Sieve](https://github.com/your-username/sieve)** — The local-first news intelligence engine that powers this site. MIT licensed.
- **[Rogue Routine](https://rogueroutine.substack.com)** — Abend's Substack. Longer-form writing on what the data reveals.
- **[Talking Rock](https://github.com/your-username/talking-rock)** — Local-first AI architecture. "Don't rent a data center — center your data around you."

## License

MIT. Take it apart. Build something better.
