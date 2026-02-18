from src.converter import DslConverter


def test_clean_headword():
    converter = DslConverter()
    assert converter.clean_headword("Wort·er") == "Worter"
    assert converter.clean_headword("Wort|bildung") == "Wortbildung"


def test_text_to_structured_content():
    converter = DslConverter()
    text = "[b]Bold[/b]"
    expected = {"tag": "span", "data": {"content": "bold"}, "content": "Bold"}
    assert converter._text_to_structured_content(text) == expected


def test_text_to_structured_content_nested():
    converter = DslConverter()
    text = "[b][i]Bold Italic[/i][/b]"
    # Nested styled elements stay as spans (they're inline content)
    expected = {
        "tag": "span",
        "data": {"content": "bold"},
        "content": {"tag": "span", "data": {"content": "italic"}, "content": "Bold Italic"},
    }
    assert converter._text_to_structured_content(text) == expected


def test_text_to_structured_content_mixed():
    converter = DslConverter()
    text = "Text [b]Bold[/b] more text"
    expected = ["Text ", {"tag": "span", "data": {"content": "bold"}, "content": "Bold"}, " more text"]
    assert converter._text_to_structured_content(text) == expected


def test_malformed_nesting():
    converter = DslConverter()
    # [m1][p][i][c][com]f[/p] [p]=[/com][/c][/i][/p][/m]
    # Simplified:
    text = "[p][i][c]f[/p] [p]=[/c][/i][/p]"
    # Our token parser should handle this by closing tags correctly.
    result = converter._text_to_structured_content(text)
    # Expected behavior:
    # [p][i][c]f closes at [/p], then next [p] opens, then = closes at [/c]...
    # This is complex, but it shouldn't crash and should return something sensible.
    assert isinstance(result, list)
    # The first span should be 'f' wrapped in p, i, c - now uses div due to nesting
    assert result[0]["tag"] in ("span", "div")
    assert "abbreviation" in str(result[0])
