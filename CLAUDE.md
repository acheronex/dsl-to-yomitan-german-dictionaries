# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python tool that converts ABBYY Lingvo DSL and FreeDict TEI dictionaries into Yomitan-compatible ZIP archives. Two pipelines: DSL parsing → tag conversion to structured-content JSON → ZIP packing; TEI XML parsing → structured-content JSON → ZIP packing. Supports German (De-De, De-Ru, Ru-De) and Dutch (Nl-Ru, Ru-Nl) language pairs.

## Commands

```bash
# Install dependencies (Python 3.10+, use a venv)
pip install -r requirements.txt

# Run the converter
python main.py --input <dsl-or-tei-directory> --output <output-directory>

# Run all Python tests
pytest

# Run a single test file or function
pytest tests/test_converter.py
pytest tests/test_converter.py::test_clean_headword

# Run JS tests for german-transforms (Node.js built-in test runner)
cd yomitan-de-language && node --test

# Lint and format
ruff check .
ruff check . --fix
ruff format .
```

## Architecture

Two parallel pipelines share a common packer. `main.py` auto-detects `.dsl` vs `.tei` files in the input directory and routes to the appropriate pipeline.

**DSL pipeline** (three-stage):

1. **`src/parser.py`** — `DslParser` reads UTF-16 encoded `.dsl` files, yields `DslEntry` TypedDict items (headword + body lines). Non-indented lines are headwords, tab-indented lines are definition body.

2. **`src/converter.py`** — `DslConverter` transforms DSL tag markup into Yomitan structured-content JSON. Uses a stack-based tokenizer/parser (`_tokenize` → `_build_tree` → `_create_tag_object`) that handles malformed/overlapping tags gracefully. This is the most complex module (~350 lines).

3. **`src/packer.py`** — `YomitanPacker` bundles entries into Yomitan v3 format ZIP archives. Splits term banks at 10,000 entries each. ZIP contains `index.json`, `styles.css`, `term_bank_N.json`, and optional media files.

**TEI pipeline** (two-stage):

1. **`src/tei_parser.py`** — `TeiParser` reads FreeDict TEI XML files via `xml.etree.ElementTree`, yields `TeiEntry` objects (headword, pronunciations, POS, translations, definitions). `tei_entry_to_structured_content()` converts entries directly to Yomitan structured-content JSON, bypassing the DSL converter. POS labels are mapped to Russian abbreviations (`_pos_to_label`).

2. Shares `YomitanPacker` with the DSL pipeline.

**Supporting modules:**
- **`src/tag_map.py`** — Centralized regex patterns for DSL tag matching (used by converter, not by TEI pipeline)
- **`src/exceptions.py`** — `MalformedDslError` for invalid DSL input
- **`main.py`** — CLI entry point; handles abbreviation loading, POS detection heuristics, dictionary language pair auto-detection (De-De, De-Ru, Ru-De, Nl-Ru, Ru-Nl), and dictionary title normalization for known dictionaries (Langenscheidt, Duden variants)

**Non-Python components:**
- **`yomitan-de-language/german-transforms.js`** — German deinflection rules for Yomitan (standalone JS, not part of the Python pipeline). Uses ES module exports. Tests use Node.js built-in test runner (`node --test`).
- **`data/styles.css`** — Stylesheet bundled into output ZIPs. Uses `data-sc-content` and `data-sc-class` attributes for semantic styling. Includes dark mode via `@media (prefers-color-scheme: dark)`.

## Key Technical Details

- DSL files are UTF-16 encoded; the parser opens with `encoding="utf-16"`
- TEI files are standard UTF-8 XML with namespace `http://www.tei-c.org/ns/1.0`
- The DSL converter maps tags (e.g. `[b]`, `[c]`, `[m1]`, `[ex]`, `[trn]`) to HTML elements with `data` attributes that Yomitan renders via `styles.css`
- Converter auto-upgrades `span` to `div` when content contains block-level elements (nested divs)
- Yomitan entry format is a v3 8-element array: `[term, reading, def_tags, rules, score, glossary, sequence, term_tags]`
- Media files (audio/images) are included in ZIPs except TIFF (skipped for Langenscheidt compatibility)
- POS detection for DSL is heuristic: searches raw body text for `[p]...[/p]` patterns matching gender markers (nouns), verb tags, adj/adv
- Language pair detection uses filename and dictionary title substrings (e.g. "de-ru", "nl-ru", "nld-rus")
