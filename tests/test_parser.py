from mai.parser import parse_line, parse_tracklist


def pairs(description):
    return [(t.left, t.right, t.kind) for t in parse_tracklist(description)]


def test_timestamped_tracklist():
    desc = """Best chill mix of the year!

Tracklist:
00:00 Nujabes - Aruarian Dance
03:12 Tomppabeats - Monday Loop
1:02:33 J Dilla – Time: The Donut of the Heart
"""
    assert pairs(desc) == [
        ("Nujabes", "Aruarian Dance", "track"),
        ("Tomppabeats", "Monday Loop", "track"),
        ("J Dilla", "Time: The Donut of the Heart", "track"),
    ]


def test_numbered_and_trailing_timestamps():
    desc = """1. Daft Punk - Digital Love (0:00)
2) Air - La Femme d'Argent [04:58]
#3 Phoenix — 1901 - 12:01
"""
    assert pairs(desc) == [
        ("Daft Punk", "Digital Love", "track"),
        ("Air", "La Femme d'Argent", "track"),
        ("Phoenix", "1901", "track"),
    ]


def test_title_by_artist_is_flipped():
    assert parse_line("Clair de Lune by Claude Debussy").left == "Claude Debussy"


def test_timestamp_without_artist():
    item = parse_line("12:30 Untitled Interlude")
    assert (item.left, item.right) == ("Untitled Interlude", "")


def test_noise_is_ignored():
    desc = """🎧 Listen on Spotify: https://open.spotify.com/xyz
Follow me on Instagram - @someone
#lofi #chill #beats
Subscribe for more!
This is just a sentence about the mix
© 2024 All rights reserved
Boards of Canada - Roygbiv
"""
    assert pairs(desc) == [("Boards of Canada", "Roygbiv", "track")]


def test_emojis_bullets_and_video_tags():
    desc = """🔥 Kendrick Lamar - HUMBLE. (Official Video)
• SZA - Good Days [Official Audio]
"""
    assert pairs(desc) == [
        ("Kendrick Lamar", "HUMBLE.", "track"),
        ("SZA", "Good Days", "track"),
    ]


def test_album_markers_and_sections():
    desc = """Radiohead - OK Computer (Album)
Albums:
Massive Attack - Mezzanine
Portishead - Dummy
Songs:
Björk - Hyperballad
"""
    assert pairs(desc) == [
        ("Radiohead", "OK Computer", "album"),
        ("Massive Attack", "Mezzanine", "album"),
        ("Portishead", "Dummy", "album"),
        ("Björk", "Hyperballad", "track"),
    ]


def test_duplicates_removed():
    desc = "00:00 A - B\n10:00 A - B\n"
    assert len(parse_tracklist(desc)) == 1
