import logging
from collections.abc import Iterator
from typing import TypedDict

logger = logging.getLogger(__name__)

class DslEntry(TypedDict):
    headword: str
    body: list[str]

class DslParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.headers: dict[str, str] = {}

    def parse(self) -> Iterator[DslEntry]:
        """Parses the DSL file and yields entries."""
        try:
            with open(self.file_path, "r", encoding="utf-16") as f:
                current_headword: str | None = None
                current_body: list[str] = []

                for line in f:
                    line = line.rstrip("\n\r")
                    if not line:
                        if current_headword:
                            yield {"headword": current_headword, "body": current_body}
                            current_headword = None
                            current_body = []
                        continue

                    if line.startswith("#"):
                        self._parse_header(line)
                        continue
                    
                    if line.startswith("\t"):
                        if current_headword:
                            current_body.append(line.lstrip("\t"))
                        else:
                            logger.warning(f"Found body line without headword: {line}")
                        continue
                    
                    # If we have a previous entry, yield it before starting a new one
                    if current_headword:
                        yield {"headword": current_headword, "body": current_body}
                        current_body = []
                    
                    current_headword = line.strip()

                # Yield the last entry
                if current_headword:
                    yield {"headword": current_headword, "body": current_body}

        except UnicodeError:
            logger.error(f"Failed to decode {self.file_path} as UTF-16")
            raise

    def _parse_header(self, line: str) -> None:
        """Parses header lines like #NAME \"Dictionary\"."""
        line = line.lstrip("#").strip()
        if "\t" in line:
            key, value = line.split("\t", 1)
            self.headers[key] = value.strip('"')
        elif " " in line:
            key, value = line.split(" ", 1)
            self.headers[key] = value.strip('"')
