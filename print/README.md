# Print & ebook editions (PDF, EPUB)

Generates `dakshinamurti-stotram.pdf` (A4 portrait, in the site's visual
style) and `dakshinamurti-stotram.epub` (reflowable, embedded fonts) from
the **built** site output in `_site/`.

## One-time setup

```bash
# 1. Python dependencies
pip install weasyprint beautifulsoup4 fonttools ebooklib

#    macOS: WeasyPrint needs Pango — install it first:
#    brew install pango

# 2. Fonts (downloads + installs to your user font dir)
./print/get_fonts.sh
```

## Regenerate

```bash
npm run build               # rebuild _site/ (both editions read from it)
python3 print/build_pdf.py  # → print/dakshinamurti-stotram.pdf
python3 print/build_epub.py # → print/dakshinamurti-stotram.epub
```

Run the PDF first: the EPUB rasterizes its cover from the PDF's first
page (needs `pdftoppm` from poppler — `brew install poppler` on macOS;
without it the EPUB still builds, with a styled title page instead).

Copy the results into `src/downloads/` so the site's download buttons
serve them:

```bash
cp print/dakshinamurti-stotram.pdf print/dakshinamurti-stotram.epub src/downloads/
npm run build
```

## How it works

- `build_pdf.py` parses the built HTML in `_site/` (homepage intro, about,
  the ten verse pages incl. word-by-word data, colophon, glossary,
  transliteration notes, license) and assembles `print/print.html`.
- `build_epub.py` extracts the same content into a reflowable EPUB 3:
  one chapter per verse (nested under a Stotram section in the TOC),
  word-by-word as hanging-indent entries, the IAST reference grid
  converted to real tables for e-reader compatibility, and the site's
  fonts embedded (all OFL-licensed, so embedding is permitted).
- `print.css` is the print stylesheet: A4 page setup, running header,
  page numbers, table of contents with `target-counter()` page
  references, and the site's parchment/bronze palette and font stack.
- WeasyPrint renders the final PDF. Devanagari shaping is handled by
  Pango/HarfBuzz.

Content changes (verses, translations, pages) require **no changes
here** — edit the site sources, rebuild, rerun. Only layout/styling
changes touch `print.css`.

## Notes

- The fonts must be installed system-wide (fontconfig): WeasyPrint's
  `@font-face` file loading is unreliable, so `print.css` references the
  families by name. `get_fonts.sh` handles installation on Linux and
  macOS.
- Known WeasyPrint quirks handled in the stylesheet: grid items must be
  `display: block`; no floated `::first-letter` drop caps.
