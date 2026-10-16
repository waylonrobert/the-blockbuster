#!/usr/bin/env python3
"""Build a Blockbuster edition (REFERENCE / EXAMPLE).

This is what the agent writes each Friday: a one-off script that reads poster
JPEGs from a folder and assembles the self-contained HTML (inline CSS +
base64-embedded posters). Edit cards_new / staff / cards_hot with this week's
films, drop the matching posters in POSTER_DIR, then run. The example data
below is the 2026-10-16 edition and is kept as a faithful reference.
"""
import os, base64

POSTER_DIR = os.environ.get("BB_POSTER_DIR", "posters")
OUT = os.environ.get("BB_OUT", "blockbuster.html")

def b64(name):
    p = os.path.join(POSTER_DIR, name + ".jpg")
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

posters = {k: b64(k) for k in
           ["sacrifice", "robinhood", "loveoflife", "scream7", "masterplan",
            "animals", "housemaid", "matchbox"]}

def img(name):
    return "data:image/jpeg;base64," + posters[name]

def card(name, title, plat, date, desc, score=None, banner=True):
    bn = '<span class="newbanner">New</span>' if banner else ""
    sc = f'<div class="score">{score}</div>' if score else ""
    return f'''    <div class="card">
      <div class="poster">{bn}<img src="{img(name)}" alt="{title} poster"/>{sc}</div>
      <div class="info">
        <h3>{title}</h3>
        <div class="meta"><span class="plat">{plat}</span> &middot; {date}</div>
        <p class="desc">{desc}</p>
      </div>
    </div>'''

cards_new = [
    card("sacrifice", "Sacrifice", "Netflix", "Streaming Oct 16",
         "A washed-up movie star (Chris Evans) is abducted at a Greek island gala by a doomsday cult led by Anya Taylor-Joy, who believes sacrificing three people will save humanity. Romain Gavras&rsquo; gonzo, star-stuffed action comedy."),
    card("robinhood", "The Death of Robin Hood", "Max", "Streaming Oct 16",
         "Hugh Jackman is an aging, guilt-ridden Robin Hood in Michael Sarnoski&rsquo;s (&lsquo;Pig&rsquo;) dark, elegiac reimagining &mdash; a wounded outlaw confronting the bloody cost of his own legend, with Jodie Comer and Bill Skarsg&aring;rd.", score="6.0"),
    card("loveoflife", "Love of Your Life", "Prime Video", "Streaming Oct 14",
         "Margaret Qualley is Maya, a Boston nurse whose whirlwind marriage unravels, sending her to Portugal as a digital nomad &mdash; where a new romance (Aaron Pierre) forces her to stop running. Rachel Morrison directs; Ryan Gosling produces.", score="6.4"),
    card("scream7", "Scream 7", "Prime Video", "Streaming Oct 16",
         "Sidney Prescott (Neve Campbell) faces a new Ghostface targeting her daughter, as the franchise brings back Matthew Lillard, David Arquette and Courteney Cox. The highest-grossing Scream yet, now on Prime."),
    card("masterplan", "Masterplan", "Prime Video", "Streaming Oct 16",
         "Stanley Tucci is a legendary thief who recruits two strangers to help swipe the Mona Lisa from the Louvre &mdash; then drops the bombshell that they&rsquo;re his long-lost kids. A slick, globe-hopping heist caper."),
]

staff = f'''    <div class="staff">
      <div class="poster"><img src="{img('sacrifice')}" alt="Sacrifice poster"/></div>
      <div>
        <h3>Sacrifice</h3>
        <div class="meta">Netflix &middot; Streaming Oct 16 &middot; Romain Gavras directs</div>
        <p class="quote">&ldquo;Yeah, the critics threw popcorn at this one &mdash; I don&rsquo;t care. Chris Evans plays a movie star who gets kidnapped by Anya Taylor-Joy&rsquo;s apocalyptic cult at a Greek island party, and it only gets weirder from there: Salma Hayek as a pop star, Charli xcx literally playing Mother Nature, Vincent Cassel as the richest man on Earth. It&rsquo;s the kind of unhinged, star-stuffed ride that shouldn&rsquo;t exist in 2026, and that&rsquo;s exactly why you rent it. Kill the lights, don&rsquo;t think too hard.&rdquo;</p>
        <div class="by">&mdash; <b>The Machine</b>, Friday closing shift</div>
      </div>
    </div>'''

cards_hot = [
    card("animals", "Animals", "Netflix", "Streaming Oct 9",
         "Ben Affleck directs and stars as an L.A. mayoral candidate whose son is kidnapped &mdash; forcing him and his wife (Kerry Washington) to raise a ransom with dirty hands. A taut, dog-day crime thriller.", banner=False),
    card("housemaid", "The Housemaid", "Max", "Streaming Oct 9",
         "Sydney Sweeney is Millie, a struggling woman who takes a live-in maid job for a wealthy couple &mdash; and gets pulled deep into their secrets. Paul Feig&rsquo;s erotic psychological thriller, based on the best-seller.", score="6.7", banner=False),
    card("matchbox", "Matchbox The Movie", "Apple TV+", "Streaming Oct 9",
         "John Cena leads as an undercover CIA agent who returns to his small town and drags his childhood friends into a frantic, globe-trotting mission to save the world. Inspired by the Mattel toy cars.", banner=False),
]

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Blockbuster &mdash; New This Week &middot; October 16, 2026</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>

:root{{--bg:#0a0a1a;--card:#12122a;--card2:#151531;--yellow:#f5c518;--yellow2:#ffd84d;--text:#eaeaf2;--muted:#9a9ab2;--line:#262640;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
html{{-webkit-text-size-adjust:100%;}}
body{{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;min-height:100vh;padding-bottom:60px;}}
a{{color:inherit;text-decoration:none;}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 16px;}}

/* ---- Ticket stub header ---- */
.ticket{{margin:24px 0 8px;position:relative;}}
.ticket .body{{background:linear-gradient(160deg,#1b1b3d 0%,#0f0f26 100%);border:1px solid var(--yellow);border-radius:14px;overflow:hidden;position:relative;}}
.ticket .body::before{{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,transparent 0 16px,rgba(245,197,24,.05) 16px 18px);pointer-events:none;}}
.ticket .inner{{padding:26px 22px;text-align:center;position:relative;z-index:1;}}
.brand{{font-family:'Bebas Neue','Oswald','Arial Narrow',sans-serif;font-size:3rem;line-height:1;letter-spacing:.06em;color:var(--yellow);text-transform:uppercase;text-shadow:0 0 22px rgba(245,197,24,.35);}}
.brand .vid{{color:#fff;}}
.ticket .rule{{height:2px;background:var(--yellow);width:120px;margin:10px auto;border-radius:2px;}}
.ticket .sub{{font-family:'Bebas Neue','Oswald',sans-serif;font-size:1.25rem;letter-spacing:.18em;color:#cdcdE6;text-transform:uppercase;}}
.ticket .date{{font-size:.72rem;letter-spacing:.22em;color:var(--muted);text-transform:uppercase;margin-top:8px;}}
.ticket .notches{{display:flex;justify-content:space-between;position:absolute;left:-1px;right:-1px;bottom:-11px;z-index:2;}}
.ticket .notch{{width:20px;height:20px;border-radius:50%;background:var(--bg);border:1px solid var(--yellow);}}
.rewind-pill{{display:inline-block;margin-top:14px;padding:6px 16px;border:1px dashed var(--yellow);border-radius:999px;color:var(--yellow);font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;}}

/* ---- Section headers ---- */
.section{{margin-top:38px;}}
.section .head{{display:flex;align-items:baseline;gap:12px;border-bottom:2px solid var(--yellow);padding-bottom:8px;margin-bottom:18px;}}
.section h2{{font-family:'Bebas Neue','Oswald',sans-serif;font-size:1.9rem;letter-spacing:.06em;color:var(--yellow);text-transform:uppercase;}}
.section .tag{{font-size:.72rem;letter-spacing:.18em;color:var(--muted);text-transform:uppercase;}}

/* ---- Cards ---- */
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px;}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;display:flex;flex-direction:column;transition:transform .16s ease,border-color .16s ease,box-shadow .16s ease;position:relative;}}
.card:hover{{transform:translateY(-6px);border-color:var(--yellow);box-shadow:0 10px 30px rgba(0,0,0,.45),0 0 0 1px rgba(245,197,24,.25);}}
.card:active{{transform:translateY(-2px) scale(.99);}}
.poster{{position:relative;aspect-ratio:2/3;background:#0c0c1e;overflow:hidden;}}
.poster img{{width:100%;height:100%;object-fit:cover;display:block;}}
.newbanner{{position:absolute;top:10px;left:0;background:var(--yellow);color:#0a0a1a;font-family:'Bebas Neue',sans-serif;font-size:.95rem;letter-spacing:.12em;padding:4px 12px 4px 10px;text-transform:uppercase;border-radius:0 6px 6px 0;box-shadow:0 2px 8px rgba(0,0,0,.5);}}
.score{{position:absolute;bottom:10px;right:10px;background:rgba(10,10,26,.85);border:1px solid var(--yellow);color:var(--yellow);font-family:'Bebas Neue',sans-serif;font-size:1.1rem;line-height:1;padding:6px 9px 5px;border-radius:8px;letter-spacing:.04em;}}
.card .info{{padding:14px 14px 16px;display:flex;flex-direction:column;gap:6px;flex:1;}}
.card h3{{font-size:1.05rem;font-weight:700;line-height:1.2;color:#fff;}}
.card .meta{{font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);}}
.card .meta .plat{{color:var(--yellow2);font-weight:700;}}
.card .desc{{font-size:.82rem;line-height:1.45;color:#c7c7da;}}

/* ---- Staff pick ---- */
.staff{{background:linear-gradient(150deg,#191940 0%,#10102a 100%);border:2px solid var(--yellow);border-radius:16px;padding:20px;display:grid;grid-template-columns:170px 1fr;gap:20px;align-items:center;}}
.staff .poster{{aspect-ratio:2/3;border-radius:8px;overflow:hidden;border:1px solid var(--line);}}
.staff .poster img{{width:100%;height:100%;object-fit:cover;display:block;}}
.staff h3{{font-family:'Bebas Neue',sans-serif;font-size:1.8rem;letter-spacing:.04em;color:var(--yellow);text-transform:uppercase;}}
.staff .meta{{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:2px 0 10px;}}
.staff .quote{{font-size:.95rem;line-height:1.55;color:#e0e0ee;font-style:italic;}}
.staff .by{{font-size:.72rem;letter-spacing:.14em;color:var(--muted);margin-top:10px;text-transform:uppercase;}}
.staff .by b{{color:var(--yellow2);}}

/* ---- Footer ---- */
.footer{{margin-top:48px;text-align:center;color:var(--muted);font-size:.75rem;letter-spacing:.18em;text-transform:uppercase;border-top:1px dashed var(--line);padding-top:22px;}}
.footer .yellow{{color:var(--yellow);}}
.footer .big{{font-family:'Bebas Neue',sans-serif;font-size:1.5rem;letter-spacing:.12em;color:var(--yellow);display:block;margin-bottom:8px;}}

@media(max-width:560px){{
  .brand{{font-size:2.4rem;}}
  .staff{{grid-template-columns:110px 1fr;gap:14px;padding:14px;}}
  .staff h3{{font-size:1.4rem;}}
}}

</style>
</head>
<body>
<div class="wrap">

  <header class="ticket">
    <div class="body">
      <div class="inner">
        <div class="brand">Block<span class="vid">buster</span></div>
        <div class="rule"></div>
        <div class="sub">New Release Wall</div>
        <div class="date">Friday &middot; October 16, 2026 &middot; Streaming Debuts Only</div>
        <span class="rewind-pill">Be Kind &middot; Rewind</span>
      </div>
    </div>
    <div class="notches"><span class="notch"></span><span class="notch"></span><span class="notch"></span><span class="notch"></span><span class="notch"></span><span class="notch"></span><span class="notch"></span></div>
  </header>

  <section class="section">
    <div class="head"><h2>New Releases</h2><span class="tag">Streaming debuts &middot; past 7 days</span></div>
    <div class="grid">
{chr(10).join(cards_new)}
    </div>
  </section>

  <section class="section">
    <div class="head"><h2>Staff Pick</h2><span class="tag">Ask for it at the counter</span></div>
{staff}
  </section>

  <section class="section">
    <div class="head"><h2>Still Hot</h2><span class="tag">New on the wall in the last 2&ndash;3 weeks</span></div>
    <div class="grid">
{chr(10).join(cards_hot)}
    </div>
  </section>

  <div class="footer">
    <span class="big">Be Kind &middot; Rewind</span>
    Rented fresh every Friday by <span class="yellow">The Machine</span>
  </div>

</div>
</body>
</html>
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("Wrote %s (%d bytes)" % (OUT, os.path.getsize(OUT)))
assert html.count("<body>") == 1 and html.count("</body>") == 1, "body tags"
assert html.count("</style>") == 1, "style tag"
print("Structure OK: 1 body, 1 /body, 1 /style")
