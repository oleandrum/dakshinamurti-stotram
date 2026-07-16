// src/_data/verses.js
//
// Loads every YAML file in verse-files/, sorted by verse.order.
// To add a verse: drop a new .csf-schema YAML file into verse-files/.
// To reuse this whole site for a different work: replace the files in
// verse-files/ — no template changes needed.

const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

module.exports = () => {
  const dir = path.join(__dirname, "verse-files");
  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".yaml") || f.endsWith(".yml"));

  const verses = files.map((f) => {
    const raw = fs.readFileSync(path.join(dir, f), "utf8");
    return yaml.load(raw);
  });

  verses.sort((a, b) => a.verse.order - b.verse.order);
  return verses;
};
