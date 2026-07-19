#!/usr/bin/env python3
"""Assemble a print edition PDF from the built _site of dakshinamurti-stotram."""
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
FONTS = ROOT / "print" / "fonts"
OUT_HTML = ROOT / "print" / "print.html"
OUT_PDF = ROOT / "print" / "dakshinamurti-stotram.pdf"

def soup_of(p):
    return BeautifulSoup((SITE / p).read_text(), "html.parser")

def strip_links(el):
    """Replace <a> with plain spans (internal site links are meaningless in print)."""
    for a in el.find_all("a"):
        a.name = "span"
        for attr in ("href", "target", "rel", "class"):
            if attr != "class" and a.has_attr(attr):
                del a[attr]
    return el

def prose_of(page, drop_h1=True):
    s = soup_of(page)
    el = s.select_one(".wrap.prose")
    if drop_h1:
        h1 = el.find("h1")
        if h1:
            h1.decompose()
    return el.decode_contents()

# ---------------- gather content ----------------

# Homepage intro
home = soup_of("index.html")
intro_html = home.select_one(".hero-intro").decode_contents()

# About / Colophon / Transliteration notes (strip verse links in glossary later)
about_html = prose_of("about/index.html")
colophon_html = prose_of("colophon/index.html")
translit_html = prose_of("transliteration-notes/index.html")

# License summary (short, from license page first paragraph)
lic = soup_of("license/index.html").select_one(".wrap.prose")

# Verses
verses = []
for i in range(1, 11):
    s = soup_of(f"verses/sds-{i:03d}/index.html")
    num = s.select_one(".verse-number").get_text(strip=True)
    deva = [sp.get_text(strip=True) for sp in s.select(".verse-source-deva > span")]
    iast = [sp.get_text(strip=True) for sp in s.select(".verse-source-iast > span")]
    trans = s.select_one(".verse-translation p").get_text(strip=True)
    wbw = []
    for card in s.select(".wbw-card"):
        wbw.append({
            "deva": card.select_one(".wbw-card-deva").get_text(strip=True),
            "iast": card.select_one(".wbw-card-iast").get_text(strip=True),
            "gloss": card.select_one(".wbw-card-gloss").get_text(strip=True),
            "tags": card.select_one(".wbw-card-tags").get_text(strip=True),
        })
    verses.append({"num": num, "deva": deva, "iast": iast, "trans": trans, "wbw": wbw})

# Glossary
gl = soup_of("glossary/index.html")
glossary = []
for li in gl.select(".glossary-entry"):
    occ = ", ".join(a.get_text(strip=True) for a in li.select(".glossary-occurrences a"))
    glossary.append({
        "deva": li.select_one(".glossary-headword").get_text(strip=True),
        "iast": li.select_one(".glossary-iast").get_text(strip=True),
        "gloss": li.select_one(".glossary-gloss").get_text(strip=True),
        "occ": occ,
    })

# ---------------- build html ----------------

BOOK_SVG = """<svg class="{cls}" viewBox="0 0 24 24"><path d="M12 7.4c-1.7-1.3-3.8-1.8-5.7-1.8-.6 0-1.2 0-1.8.1v11.8c.6-.1 1.2-.1 1.8-.1 1.9 0 4 .5 5.7 1.8 1.7-1.3 3.8-1.8 5.7-1.8.6 0 1.2 0 1.8.1V5.7c-.6-.1-1.2-.1-1.8-.1-1.9 0-4 .5-5.7 1.8Z" fill="none" stroke="#a8672e" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 7.4v11.8" fill="none" stroke="#a8672e" stroke-width="1.4" stroke-linecap="round"/></svg>"""

verse_blocks = []
for v in verses:
    deva_lines = "<br/>".join(v["deva"])
    iast_lines = "<br/>".join(v["iast"])
    cards = "".join(
        f'<div class="wbw"><span class="wbw-deva" lang="sa">{c["deva"]}</span>'
        f'<span class="wbw-iast">{c["iast"]}</span>'
        f'<span class="wbw-gloss">{c["gloss"]}</span>'
        f'<span class="wbw-tags">{c["tags"]}</span></div>'
        for c in v["wbw"]
    )
    wbw_html = f'<p class="wbw-label">Word by word</p><div class="wbw-grid">{cards}</div>' if v["wbw"] else ""
    verse_blocks.append(f"""
<section class="verse">
  <p class="verse-num" lang="sa">{v["num"]}</p>
  <p class="v-deva" lang="sa">{deva_lines}</p>
  <p class="v-iast">{iast_lines}</p>
  <p class="v-trans">{v["trans"]}</p>
  {wbw_html}
</section>""")

gl_rows = "".join(
    f'<div class="gl-row"><span class="gl-deva" lang="sa">{g["deva"]}</span>'
    f'<span class="gl-iast">{g["iast"]}</span>'
    f'<span class="gl-gloss">{g["gloss"]}</span>'
    f'<span class="gl-occ" lang="sa">{g["occ"]}</span></div>'
    for g in glossary
)

html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Śrī Dakṣiṇāmūrti Stotram</title></head>
<body>

<!-- ============ Cover ============ -->
<section class="cover">
  <div class="cover-inner">
    {BOOK_SVG.format(cls="cover-mark")}
    <h1 class="cover-title"><span class="ct-main">Śrī Dakṣiṇāmūrti</span><br/><span class="ct-accent">Stotram</span></h1>
    <p class="cover-deva" lang="sa">श्रीदक्षिणामूर्तिस्तोत्रम्</p>
    <p class="cover-tagline">Sanskrit text · transliteration · annotated English translation</p>
  </div>
  <p class="cover-foot">oleandrum.github.io/dakshinamurti-stotram · 2026</p>
</section>

<!-- ============ Contents ============ -->
<section class="chapter toc-page">
  <h2 id="toc">Contents</h2>
  <ul class="toc">
    <li><a href="#intro">Introduction</a></li>
    <li><a href="#about">About the Text</a></li>
    <li><a href="#stotram">Śrī Dakṣiṇāmūrti Stotram</a></li>
    <li><a href="#colophon">Colophon</a></li>
    <li><a href="#glossary">Glossary</a></li>
    <li><a href="#translit">Transliteration &amp; Translation Notes</a></li>
    <li><a href="#license">License</a></li>
  </ul>
</section>

<!-- ============ Introduction ============ -->
<section class="chapter">
  <h2 id="intro">Introduction</h2>
  <div class="prose intro">{intro_html}</div>
</section>

<!-- ============ About ============ -->
<section class="chapter">
  <h2 id="about">About the Text</h2>
  <div class="prose">{about_html}</div>
</section>

<!-- ============ Stotram ============ -->
<section class="chapter">
  <h2 id="stotram">Śrī Dakṣiṇāmūrti Stotram</h2>
  {"".join(verse_blocks)}
</section>

<!-- ============ Colophon ============ -->
<section class="chapter">
  <h2 id="colophon">Colophon</h2>
  <div class="prose">{colophon_html}</div>
</section>

<!-- ============ Glossary ============ -->
<section class="chapter">
  <h2 id="glossary">Glossary</h2>
  <p class="gl-note">Every distinct word appearing across all verses, drawn from the word-by-word data. Numbers refer to the verse(s) in which each word occurs.</p>
  <div class="gl">{gl_rows}</div>
</section>

<!-- ============ Transliteration notes ============ -->
<section class="chapter">
  <h2 id="translit">Transliteration &amp; Translation Notes</h2>
  <div class="prose">{translit_html}</div>
</section>

<!-- ============ License ============ -->
<section class="chapter">
  <h2 id="license">License</h2>
  <div class="prose">{strip_links(lic).decode_contents() if lic else ""}</div>
</section>

</body></html>"""

# Strip site-internal links from prose blocks (occurrence links, nav links)
doc = BeautifulSoup(html, "html.parser")
for a in doc.select(".prose a, .gl a"):
    href = a.get("href", "")
    if "creativecommons" in href or href.startswith("http"):
        continue  # keep external URLs (rendered as plain text anyway)
    a.name = "span"
# drop the license h1 remnants if any
for h1 in doc.select(".prose h1"):
    h1.decompose()
# drop a duplicated leading "License" subheading inside the license chapter
lic_ch = doc.select_one("#license")
if lic_ch:
    first_h2 = lic_ch.find_next("h2")
    if first_h2 and first_h2.get_text(strip=True) == "License":
        first_h2.decompose()
html = str(doc)

OUT_HTML.write_text(html)
print("HTML assembled:", len(html), "chars,", len(verses), "verses,", len(glossary), "glossary entries")


# ---------------- render ----------------
from weasyprint import HTML, CSS
HTML(str(OUT_HTML)).write_pdf(str(OUT_PDF), stylesheets=[CSS(str(Path(__file__).parent / "print.css"))])
print("PDF written:", OUT_PDF)
