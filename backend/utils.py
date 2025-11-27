"""Utility functions."""

from os import SEEK_END


def uri_to_url(uri: str) -> str:
    """Convert Spotify URI to web URL."""
    tokens = uri.split(":")
    return f"https://open.spotify.com/{tokens[1]}/{tokens[2]}"


def tail(fname: str, n: int) -> str:
    """Read last n lines from a file."""
    with open(fname, "rb") as f:
        f.seek(0, SEEK_END)
        pos = f.tell()
        linecnt = 0

        while pos > 0:
            pos -= 1
            f.seek(pos)
            char = f.read(1)

            if char == b"\n":
                linecnt += 1
                if linecnt == n:
                    break

        if pos == 0:
            f.seek(0)

        return f.read().decode("utf-8", "replace")
