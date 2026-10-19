# Mai

Turn the tracklist in a YouTube video's description into a Tidal playlist.

Mai reads the video's title, description and thumbnail, finds each song (or album)
on Tidal, lets you review the matches, and creates a playlist named after the video.

## Install

```sh
py -m venv .venv
.venv\Scripts\activate        # Windows (source .venv/bin/activate elsewhere)
pip install -e .
```

## Use

```sh
mai "https://www.youtube.com/watch?v=..."
```

Or just run `mai` and paste the link when asked.

The first run asks you to log in to Tidal: open the link shown, enter the code,
and Mai saves the session in `~/.mai/tidal_session.json` so you won't be asked again.

The video thumbnail is saved to `covers/`. Tidal's API doesn't allow setting a
playlist image yet, so Mai opens the playlist and the cover folder for you to set it
by hand in the Tidal app.

Matches under 80% similarity are shown in yellow and you decide whether to keep them;
songs not found on Tidal are listed at the end.

---

made with love @jakedogguy
