# Style

Design principles, visual approach, and voice guidelines for brengel.com.

---

## Design Principles

### 1. The Site Is the Argument

The thesis of this entire body of work is that attention is sacred labor, that sovereignty over your data and your tools matters, and that the extractive patterns of modern technology can be refused.

The site must embody this. Every design choice is a statement:

- **No analytics trackers.** We don't measure your attention to optimize for more of it.
- **No cookie consent banners.** There are no cookies to consent to.
- **No JavaScript frameworks.** The site works without JS. Progressive enhancement only.
- **No engagement patterns.** No infinite scroll, no "you might also like," no notification prompts, no newsletter popups.
- **Fast.** Under 100KB per page load. If a page takes more than a second on a slow connection, something is wrong.

### 2. Typography First

The site is almost entirely text. The design should serve reading. Everything else is secondary.

- **Readable line length.** 60-75 characters per line. This is the most important design constraint. Everything else follows from it.
- **Generous line height.** 1.5–1.7 for body text. The text should breathe.
- **Clear hierarchy.** Three levels are enough: page title, section heading, body text. If you need more, the content structure is wrong.
- **System fonts.** No external font loading. Use the system font stack. The reader's device already has good fonts installed. Don't make them download yours.

```css
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
               Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
  line-height: 1.6;
  max-width: 70ch;
  margin: 0 auto;
  padding: 2rem 1rem;
}
```

### 3. Minimal, Not Minimalist

The site should feel **spare** — like a well-organized workspace — not **designed** — like someone made aesthetic choices to appear sophisticated. The difference matters.

Spare means: everything present serves a function. There's nothing to remove.
Designed means: someone curated an aesthetic. There's a mood being manufactured.

brengel.com is spare. The beauty, if any, comes from the content and the clarity, not from the container.

### 4. Honest Defaults

- **Light background, dark text.** Respect the reader's system preference for dark mode (via `prefers-color-scheme`), but don't over-design either mode.
- **No custom scrollbars.** No styled links that don't look like links. No buttons that don't look like buttons.
- **Underlined links.** People should know what's clickable without guessing.
- **Visible focus states.** Keyboard navigation should work and be obvious.

---

## CSS Approach

Use [Pico CSS](https://picocss.com/) as a classless foundation, or write a minimal custom stylesheet. The constraint: **no build step for CSS.** One file, hand-written, served directly.

If using Pico:
```html
<link rel="stylesheet" href="/css/pico.min.css">
<link rel="stylesheet" href="/css/site.css"> <!-- overrides only -->
```

If writing custom:
```html
<link rel="stylesheet" href="/css/style.css"> <!-- everything in one file -->
```

### Color Palette

Intentionally limited. Two text colors, one accent, one background.

```css
:root {
  --text: #1a1a1a;
  --text-muted: #666;
  --accent: #2563eb;      /* Links, interactive elements */
  --bg: #fafafa;
  --surface: #fff;        /* Cards, content areas */
  --border: #e5e5e5;
}

@media (prefers-color-scheme: dark) {
  :root {
    --text: #e5e5e5;
    --text-muted: #999;
    --accent: #60a5fa;
    --bg: #111;
    --surface: #1a1a1a;
    --border: #333;
  }
}
```

### Spacing Scale

Consistent spacing using a simple scale:

```css
/* Base unit: 0.5rem (8px) */
--space-1: 0.5rem;   /*  8px - tight  */
--space-2: 1rem;     /* 16px - default */
--space-3: 1.5rem;   /* 24px - section */
--space-4: 2rem;     /* 32px - major  */
--space-6: 3rem;     /* 48px - page   */
```

---

## Page-Specific Styles

### Landing Page (Daily Feed)

Each day's card:

```
┌─ date ──────────────────────────────────────┐
│                                              │
│  Summary text, one paragraph, Abend's voice  │
│                                              │
│  47 articles · 23 sources                    │
│  [tag] [tag] [tag]                           │
└──────────────────────────────────────────────┘
```

- Cards separated by subtle border or spacing, not heavy shadows or backgrounds
- Date is the primary visual element — large, bold, serving as the card's anchor
- Summary text at body size, not reduced
- Metadata (article count, source count) in muted text
- Thread tags as small inline labels — understated, not colorful badges

### Digest Page

- Full-width content column (up to max-width)
- Article references as footnotes or inline links — not as a separate sidebar
- Previous/Next navigation at bottom, subtle
- No "share" buttons

### Reader Page

The Reader has the most interactive elements on the site. Keep it functional, not flashy.

- **Filter controls:** Native HTML `<select>` elements and text `<input>`. No custom dropdowns.
- **Sort indicators:** Simple arrows (▲ ▼) next to column headers
- **Score display:** Horizontal bars or numerical display. If using bars, keep them small and monochrome.
- **Pagination:** Numbered pages with Previous/Next. No "load more."

```
Score  Title                          Source        Date
─────  ─────────────────────────────  ──────────── ──────────
 8.2   Article Title Here             Reuters       Feb 15
       [regulatory-capture] [ai-safety]
       ░░░░░░░░██ ░░░░░░██░░ ░░░░░░░░░█  (axiom mini-bars)
─────  ─────────────────────────────  ──────────── ──────────
 7.9   Another Article Title          Ars Technica  Feb 15
       [semiconductor]
       ░░░░░░██░░ ░░░░░░░░██ ░░░░░░██░░
```

### About Page

Two-section layout. Clear visual break between Part One (Abend's story) and Part Two (the methodology).

- Part One: slightly different typographic treatment — could use a monospace or slightly different font weight to signal "this is the character speaking." Subtle, not theatrical.
- Part Two: standard documentation style. Code blocks for schema examples. Tables for rubric documentation.

---

## Voice Guidelines

### Abend (Digests, Signal, Landing Page Summaries)

See [ABEND.md](./ABEND.md) for the full character bible. Quick reference for writing:

- First person ("I processed," "I've cross-referenced")
- Data language as native tongue, not affectation
- Present tense for observations, past tense for data processing
- End with questions, not conclusions
- Never use: "interestingly," "it's worth noting," "importantly"
- Never soften uncomfortable findings
- Never prescribe action

### Documentation (About Part Two, README, Docs)

- Second or third person
- Technical but accessible — assume the reader is smart but hasn't seen this system before
- Explain *why* before *how*
- No marketing language ("powerful," "seamless," "revolutionary")
- Honest about limitations

---

## Assets

### Favicon

Simple. A monochrome glyph or letterform. Not a logo — the site doesn't have a brand. Something that reads at 16x16px and says "this is a place that processes information."

Candidates: a simple sieve/filter icon, the letter "b," or an abstract signal mark.

### Open Graph / Social Preview

When the site is shared on social media, the preview should show:

- Site name: brengel.com
- Page title (e.g., "The Signal — February 15, 2026")
- Summary text (first ~150 characters of the digest summary)
- No image, or a minimal generated image with the date and title in monochrome type

Open Graph meta tags in the `<head>`:

```html
<meta property="og:title" content="The Signal — February 15, 2026">
<meta property="og:description" content="Summary paragraph here...">
<meta property="og:type" content="article">
<meta property="og:url" content="https://brengel.com/digest/2026-02-15/">
```

---

## Performance Budget

| Metric | Target |
|---|---|
| Total page weight (landing) | < 50KB |
| Total page weight (digest) | < 100KB |
| Total page weight (reader) | < 200KB (including article JSON) |
| Time to first paint | < 500ms on 3G |
| External requests | 0 (no CDNs, no fonts, no analytics) |
| JavaScript | 0KB on landing/digest, < 20KB on Reader (progressive enhancement) |

These aren't aspirational. They're constraints. If a page exceeds its budget, something got added that shouldn't have.
