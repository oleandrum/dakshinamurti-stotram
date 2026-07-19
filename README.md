# Śrī Dakṣiṇāmūrti Stotram

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21438525.svg)](https://doi.org/10.5281/zenodo.21438525)

A personal translation of the *Śrī Dakṣiṇāmūrti Stotram* — Devanagari text,
IAST transliteration, word-by-word grammatical analysis, and an English
translation — built with [Eleventy](https://www.11ty.dev/) as a static site.

🔗 **[Live site →](https://oleandrum.github.io/dakshinamurti-stotram/)**

## Running locally

```sh
npm install
npm run serve      # dev server with live reload, http://localhost:8080
npm run build       # production build to _site/
```

Requires Node 18+.

## Project structure

```
src/
├── _data/
│   ├── site.json          site title, description, repo link, etc.
│   ├── verses.js            loads & sorts every YAML file in verse-files/
│   ├── verse-files/          the 10 verse YAML files (csf schema)
│   └── glossary.js           auto-generated concordance across all verses
├── _includes/
│   └── layouts/
│       ├── base.njk           site chrome: header, nav, theme switch, footer
│       └── page.njk            markdown-page wrapper (extends base)
├── assets/
│   ├── css/style.css
│   └── js/ (theme.js, toggle.js)
├── downloads/                 PDF/EPUB go here (see downloads/README.txt)
├── verses.njk                  paginated verse-page template (1 page per verse)
├── contents.njk                 contents page at /verses/ — lists all verses
├── index.njk                    homepage — hero, introduction, opening verse
├── glossary.njk                  renders the auto-generated glossary
├── about.md
├── colophon.md
├── license.md
└── transliteration-notes.md
```

## How the verse pages work

Each verse lives as one YAML file in `src/_data/verse-files/`, following the
`csf` (custom structured format) schema: Devanagari + IAST source text,
a `lexical_units` array (word-by-word grammatical analysis), and an English
`literary_translation`.

`src/_data/verses.js` loads and sorts every file in that folder. A single
template, `src/verses.njk`, uses Eleventy's `pagination` feature over that
data to generate one page per verse — **adding a verse is just dropping in
a new YAML file, no template changes needed.**

`src/_data/glossary.js` aggregates every `lexical_unit` across every verse,
deduplicated by `dictionary_headword`, into a site-wide glossary with
back-links to every verse a word appears in — derived entirely from data
already present in the verse files.

## Using this as a template for another translation

This was built to be reused:

1. Replace the files in `src/_data/verse-files/` with the new work's YAML
   files (same `csf` schema)
2. Update `src/_data/site.json` (title, description, slug, repo link)
3. Replace `about.md`, `colophon.md`, `transliteration-notes.md` content
4. Everything else — layouts, glossary, navigation, shortcodes, theme —
   works unchanged

## Markdown shortcodes

Available inside any `.md` page:

| Shortcode | Use |
|---|---|
| `{% deva "..." %}` | single-line Devanagari (e.g. a mantra) |
| `{% devaBlock %}...{% enddevaBlock %}` | multi-line Devanagari (e.g. a śloka), one line per source line |
| `{% iast "..." %}` | single-line IAST |
| `{% iastBlock %}...{% endiastBlock %}` | multi-line IAST |
| `{% devaIast %}देवनागरी \| iast{% enddevaIast %}` | paired Devanagari + IAST, one `deva \| iast` pair per line |
| `{% quote %}...{% endquote %}` | pull-quote, no attribution |
| `{% quoteBy "Author" %}...{% endquoteBy %}` | pull-quote with attribution |
| `{% figure "/path.jpg", "alt text", "caption" %}` | image with optional caption |

Markdown pages also support:

- **Footnotes** — `text[^1]` ... `[^1]: note text` (via markdown-it-footnote)
- **Abbreviations** — `*[abbr]: expansion` anywhere in the file, then just
  write `abbr` in text; renders as a hoverable `<abbr>` tag
- **Callout boxes** — `::: note` / `::: warning` / `::: tip` containers,
  styled to match the site (not the plugin's default look)

## Fonts

Tiro Devanagari Sanskrit, Gentium Book Plus, Source Serif 4, and JetBrains
Mono, served via [Bunny Fonts](https://fonts.bunny.net) (a privacy-friendly
Google Fonts mirror, no cookies/tracking).

## Deployment

Deploys via GitHub Actions ([`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml))
on every push to `main`. Set **Settings → Pages → Source** to **GitHub Actions**.

## Downloads

PDF and EPUB download buttons are already wired up in the footer, pointing
to `/downloads/<slug>.pdf` and `.epub`. See
[`src/downloads/README.txt`](src/downloads/README.txt) — add the generated
files there and the links work with no further changes.

## Contact page

Intentionally omitted for now, since GitHub Pages has no backend. If added
later, [Formspree](https://formspree.io) (free tier, no backend required) is
a reasonable option.

## License

Site code (templates, CSS, JS, build config) is MIT-licensed. The
translation, word-by-word analysis, and notes are licensed under
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) —
see [`license.md`](src/license.md) for details.
