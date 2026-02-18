from src.parser import DslParser

def test_parse_basic_entry(tmp_path):
    dsl_content = (
        '#NAME\t"Test Dict"\n'
        '#INDEX_LANGUAGE\t"German"\n'
        '\n'
        'Wort\n'
        '\t[m1]Definition[/m]\n'
        '\n'
        'Anderes Wort\n'
        '\t[m2]Zweite Definition[/m]\n'
    )
    dsl_file = tmp_path / "test.dsl"
    # DSL is UTF-16 with BOM
    dsl_file.write_text(dsl_content, encoding="utf-16")
    
    parser = DslParser(str(dsl_file))
    entries = list(parser.parse())
    
    assert len(entries) == 2
    assert entries[0]["headword"] == "Wort"
    assert entries[0]["body"] == ["[m1]Definition[/m]"]
    assert entries[1]["headword"] == "Anderes Wort"
    assert entries[1]["body"] == ["[m2]Zweite Definition[/m]"]
    assert parser.headers["NAME"] == "Test Dict"

def test_parse_header(tmp_path):
    dsl_content = '#NAME "Another Test"\n\nWord\n\tBody\n'
    dsl_file = tmp_path / "test.dsl"
    dsl_file.write_text(dsl_content, encoding="utf-16")
    
    parser = DslParser(str(dsl_file))
    # We need to call parse() or at least read the header
    list(parser.parse())
    assert parser.headers["NAME"] == "Another Test"
