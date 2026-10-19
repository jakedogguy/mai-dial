"""Heuristic tracklist extraction from free-form YouTube descriptions."""

import re
import unicodedata
from dataclasses import dataclass


@dataclass
class TrackQuery:
    raw: str
    left: str
    right: str = ""
    kind: str = "track"  # "track" or "album"

    @property
    def query(self) -> str:
        return f"{self.left} {self.right}".strip()


TIMESTAMP = r"[\[(]?\d{1,2}:\d{2}(?::\d{2})?[\])]?"
LEADING_TS = re.compile(rf"^{TIMESTAMP}\s*[-–—|:]?\s*")
TRAILING_TS = re.compile(rf"\s*[-–—|]?\s*{TIMESTAMP}$")
NUMBERING = re.compile(r"^(?:#\d{1,3}|\d{1,3}\s*[.)]|\d{1,3}\s+[-–—]\s+(?=.+\s[-–—]\s))\s*")
BULLET = re.compile(r"^[-–—•*·▶►→>~|]+\s*")
SEPARATORS = re.compile(r"\s+[-–—|~]\s+|\s+by\s+|:\s+", re.IGNORECASE)
ALBUM_MARK = re.compile(r"\s*[\[(](?:album|full album|lp|ep)[\])]\s*|\s+\b(?:LP|EP)\b\s*$", re.IGNORECASE)
VIDEO_NOISE = re.compile(
    r"\s*[\[(](?:official\s+)?(?:music\s+)?(?:video|audio|lyrics?(?:\s+video)?|visualizer|hd|hq|4k)[\])]",
    re.IGNORECASE,
)
NOISE_WORDS = re.compile(
    r"https?://|www\.|subscribe|follow|instagram|twitter|facebook|tiktok|soundcloud|spotify|"
    r"apple music|bandcamp|patreon|discord|merch|copyright|©|all rights|provided to youtube|"
    r"auto-generated|listen on|stream (?:it|now)|download|contact|e-?mail|business",
    re.IGNORECASE,
)
HEADER = re.compile(r"^(?:full\s+)?(tracklist|track list|songs?|tracks|albums?|discography)\b.*:?$", re.IGNORECASE)


def _strip_symbols(text: str) -> str:
    """Drop emojis and other decorative symbols from both ends."""
    def decorative(ch: str) -> bool:
        return unicodedata.category(ch) in ("So", "Sk", "Cf") or ch in "️"

    start, end = 0, len(text)
    while start < end and (decorative(text[start]) or text[start].isspace()):
        start += 1
    while end > start and (decorative(text[end - 1]) or text[end - 1].isspace()):
        end -= 1
    return text[start:end]


def _clean(part: str) -> str:
    part = VIDEO_NOISE.sub("", part)
    return part.strip(" \"'“”‘’*_").strip()


def parse_line(line: str, in_album_section: bool = False) -> TrackQuery | None:
    raw = line.strip()
    text = _strip_symbols(raw)
    if not text or len(text) > 150 or NOISE_WORDS.search(text):
        return None
    if all(tok.startswith("#") for tok in text.split()) and not NUMBERING.match(text):
        return None

    had_ts = bool(LEADING_TS.match(text) or TRAILING_TS.search(text))
    text = LEADING_TS.sub("", text)
    text = TRAILING_TS.sub("", text)
    text = BULLET.sub("", text)
    text = NUMBERING.sub("", text)
    text = _strip_symbols(text)

    kind = "album" if in_album_section else "track"
    if ALBUM_MARK.search(text):
        kind = "album"
        text = ALBUM_MARK.sub(" ", text).strip()

    match = SEPARATORS.search(text)
    if match:
        left, right = _clean(text[: match.start()]), _clean(text[match.end() :])
        if match.group().strip().lower() == "by":
            # "Title by Artist" -> keep the conventional "Artist - Title" order.
            left, right = right, left
        if left and right:
            return TrackQuery(raw=raw, left=left, right=right, kind=kind)
        text = left or right

    text = _clean(text)
    if had_ts and text:
        return TrackQuery(raw=raw, left=text, kind=kind)
    return None


def parse_tracklist(description: str) -> list[TrackQuery]:
    results: list[TrackQuery] = []
    seen: set[str] = set()
    in_album_section = False

    for line in description.splitlines():
        stripped = _strip_symbols(line.strip())
        header = HEADER.match(stripped)
        if header and len(stripped) < 40:
            in_album_section = header.group(1).lower().startswith(("album", "discography"))
            continue

        item = parse_line(line, in_album_section)
        if item is None:
            continue
        key = f"{item.kind}:{item.query.lower()}"
        if key not in seen:
            seen.add(key)
            results.append(item)
    return results
