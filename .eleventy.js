const markdownIt = require("markdown-it");
const markdownItFootnote = require("markdown-it-footnote");
const markdownItAttrs = require("markdown-it-attrs");
const markdownItAbbr = require("markdown-it-abbr");
const markdownItContainer = require("markdown-it-container");

module.exports = function (eleventyConfig) {
  // ---------------------------------------------------------------------
  // Passthrough copy
  // ---------------------------------------------------------------------
  eleventyConfig.addPassthroughCopy("src/assets");
  eleventyConfig.addPassthroughCopy("src/downloads");

  // ---------------------------------------------------------------------
  // Markdown-it setup: footnotes, attrs, and {% note %} / {% warning %}
  // style containers rendered as site-styled callout boxes.
  // ---------------------------------------------------------------------
  const md = markdownIt({ html: true, breaks: false, linkify: true })
    .use(markdownItFootnote)
    .use(markdownItAttrs)
    .use(markdownItAbbr)
    .use(markdownItContainer, "note", {
      render(tokens, idx) {
        if (tokens[idx].nesting === 1) {
          const title = tokens[idx].info.trim().slice("note".length).trim() || "Note";
          return `<div class="callout callout-note"><p class="callout-title">${title}</p>\n`;
        }
        return "</div>\n";
      },
    })
    .use(markdownItContainer, "warning", {
      render(tokens, idx) {
        if (tokens[idx].nesting === 1) {
          const title = tokens[idx].info.trim().slice("warning".length).trim() || "Warning";
          return `<div class="callout callout-warning"><p class="callout-title">${title}</p>\n`;
        }
        return "</div>\n";
      },
    })
    .use(markdownItContainer, "tip", {
      render(tokens, idx) {
        if (tokens[idx].nesting === 1) {
          const title = tokens[idx].info.trim().slice("tip".length).trim() || "Tip";
          return `<div class="callout callout-tip"><p class="callout-title">${title}</p>\n`;
        }
        return "</div>\n";
      },
    });

  eleventyConfig.setLibrary("md", md);

  // Markdown files also run through Nunjucks first, so shortcodes work
  // directly inside .md content, not just .njk templates.
  eleventyConfig.setFrontMatterParsingOptions({});
  eleventyConfig.addTemplateFormats("md");
  eleventyConfig.setLibrary("md", md);

  // ---------------------------------------------------------------------
  // Shortcodes for markdown pages
  // ---------------------------------------------------------------------

  // Single-line Devanagari (e.g. a mantra): {% deva "ॐ नमः शिवाय" %}
  eleventyConfig.addShortcode("deva", function (text) {
    return `<p class="script-line script-line--deva">${text}</p>`;
  });

  // Multi-line Devanagari block (e.g. a śloka), paired shortcode so line
  // breaks in the source are preserved:
  // {% devaBlock %}
  // line one
  // line two
  // {% enddevaBlock %}
  eleventyConfig.addPairedShortcode("devaBlock", function (content) {
    const lines = content.trim().split("\n").map((l) => l.trim()).filter(Boolean);
    const html = lines.map((l) => `<span class="script-block-line">${l}</span>`).join("\n");
    return `<div class="script-block script-block--deva">\n${html}\n</div>`;
  });

  // Single-line IAST: {% iast "namaste" %}
  eleventyConfig.addShortcode("iast", function (text) {
    return `<p class="script-line script-line--iast">${text}</p>`;
  });

  // Multi-line IAST block
  eleventyConfig.addPairedShortcode("iastBlock", function (content) {
    const lines = content.trim().split("\n").map((l) => l.trim()).filter(Boolean);
    const html = lines.map((l) => `<span class="script-block-line">${l}</span>`).join("\n");
    return `<div class="script-block script-block--iast">\n${html}\n</div>`;
  });

  // Combined Devanagari + IAST, line-paired:
  // {% devaIast %}
  // देवनागरी पंक्ति १ | iast line one
  // देवनागरी पंक्ति २ | iast line two
  // {% enddevaIast %}
  eleventyConfig.addPairedShortcode("devaIast", function (content) {
    const lines = content.trim().split("\n").map((l) => l.trim()).filter(Boolean);
    const rows = lines
      .map((l) => {
        const [deva, iast] = l.split("|").map((s) => (s || "").trim());
        return `<div class="deva-iast-row">
          <span class="deva-iast-deva">${deva || ""}</span>
          <span class="deva-iast-iast">${iast || ""}</span>
        </div>`;
      })
      .join("\n");
    return `<div class="deva-iast-block">\n${rows}\n</div>`;
  });

  // Quote without attribution: {% quote %}text{% endquote %}
  eleventyConfig.addPairedShortcode("quote", function (content) {
    return `<blockquote class="pull-quote"><p>${md.renderInline(content.trim())}</p></blockquote>`;
  });

  // Quote with author: {% quoteBy "Author Name" %}text{% endquoteBy %}
  eleventyConfig.addPairedShortcode("quoteBy", function (content, author) {
    return `<blockquote class="pull-quote pull-quote--attributed">
      <p>${md.renderInline(content.trim())}</p>
      <cite>— ${author}</cite>
    </blockquote>`;
  });

  // Figure/illustration: {% figure "/assets/img/x.jpg", "Alt text", "Optional caption" %}
  eleventyConfig.addShortcode("figure", function (src, alt, caption) {
    const capHtml = caption ? `<figcaption>${caption}</figcaption>` : "";
    return `<figure class="page-figure">
      <img src="${src}" alt="${alt || ""}" loading="lazy">
      ${capHtml}
    </figure>`;
  });

  // ---------------------------------------------------------------------
  // Filters
  // ---------------------------------------------------------------------
  eleventyConfig.addFilter("slugify", function (str) {
    return String(str)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, "");
  });

  eleventyConfig.addFilter("splitLines", function (str) {
    return String(str)
      .trim()
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean);
  });

  const ABBR = {
    gender: { masculine: "m.", feminine: "f.", neuter: "n." },
    number: { singular: "sg.", dual: "du.", plural: "pl." },
    case: {
      nominative: "nom.", accusative: "acc.", instrumental: "instr.",
      dative: "dat.", ablative: "abl.", genitive: "gen.", locative: "loc.",
      vocative: "voc.", stem: "stem",
    },
    person: { first: "1st", second: "2nd", third: "3rd" },
    pada: { parasmaipada: "para.", ātmanepada: "ātm." },
  };

  eleventyConfig.addFilter("grammarTag", function (lu) {
    const parts = [];
    if (lu.pos) parts.push(lu.pos);
    if (lu.gender) parts.push(ABBR.gender[lu.gender] || lu.gender);
    if (lu.number) parts.push(ABBR.number[lu.number] || lu.number);
    if (lu.case) parts.push(ABBR.case[lu.case] || lu.case);
    if (lu.person) parts.push(ABBR.person[lu.person] || lu.person);
    if (lu.pada) parts.push(ABBR.pada[lu.pada] || lu.pada);
    if (lu.lakara) parts.push(lu.lakara);
    if (lu.participle) parts.push(lu.participle);
    return parts.join(" · ");
  });

  return {
    pathPrefix: "/dakshinamurti-stotram/",
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      data: "_data",
    },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
};
