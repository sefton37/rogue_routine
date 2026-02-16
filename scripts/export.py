#!/usr/bin/env python3
"""
Sieve → Hugo Export Pipeline

Exports articles, digests, and threads from Sieve database to Hugo-compatible formats.
"""

import sqlite3
import json
import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Export Sieve database content to Hugo formats"
    )
    parser.add_argument(
        "--sieve-db",
        default="/home/kellogg/data/sieve.db",
        help="Path to Sieve SQLite database (default: /home/kellogg/data/sieve.db)",
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--date",
        help="Export single date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--from",
        dest="date_from",
        help="Export from date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--to",
        dest="date_to",
        help="Export to date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be written without writing files",
    )
    parser.add_argument(
        "--articles-only",
        action="store_true",
        help="Only export articles.json",
    )
    parser.add_argument(
        "--digests-only",
        action="store_true",
        help="Only export digest markdown files",
    )
    return parser.parse_args()


def extract_date(datetime_str: Optional[str]) -> Optional[str]:
    """Extract YYYY-MM-DD from ISO datetime string."""
    if not datetime_str:
        return None
    # Convert to string if it's not already
    datetime_str = str(datetime_str)
    # Handle ISO format with timezone: 2026-01-29T18:30:52+00:00
    match = re.match(r"(\d{4}-\d{2}-\d{2})", datetime_str)
    return match.group(1) if match else None


def strip_markdown(text: str) -> str:
    """Strip basic markdown formatting from text."""
    # Remove headers
    text = re.sub(r"#{1,6}\s+", "", text)
    # Remove bold/italic
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    # Remove links but keep text
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    # Remove list markers
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.MULTILINE)
    return text.strip()


def extract_big_picture(content: str) -> str:
    """Extract the full Big Picture section from digest content."""
    if not content:
        return ""

    lines = content.split("\n")
    in_section = False
    section = []
    for line in lines:
        if re.match(r"^##\s+.*Big Picture", line, re.IGNORECASE):
            in_section = True
            continue
        elif in_section and line.startswith("## "):
            break
        elif in_section:
            section.append(line)

    text = "\n".join(section).strip()
    if text:
        return text

    # Fallback: extract first substantive paragraph if no Big Picture heading
    paragraphs = re.split(r"\n\n+", content)
    for para in paragraphs:
        para = para.strip()
        if not para or para.startswith("#"):
            continue
        clean = strip_markdown(para)
        if len(clean) >= 40:
            return clean
    return ""


def extract_summary(content: str, max_length: int = 200) -> str:
    """Extract first substantive paragraph from digest content and truncate."""
    if not content:
        return ""

    # Split by double newline to get paragraphs
    paragraphs = re.split(r"\n\n+", content)

    # Find first substantive paragraph (not a header, not too short)
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # Skip headers
        if para.startswith("#"):
            continue
        # Strip markdown
        clean = strip_markdown(para)
        # Skip very short lines (likely sub-headers or labels)
        if len(clean) < 40:
            continue
        # Truncate
        if len(clean) > max_length:
            return clean[:max_length].rsplit(" ", 1)[0] + "..."
        return clean

    return ""


def format_yaml_frontmatter(data: Dict[str, Any]) -> str:
    """Generate YAML frontmatter manually (no pyyaml dependency)."""
    lines = ["---"]

    for key, value in data.items():
        if value is None:
            continue
        elif isinstance(value, str):
            if "\n" in value:
                # Multiline: use YAML literal block scalar
                lines.append(f"{key}: |")
                for line in value.split("\n"):
                    lines.append(f"  {line}")
            else:
                # Escape quotes in strings
                escaped = value.replace('"', '\\"')
                lines.append(f'{key}: "{escaped}"')
        elif isinstance(value, (int, float)):
            lines.append(f"{key}: {value}")
        elif isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            elif isinstance(value[0], dict):
                # List of objects
                lines.append(f"{key}:")
                for item in value:
                    lines.append("  -")
                    for k, v in item.items():
                        if isinstance(v, str):
                            escaped = v.replace('"', '\\"')
                            lines.append(f'    {k}: "{escaped}"')
                        else:
                            lines.append(f"    {k}: {v}")
            else:
                # List of strings
                lines.append(f"{key}:")
                for item in value:
                    escaped = str(item).replace('"', '\\"')
                    lines.append(f'  - "{escaped}"')

    lines.append("---")
    return "\n".join(lines)


def get_articles_for_digest_date(
    conn: sqlite3.Connection, digest_date: str
) -> List[Dict[str, Any]]:
    """Get all articles for a digest date."""
    cursor = conn.cursor()

    # Articles match digest date if their scored_at OR pub_date date matches
    query = """
        SELECT
            id, title, source, url, pub_date, composite_score, summary,
            d1_attention_economy, d2_data_sovereignty, d3_power_consolidation,
            d4_coercion_cooperation, d5_fear_trust, d6_democratization,
            d7_systemic_design, scored_at, topics
        FROM articles
        WHERE composite_score IS NOT NULL
          AND (date(scored_at) = ? OR date(pub_date) = ?)
        ORDER BY composite_score DESC
    """

    cursor.execute(query, (digest_date, digest_date))

    articles = []
    for row in cursor.fetchall():
        # Parse topics
        topics_raw = row[15] or ""
        topics = [t.strip() for t in topics_raw.split(",") if t.strip()]

        articles.append(
            {
                "id": row[0],
                "title": row[1],
                "source": row[2],
                "url": row[3],
                "published": extract_date(row[4]),
                "overall_score": row[5],
                "axiom_scores": {
                    "attention_economy": row[7],
                    "data_sovereignty": row[8],
                    "power_consolidation": row[9],
                    "coercion_cooperation": row[10],
                    "fear_trust": row[11],
                    "democratization": row[12],
                    "systemic_design": row[13],
                },
                "topics": topics,
                "digest_date": digest_date,
                "summary": row[6],
            }
        )

    return articles


def export_digest_markdown(
    conn: sqlite3.Connection,
    digest_date: str,
    output_dir: Path,
    dry_run: bool = False,
) -> None:
    """Export a single digest as Hugo markdown."""
    cursor = conn.cursor()

    # Get digest
    cursor.execute(
        "SELECT content, article_count FROM digests WHERE digest_date = ?",
        (digest_date,),
    )
    result = cursor.fetchone()

    if not result:
        print(f"WARNING: No digest found for {digest_date}")
        return

    content, article_count = result

    # Get articles for this date
    articles = get_articles_for_digest_date(conn, digest_date)

    # Calculate source count
    sources = {a["source"] for a in articles if a["source"]}
    source_count = len(sources)

    # Get top topics from articles on this date
    topic_counts = {}
    for article in articles:
        for topic in article.get("topics", []):
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    top_topics = sorted(topic_counts.keys(), key=lambda t: topic_counts[t], reverse=True)[:5]

    # Get top scoring articles
    top_articles = sorted(articles, key=lambda a: a["overall_score"] or 0, reverse=True)[:5]
    top_scoring_articles = [
        {
            "title": a["title"],
            "source": a["source"],
            "score": a["overall_score"],
            "url": a["url"],
        }
        for a in top_articles
    ]

    # Generate frontmatter
    big_picture = extract_big_picture(content)
    # Use big_picture for summary (truncated) — more reliable than first-paragraph guessing
    if big_picture:
        clean_bp = strip_markdown(big_picture.split("\n\n")[0])
        summary = clean_bp[:200].rsplit(" ", 1)[0] + "..." if len(clean_bp) > 200 else clean_bp
    else:
        summary = extract_summary(content)
    frontmatter_data = {
        "title": f"Daily Signal — {digest_date}",
        "date": digest_date,
        "summary": summary,
        "big_picture": big_picture,
        "article_count": len(articles),
        "source_count": source_count,
        "top_topics": top_topics,
        "top_scoring_articles": top_scoring_articles,
    }

    frontmatter = format_yaml_frontmatter(frontmatter_data)

    # Combine frontmatter and content
    full_content = f"{frontmatter}\n\n{content}\n"

    # Write to file
    output_path = output_dir / "content" / "digests" / f"{digest_date}.md"

    if dry_run:
        print(f"\n[DRY RUN] Would write to: {output_path}")
        print(f"Content preview (first 500 chars):")
        print(full_content[:500])
        print("...")
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(full_content)
        print(f"Exported digest: {output_path}")


def export_articles_json(
    conn: sqlite3.Connection,
    output_dir: Path,
    date_filter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    """Export all articles to JSON."""
    cursor = conn.cursor()

    # Build query with optional date filter
    query = """
        SELECT
            id, title, source, url, pub_date, composite_score, summary,
            d1_attention_economy, d2_data_sovereignty, d3_power_consolidation,
            d4_coercion_cooperation, d5_fear_trust, d6_democratization,
            d7_systemic_design, scored_at, entities, topics
        FROM articles
        WHERE composite_score IS NOT NULL
    """
    params = []

    if date_filter:
        query += " AND (date(scored_at) = ? OR date(pub_date) = ?)"
        params.extend([date_filter, date_filter])
    elif date_from or date_to:
        if date_from:
            query += " AND (date(scored_at) >= ? OR date(pub_date) >= ?)"
            params.extend([date_from, date_from])
        if date_to:
            query += " AND (date(scored_at) <= ? OR date(pub_date) <= ?)"
            params.extend([date_to, date_to])

    query += " ORDER BY scored_at DESC"

    cursor.execute(query, params)

    articles = []
    for row in cursor.fetchall():
        article_id = row[0]

        # Determine digest date (date of scored_at)
        digest_date = extract_date(row[14])

        # Parse topics
        topics_raw = row[16] or ""
        topics = [t.strip() for t in topics_raw.split(",") if t.strip()]

        articles.append(
            {
                "id": article_id,
                "title": row[1],
                "source": row[2],
                "url": row[3],
                "published": extract_date(row[4]),
                "overall_score": row[5],
                "axiom_scores": {
                    "attention_economy": row[7],
                    "data_sovereignty": row[8],
                    "power_consolidation": row[9],
                    "coercion_cooperation": row[10],
                    "fear_trust": row[11],
                    "democratization": row[12],
                    "systemic_design": row[13],
                },
                "topics": topics,
                "digest_date": digest_date,
                "summary": row[6],
            }
        )

    output_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_articles": len(articles),
        "articles": articles,
    }

    output_path = output_dir / "data" / "articles.json"

    if dry_run:
        print(f"\n[DRY RUN] Would write to: {output_path}")
        print(f"Total articles: {len(articles)}")
        if articles:
            print(f"Sample article: {json.dumps(articles[0], indent=2)[:500]}...")
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w") as f:
            json.dump(output_data, f, indent=2)
        print(f"Exported {len(articles)} articles to: {output_path}")


def export_threads_json(
    conn: sqlite3.Connection,
    output_dir: Path,
    dry_run: bool = False,
) -> None:
    """Export all threads to JSON."""
    cursor = conn.cursor()

    # Get all threads with their articles
    cursor.execute(
        """
        SELECT
            t.id, t.name, t.article_count, t.created_at, t.updated_at
        FROM threads t
        ORDER BY t.name
        """
    )

    threads = []
    for row in cursor.fetchall():
        thread_id, name, article_count, created_at, updated_at = row

        # Get all article IDs for this thread
        cursor.execute(
            """
            SELECT a.id, a.scored_at, a.pub_date
            FROM articles a
            JOIN article_threads at ON a.id = at.article_id
            WHERE at.thread_id = ? AND a.composite_score IS NOT NULL
            ORDER BY a.scored_at ASC
            """,
            (thread_id,),
        )

        article_rows = cursor.fetchall()
        article_ids = [r[0] for r in article_rows]

        if not article_rows:
            continue

        # Determine first and last seen dates
        first_date = extract_date(article_rows[0][1]) or extract_date(article_rows[0][2])
        last_date = extract_date(article_rows[-1][1]) or extract_date(article_rows[-1][2])

        threads.append(
            {
                "id": thread_id,
                "label": name,
                "first_seen": first_date,
                "last_seen": last_date,
                "article_count": len(article_ids),
                "article_ids": article_ids,
            }
        )

    output_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "active_threads": threads,
    }

    output_path = output_dir / "data" / "threads.json"

    if dry_run:
        print(f"\n[DRY RUN] Would write to: {output_path}")
        print(f"Total threads: {len(threads)}")
        if threads:
            print(f"Sample thread: {json.dumps(threads[0], indent=2)}")
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w") as f:
            json.dump(output_data, f, indent=2)
        print(f"Exported {len(threads)} threads to: {output_path}")


def main():
    args = parse_args()

    # Validate paths
    db_path = Path(args.sieve_db)
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return 1

    output_dir = Path(args.output).resolve()

    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"ERROR: Failed to connect to database: {e}")
        return 1

    # Verify required tables exist
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}

    required_tables = {"articles", "digests", "threads", "article_threads"}
    missing_tables = required_tables - tables
    if missing_tables:
        print(f"ERROR: Missing required tables: {missing_tables}")
        return 1

    try:
        # Determine what to export
        export_digests = not args.articles_only
        export_data = not args.digests_only

        # Export digests
        if export_digests:
            if args.date:
                # Single date
                export_digest_markdown(conn, args.date, output_dir, args.dry_run)
            else:
                # Get all digests or filtered range
                query = "SELECT digest_date FROM digests"
                params = []

                if args.date_from or args.date_to:
                    conditions = []
                    if args.date_from:
                        conditions.append("digest_date >= ?")
                        params.append(args.date_from)
                    if args.date_to:
                        conditions.append("digest_date <= ?")
                        params.append(args.date_to)
                    query += " WHERE " + " AND ".join(conditions)

                query += " ORDER BY digest_date ASC"

                cursor.execute(query, params)
                digest_dates = [row[0] for row in cursor.fetchall()]

                if not digest_dates:
                    print("WARNING: No digests found matching criteria")
                else:
                    print(f"Exporting {len(digest_dates)} digests...")
                    for digest_date in digest_dates:
                        export_digest_markdown(conn, digest_date, output_dir, args.dry_run)

        # Export data files
        if export_data:
            export_articles_json(
                conn, output_dir, args.date, args.date_from, args.date_to, args.dry_run
            )
            export_threads_json(conn, output_dir, args.dry_run)

        print("\nExport complete!")
        return 0

    except Exception as e:
        print(f"ERROR: Export failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    exit(main())
