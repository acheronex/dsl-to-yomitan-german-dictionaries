# DSL to Yomitan German Dictionaries

A Python tool for converting German ABBYY Lingvo DSL dictionaries to Yomitan format.

[README in Russian](./README.ru.md)

---

## Description

This converter transforms German DSL dictionaries (used by GoldenDict, ABBYY Lingvo) into Yomitan-compatible ZIP archives. Optimized for German dictionaries like Duden, Langenscheidt, and Universal, but works with any DSL format dictionary.

## Features

- **DSL parsing** — reads UTF-16 encoded .dsl files with proper header extraction
- **Tag conversion** — transforms DSL tags (bold, italic, colors, margins, translations) to Yomitan structured-content JSON
- **Multi-dictionary support** — handles Duden, Langenscheidt, Universal, and other German DSL dictionaries
- **Automatic language detection** — detects De-De, De-Ru, Ru-De from dictionary headers
- **Dark mode support** — CSS uses `prefers-color-scheme` for automatic theme switching
- **Term bank splitting** — splits large dictionaries into 10,000 entry chunks
- **Unit tests** — pytest-based test coverage for parser, converter, and packer

## Installation

```bash
# Clone the repository
git clone https://github.com/acheronex/dsl-to-yomitan-german-dictionaries.git
cd dsl-to-yomitan-german-dictionaries

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Requirements

- Python 3.10+
- pytest (for testing)
- chardet (for encoding detection)
- ruff (for code linting)

## Usage

### Basic usage

```bash
python main.py --input "path/to/dsl/folder" --output "out/"
```

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

### Running tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_parser.py

# Run specific test
pytest tests/test_parser.py::test_bold_tag
```

### Code quality

```bash
# Lint
ruff check .

# Auto-fix lint errors
ruff check . --fix

# Format code
ruff format .
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

### Supported DSL tags

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

## Output Format

The tool creates a ZIP archive compatible with Yomitan:

```
output/
└── DictionaryName.zip
    ├── index.json          # Dictionary metadata
    ├── term_bank_1.json    # First 10,000 entries
    ├── term_bank_2.json    # Next 10,000 entries (if needed)
    └── styles.css          # Dictionary styles
```

## Where to Get DSL Dictionaries

This tool converts existing DSL dictionaries. You can find them in:

- **GoldenDict forums** — community discussions and resources
- **Ru-Board** — Russian software forums
- **Torrents** — various dictionary collections
- **Your existing GoldenDict/Lingvo installation**

*Note: DSL dictionaries are typically proprietary and require proper licensing. Please respect copyright laws in your jurisdiction.*

## Supported Dictionaries

Tested and working with:

- **Langenscheidt** — Deutsch als Fremdsprache (De-De)
- **Duden** — Das große Wörterbuch (De-De)
- **Duden** — Synonyme (De-De)
- **Duden** — Etymologie (De-De)
- **Universal** — De-Ru, Ru-De

## Project Structure

```
.
├── main.py                  # CLI entry point
├── src/
│   ├── parser.py            # DSL file reading and entry extraction
│   ├── converter.py         # DSL tags → Yomitan structured-content JSON
│   ├── packer.py            # ZIP archive creation
│   ├── tag_map.py           # DSL tag definitions and regex patterns
│   └── exceptions.py        # Custom exceptions
├── data/
│   └── styles.css           # Default German dictionary stylesheet
├── tests/
│   ├── test_parser.py
│   ├── test_converter.py
│   └── test_packer.py
└── requirements.txt
```

## License

MIT License — see LICENSE file for details.

## Author

Evgeny Eroshev (GitHub: @acheronex)
