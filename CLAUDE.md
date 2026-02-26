# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python tool that converts German ABBYY Lingvo DSL dictionaries into Yomitan-compatible ZIP archives. Pipeline: DSL parsing → tag conversion to structured-content JSON → ZIP packing.

## Commands

```bash
# Install dependencies (Python 3.10+, use a venv)
pip install -r requirements.txt

# Run the converter
python main.py --input <dsl-directory> --output <output-directory>

# Run all tests
pytest

# Run a single test file or function
pytest tests/test_converter.py
pytest tests/test_converter.py::test_clean_headword

# Lint and format
ruff check .
ruff check . --fix
ruff format .
```

## Architecture

Three-stage pipeline with clear module boundaries:

1. **`src/parser.py`** — `DslParser` reads UTF-16 encoded `.dsl` files, yields `DslEntry` TypedDict items (headword + body lines). Non-indented lines are headwords, tab-indented lines are definition body.

2. **`src/converter.py`** — `DslConverter` transforms DSL tag markup into Yomitan structured-content JSON. Uses a stack-based tokenizer/parser (`_tokenize` → `_build_tree` → `_create_tag_object`) that handles malformed/overlapping tags gracefully. This is the most complex module (~350 lines).

3. **`src/packer.py`** — `YomitanPacker` bundles entries into Yomitan v3 format ZIP archives. Splits term banks at 10,000 entries each. ZIP contains `index.json`, `styles.css`, `term_bank_N.json`, and optional media files.

Supporting modules:
- **`src/tag_map.py`** — Centralized regex patterns for DSL tag matching
- **`src/exceptions.py`** — `MalformedDslError` for invalid DSL input
- **`main.py`** — CLI entry point; handles abbreviation loading, POS detection heuristics, and dictionary language pair auto-detection (De-De, De-Ru, Ru-De)

Non-Python components:
- **`yomitan-de-language/german-transforms.js`** — German deinflection rules for Yomitan (standalone JS, not part of the Python pipeline)
- **`data/styles.css`** — Stylesheet bundled into output ZIPs, includes dark mode support via `prefers-color-scheme`

## Key Technical Details

- DSL files are UTF-16 encoded; `chardet` is used for encoding detection
- The converter maps DSL tags (e.g. `[b]`, `[c]`, `[m1]`, `[ex]`, `[trn]`) to HTML elements with `data-content` attributes that Yomitan uses for semantic styling
- Yomitan entry format is a v3 8-element array: `[term, reading, def_tags, rules, score, glossary, sequence, term_tags]`
- Media files (audio/images) are included in ZIPs except TIFF (skipped for Langenscheidt compatibility)
