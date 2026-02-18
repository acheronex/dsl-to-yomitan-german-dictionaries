import re

# Simple tag replacements
TAG_PATTERNS = {
    "bold": (re.compile(r"\[b\](.*?)\[/b\]", re.DOTALL), r"<b>\1</b>"),
    "italic": (re.compile(r"\[i\](.*?)\[/i\]", re.DOTALL), r"<i>\1</i>"),
    "underline": (re.compile(r"\[u\](.*?)\[/u\]", re.DOTALL), r"<u>\1</u>"),
    "sup": (re.compile(r"\[sup\](.*?)\[/sup\]", re.DOTALL), r"<sup>\1</sup>"),
    "sub": (re.compile(r"\[sub\](.*?)\[/sub\]", re.DOTALL), r"<sub>\1</sub>"),
    "trn": (re.compile(r"\[trn\](.*?)\[/trn\]", re.DOTALL), r"\1"),  # Usually just a wrapper
    "ex": (re.compile(r"\[ex\](.*?)\[/ex\]", re.DOTALL), r'<div class="example">\1</div>'),
    "com": (re.compile(r"\[com\](.*?)\[/com\]", re.DOTALL), r'<span class="comment">\1</span>'),
}

# Complex tags that need special handling
COLOR_PATTERN = re.compile(r"\[c\s*(?P<color>\w+)?\](?P<content>.*?)\[/c\]", re.DOTALL)
MARGIN_PATTERN = re.compile(r"\[m(?P<level>\d)\](?P<content>.*?)\[/m\]", re.DOTALL)
REF_PATTERN = re.compile(r"\[ref\](?P<target>.*?)\[/ref\]", re.DOTALL)
LANG_PATTERN = re.compile(r"\[lang\s+id=(?P<id>\d+)\](?P<content>.*?)\[/lang\]", re.DOTALL)
STRESS_PATTERN = re.compile(r"\['\](?P<vowel>.)\[/'\]")
OPTIONAL_PATTERN = re.compile(r"\[\*\](?P<content>.*?)\[/\*\]", re.DOTALL)

# Escaped brackets
ESC_OPEN_BRACKET = re.compile(r"\\\[")
ESC_CLOSE_BRACKET = re.compile(r"\\\]")
