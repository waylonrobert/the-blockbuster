# The Blockbuster

A weekly streaming digest with 90s Blockbuster Video energy — poster art,
"be kind rewind" staff picks, ticket-stub aesthetic. Every Friday an agent
finds the films whose **streaming debut** landed in the past week, verifies
each one against IMDb, and publishes a self-contained dark-themed HTML page.

## How it works

1. **Find** *(agent)* — search "new on [service] this week", keeping only
   subscription-included, scripted (non-documentary) films.
2. **Verify** *(agent)* — every film's streaming date is checked against
   **IMDb** (the authoritative source). Wikipedia is used *only* for posters.
3. **Build** *(agent)* — posters are downloaded, resized to 400px, and
   base64-embedded into a self-contained HTML file (inline CSS + Google Fonts).
   See `scripts/build_edition.py` for the reference structure.
4. **Publish** *(`scripts/publish.py`)* — copies the new edition into the
   archive, shrinks any oversized posters, injects ←/→ navigation, and rebuilds
   the archive index.
5. **Serve** — Flask serves the static archive (`serving/flask_route.py`).

## Repository layout

| Path | What it is |
|---|---|
| `prompt/blockbuster_prompt.md` | The full agent prompt — mission, hard exclusions, allowed services, the 5 steps. The "brain". |
| `scripts/build_edition.py` | Reference: how an edition's HTML is assembled (real example data). |
| `scripts/publish.py` | Deterministic glue: copy → shrink → nav → index (stdlib-only). |
| `scripts/shrink.py` | Pillow poster optimizer — 400px max, JPEG q80, idempotent. |
| `serving/flask_route.py` | Flask routes to serve the archive. |
| `static/blockbuster/` | The published archive — `index.html` + every edition page (committed). |

## Requirements

- Python 3.x — `pip install -r requirements.txt` (only Pillow; `publish.py`
  and `build_edition.py` are stdlib-only).
- An LLM agent / cron that runs `prompt/blockbuster_prompt.md` on a schedule
  (the prompt is written for a Hermes-style agent with web search/extract).

## Configuration

All paths are driven by environment variables (defaults in parentheses):

| Var | Default | Purpose |
|---|---|---|
| `BB_SRC_DIR` | `~` | where new `blockbuster_YYYY-MM-DD.html` files land |
| `BB_STATIC_DIR` | `static/blockbuster` | served archive directory |
| `BB_PUBLIC_URL` | `http://localhost:8678/blockbuster/` | success-line URL |
| `BB_POSTER_DIR` | `posters` | poster JPEGs for the build step |

## Secrets

**None of the code in this repo contains API keys.** The only external service
that requires a key is [Firecrawl](https://firecrawl.dev) (web search/extract
backend). Put that key in your agent's config — *not* this repo — and copy
`.env.example` to `.env` if you want a local reference (it's git-ignored).

## APIs used

- **Firecrawl** — web search + page extraction (discovery + IMDb scraping). *Key required.*
- **IMDb** — scraped directly; there is no official free API, no key.
- **Wikipedia REST API** — poster thumbnails; keyless.
- **Google Fonts** — Bebas Neue + Inter; keyless.
- TMDB is **not** used.

## Running the pipeline by hand

```bash
# 1. Build an edition (the agent normally does this; build_edition.py is a reference)
python3 scripts/build_edition.py
# 2. Publish it (copy + shrink + nav + rebuild index)
python3 scripts/publish.py
```

`publish.py` is idempotent and safe to re-run.

## License

[MIT](LICENSE) — the code, scripts, prompt, and documentation in this repository
are MIT-licensed. See the `LICENSE` file for the full text.

## Copyrights & Trademarks

The MIT license covers only the code and documentation in this repository.
All film titles, synopses, poster images, and other artwork are the property
of their respective owners and are reproduced here solely for personal,
non-commercial, archival use. "Blockbuster" and its related names, logos, and
trade dress are trademarks of their respective owners. This project is not
affiliated with, endorsed by, or sponsored by Blockbuster LLC, any film
studio, distributor, or streaming service.
