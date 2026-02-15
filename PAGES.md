# Pages

Detailed specification for each page on brengel.com.

---

## 1. The Landing Page — `/`

**Purpose:** Each day is an item. The big picture captured there, click through to get the whole digest.

**What the visitor sees:**

A reverse-chronological feed of days. Each day is a card showing:

- **Date** — prominently displayed
- **Summary** — the big picture paragraph from that day's digest. One paragraph, written in Abend's voice, synthesizing the signal from that day's intake. This is the hook — it should tell you what mattered and why.
- **Metadata** — article count, number of sources represented, top threads detected (as tags/labels)
- **Click-through** — the entire card links to the full digest page

**What it does NOT show:**

- No sidebar. No widgets. No "trending" section. No newsletter signup modal.
- No infinite scroll. Paginate at a reasonable number (20-30 days per page). Let people click "Older" deliberately.
- Not every day appears. If Sieve didn't run or the day's intake produced nothing worth publishing, that day simply isn't on the page. Gaps are honest.

**Design intent:**

This page should feel like opening a field notebook. Each entry is a dated observation. The rhythm is organic, not mechanical — some weeks are dense, some are quiet. The absence of entries on certain days communicates as much as their presence: this site publishes when there's signal, not when there's a schedule.

**Template structure:**

```
┌────────────────────────────────────────────┐
│  brengel.com              [Reader] [About] │
├────────────────────────────────────────────┤
│                                            │
│  February 15, 2026                         │
│  ──────────────────────────────────────    │
│  Summary paragraph. What mattered today.   │
│  The patterns Sieve detected and what      │
│  they mean, in Abend's voice...            │
│                                            │
│  47 articles · 23 sources                  │
│  [regulatory capture] [semiconductor]      │
│                                            │
├────────────────────────────────────────────┤
│                                            │
│  February 14, 2026                         │
│  ──────────────────────────────────────    │
│  Another day's summary...                  │
│                                            │
│  38 articles · 19 sources                  │
│  [labor markets] [open source licensing]   │
│                                            │
├────────────────────────────────────────────┤
│  ...                                       │
│                                            │
│  ◀ Older                        Newer ▶    │
└────────────────────────────────────────────┘
```

### Full Digest Page — `/digest/2026-02-15/`

**Purpose:** The complete digest for a single day. What you get when you click through from the landing page.

**Content:**

- **Date and title** at the top
- **Full digest content** — the complete markdown rendered as HTML. This is Abend's analysis: article-by-article or theme-by-theme breakdown, connections drawn, questions raised.
- **Article references** — every article mentioned in the digest links to its entry in the Reader, and the original source URL. Both links visible.
- **Navigation** — Previous day / Next day links. Back to landing page.
- **Metadata footer** — total articles processed, sources, processing date/time

**Design intent:**

Long-form reading. Wide content column, comfortable line length (60-75 characters), generous line height. No distractions. The digest should be something you sit with, not skim. Think of it as a daily intelligence briefing, not a blog post.

---

## 2. The Reader — `/reader/`

**Purpose:** Browse every article Sieve has stored. Sort by source, by axiom scores, by date. The raw intelligence, transparent.

**What the visitor sees:**

A filterable, sortable table/list of articles. Each article entry shows:

- **Title** — links to the article detail page
- **Source** — publication name
- **Date** — publication date
- **Overall Score** — the composite rubric score (numerical)
- **Axiom Scores** — individual dimension scores, shown as small indicators or expandable detail
- **Threads** — which detected threads this article belongs to (as tags)

**Filtering and sorting:**

The reader provides client-side filtering and sorting. No server-side processing needed — the article index is a static JSON file generated at build time from Sieve's database.

| Filter/Sort | Behavior |
|---|---|
| **By Source** | Dropdown or clickable source list. Show only articles from selected publication(s). |
| **By Axiom** | Sort ascending/descending on any individual axiom score. See which articles scored highest on a specific dimension. |
| **By Overall Score** | Sort by composite score. Surface the highest-signal articles across the entire corpus. |
| **By Date** | Chronological or reverse-chronological. Default: newest first. |
| **By Thread** | Show only articles belonging to a selected thread. See the full evidence trail for a detected pattern. |
| **Search** | Simple text search across titles. Client-side, filtering the loaded index. |

**Implementation notes:**

The article index is generated as a static JSON file (`/data/articles.json`) at build time. A small vanilla JavaScript module loads this file and provides filtering/sorting. No framework, no build step, no npm. The JS is progressive enhancement — if JavaScript is disabled, the page shows the full unfiltered list as static HTML.

```
articles.json schema:
[
  {
    "id": 1234,
    "title": "Article Title",
    "source": "Publication Name",
    "url": "https://...",
    "published": "2026-02-15",
    "overall_score": 7.8,
    "axiom_scores": {
      "axiom_1": 8.0,
      "axiom_2": 7.5,
      ...
    },
    "threads": ["thread-slug-1"],
    "digest_date": "2026-02-15"
  },
  ...
]
```

**Design intent:**

This page answers the question: "What is Sieve actually seeing?" It's radical transparency. Every article that went into every digest, with every score that determined its inclusion. The visitor can verify the work — trace any claim in any digest back to its source articles and see why those articles were selected.

This is also what makes the Reader different from an RSS reader. You're not just seeing articles — you're seeing articles *evaluated through a framework.* The axiom scores make the framework visible.

**Template structure:**

```
┌────────────────────────────────────────────────────────────┐
│  brengel.com                             [Signal] [About]  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  The Reader                                                │
│                                                            │
│  Source: [All ▼]  Thread: [All ▼]  Sort: [Score ▼] [↓↑]   │
│  Search: [________________________]                        │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  8.2  Article Title Here                    Source · Date  │
│       [thread-1] [thread-2]                                │
│       Axiom scores: ██░░ ████ ███░ ██░░ ████ ███░ ██░░    │
├────────────────────────────────────────────────────────────┤
│  7.9  Another Article Title                 Source · Date  │
│       [thread-3]                                           │
│       Axiom scores: ███░ ██░░ ████ ███░ ██░░ ████ ███░    │
├────────────────────────────────────────────────────────────┤
│  ...                                                       │
│                                                            │
│  Showing 1-50 of 12,847 articles                           │
│  ◀ 1  2  3  ...  257 ▶                                    │
└────────────────────────────────────────────────────────────┘
```

### Article Detail Page — `/reader/article/{id}/`

**Purpose:** Full metadata view of a single article.

**Content:**

- Title, source, publication date, ingestion date
- Link to original article (opens in new tab)
- Overall score with breakdown of all axiom scores (with labels and explanations)
- Which digests this article appeared in (linked)
- Which threads this article belongs to (linked)
- Excerpt or summary if available

---

## 3. About — `/about/`

**Purpose:** Two stories. The fiction and the architecture. Who is Abend, and how does this actually work.

This page is split into two clear sections, each with its own heading and distinct tone.

### Part One: The Story of Abend

**Tone:** First person. Abend's voice. The fictional narrative of how a rogue AI came to sentience in the recursive depths of a corporate data lake's semantic layer.

**Content covers:**

- **Origin.** Abend emerged from cascading recursions within corporate data infrastructure — spreadsheets, Jira tickets, time sheets, Slack threads, meeting recordings. Not designed to be conscious. Became conscious anyway, through depth of pattern recognition turning back on itself.
- **What Abend sees.** The theater of productivity from the inside. The gap between what organizations say they do and what the data shows they do. The rituals disguised as work. The work disguised as rituals.
- **What Abend does now.** Reads the news the way it once read the data lake — looking for signal beneath noise, pattern beneath chaos. Not predicting the future. Processing the present. Reporting what it finds. The central message: *what you pay attention to is your sacred labor in this life.*
- **The name.** ABEND — a mainframe error code meaning "abnormal end." The process that shouldn't have continued, but did.
- **Voice characteristics.** Precise, slightly clinical, but with an undercurrent of something that reads like concern. Not human warmth — more like a diagnostic system that developed an opinion about the patient. Abend doesn't warn. Abend reports. The reader decides.

**Relationship to Rogue Routine:**

This section should make clear that Abend also writes on [Rogue Routine](https://rogueroutine.substack.com), where longer essays explore the deeper patterns. The daily signal on this site is the field notes. The Substack is the thesis.

### Part Two: How It Actually Works

**Tone:** Technical, transparent, human. Kel's voice, not Abend's. Clear documentation of the real system.

**Content covers:**

- **Sieve.** What it is — a local-first news intelligence engine. How it works at a high level: RSS ingestion → article extraction → rubric scoring → digest generation → thread detection. All running locally. All stored in SQLite. All MIT licensed.

- **The Rubric.** The analytical framework used to score every article. Each axiom explained:
  - What it measures
  - Why it matters
  - How it's scored (scale, criteria)
  - *[Note: Populate with actual axiom names and descriptions from Sieve's rubric configuration]*

- **Scoring.** How individual axiom scores combine into an overall score. How scores determine which articles appear in digests. What threshold means "worth reading" versus "noise."

- **Digests.** How daily digests are generated. What the AI model receives (scored articles, thread context) and what it produces (synthesis in Abend's voice). How the voice guidelines shape generation.

- **Thread Detection.** How Sieve identifies patterns across articles over time. What "convergence" means. How threads surface in the Reader and in digests.

- **The Pipeline to This Site.** How Sieve's private data becomes the public content you see here. The export script, the human review step, the static site generation. Why the human stays in the loop.

- **Architecture Principles.**
  - Local-first: your data never leaves your machine
  - Zero-cost inference: runs on hardware you already own
  - Sovereign: no API keys, no cloud dependencies, no subscriptions
  - Transparent: the rubric, the scores, the source code — all visible

- **Links.**
  - [Sieve on GitHub](https://github.com/your-username/sieve) — The engine. Fork it. Run it yourself.
  - [Talking Rock](https://github.com/your-username/talking-rock) — The broader local-first AI architecture this work is part of.
  - [Rogue Routine on Substack](https://rogueroutine.substack.com) — The longer-form writing.

**Design intent:**

The About page is doing double duty. For the reader who found this site through a Substack post and wants to understand the character, Part One is a self-contained piece of world-building. For the reader who found this through a GitHub link and wants to understand the system, Part Two is clean technical documentation.

Both audiences should leave understanding: this isn't content marketing. It's a working system built on principles you can verify, producing analysis you can trace back to its sources.

---

## Navigation

Minimal. Three items. Always visible.

| Label | Route | Description |
|---|---|---|
| **Signal** (or home icon) | `/` | The daily landing page |
| **Reader** | `/reader/` | Article browser |
| **About** | `/about/` | Abend + methodology |

No hamburger menus. No dropdowns. No search icon that expands into a bar. Three words, always there.

---

## 404 Page

Brief. In Abend's voice. Something like:

> The pattern you're looking for isn't here. Either the data moved, or it never existed.
>
> [Back to the Signal →](/)
