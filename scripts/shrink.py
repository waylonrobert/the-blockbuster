#!/usr/bin/env python3
"""
Shrink base64-embedded posters inside Blockbuster edition HTML files.

The cron embeds posters as data: URIs. Full-res posters make each page ~1MB,
which is slow to load on mobile. The cards render small, so we cap the longest
side at 400px and re-encode as JPEG q80.

Idempotent: images already at/below the cap are left alone.
"""
import base64
import io
import os
import re
import sys

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed for this interpreter", file=sys.stderr)
    sys.exit(1)

MAX_PX = 400
QUALITY = 80
MARKER = "<!-- posters-optimized -->"

DATA_URI_RE = re.compile(r'data:image/(?:jpeg|jpg|png|webp|gif);base64,([A-Za-z0-9+/=]+)')


def shrink_b64(b64_data, max_px=MAX_PX, quality=QUALITY):
    """Return (new_b64, changed). Falls back to original on any failure."""
    try:
        raw = base64.b64decode(b64_data)
    except Exception:
        return b64_data, False

    try:
        img = Image.open(io.BytesIO(raw))
        img.load()
    except Exception:
        return b64_data, False

    w, h = img.size
    longest = max(w, h)

    if longest > max_px:
        scale = max_px / float(longest)
        new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
        img = img.resize(new_size, Image.LANCZOS)

    # JPEG can't hold alpha
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
    new_raw = buf.getvalue()

    # Only accept if it actually got smaller
    if len(new_raw) >= len(raw):
        return b64_data, False

    return base64.b64encode(new_raw).decode("ascii"), True


def shrink_html(path, max_px=MAX_PX, quality=QUALITY):
    """Rewrite one HTML file in place. Returns (before_bytes, after_bytes, n_imgs, n_changed).

    Skips files already carrying the optimized marker, so repeated runs cannot
    cause generational JPEG quality loss.
    """
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    before = len(html)

    if MARKER in html:
        return before, before, 0, 0

    stats = {"n": 0, "changed": 0}

    def repl(m):
        stats["n"] += 1
        new_b64, changed = shrink_b64(m.group(1), max_px, quality)
        if changed:
            stats["changed"] += 1
        return "data:image/jpeg;base64," + new_b64

    new_html = DATA_URI_RE.sub(repl, html)

    # Mark as processed regardless, so we only ever re-encode once.
    if "</head>" in new_html:
        new_html = new_html.replace("</head>", MARKER + "\n</head>", 1)
    else:
        new_html = MARKER + "\n" + new_html

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)

    after = len(new_html)
    return before, after, stats["n"], stats["changed"]


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BB_STATIC_DIR", "static/blockbuster")

    if os.path.isfile(target):
        files = [target]
    else:
        files = sorted(
            os.path.join(target, f)
            for f in os.listdir(target)
            if f.startswith("blockbuster_") and f.endswith(".html")
        )

    tot_before = tot_after = 0
    for p in files:
        b, a, n, c = shrink_html(p)
        tot_before += b
        tot_after += a
        pct = (100.0 * (b - a) / b) if b else 0
        print(f"{os.path.basename(p):34s} {b:>9,} -> {a:>9,} ({pct:5.1f}% smaller)  {c}/{n} imgs resized")

    if tot_before:
        pct = 100.0 * (tot_before - tot_after) / tot_before
        print(f"\nTOTAL {tot_before:,} -> {tot_after:,} bytes ({pct:.1f}% smaller)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
