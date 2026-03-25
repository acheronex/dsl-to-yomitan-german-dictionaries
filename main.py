import argparse
import itertools
import logging
import sys
from datetime import datetime
from pathlib import Path

from src.parser import DslParser
from src.converter import DslConverter
from src.packer import YomitanPacker
from src.tei_parser import (
    TeiParser,
    tei_entry_to_structured_content,
    tei_pos_to_rules,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def load_abbreviations(input_path: Path) -> dict[str, str]:
    abbrevs = {}
    abrv_files = list(input_path.glob("*_abrv.dsl"))
    for abrv_file in abrv_files:
        logger.info(f"Loading abbreviations from {abrv_file.name}...")
        try:
            # Abrv files are simple: headword \n \t expansion
            with open(abrv_file, "r", encoding="utf-16") as f:
                current_abrv = None
                for line in f:
                    line = line.rstrip("\r\n")
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("\t"):
                        if current_abrv:
                            abbrevs[current_abrv] = line.strip()
                            current_abrv = None
                    else:
                        current_abrv = line.strip()
        except Exception as e:
            logger.warning(f"Failed to load abbreviations from {abrv_file}: {e}")
    return abbrevs

def get_rules_for_entry(body_text: str) -> list[str]:
    rules = []
    # Heuristic for German POS tagging based on abbreviations
    # Nouns
    if any(p in body_text for p in ["[p]f[/p]", "[p]m[/p]", "[p]n[/p]", "[p]nm[/p]", "[p]nf[/p]"]):
        rules.append("n")
    # Verbs
    if any(p in body_text for p in ["[p]v[/p]", "[p]vt[/p]", "[p]vi[/p]", "[p]refl[/p]"]):
        rules.append("v")
    # Adjectives
    if "[p]adj[/p]" in body_text:
        rules.append("adj")
    # Adverbs
    if "[p]adv[/p]" in body_text:
        rules.append("adv")

    return list(set(rules))


def detect_languages(dict_title: str, filename: str) -> tuple[str, str]:
    """Detect source and target languages from title/filename.

    Returns (source_language, target_language) ISO codes.
    """
    combined = f"{dict_title} {filename}".lower()

    # Dutch pairs
    if "nl-ru" in combined or "nld-rus" in combined:
        return "nl", "ru"
    if "ru-nl" in combined or "rus-nld" in combined:
        return "ru", "nl"
    if "nl-de" in combined or "nld-deu" in combined:
        return "nl", "de"
    if "de-nl" in combined or "deu-nld" in combined:
        return "de", "nl"

    # German pairs
    if "de-ru" in combined or "deu-rus" in combined:
        return "de", "ru"
    if "ru-de" in combined or "rus-deu" in combined:
        return "ru", "de"

    # Default: German-German
    return "de", "de"


def process_tei_files(input_path: Path, output_dir: str) -> None:
    """Process TEI XML dictionary files."""
    tei_files = list(input_path.glob("*.tei"))
    if not tei_files:
        return

    for tei_file in tei_files:
        logger.info(f"Processing TEI file {tei_file.name}...")

        tei_parser = TeiParser(str(tei_file))
        dict_name = tei_file.stem
        packer = YomitanPacker(output_dir, dict_name)

        # Get first entry to trigger header parsing, then read metadata
        entries_iter = tei_parser.parse()
        first_entry = next(entries_iter, None)

        dict_title = tei_parser.title or dict_name
        source_lang, target_lang = detect_languages(dict_title, dict_name)

        if tei_parser.source_lang:
            source_lang = tei_parser.source_lang

        sequence = 1
        all_entries = itertools.chain([first_entry], entries_iter) if first_entry else iter([])
        for entry in all_entries:
            structured_content = tei_entry_to_structured_content(entry, target_lang)
            glossary = [{"type": "structured-content", "content": structured_content}]
            rules = tei_pos_to_rules(entry.pos)

            packer.add_entry(entry.headword, "", glossary, sequence, rules)
            sequence += 1

        metadata = {
            "title": dict_title,
            "format": 3,
            "author": "DSL to Yomitan Converter",
            "sourceLanguage": source_lang,
            "targetLanguage": target_lang,
            "description": f"Converted from {tei_file.name}",
            "revision": datetime.now().strftime("%Y.%m.%d.%H%M%S"),
        }

        zip_path = packer.pack(metadata)
        logger.info(f"Successfully created {zip_path} with {sequence - 1} entries.")


def process_dsl_files(input_path: Path, output_dir: str) -> None:
    """Process DSL dictionary files."""
    abbreviations = load_abbreviations(input_path)

    dsl_files = list(input_path.glob("*.dsl"))
    main_dsls = [f for f in dsl_files if not f.name.endswith("_abrv.dsl")]

    if not main_dsls:
        return

    for main_dsl in main_dsls:
        logger.info(f"Processing {main_dsl.name}...")

        dsl_parser = DslParser(str(main_dsl))
        converter = DslConverter(abbreviations)

        # Get first entry to trigger header parsing, then read metadata
        entries_iter = dsl_parser.parse()
        first_entry = next(entries_iter, None)

        dict_title = dsl_parser.headers.get("NAME", main_dsl.stem)
        filename = main_dsl.stem
        if "Langenscheidt" in dict_title or "langens" in filename.lower():
            dict_title = "Langenscheidt De-De"
        elif "duden" in filename.lower() and "big" in filename.lower():
            dict_title = "Duden Big De-De"
        elif "duden" in filename.lower() and "synonym" in filename.lower():
            dict_title = "Duden Synonym De-De"
        elif "duden" in filename.lower() and "etym" in filename.lower():
            dict_title = "Duden Etym De-De"
        packer = YomitanPacker(output_dir, main_dsl.stem)

        sequence = 1
        all_entries = itertools.chain([first_entry], entries_iter) if first_entry else iter([])
        for entry in all_entries:
            headword = entry["headword"]
            clean_headword = converter.clean_headword(headword)

            body = entry["body"]
            body_text = "\n".join(body)

            structured_content = converter.convert_to_structured_content(body)
            glossary = [{"type": "structured-content", "content": structured_content}]
            rules = get_rules_for_entry(body_text)

            packer.add_entry(clean_headword, "", glossary, sequence, rules)
            sequence += 1

        # Add media files to packer (skip for Langens - TIFF images don't work in Yomitan)
        skip_media = "Langens" in dict_title or "langens" in str(input_path).lower()
        if not skip_media:
            for media_filename in converter.media_files:
                media_path = input_path / media_filename
                if media_path.exists():
                    packer.add_media_file(media_path)

        source_lang, target_lang = detect_languages(dict_title, filename)

        metadata = {
            "title": dict_title,
            "format": 3,
            "author": "DSL to Yomitan Converter",
            "sourceLanguage": source_lang,
            "targetLanguage": target_lang,
            "description": f"Converted from {main_dsl.name}",
            "revision": datetime.now().strftime("%Y.%m.%d.%H%M%S")
        }

        zip_path = packer.pack(metadata)
        logger.info(f"Successfully created {zip_path} with {sequence - 1} entries.")


def main():
    parser = argparse.ArgumentParser(description="Convert DSL/TEI dictionaries to Yomitan format.")
    parser.add_argument("--input", required=True, help="Path to the directory containing .dsl or .tei files")
    parser.add_argument("--output", required=True, help="Path to the output directory")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input path {input_path} does not exist.")
        sys.exit(1)

    tei_files = list(input_path.glob("*.tei"))
    dsl_files = [f for f in input_path.glob("*.dsl") if not f.name.endswith("_abrv.dsl")]

    if not tei_files and not dsl_files:
        logger.error(f"No .dsl or .tei files found in {input_path}")
        sys.exit(1)

    if tei_files:
        process_tei_files(input_path, args.output)

    if dsl_files:
        process_dsl_files(input_path, args.output)

if __name__ == "__main__":
    main()
