import re
import unicodedata
import webbrowser
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Callable

import tidalapi

from mai.parser import TrackQuery

SESSION_FILE = Path.home() / ".mai" / "tidal_session.json"
SURE = 0.8  # scores at or above this are accepted without asking


@dataclass
class Match:
    query: TrackQuery
    item: tidalapi.Track | tidalapi.Album | None
    score: float

    @property
    def label(self) -> str:
        if self.item is None:
            return ""
        artists = ", ".join(a.name for a in self.item.artists or [] if a.name)
        return f"{artists} - {self.item.name}"


def login(show_link: Callable[[str, int], None]) -> tidalapi.Session:
    """Reuse the saved session, or run Tidal's device login and save it.

    `show_link(url, expires_in)` is called so the UI can tell the user where to log in.
    """
    session = tidalapi.Session()
    session.load_session_from_file(SESSION_FILE)
    if session.check_login():
        return session

    link, future = session.login_oauth()
    url = f"https://{link.verification_uri_complete}"
    show_link(url, link.expires_in)
    webbrowser.open(url)
    future.result()  # blocks until the user approves (or raises TimeoutError)

    if not session.check_login():
        raise RuntimeError("Tidal login failed")
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    session.save_session_to_file(SESSION_FILE)
    return session


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    text = re.sub(r"[(\[].*?[)\]]", " ", text)  # (feat. X), [Remastered 2011], ...
    text = re.sub(r"\b(feat|ft)\.?\s.*$", " ", text)
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    return " ".join(text.split())


def _sim(a: str, b: str) -> float:
    a, b = _norm(a), _norm(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


def score(query: TrackQuery, item) -> float:
    """How well a Tidal track/album matches the query, 0..1.

    Descriptions don't agree on "Artist - Title" vs "Title - Artist", so both
    orientations are tried and the best one wins.
    """
    title = item.name or ""
    artists = [a.name for a in item.artists or [] if a.name] or [""]

    def artist_sim(text: str) -> float:
        return max(max(_sim(text, a) for a in artists), _sim(text, " ".join(artists)))

    if not query.right:
        full = f"{artists[0]} {title}"
        return max(_sim(query.left, title), _sim(query.left, full))

    straight = (artist_sim(query.left) + _sim(query.right, title)) / 2
    flipped = (artist_sim(query.right) + _sim(query.left, title)) / 2
    return max(straight, flipped)


def find_match(session: tidalapi.Session, query: TrackQuery) -> Match:
    model = tidalapi.Album if query.kind == "album" else tidalapi.Track
    key = "albums" if query.kind == "album" else "tracks"
    candidates = session.search(query.query, models=[model], limit=10)[key]
    if not candidates and query.right:
        # Long titles with extra words sometimes return nothing; the title alone often does.
        candidates = session.search(query.right, models=[model], limit=10)[key]
    if not candidates:
        return Match(query, None, 0.0)
    best = max(candidates, key=lambda item: score(query, item))
    return Match(query, best, score(query, best))


def track_ids(matches: list[Match]) -> list[str]:
    """Flatten matches into track ids; albums contribute all their tracks."""
    ids: list[str] = []
    for m in matches:
        if isinstance(m.item, tidalapi.Album):
            ids.extend(str(t.id) for t in m.item.tracks())
        elif m.item is not None:
            ids.append(str(m.item.id))
    return list(dict.fromkeys(ids))


def create_playlist(session: tidalapi.Session, title: str, description: str, ids: list[str]):
    playlist = session.user.create_playlist(title, description)
    for i in range(0, len(ids), 100):  # Tidal accepts up to 100 items per request
        playlist.add(ids[i : i + 100])
    return playlist
