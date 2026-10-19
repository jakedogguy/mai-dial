<div align="center">
    <br/>
<pre>
███╗   ███╗  █████╗  ██╗
████╗ ████║ ██╔══██╗ ██║
██╔████╔██║ ███████║ ██║
██║╚██╔╝██║ ██╔══██║ ██║
██║ ╚═╝ ██║ ██║  ██║ ██║
╚═╝     ╚═╝ ╚═╝  ╚═╝ ╚═╝
</pre>
    <p>
        youtube tracklist → tidal playlist
    </p>
    <p>
        made with love @jakedogguy
    </p>
    <br/>
</div>

mai turns the tracklist in a youtube video's description into a tidal playlist. no api keys, no copy-pasting songs one by one.

paste the link, review the matches, get the playlist. that simple.

### how it works
- reads the video's title, description and thumbnail with [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- finds the songs and albums in the description: timestamps, numbered lists, `artist - title`, `title by artist`, and so on
- searches each one on tidal and shows a table of matches: green is sure, yellow is doubtful, red is not found
- you decide on the doubtful ones, then mai creates the playlist named after the video
- the thumbnail is saved to `covers/`. tidal's api can't set playlist images yet, so mai opens the playlist and the cover for you to set it by hand

### install
```sh
py -m venv .venv
.venv\Scripts\activate        # windows (source .venv/bin/activate elsewhere)
pip install -e .
```

### usage
```sh
mai "https://www.youtube.com/watch?v=..."
```
or just run `mai` and paste the link when asked.

the first run asks you to log in to tidal: open the link shown and approve it. no developer app or token needed.

### your secrets
mai never asks for your tidal password. it uses tidal's device login and saves the session to `~/.mai/tidal_session.json`, outside this repository. treat that file like a password: don't share it or commit it. delete it to log out.

### development
```sh
pip install -e ".[dev]"
pytest
```

### thank you
mai is built on [tidalapi](https://github.com/tamland/python-tidal), [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [rich](https://github.com/Textualize/rich).
