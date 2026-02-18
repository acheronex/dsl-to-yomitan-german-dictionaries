import json
import zipfile
from pathlib import Path
from typing import Any

# Default styles.css location relative to project root
DEFAULT_STYLES_PATH = Path(__file__).parent.parent / "data" / "styles.css"


class YomitanPacker:
    def __init__(self, output_dir: str, dictionary_name: str):
        self.output_dir = Path(output_dir)
        self.dictionary_name = dictionary_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.entries: list[list[Any]] = []
        self.media_files: dict[str, Path] = {}  # filename -> source_path
        self.max_entries_per_bank = 10000

    def add_entry(self, term: str, reading: str, glossary: list[dict[str, Any]], sequence: int, rules: list[str] | None = None):
        """
        Adds an entry in Yomitan format:
        [term, reading, definition_tags, rules, score, [glossary], sequence, term_tags]
        """
        entry = [
            term,
            reading,
            "",  # definition_tags
            " ".join(rules) if rules else "",  # rules
            0,   # score
            glossary,
            sequence,
            ""   # term_tags
        ]
        self.entries.append(entry)

    def add_media_file(self, source_path: Path):
        """Adds a media file to be included in the ZIP root."""
        if source_path.exists():
            self.media_files[source_path.name] = source_path

    def pack(self, metadata: dict[str, Any], styles_path: Path | None = None):
        """Creates the ZIP archive with index.json, styles.css, term banks."""
        zip_path = self.output_dir / f"{self.dictionary_name}.zip"

        # Use provided styles_path or fall back to default
        style_to_use = styles_path if styles_path else DEFAULT_STYLES_PATH

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Write index.json
            zipf.writestr("index.json", json.dumps(metadata, ensure_ascii=False, indent=4))

            # Always include styles.css if it exists
            if style_to_use and style_to_use.exists():
                zipf.write(style_to_use, "styles.css")

            # Write media files to root
            for filename, source_path in self.media_files.items():
                zipf.write(source_path, filename)

            # Write term banks
            for i in range(0, len(self.entries), self.max_entries_per_bank):
                bank_num = (i // self.max_entries_per_bank) + 1
                bank_entries = self.entries[i : i + self.max_entries_per_bank]
                filename = f"term_bank_{bank_num}.json"
                zipf.writestr(filename, json.dumps(bank_entries, ensure_ascii=False))

        return zip_path
