#!/usr/bin/env python3
"""
Publish Blockbuster editions to the web archive.

- Copies blockbuster_*.html from BB_SRC_DIR into the served static dir
- Injects prev/next + archive nav into each edition (idempotent)
- Regenerates index.html from whatever editions exist

Safe to run repeatedly. Run after each new edition is generated.
"""
import os
import re
import shutil
import sys
from datetime import datetime

SRC_DIR = os.environ.get("BB_SRC_DIR", os.path.expanduser("~"))
DEST_DIR = os.environ.get("BB_STATIC_DIR", "static/blockbuster")
PUBLIC_URL = os.environ.get("BB_PUBLIC_URL", "http://localhost:8678/blockbuster/")

LARROW = "\u2190"
RARROW = "\u2192"

NAV_MARKER = 'class="edition-nav"'

NAV_CSS = """
.edition-nav { max-width:1100px; margin:0 auto; padding:18px 20px; display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }
.edition-nav .nav-group { display:flex; gap:10px; align-items:center; }
.edition-nav a, .edition-nav .disabled { font-family:'Bebas Neue',cursive; font-size:1.15em; letter-spacing:1.5px; color:#f5c518; text-decoration:none; padding:8px 18px; border:1px solid #f5c518; border-radius:8px; background:#111133; display:inline-block; transition:all .15s ease; }
.edition-nav a:hover { background:#f5c518; color:#0a0a1a; }
.edition-nav .disabled { opacity:0.3; }
"""

# Legacy filenames without an ISO date
LEGACY_DATES = {"blockbuster_june27": "2026-06-27"}


def edition_date(slug):
    """Return ISO date string for an edition slug, or None."""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", slug)
    if m:
        return m.group(1)
    return LEGACY_DATES.get(slug)


def copy_new_editions():
    """Copy any blockbuster_*.html from home dir into the archive."""
    copied = []
    for fn in os.listdir(SRC_DIR):
        if not (fn.startswith("blockbuster_") and fn.endswith(".html")):
            continue
        src = os.path.join(SRC_DIR, fn)
        if not os.path.isfile(src):
            continue
        dest = os.path.join(DEST_DIR, fn)
        # Only copy editions we haven't published yet. Published files get nav
        # injected (so sizes differ from source) — re-copying would clobber it.
        if not os.path.exists(dest):
            shutil.copy2(src, dest)
            copied.append(fn)
    return copied


def list_editions():
    """All editions in the archive, newest first."""
    eds = []
    for fn in os.listdir(DEST_DIR):
        if not (fn.startswith("blockbuster_") and fn.endswith(".html")):
            continue
        slug = fn[:-5]
        d = edition_date(slug)
        if d:
            eds.append((d, slug))
    eds.sort(reverse=True)
    return eds


def build_nav(newer, older):
    def link(label, name):
        if name is None:
            return f'<span class="disabled">{label}</span>'
        return f'<a href="/blockbuster/{name}.html">{label}</a>'
    return (
        '<div class="edition-nav">\n'
        f'  <a href="/blockbuster/">{LARROW} All Editions</a>\n'
        '  <div class="nav-group">\n'
        f'    {link(LARROW + " Newer", newer)}\n'
        f'    {link("Older " + RARROW, older)}\n'
        '  </div>\n'
        '</div>'
    )


def strip_existing_nav(html):
    """Remove previously injected nav blocks + CSS so we can re-inject fresh."""
    html = re.sub(
        r'<div class="edition-nav">.*?</div>\s*</div>',
        "",
        html,
        flags=re.DOTALL,
    )
    html = html.replace(NAV_CSS, "")
    return html


def inject_nav(eds):
    """Add/refresh nav on every edition page."""
    updated = 0
    for i, (date, slug) in enumerate(eds):
        newer = eds[i - 1][1] if i > 0 else None
        older = eds[i + 1][1] if i < len(eds) - 1 else None
        path = os.path.join(DEST_DIR, slug + ".html")

        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        if NAV_MARKER in html:
            html = strip_existing_nav(html)

        if html.count("</style>") != 1 or html.count("<body>") != 1 or html.count("</body>") != 1:
            print(f"  SKIP {slug}: unexpected structure")
            continue

        nav = build_nav(newer, older)
        html = html.replace("</style>", NAV_CSS + "</style>", 1)
        html = html.replace("<body>", "<body>\n\n" + nav, 1)
        html = html.replace("</body>", nav + "\n\n</body>", 1)

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        updated += 1
    return updated


def pretty_date(iso):
    dt = datetime.strptime(iso, "%Y-%m-%d")
    return dt.strftime("%b %-d, %Y") if os.name != "nt" else dt.strftime("%b %d, %Y")


def build_index(eds):
    cards = []
    for i, (date, slug) in enumerate(eds):
        dt = datetime.strptime(date, "%Y-%m-%d")
        day = dt.strftime("%b %-d")
        year = dt.strftime("%Y")
        is_latest = i == 0
        is_first = i == len(eds) - 1

        meta = ""
        if is_latest:
            meta = '        <div class="meta">Latest edition</div>\n'
        elif is_first:
            meta = '        <div class="meta">First edition</div>\n'

        badge = '      <span class="badge">Latest</span>\n' if is_latest else ""
        cls = "edition is-latest" if is_latest else "edition"

        cards.append(
            f'    <a class="{cls}" href="{slug}.html">\n'
            f'      <div>\n'
            f'        <div class="date"><span class="day">{day}</span>, {year}</div>\n'
            f'{meta}'
            f'      </div>\n'
            f'{badge}'
            f'      <span class="arrow">{RARROW}</span>\n'
            f'    </a>\n'
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<base href="/blockbuster/">
<title>Blockbuster \u2014 Video Archive</title>
<style>
  :root {{
    --bg: #0a0a1a;
    --card: #141428;
    --yellow: #f5c518;
    --text: #e8e8f0;
    --muted: #8a8aa0;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    min-height: 100vh;
    padding: 2rem 1rem;
  }}
  .wrap {{ max-width: 720px; margin: 0 auto; }}
  .header {{
    background: linear-gradient(135deg, #1a1a3a, #0f0f22);
    border: 2px solid var(--yellow);
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
  }}
  .header::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(90deg, transparent 0 14px, rgba(245,197,24,0.04) 14px 15px);
    pointer-events: none;
  }}
  .header h1 {{
    font-size: 2.5rem;
    letter-spacing: 0.08em;
    color: var(--yellow);
    text-transform: uppercase;
    font-weight: 900;
    text-shadow: 0 0 20px rgba(245,197,24,0.3);
  }}
  .header .tagline {{
    color: var(--muted);
    margin-top: 0.5rem;
    font-size: 0.95rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
  }}
  .header .rewind {{
    margin-top: 1rem;
    display: inline-block;
    padding: 0.4rem 1.2rem;
    border: 1px dashed var(--yellow);
    border-radius: 999px;
    color: var(--yellow);
    font-size: 0.8rem;
    letter-spacing: 0.15em;
  }}
  .count {{
    color: var(--muted);
    font-size: 0.85rem;
    margin-bottom: 1rem;
    letter-spacing: 0.05em;
  }}
  .edition {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    background: var(--card);
    border: 1px solid #23233a;
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.75rem;
    text-decoration: none;
    color: var(--text);
    transition: transform 0.12s ease, border-color 0.12s ease, background 0.12s ease;
  }}
  .edition:active {{ transform: scale(0.99); }}
  .edition:hover {{
    transform: translateX(4px);
    border-color: var(--yellow);
    background: #181834;
  }}
  .edition .date {{ font-weight: 700; font-size: 1.15rem; letter-spacing: 0.02em; color: var(--yellow); }}
  .edition .meta {{ color: var(--muted); font-size: 0.82rem; }}
  .edition .arrow {{ color: var(--yellow); font-size: 1.3rem; flex-shrink: 0; }}
  .edition.is-latest {{
    border-color: var(--yellow);
    box-shadow: 0 0 14px rgba(245,197,24,0.12);
  }}
  .edition .badge {{
    background: var(--yellow);
    color: #0a0a1a;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    text-transform: uppercase;
  }}
  .footer {{
    text-align: center;
    margin-top: 2.5rem;
    color: var(--muted);
    font-size: 0.8rem;
    letter-spacing: 0.15em;
  }}
  .footer .yellow {{ color: var(--yellow); }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <h1>Blockbuster</h1>
      <div class="tagline">Weekly Streaming Digest \u00b7 Archive</div>
      <div class="rewind">BE KIND \u00b7 REWIND</div>
    </div>

    <div class="count">{len(eds)} editions</div>

{"".join(cards)}
    <div class="footer">Powered by <span class="yellow">The Machine</span> \u00b7 Be kind, rewind</div>
  </div>
</body>
</html>
"""
    with open(os.path.join(DEST_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    copied = copy_new_editions()
    if copied:
        print(f"Copied {len(copied)} new edition(s): {', '.join(sorted(copied))}")
    else:
        print("No new editions to copy.")

    # Shrink embedded posters so pages stay fast on mobile. Safe/idempotent:
    # files carrying the optimized marker are skipped.
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from shrink import shrink_html
        saved = 0
        for fn in sorted(os.listdir(DEST_DIR)):
            if fn.startswith("blockbuster_") and fn.endswith(".html"):
                b, a, n, c = shrink_html(os.path.join(DEST_DIR, fn))
                saved += (b - a)
        if saved:
            print(f"Poster optimization saved {saved:,} bytes.")
    except Exception as e:
        print(f"WARNING: poster shrink skipped ({e})")

    eds = list_editions()
    if not eds:
        print("ERROR: no editions found in archive", file=sys.stderr)
        return 1

    n = inject_nav(eds)
    build_index(eds)
    print(f"Nav injected on {n}/{len(eds)} editions; index.html rebuilt.")
    print(f"Archive: {PUBLIC_URL}  (latest: {eds[0][1]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
