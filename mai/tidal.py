import webbrowser
from pathlib import Path
from typing import Callable

import tidalapi

SESSION_FILE = Path.home() / ".mai" / "tidal_session.json"


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
