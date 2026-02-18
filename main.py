import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from src.parser import DslParser
from src.converter import DslConverter
from src.packer import YomitanPacker

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

def main():
    parser = argparse.ArgumentParser(description="Convert German DSL dictionaries to Yomitan format.")
    parser.add_argument("--input", required=True, help="Path to the directory containing .dsl files")
    parser.add_argument("--output", required=True, help="Path to the output directory")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input path {input_path} does not exist.")
        sys.exit(1)

    abbreviations = load_abbreviations(input_path)

    # Find all main DSL files (not _abrv.dsl)
    dsl_files = list(input_path.glob("*.dsl"))
    main_dsls = [f for f in dsl_files if not f.name.endswith("_abrv.dsl")]

    if not main_dsls:
        logger.error(f"No main .dsl file found in {input_path}")
        sys.exit(1)

    for main_dsl in main_dsls:
        logger.info(f"Processing {main_dsl.name}...")

        dsl_parser = DslParser(str(main_dsl))
        converter = DslConverter(abbreviations)
        
        # Trigger header parsing
        temp_parser = DslParser(str(main_dsl))
        try:
            next(temp_parser.parse())
        except StopIteration:
            pass
        
        dict_title = temp_parser.headers.get("NAME", main_dsl.stem)
        filename = main_dsl.stem
        if "Langenscheidt" in dict_title or "langens" in filename.lower():
            dict_title = "Langenscheidt De-De"
        elif "duden" in filename.lower() and "big" in filename.lower():
            dict_title = "Duden Big De-De"
        elif "duden" in filename.lower() and "synonym" in filename.lower():
            dict_title = "Duden Synonym De-De"
        elif "duden" in filename.lower() and "etym" in filename.lower():
            dict_title = "Duden Etym De-De"
        packer = YomitanPacker(args.output, main_dsl.stem)

        sequence = 1
        for entry in dsl_parser.parse():
            headword = entry["headword"]
            clean_headword = converter.clean_headword(headword)
            
            body = entry["body"]
            body_text = "\n".join(body)
            
            # Convert tags in body lines
            # Reset converter media files for this entry if needed, but it's better to keep them cumulative for the dictionary
            structured_content = converter.convert_to_structured_content(body)
            
            # Wrap in the format Yomitan expects for glossary items
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
                else:
                    pass

        metadata = {
            "title": dict_title,
            "format": 3,
            "author": "DSL to Yomitan Converter",
            "sourceLanguage": "de",
            "targetLanguage": "de", # Default to German-German
            "description": f"Converted from {main_dsl.name}",
            "revision": datetime.now().strftime("%Y.%m.%d.%H%M%S")
        }
        
        # Check if it's De-Ru
        if "De-Ru" in dict_title or "DeRu" in main_dsl.name:
            metadata["targetLanguage"] = "ru"
        elif "Ru-De" in dict_title or "RuDe" in main_dsl.name:
            metadata["sourceLanguage"] = "ru"
            metadata["targetLanguage"] = "de"

        # Packer automatically includes data/styles.css
        zip_path = packer.pack(metadata)
        logger.info(f"Successfully created {zip_path} with {sequence - 1} entries.")

if __name__ == "__main__":
    main()
