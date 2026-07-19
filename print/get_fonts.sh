#!/usr/bin/env bash
# Download the print-edition fonts (same families the site uses) into print/fonts/
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p fonts && cd fonts

GF="https://raw.githubusercontent.com/google/fonts/main/ofl"
JB="https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/fonts/ttf"

curl -sfLo TiroDevanagariSanskrit-Regular.ttf "$GF/tirodevanagarisanskrit/TiroDevanagariSanskrit-Regular.ttf"
curl -sfLo GentiumBookPlus-Regular.ttf        "$GF/gentiumbookplus/GentiumBookPlus-Regular.ttf"
curl -sfLo GentiumBookPlus-Italic.ttf         "$GF/gentiumbookplus/GentiumBookPlus-Italic.ttf"
curl -sfLo JetBrainsMono-Regular.ttf          "$JB/JetBrainsMono-Regular.ttf"
curl -sfLo JetBrainsMono-Medium.ttf           "$JB/JetBrainsMono-Medium.ttf"
curl -sfLo SourceSerif4-VF.ttf                "$GF/sourceserif4/SourceSerif4%5Bopsz%2Cwght%5D.ttf"
curl -sfLo SourceSerif4-Italic-VF.ttf         "$GF/sourceserif4/SourceSerif4-Italic%5Bopsz%2Cwght%5D.ttf"

# Instantiate static Source Serif 4 weights from the variable font
python3 - << 'PY'
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
for src, axes, out in [
    ("SourceSerif4-VF.ttf",        {"wght": 400, "opsz": 14}, "SourceSerif4-Regular.ttf"),
    ("SourceSerif4-VF.ttf",        {"wght": 600, "opsz": 14}, "SourceSerif4-Semibold.ttf"),
    ("SourceSerif4-VF.ttf",        {"wght": 700, "opsz": 14}, "SourceSerif4-Bold.ttf"),
    ("SourceSerif4-Italic-VF.ttf", {"wght": 400, "opsz": 14}, "SourceSerif4-Italic.ttf"),
]:
    f = TTFont(src)
    instantiateVariableFont(f, axes, inplace=True)
    f.save(out)
    print("instanced:", out)
PY

# Register the fonts with fontconfig so WeasyPrint/Pango can find them
FONT_DIR="$HOME/.local/share/fonts"   # Linux
if [[ "$(uname)" == "Darwin" ]]; then FONT_DIR="$HOME/Library/Fonts"; fi
mkdir -p "$FONT_DIR"
cp TiroDevanagariSanskrit-Regular.ttf GentiumBookPlus-*.ttf JetBrainsMono-*.ttf \
   SourceSerif4-Regular.ttf SourceSerif4-Semibold.ttf SourceSerif4-Bold.ttf SourceSerif4-Italic.ttf \
   "$FONT_DIR/"
command -v fc-cache >/dev/null && fc-cache -f "$FONT_DIR" || true
echo "Fonts installed to $FONT_DIR"
