"""Utility functions."""

from os import SEEK_END
from collections import deque


def uri_to_url(uri: str) -> str:
    """Convert Spotify URI to web URL."""
    tokens = uri.split(":")
    return f"https://open.spotify.com/{tokens[1]}/{tokens[2]}"


def tail(file: str, n: int) -> str:
    """Read last n lines from a file."""
    with open(file, 'rb') as f:
        f.seek(0, SEEK_END)
        file_size = f.tell()

        if file_size == 0:
            return ""

        lines_found: deque[bytes] = deque()
        pos = file_size

        while pos > 0 and len(lines_found) < n:
            chunk_start = max(0, pos - 8192)
            chunk_size = pos - chunk_start

            f.seek(chunk_start)
            chunk = f.read(chunk_size)

            chunk_lines = chunk.split(b'\n')

            # handle partial line at the end of the chunk
            if lines_found and chunk_lines:
                lines_found[0] = chunk_lines.pop() + lines_found[0]

            # Prepend newly read lines to the deque
            lines_found.extendleft(reversed(chunk_lines))

            pos = chunk_start

        result_lines = list(lines_found)[-n:]
        return b'\n'.join(result_lines).decode('utf-8', 'replace')
