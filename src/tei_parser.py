"""Parser for FreeDict TEI XML dictionaries.

Parses TEI-formatted XML files (e.g. from freedict.org) and yields entries
that can be directly packed into Yomitan format without going through DSL.
"""

import logging
from collections.abc import Iterator
from typing import Any
from xml.etree.ElementTree import Element

import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class TeiEntry:
    """A parsed TEI dictionary entry."""

    def __init__(
        self,
        headword: str,
        pronunciations: list[str],
        pos: str,
        translations: list[str],
        definitions: list[str],
    ):
        self.headword = headword
        self.pronunciations = pronunciations
        self.pos = pos
        self.translations = translations
        self.definitions = definitions


class TeiParser:
    """Parses FreeDict TEI XML files."""

    NS = {"tei": "http://www.tei-c.org/ns/1.0"}

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.title: str = ""
        self.source_lang: str = ""
        self.headword_count: int = 0

    def parse(self) -> Iterator[TeiEntry]:
        """Parses the TEI file and yields TeiEntry items."""
        tree = ET.parse(self.file_path)
        root = tree.getroot()

        self._parse_header(root)

        body = root.find(".//tei:body", self.NS)
        if body is None:
            logger.error(f"No <body> element found in {self.file_path}")
            return

        for entry_elem in body.findall("tei:entry", self.NS):
            parsed = self._parse_entry(entry_elem)
            if parsed:
                yield parsed

    def _parse_header(self, root: Element) -> None:
        """Extracts metadata from TEI header."""
        title_elem = root.find(".//tei:titleStmt/tei:title", self.NS)
        if title_elem is not None and title_elem.text:
            self.title = title_elem.text

        extent_elem = root.find(".//tei:extent", self.NS)
        if extent_elem is not None and extent_elem.text:
            # e.g. "13283 headwords"
            parts = extent_elem.text.split()
            if parts and parts[0].isdigit():
                self.headword_count = int(parts[0])

        body = root.find(".//tei:body", self.NS)
        if body is not None:
            self.source_lang = body.get("{http://www.w3.org/XML/1998/namespace}lang", "")

    def _parse_entry(self, entry: Element) -> TeiEntry | None:
        """Parses a single <entry> element."""
        # Headword
        orth = entry.find("tei:form/tei:orth", self.NS)
        if orth is None or not orth.text:
            return None
        headword = orth.text.strip()

        # Pronunciations
        pronunciations = []
        for pron in entry.findall("tei:form/tei:pron", self.NS):
            if pron.text:
                pronunciations.append(pron.text.strip())

        # Part of speech
        pos = ""
        pos_elem = entry.find("tei:gramGrp/tei:pos", self.NS)
        if pos_elem is not None and pos_elem.text:
            pos = pos_elem.text.strip()

        # Translations and definitions from sense elements
        translations = []
        definitions = []
        self._extract_sense(entry, translations, definitions)

        if not translations:
            return None

        return TeiEntry(
            headword=headword,
            pronunciations=pronunciations,
            pos=pos,
            translations=translations,
            definitions=definitions,
        )

    def _extract_sense(
        self,
        elem: Element,
        translations: list[str],
        definitions: list[str],
    ) -> None:
        """Recursively extracts translations and definitions from sense elements."""
        for sense in elem.findall("tei:sense", self.NS):
            # Translations: <cit type="trans"><quote>...</quote></cit>
            for cit in sense.findall("tei:cit[@type='trans']", self.NS):
                for quote in cit.findall("tei:quote", self.NS):
                    if quote.text:
                        translations.append(quote.text.strip())

            # Definitions from nested senses: <sense><def>...</def></sense>
            for nested_sense in sense.findall("tei:sense", self.NS):
                for defn in nested_sense.findall("tei:def", self.NS):
                    if defn.text:
                        definitions.append(defn.text.strip())

            # Direct definitions
            for defn in sense.findall("tei:def", self.NS):
                if defn.text:
                    definitions.append(defn.text.strip())


def tei_entry_to_structured_content(entry: TeiEntry, target_lang: str = "ru") -> list[dict[str, Any]]:
    """Converts a TeiEntry to Yomitan structured-content JSON."""
    content_items: list[dict[str, Any]] = []

    # POS line
    if entry.pos:
        pos_label = _pos_to_label(entry.pos, target_lang)
        content_items.append({
            "tag": "div",
            "data": {"content": "sense"},
            "content": {
                "tag": "span",
                "data": {"content": "abbreviation"},
                "content": pos_label,
            },
        })

    # Pronunciation
    if entry.pronunciations:
        pron_text = ", ".join(entry.pronunciations)
        content_items.append({
            "tag": "div",
            "data": {"content": "sense"},
            "content": [
                {
                    "tag": "span",
                    "data": {"content": "transcription"},
                    "content": f"[{pron_text}]",
                }
            ],
        })

    # Translations
    if entry.translations:
        trans_parts: list[Any] = []
        for i, t in enumerate(entry.translations):
            if i > 0:
                trans_parts.append(", ")
            trans_parts.append({
                "tag": "span",
                "data": {"content": "translation"},
                "content": t,
            })
        content_items.append({
            "tag": "div",
            "data": {"content": "sense", "class": "margin-1"},
            "content": trans_parts if len(trans_parts) > 1 else trans_parts[0],
        })

    # Definitions (Dutch explanations)
    for defn in entry.definitions:
        content_items.append({
            "tag": "div",
            "data": {"content": "sense", "class": "margin-2"},
            "content": {
                "tag": "span",
                "data": {"content": "comment"},
                "content": defn,
            },
        })

    return content_items


def _pos_to_label(pos: str, target_lang: str = "ru") -> str:
    """Maps TEI POS codes to human-readable labels."""
    mappings = {
        "ru": {
            "n": "сущ.", "v": "гл.", "adj": "прил.", "adv": "нареч.",
            "pn": "собств.", "suffix": "суфф.", "prefix": "прист.",
            "prep": "предл.", "conj": "союз", "interj": "межд.",
            "pron": "мест.", "num": "числ.", "art": "арт.",
        },
        "de": {
            "n": "Subst.", "v": "V.", "adj": "Adj.", "adv": "Adv.",
            "pn": "Eigenn.", "suffix": "Suff.", "prefix": "Präf.",
            "prep": "Präp.", "conj": "Konj.", "interj": "Interj.",
            "pron": "Pron.", "num": "Num.", "art": "Art.",
        },
        "nl": {
            "n": "znw.", "v": "ww.", "adj": "bn.", "adv": "bw.",
            "pn": "eigenn.", "suffix": "suff.", "prefix": "voorv.",
            "prep": "vz.", "conj": "vw.", "interj": "tw.",
            "pron": "vnw.", "num": "telw.", "art": "lidw.",
        },
    }
    mapping = mappings.get(target_lang, mappings["ru"])
    return mapping.get(pos, pos)


def tei_pos_to_rules(pos: str) -> list[str]:
    """Maps TEI POS to Yomitan deinflection rules."""
    mapping = {
        "n": ["n"],
        "v": ["v"],
        "adj": ["adj"],
        "adv": ["adv"],
    }
    return mapping.get(pos, [])
