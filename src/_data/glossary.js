// src/_data/glossary.js
//
// Builds a deduplicated glossary from every lexical_unit across every
// verse, grouped by dictionary_headword, each entry listing every verse
// it appears in. Pure derived data — nothing to maintain by hand.

module.exports = (data) => {
  // eleventyConfig data files can't depend on other data files by import
  // in older 11ty; instead this runs as a lazy fn re-reading verses.js.
  const loadVerses = require("./verses.js");
  const verses = loadVerses();

  const byHeadword = new Map();

  for (const v of verses) {
    const verseRef = {
      verseId: v.verse.id,
      order: v.verse.order,
      displayNumber: v.verse.display_number,
    };

    for (const lu of v.lexical_units || []) {
      const key = lu.dictionary_headword || lu.lemma;
      if (!byHeadword.has(key)) {
        byHeadword.set(key, {
          headword: key,
          lemma: lu.lemma,
          lemmaIast: lu.iast && lu.iast.lemma,
          pos: lu.pos,
          gloss: lu.gloss,
          occurrences: [],
        });
      }
      const entry = byHeadword.get(key);
      // Avoid duplicate verse references if a word appears twice in one verse
      if (!entry.occurrences.some((o) => o.verseId === verseRef.verseId)) {
        entry.occurrences.push(verseRef);
      }
    }
  }

  const entries = Array.from(byHeadword.values());
  // Sort by Devanagari headword (codepoint order groups the script sensibly)
  entries.sort((a, b) => a.headword.localeCompare(b.headword, "sa"));

  return entries;
};
