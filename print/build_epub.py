#!/usr/bin/env python3
"""Build the EPUB edition of dakshinamurti-stotram from the built _site output.

Usage:  python3 print/build_epub.py
Output: print/dakshinamurti-stotram.epub

Reads the same built HTML the PDF pipeline uses, so content edits to the
site flow into the ebook automatically. Embeds the site's fonts (all OFL).
If print/dakshinamurti-stotram.pdf exists and `pdftoppm` (poppler) is
available, its first page is rasterized into the EPUB cover image.
"""
import shutil
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup
from ebooklib import epub

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
FONTS = ROOT / "print" / "fonts"
OUT = ROOT / "print" / "dakshinamurti-stotram.epub"
PDF = ROOT / "print" / "dakshinamurti-stotram.pdf"

# ---------------- content extraction (same approach as build_pdf.py) ----------------

def soup_of(p):
    return BeautifulSoup((SITE / p).read_text(), "html.parser")

def prose_of(page, drop_h1=True):
    s = soup_of(page)
    el = s.select_one(".wrap.prose")
    if drop_h1:
        h1 = el.find("h1")
        if h1:
            h1.decompose()
    # internal site links become plain text
    for a in el.find_all("a"):
        href = a.get("href", "")
        if not href.startswith("http"):
            a.name = "span"
            a.attrs = {}
    return el.decode_contents()

home = soup_of("index.html")
intro_html = home.select_one(".hero-intro").decode_contents()
about_html = prose_of("about/index.html")
colophon_html = prose_of("colophon/index.html")
translit_html = prose_of("transliteration-notes/index.html")
license_html = prose_of("license/index.html")

verses = []
for i in range(1, 11):
    s = soup_of(f"verses/sds-{i:03d}/index.html")
    verses.append({
        "num": s.select_one(".verse-number").get_text(strip=True),
        "deva": [x.get_text(strip=True) for x in s.select(".verse-source-deva > span")],
        "iast": [x.get_text(strip=True) for x in s.select(".verse-source-iast > span")],
        "trans": s.select_one(".verse-translation p").get_text(strip=True),
        "wbw": [{
            "deva": c.select_one(".wbw-card-deva").get_text(strip=True),
            "iast": c.select_one(".wbw-card-iast").get_text(strip=True),
            "gloss": c.select_one(".wbw-card-gloss").get_text(strip=True),
            "tags": c.select_one(".wbw-card-tags").get_text(strip=True),
        } for c in s.select(".wbw-card")],
    })

gl = soup_of("glossary/index.html")
glossary = [{
    "deva": li.select_one(".glossary-headword").get_text(strip=True),
    "iast": li.select_one(".glossary-iast").get_text(strip=True),
    "gloss": li.select_one(".glossary-gloss").get_text(strip=True),
    "occ": ", ".join(a.get_text(strip=True) for a in li.select(".glossary-occurrences a")),
} for li in gl.select(".glossary-entry")]

# The tt reference grid uses CSS grid — convert to real tables for e-readers.
def tt_to_tables(html):
    doc = BeautifulSoup(html, "html.parser")
    tt = doc.select_one(".tt")
    if not tt:
        return html
    out = BeautifulSoup("<div class='tt'></div>", "html.parser")
    container = out.div
    for child in tt.children:
        if getattr(child, "name", None) == "p" and "tt-label" in child.get("class", []):
            p = out.new_tag("p", **{"class": "tt-label"})
            p.string = child.get_text(strip=True)
            container.append(p)
        elif getattr(child, "name", None) == "div" and "tt-grid" in child.get("class", []):
            table = out.new_tag("table", **{"class": "tt-table"})
            tr = out.new_tag("tr")
            for cell in child.select(".tt-cell"):
                td = out.new_tag("td")
                d = out.new_tag("span", **{"class": "tt-deva"})
                d.string = cell.select_one(".tt-deva").get_text(strip=True)
                i = out.new_tag("span", **{"class": "tt-iast"})
                i.string = cell.select_one(".tt-iast").get_text(strip=True)
                td.append(d)
                td.append(out.new_tag("br"))
                td.append(i)
                tr.append(td)
            table.append(tr)
            container.append(table)
    tt.replace_with(container)
    return str(doc)

translit_html = tt_to_tables(translit_html)

# ---------------- epub assembly ----------------

book = epub.EpubBook()
book.set_identifier("oleandrum-dakshinamurti-stotram")
book.set_title("Śrī Dakṣiṇāmūrti Stotram")
book.set_language("en")
book.add_metadata("DC", "language", "sa")
book.add_metadata("DC", "rights", "Translation and notes: CC BY-NC-SA 4.0. Site code: MIT.")
book.add_metadata("DC", "source", "https://oleandrum.github.io/dakshinamurti-stotram/")

CSS = """
body { font-family: "Source Serif 4", serif; line-height: 1.6; }
h1, h2 { font-family: "Source Serif 4", serif; font-weight: 600; }
h1 { font-size: 1.5em; }
h2 { font-size: 1.15em; color: #7a4e22; }
em, i { font-style: italic; }
.sa, [lang="sa"] { font-family: "Tiro Devanagari Sanskrit", serif; }
.iast { font-family: "Gentium Book Plus", serif; font-style: italic; }

.titlepage { text-align: center; margin-top: 18%; }
.tp-main { font-size: 1.9em; font-weight: 600; }
.tp-accent { font-size: 1.25em; color: #a8672e; letter-spacing: .18em; text-transform: uppercase; }
.tp-deva { font-family: "Tiro Devanagari Sanskrit", serif; font-size: 1.2em; margin: 1.2em 0; }
.tp-tag { font-size: .75em; color: #6b5d46; letter-spacing: .08em; text-transform: uppercase; }
.tp-foot { font-size: .7em; color: #6b5d46; margin-top: 3em; }

.verse-num { text-align: center; color: #a8672e; font-family: "Tiro Devanagari Sanskrit", serif; margin: 1.6em 0 .8em; }
.v-deva { font-family: "Tiro Devanagari Sanskrit", serif; text-align: center; font-size: 1.15em; line-height: 1.7; margin: 0 0 .6em; }
.v-iast { font-family: "Gentium Book Plus", serif; font-style: italic; text-align: center; color: #555; line-height: 1.6; margin: 0 0 1em; }
.v-trans { margin: 0 0 1.2em; }
.wbw-h { font-size: .8em; letter-spacing: .1em; text-transform: uppercase; color: #a8672e; margin: 1.2em 0 .5em; }
.wbw { margin: 0 0 .55em; font-size: .9em; text-indent: -1.2em; padding-left: 1.2em; }
.wbw .sa { font-size: 1.05em; }
.wbw .gloss { }
.wbw .tags { font-size: .8em; color: #777; }

.gl-entry { margin: 0 0 .7em; font-size: .92em; text-indent: -1.2em; padding-left: 1.2em; }
.gl-entry .occ { font-size: .82em; color: #777; }

.tt-label { font-size: .8em; letter-spacing: .1em; text-transform: uppercase; color: #a8672e; margin: 1.2em 0 .4em; }
table.tt-table { border-collapse: collapse; margin: 0 0 .5em; }
table.tt-table td { border: 1px solid #cbbf9f; padding: .3em .55em; text-align: center; }
.tt-deva { font-family: "Tiro Devanagari Sanskrit", serif; }
.tt-iast { font-family: "Gentium Book Plus", serif; font-style: italic; font-size: .82em; color: #7a4e22; }

table { border-collapse: collapse; }
th { text-align: left; font-size: .8em; text-transform: uppercase; letter-spacing: .06em;
     border-bottom: 2px solid #cbbf9f; padding: .3em .55em; }
td { border-bottom: 1px solid #ddd0ae; padding: .3em .55em; }

blockquote { margin: 1em 0 1em 1em; padding-left: 1em; border-left: 3px solid #7a4e22;
             font-family: "Gentium Book Plus", serif; font-style: italic; }
.callout, .callout-note, .callout-warning, .callout-tip {
  border: 1px solid #ddd0ae; padding: .8em 1em; margin: 1em 0; }
.callout-title { font-size: .8em; letter-spacing: .08em; text-transform: uppercase; color: #a8672e; margin: 0 0 .5em; }
abbr { text-decoration: none; border-bottom: 1px dotted #a8672e; }
"""
style = epub.EpubItem(uid="style", file_name="style/main.css", media_type="text/css", content=CSS)
book.add_item(style)

# Fonts (all OFL — embedding permitted)
font_files = [
    "TiroDevanagariSanskrit-Regular.ttf",
    "GentiumBookPlus-Regular.ttf",
    "GentiumBookPlus-Italic.ttf",
    "SourceSerif4-Regular.ttf",
    "SourceSerif4-Semibold.ttf",
    "SourceSerif4-Italic.ttf",
]
font_face = ""
for f in font_files:
    p = FONTS / f
    if not p.exists():
        continue
    book.add_item(epub.EpubItem(uid=f, file_name=f"fonts/{f}",
                                media_type="font/ttf", content=p.read_bytes()))
    fam = ("Tiro Devanagari Sanskrit" if "Tiro" in f
           else "Gentium Book Plus" if "Gentium" in f
           else "Source Serif 4")
    style_kind = "font-style: italic;" if "Italic" in f else ""
    weight = "font-weight: 600;" if "Semibold" in f else ""
    font_face += f'@font-face {{ font-family: "{fam}"; {style_kind} {weight} src: url("../fonts/{f}"); }}\n'
style.content = font_face + CSS

def chapter(uid, title, body_html):
    c = epub.EpubHtml(uid=uid, title=title, file_name=f"{uid}.xhtml", lang="en")
    c.content = f"<h1>{title}</h1>\n{body_html}"
    c.add_item(style)
    book.add_item(c)
    return c

# Cover (rasterized from the PDF if possible)
cover_added = False
if PDF.exists() and shutil.which("pdftoppm"):
    try:
        subprocess.run(["pdftoppm", "-png", "-r", "120", "-f", "1", "-l", "1",
                        str(PDF), "/tmp/epub-cover"], check=True)
        cover_png = Path("/tmp/epub-cover-1.png")
        if not cover_png.exists():
            cover_png = Path("/tmp/epub-cover-01.png")
        book.set_cover("cover.png", cover_png.read_bytes())
        cover_added = True
        print("cover: rasterized from PDF")
    except Exception as e:
        print("cover: skipped,", e)

# Title page
title_page = epub.EpubHtml(uid="titlepage", title="Title", file_name="titlepage.xhtml", lang="en")
title_page.content = """
<div class="titlepage">
  <p class="tp-main">Śrī Dakṣiṇāmūrti</p>
  <p class="tp-accent">Stotram</p>
  <p class="tp-deva" lang="sa">श्रीदक्षिणामूर्तिस्तोत्रम्</p>
  <p class="tp-tag">Sanskrit text · transliteration · annotated English translation</p>
  <p class="tp-foot">oleandrum.github.io/dakshinamurti-stotram · 2026</p>
</div>"""
title_page.add_item(style)
book.add_item(title_page)

ch_intro = chapter("intro", "Introduction", f'<div class="intro">{intro_html}</div>')
ch_about = chapter("about", "About the Text", about_html)

# Stotram — one file per verse, grouped in the TOC
verse_chapters = []
for v in verses:
    wbw = ""
    if v["wbw"]:
        units = "\n".join(
            f'<p class="wbw"><span class="sa" lang="sa">{u["deva"]}</span> '
            f'<span class="iast">{u["iast"]}</span> — '
            f'<span class="gloss">{u["gloss"]}</span> '
            f'<span class="tags">[{u["tags"]}]</span></p>'
            for u in v["wbw"])
        wbw = f'<p class="wbw-h">Word by word</p>\n{units}'
    n = v["num"].strip("॥ ").strip()
    uid = f"verse-{len(verse_chapters)+1:02d}"
    c = epub.EpubHtml(uid=uid, title=f"Verse {v['num']}", file_name=f"{uid}.xhtml", lang="en")
    c.content = f"""
<p class="verse-num" lang="sa">{v["num"]}</p>
<p class="v-deva" lang="sa">{"<br/>".join(v["deva"])}</p>
<p class="v-iast">{"<br/>".join(v["iast"])}</p>
<p class="v-trans">{v["trans"]}</p>
{wbw}"""
    c.add_item(style)
    book.add_item(c)
    verse_chapters.append(c)

ch_colophon = chapter("colophon", "Colophon", colophon_html)

gl_html = "\n".join(
    f'<p class="gl-entry"><span class="sa" lang="sa">{g["deva"]}</span> '
    f'<span class="iast">{g["iast"]}</span> — {g["gloss"]} '
    f'<span class="occ" lang="sa">{g["occ"]}</span></p>'
    for g in glossary)
ch_glossary = chapter("glossary", "Glossary",
    '<p>Every distinct word appearing across all verses. Numbers refer to the verse(s) in which each word occurs.</p>\n' + gl_html)

ch_translit = chapter("translit", "Transliteration &amp; Translation Notes", translit_html)
ch_license = chapter("license", "License", license_html)

# TOC + spine
book.toc = (
    ch_intro,
    ch_about,
    (epub.Section("Śrī Dakṣiṇāmūrti Stotram", href=verse_chapters[0].file_name), tuple(verse_chapters)),
    ch_colophon,
    ch_glossary,
    ch_translit,
    ch_license,
)
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())
book.spine = (["cover"] if cover_added else []) + ["titlepage", "nav", ch_intro, ch_about] + verse_chapters + [ch_colophon, ch_glossary, ch_translit, ch_license]

epub.write_epub(str(OUT), book)
print(f"EPUB written: {OUT} ({OUT.stat().st_size // 1024} KB, {len(verses)} verses, {len(glossary)} glossary entries)")
