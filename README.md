# DSL to Yomitan German Dictionaries

Convert German [ABBYY Lingvo DSL](https://lingvo.wiki/dsl-format) dictionaries into [Yomitan](https://github.com/yomidevs/yomitan)-compatible ZIP archives. Point the tool at a folder of `.dsl` files, and it produces ready-to-import dictionary packages — so you can hover over any German word in your browser and instantly see rich definitions, examples, and translations.

[README in Russian](./README.ru.md)

---

## How It Works

The converter runs a three-stage pipeline:

```
  .dsl file          Structured JSON         Yomitan ZIP
      |                    |                      |
      v                    v                      v
 +---------+       +--------------+         +---------+
 |  PARSE  | ----> |   CONVERT    | ------> |  PACK   |
 +---------+       +--------------+         +---------+
 DslParser          DslConverter             YomitanPacker
 src/parser.py      src/converter.py         src/packer.py
```

1. **Parse** — reads UTF-16 encoded `.dsl` files and extracts headword/definition pairs
2. **Convert** — transforms DSL tag markup (`[b]`, `[c]`, `[ex]`, ...) into Yomitan structured-content JSON
3. **Pack** — bundles entries into Yomitan v3 ZIP archives, splitting into 10,000-entry term banks, and includes styles with dark mode support

`main.py` orchestrates the full run: it auto-detects dictionary language pairs (De-De, De-Ru, Ru-De), loads abbreviation files, and drives entries through all three stages.

## Installation

Requires **Python 3.10+**.

```bash
git clone https://github.com/acheronex/dsl-to-yomitan-german-dictionaries.git
cd dsl-to-yomitan-german-dictionaries

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Usage

### Basic usage

```bash
python main.py --input "path/to/dsl/folder" --output "out/"
```

### Where to Get DSL Dictionaries

This tool converts existing DSL dictionaries. You can find them in:

- **GoldenDict forums** — community discussions and resources
- **Ru-Board** — Russian software forums
- **Torrents** — various dictionary collections
- **Your existing GoldenDict/Lingvo installation**

*Note: DSL dictionaries are typically proprietary and require proper licensing. Please respect copyright laws in your jurisdiction.*

### Example: Convert Langenscheidt dictionary

```bash
python main.py \
  --input "LINGVO X3 DEUTSCH AS FORIEGN BY LANGENS DE_DE_DSL" \
  --output out/
```

Output:
```
INFO: Processing De-De-Langens_gwdaf.dsl...
INFO: Successfully created out/De-De-Langens_gwdaf.zip with 32687 entries.
```

## Input Format

The tool expects a folder containing `.dsl` files:

```
your-dictionary-folder/
├── DictionaryName.dsl        # Main dictionary file
├── DictionaryName.ann        # Optional annotations file
├── DictionaryName_abrv.dsl   # Optional abbreviations
└── *.tif, *.wav             # Optional media files
```

<details>
<summary>Supported DSL tags</summary>

| Tag | Description |
|-----|-------------|
| `[b]...[/b]` | Bold |
| `[i]...[/i]` | Italic |
| `[u]...[/u]` | Underline |
| `[sup]...[/sup]` | Superscript |
| `[sub]...[/sub]` | Subscript |
| `[c]...[/c]` | Colored text |
| `[m1]`, `[m2]`, `[m3]` | Margin levels (indentation) |
| `[trn]...[/trn]` | Translation |
| `[ref]...[/ref]` | Cross-reference |
| `[ex]...[/ex]` | Example sentence |
| `[p]...[/p]` | Part of speech / abbreviation |
| `[com]...[/com]` | Comment |
| `[s]...[/s]` | Media (images/sound) |
| `[t]...[/t]` | IPA transcription |
| `[lang id=N]...[/lang]` | Language zone |

</details>

## Output Format

The tool creates a ZIP archive compatible with Yomitan:

```
output/
└── DictionaryName.zip
    ├── index.json          # Dictionary metadata
    ├── term_bank_1.json    # First 10,000 entries
    ├── term_bank_2.json    # Next 10,000 entries (if needed)
    └── styles.css          # Dictionary styles (includes dark mode)
```

## Supported Dictionaries

Tested and working with:

- **Langenscheidt** — Deutsch als Fremdsprache (De-De)
- **Duden** — Das große Wörterbuch (De-De)
- **Duden** — Synonyme (De-De)
- **Duden** — Etymologie (De-De)
- **Universal** — De-Ru, Ru-De

## German Word Deinflection

By default, Yomitan searches for exact dictionary matches. For German, this means if you have a dictionary entry for "laufen" but you look up "lief" or "gelaufen", Yomitan won't find it.

We provide a custom `german-transforms.js` file in the `yomitan-de-language/` folder that adds German word deinflection rules:

- **Verbs**: "lief" → "laufen", "gelaufen" → "laufen"
- **Nouns**: "Männer" → "Mann", "Tische" → "Tisch"
- **Adjectives**: "schnellste" → "schnell"
- **Umlauts**: "Bäume" → "Baume"

### Installation

Download the latest Yomitan release from https://github.com/yomidevs/yomitan/releases, extract it, replace `german-transforms.js` in `js/language/de/` with the one from `yomitan-de-language/`, then load it as an unpacked extension in Chrome (enable Developer mode in `chrome://extensions/` and click "Load unpacked").

**Note:** This is a community-made solution. The rules may not cover all German word forms. Feel free to improve it!

See `yomitan-de-language/README.md` for detailed instructions.

## Anki Integration

A pre-configured Anki deck optimized for German vocabulary learning with Yomitan.

- **Proper fields** — expression, reading, meaning, sentence, audio, conjugation, frequencies
- **Custom styling** — red highlights for keywords, gray translation text
- **Ready to use** — import and connect to Yomitan immediately

### Quick Setup

1. Download `anki-decks/German Yomitan.apkg` and double-click to import into Anki
2. In Yomitan settings → Anki, select deck and model: `Yomitan Close GERMAN`
3. Map fields (see `anki-decks/README.md` for detailed field mapping)
4. Click the "+" button in Yomitan to create cards

See [anki-decks/README.md](anki-decks/README.md) for complete setup guide.

## Development

### Running tests

```bash
pytest                              # all tests
pytest tests/test_converter.py      # single file
pytest tests/test_parser.py::test_bold_tag  # single test
```

### Code quality

```bash
ruff check .          # lint
ruff check . --fix    # auto-fix
ruff format .         # format
```

## Project Structure

```
.
├── main.py                  # CLI entry point (orchestrates the pipeline)
├── src/
│   ├── parser.py            # Stage 1: DSL file reading and entry extraction
│   ├── converter.py         # Stage 2: DSL tags → Yomitan structured-content JSON
│   ├── packer.py            # Stage 3: ZIP archive creation
│   ├── tag_map.py           # DSL tag definitions and regex patterns
│   └── exceptions.py        # Custom exceptions
├── data/
│   └── styles.css           # Default German dictionary stylesheet
├── yomitan-de-language/
│   ├── german-transforms.js # German word deinflection for Yomitan
│   └── README.md            # Installation instructions
├── tests/
│   ├── test_parser.py
│   ├── test_converter.py
│   └── test_packer.py
├── anki-decks/
│   ├── German Yomitan.apkg     # Pre-configured Anki deck for German
│   ├── README.md               # Setup guide (English)
│   └── README.ru.md            # Setup guide (Russian)
└── requirements.txt
```

## License

MIT License — see LICENSE file for details.

## Author

Evgeny Eroshev (GitHub: @acheronex)
