import re
from typing import Any, TypedDict

from src.tag_map import (
    ESC_CLOSE_BRACKET,
    ESC_OPEN_BRACKET,
    MARGIN_PATTERN,
)

class StructuredContent(TypedDict):
    tag: str
    content: Any
    style: dict[str, Any] | None
    data: dict[str, str] | None
    href: str | None

class DslConverter:
    def __init__(self, abbreviations: dict[str, str] | None = None):
        self.abbreviations = abbreviations or {}
        # Pre-compile some common regexes
        self.tag_regex = re.compile(r'\[(?P<close>/)?(?P<tag>[\w\*\']+)(?:\s+(?P<val>.*?))?\]')
        self.media_files: set[str] = set()

    def convert_to_structured_content(self, body_lines: list[str]) -> list[dict[str, Any]]:
        """
        Converts DSL body lines to Yomitan structured content.
        Groups consecutive lines with the same margin level into sense-groups.
        """
        # First pass: parse all lines into structured content
        parsed_lines: list[tuple[int | None, dict[str, Any]]] = []
        
        for line in body_lines:
            if not line.strip():
                continue
            
            margin_match = MARGIN_PATTERN.match(line)
            if margin_match:
                level = int(margin_match.group("level"))
                inner_text = margin_match.group("content")
                parsed_content = self._text_to_structured_content(inner_text)
                # Always use div for sense items - they will be inside sense-group divs
                parsed_lines.append((level, {
                    "tag": "div",
                    "content": parsed_content,
                    "data": {"content": "sense", "class": f"margin-{level}"}
                }))
            else:
                parsed_content = self._text_to_structured_content(line)
                # Always use div for sense items - they will be inside sense-group divs
                parsed_lines.append((None, {
                    "tag": "div",
                    "content": parsed_content,
                    "data": {"content": "sense"}
                }))
        
        # Second pass: group consecutive lines with same margin level
        content_items: list[dict[str, Any]] = []
        current_group: list[dict[str, Any]] = []
        current_level: int | None = None
        
        for level, item in parsed_lines:
            if current_level is None:
                # First item
                current_level = level
                current_group.append(item)
            elif level == current_level:
                # Same level - add to current group
                current_group.append(item)
            else:
                # Level changed - finalize current group and start new one
                if len(current_group) == 1:
                    # Single item - don't wrap
                    content_items.append(current_group[0])
                else:
                    # Always use div for sense-group since all items are divs
                    content_items.append({
                        "tag": "div",
                        "data": {"content": "sense-group"},
                        "content": current_group
                    })
                current_level = level
                current_group = [item]
        
        # Don't forget the last group
        if current_group:
            if len(current_group) == 1:
                content_items.append(current_group[0])
            else:
                # Always use div for sense-group since all items are divs
                content_items.append({
                    "tag": "div",
                    "data": {"content": "sense-group"},
                    "content": current_group
                })
        
        return content_items

    def _text_to_structured_content(self, text: str) -> Any:
        """
        Token-based parser to handle malformed/overlapping DSL tags.
        """
        # Handle escaped brackets
        text = ESC_OPEN_BRACKET.sub("[", text)
        text = ESC_CLOSE_BRACKET.sub("]", text)

        tokens = self._tokenize(text)
        return self._build_tree(tokens)

    def _tokenize(self, text: str) -> list[Any]:
        tokens = []
        last_pos = 0
        for match in self.tag_regex.finditer(text):
            if match.start() > last_pos:
                tokens.append(text[last_pos:match.start()])
            
            is_close = bool(match.group("close"))
            tag_name = match.group("tag")
            tag_val = match.group("val")
            
            tokens.append({
                "is_tag": True,
                "is_close": is_close,
                "name": tag_name,
                "val": tag_val
            })
            last_pos = match.end()
        
        if last_pos < len(text):
            tokens.append(text[last_pos:])
        
        return tokens

    def _build_tree(self, tokens: list[Any]) -> Any:
        """
        Builds a tree from tokens, handling overlapping tags by closing them early if needed.
        """
        root = []
        stack = [] # list of (tag_name, tag_val, list_of_children)

        current_content = root

        for token in tokens:
            if isinstance(token, str):
                current_content.append(token)
            else:
                if token["is_close"]:
                    # Find the corresponding opening tag in the stack
                    found_idx = -1
                    for i in range(len(stack) - 1, -1, -1):
                        if stack[i][0] == token["name"]:
                            found_idx = i
                            break
                    
                    if found_idx != -1:
                        # Close all tags up to the found one
                        while len(stack) > found_idx:
                            tag_name, tag_val, tag_children = stack.pop()
                            tag_obj = self._create_tag_object(tag_name, tag_val, tag_children)
                            if stack:
                                stack[-1][2].append(tag_obj)
                                current_content = stack[-1][2]
                            else:
                                root.append(tag_obj)
                                current_content = root
                    else:
                        # Ignore unmatched closing tag
                        pass
                else:
                    # Opening tag
                    new_tag = [token["name"], token["val"], []]
                    stack.append(new_tag)
                    current_content = new_tag[2]

        # Close any remaining open tags
        while stack:
            tag_name, tag_val, tag_children = stack.pop()
            tag_obj = self._create_tag_object(tag_name, tag_val, tag_children)
            if stack:
                stack[-1][2].append(tag_obj)
                current_content = stack[-1][2]
            else:
                root.append(tag_obj)
                current_content = root

        return root if len(root) > 1 else (root[0] if root else "")

    def _create_tag_object(self, name: str, val: str | None, content: Any) -> dict[str, Any]:
        # Unwrap content if it's a single item list
        if isinstance(content, list) and len(content) == 1:
            content = content[0]
        
        # Default container
        tag_obj = {"tag": "span", "content": content}
        
        # Helper to check if content contains a block element
        def has_block(c):
            if isinstance(c, dict):
                return c.get("tag") == "div"
            if isinstance(c, list):
                return any(has_block(item) for item in c)
            return False

        # Helper to check if content is already a structured object
        def has_structured_content(c):
            if isinstance(c, dict) and "tag" in c:
                return True
            if isinstance(c, list):
                return any(has_structured_content(item) for item in c)
            return False

        # Use data attributes for styling (CSS handles it in styles.css)
        # Only upgrade to div if content contains actual block elements (divs)
        # Don't upgrade for inline structured content like italic, bold, etc.
        if name in ("b", "'"):
            if has_block(content):
                tag_obj["tag"] = "div"
            tag_obj["data"] = {"content": "bold"}
        elif name == "i":
            if has_block(content):
                tag_obj["tag"] = "div"
            tag_obj["data"] = {"content": "italic"}
        elif name == "u":
            if has_block(content):
                tag_obj["tag"] = "div"
            tag_obj["data"] = {"content": "underline"}
        elif name == "sup":
            if has_block(content):
                tag_obj["tag"] = "div"
            tag_obj["data"] = {"content": "superscript"}
        elif name == "sub":
            if has_block(content):
                tag_obj["tag"] = "div"
            tag_obj["data"] = {"content": "subscript"}
        elif name == "c":
            color = val.strip() if val else "darkcyan"
            if has_block(content):
                tag_obj["tag"] = "div"
            tag_obj["data"] = {"content": "color", "value": color}
            tag_obj["data"]["class"] = "colored"
        elif name == "p":
            if has_block(content):
                tag_obj["tag"] = "div"
            tag_obj["data"] = {"content": "abbreviation"}
            if isinstance(content, str) and content.strip() in self.abbreviations:
                tag_obj["title"] = self.abbreviations[content.strip()]
        
        # Block elements
        elif name == "m":
            tag_obj["tag"] = "div"
            try:
                margin = int(val) if val else 1
                tag_obj["data"] = {"content": "sense", "class": f"margin-{margin}"}
            except ValueError:
                tag_obj["data"] = {"content": "sense"}
        elif name == "ex":
            tag_obj["tag"] = "span"
            tag_obj["data"] = {"content": "example-sentence"}
        elif name == "com":
            tag_obj["data"] = {"content": "comment"}
        elif name == "trn":
            tag_obj["tag"] = "span"
            tag_obj["data"] = {"content": "translation"}
        elif name == "tr":
            tag_obj["tag"] = "tr"
            if isinstance(content, list):
                new_content = []
                for child in content:
                    if isinstance(child, dict) and child.get("tag") in ("td", "th"):
                        new_content.append(child)
                    else:
                        new_content.append({"tag": "td", "content": child})
                tag_obj["content"] = new_content
            else:
                tag_obj["content"] = [{"tag": "td", "content": content}]
        elif name in ("td", "th"):
            tag_obj["tag"] = name
        elif name == "*":
            tag_obj["data"] = {"content": "optional"}
            if has_block(content):
                tag_obj["tag"] = "div"
            
        # Media & Links
        elif name == "ref":
            tag_obj["tag"] = "a"
            ref_text = self._get_plain_text(content)
            tag_obj["href"] = f"?query={ref_text}"
        elif name == "s":
            media_file = self._get_plain_text(content).strip()
            if media_file:
                # Skip images for Langens dictionary (TIFF files don't work in Yomitan)
                # The packer won't include them anyway
                if media_file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif")):
                    # Just skip adding media - the tag won't be created
                    return {"tag": "span", "content": ""}
                self.media_files.add(media_file)
                if media_file.lower().endswith(".wav"):
                    tag_obj = {
                        "tag": "a",
                        "href": f"?sound={media_file}",
                        "content": "🔊"
                    }

        # Final check: if tag is span but content has blocks, upgrade to div
        if tag_obj["tag"] == "span" and has_block(tag_obj["content"]):
            tag_obj["tag"] = "div"

        return tag_obj


    def _get_plain_text(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(self._get_plain_text(item) for item in content)
        if isinstance(content, dict):
            return self._get_plain_text(content.get("content", ""))
        return ""

    @staticmethod
    def clean_headword(headword: str) -> str:
        """Removes stress marks, dots, etc. from headword."""
        # Remove middle dot (·)
        headword = headword.replace("·", "")
        # Remove DSL stress tags
        headword = re.sub(r"\[/?\'\]", "", headword)
        # Remove other common cleanups
        headword = headword.replace("|", "")
        return headword.strip()

    @staticmethod
    def is_inline_content(content: Any) -> bool:
        """Check if content contains only inline elements (no divs)."""
        if isinstance(content, str):
            return True
        if isinstance(content, dict):
            if content.get("tag") == "div":
                return False
            # Check nested content
            return DslConverter.is_inline_content(content.get("content"))
        if isinstance(content, list):
            return all(DslConverter.is_inline_content(item) for item in content)
        return True

    def _has_structured_content(self, content: Any) -> bool:
        """Check if content contains structured content (dicts with 'tag' key)."""
        if isinstance(content, dict):
            return "tag" in content or self._has_structured_content(content.get("content"))
        if isinstance(content, list):
            return any(self._has_structured_content(item) for item in content)
        return False
