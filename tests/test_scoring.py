from types import SimpleNamespace

from mai.parser import TrackQuery
from mai.tidal import score


def track(artist, title):
    return SimpleNamespace(name=title, artists=[SimpleNamespace(name=artist)])


def test_exact_match_scores_full():
    assert score(TrackQuery("", "Nujabes", "Aruarian Dance"), track("Nujabes", "Aruarian Dance")) == 1.0


def test_either_orientation_matches():
    item = track("Nujabes", "Aruarian Dance")
    assert score(TrackQuery("", "Aruarian Dance", "Nujabes"), item) == 1.0


def test_feat_and_remaster_tags_ignored():
    item = track("Daft Punk", "Get Lucky (feat. Pharrell Williams) [Radio Edit]")
    assert score(TrackQuery("", "Daft Punk", "Get Lucky"), item) == 1.0


def test_accents_ignored():
    assert score(TrackQuery("", "Bjork", "Joga"), track("Björk", "Jóga")) == 1.0


def test_wrong_song_scores_low():
    assert score(TrackQuery("", "Nujabes", "Aruarian Dance"), track("Coldplay", "Yellow")) < 0.5


def test_title_only_query():
    assert score(TrackQuery("", "Aruarian Dance"), track("Nujabes", "Aruarian Dance")) == 1.0
