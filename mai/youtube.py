import re
from dataclasses import dataclass, field
from pathlib import Path

import requests
import yt_dlp


@dataclass
class VideoInfo:
    title: str
    description: str
    # Candidate cover URLs, best first. YouTube lists sizes that don't always exist.
    thumbnail_urls: list[str] = field(default_factory=list)


def fetch_video(url: str) -> VideoInfo:
    # We only need metadata, so don't fail when no playable formats are available.
    opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "ignore_no_formats_error": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return VideoInfo(
        title=info.get("title") or "Untitled",
        description=info.get("description") or "",
        thumbnail_urls=_thumbnail_candidates(info),
    )


def _thumbnail_candidates(info: dict) -> list[str]:
    thumbs = [t for t in info.get("thumbnails") or [] if ".jpg" in t.get("url", "")]
    # yt-dlp orders thumbnails worst -> best via "preference".
    thumbs.sort(key=lambda t: t.get("preference") or 0, reverse=True)
    urls = [t["url"] for t in thumbs]
    if info.get("thumbnail") and info["thumbnail"] not in urls:
        urls.append(info["thumbnail"])
    return urls


def safe_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name).strip(" .")
    return name[:100] or "cover"


def download_thumbnail(video: VideoInfo, folder: Path = Path("covers")) -> Path | None:
    for url in video.thumbnail_urls:
        resp = requests.get(url, timeout=30)
        if resp.ok and resp.content:
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / f"{safe_filename(video.title)}.jpg"
            path.write_bytes(resp.content)
            return path
    return None
