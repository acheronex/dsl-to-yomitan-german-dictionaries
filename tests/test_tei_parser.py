"""Tests for TEI parser."""

import pytest

from src.tei_parser import (
    TeiEntry,
    TeiParser,
    tei_entry_to_structured_content,
    tei_pos_to_rules,
)

SAMPLE_TEI = """\
<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader xml:lang="en">
    <fileDesc>
      <titleStmt>
        <title>Nederlands-Русский FreeDict+WikDict dictionary</title>
      </titleStmt>
      <extent>3 headwords</extent>
      <publicationStmt><p/></publicationStmt>
      <sourceDesc><p/></sourceDesc>
    </fileDesc>
  </teiHeader>
  <text>
    <body xml:lang="nl">
      <entry>
        <form>
          <orth>kat</orth>
        </form>
        <gramGrp>
          <pos>n</pos>
        </gramGrp>
        <sense>
          <cit type="trans" xml:lang="ru">
            <quote>кот</quote>
            <quote>кошка</quote>
          </cit>
          <sense>
            <def>(roofdieren) bepaald soort zoogdier</def>
          </sense>
        </sense>
      </entry>
      <entry>
        <form>
          <orth>lopen</orth>
          <pron>/ˈloːpə(n)/</pron>
        </form>
        <gramGrp>
          <pos>v</pos>
        </gramGrp>
        <sense>
          <cit type="trans" xml:lang="ru">
            <quote>ходить</quote>
          </cit>
        </sense>
      </entry>
      <entry>
        <form>
          <orth>groot</orth>
          <pron>/ɣroːt/</pron>
        </form>
        <gramGrp>
          <pos>adj</pos>
        </gramGrp>
        <sense>
          <cit type="trans" xml:lang="ru">
            <quote>большой</quote>
            <quote>великий</quote>
          </cit>
          <sense>
            <def>van grote omvang</def>
          </sense>
          <sense>
            <def>belangrijk</def>
          </sense>
        </sense>
      </entry>
    </body>
  </text>
</TEI>
"""


@pytest.fixture
def tei_file(tmp_path):
    f = tmp_path / "test.tei"
    f.write_text(SAMPLE_TEI, encoding="utf-8")
    return f


class TestTeiParser:
    def test_parse_entries(self, tei_file):
        parser = TeiParser(str(tei_file))
        entries = list(parser.parse())
        assert len(entries) == 3

    def test_parse_header(self, tei_file):
        parser = TeiParser(str(tei_file))
        list(parser.parse())  # trigger parsing
        assert parser.title == "Nederlands-Русский FreeDict+WikDict dictionary"
        assert parser.headword_count == 3
        assert parser.source_lang == "nl"

    def test_entry_headword(self, tei_file):
        parser = TeiParser(str(tei_file))
        entries = list(parser.parse())
        assert entries[0].headword == "kat"
        assert entries[1].headword == "lopen"
        assert entries[2].headword == "groot"

    def test_entry_pos(self, tei_file):
        parser = TeiParser(str(tei_file))
        entries = list(parser.parse())
        assert entries[0].pos == "n"
        assert entries[1].pos == "v"
        assert entries[2].pos == "adj"

    def test_entry_translations(self, tei_file):
        parser = TeiParser(str(tei_file))
        entries = list(parser.parse())
        assert entries[0].translations == ["кот", "кошка"]
        assert entries[1].translations == ["ходить"]
        assert entries[2].translations == ["большой", "великий"]

    def test_entry_definitions(self, tei_file):
        parser = TeiParser(str(tei_file))
        entries = list(parser.parse())
        assert entries[0].definitions == ["(roofdieren) bepaald soort zoogdier"]
        assert entries[1].definitions == []
        assert entries[2].definitions == ["van grote omvang", "belangrijk"]

    def test_entry_pronunciation(self, tei_file):
        parser = TeiParser(str(tei_file))
        entries = list(parser.parse())
        assert entries[0].pronunciations == []
        assert entries[1].pronunciations == ["/ˈloːpə(n)/"]
        assert entries[2].pronunciations == ["/ɣroːt/"]


class TestTeiEntryToStructuredContent:
    def test_basic_entry(self):
        entry = TeiEntry(
            headword="kat",
            pronunciations=[],
            pos="n",
            translations=["кот", "кошка"],
            definitions=[],
        )
        content = tei_entry_to_structured_content(entry)
        assert len(content) == 2  # POS + translations

        # POS
        assert content[0]["data"]["content"] == "sense"
        pos_span = content[0]["content"]
        assert pos_span["data"]["content"] == "abbreviation"
        assert pos_span["content"] == "сущ."

        # Translations
        trans_div = content[1]
        assert trans_div["data"]["content"] == "sense"

    def test_entry_with_pronunciation(self):
        entry = TeiEntry(
            headword="lopen",
            pronunciations=["/ˈloːpə(n)/"],
            pos="v",
            translations=["ходить"],
            definitions=[],
        )
        content = tei_entry_to_structured_content(entry)
        assert len(content) == 3  # POS + pron + translations

        # Pronunciation
        pron_div = content[1]
        pron_span = pron_div["content"][0]
        assert pron_span["data"]["content"] == "transcription"
        assert "[/ˈloːpə(n)/]" in pron_span["content"]

    def test_entry_with_definitions(self):
        entry = TeiEntry(
            headword="groot",
            pronunciations=[],
            pos="adj",
            translations=["большой"],
            definitions=["van grote omvang", "belangrijk"],
        )
        content = tei_entry_to_structured_content(entry)
        assert len(content) == 4  # POS + translation + 2 definitions

        # Definitions are comments
        for defn_div in content[2:]:
            comment_span = defn_div["content"]
            assert comment_span["data"]["content"] == "comment"

    def test_german_pos_labels(self):
        entry = TeiEntry(
            headword="Haus",
            pronunciations=[],
            pos="n",
            translations=["house"],
            definitions=[],
        )
        content = tei_entry_to_structured_content(entry, target_lang="de")
        pos_span = content[0]["content"]
        assert pos_span["content"] == "Subst."

    def test_dutch_pos_labels(self):
        entry = TeiEntry(
            headword="kat",
            pronunciations=[],
            pos="n",
            translations=["кот"],
            definitions=[],
        )
        content = tei_entry_to_structured_content(entry, target_lang="nl")
        pos_span = content[0]["content"]
        assert pos_span["content"] == "znw."

    def test_unknown_lang_falls_back_to_russian(self):
        entry = TeiEntry(
            headword="chat",
            pronunciations=[],
            pos="n",
            translations=["кот"],
            definitions=[],
        )
        content = tei_entry_to_structured_content(entry, target_lang="fr")
        pos_span = content[0]["content"]
        assert pos_span["content"] == "сущ."


class TestTeiPosToRules:
    def test_noun(self):
        assert tei_pos_to_rules("n") == ["n"]

    def test_verb(self):
        assert tei_pos_to_rules("v") == ["v"]

    def test_adjective(self):
        assert tei_pos_to_rules("adj") == ["adj"]

    def test_unknown(self):
        assert tei_pos_to_rules("pn") == []
        assert tei_pos_to_rules("suffix") == []
