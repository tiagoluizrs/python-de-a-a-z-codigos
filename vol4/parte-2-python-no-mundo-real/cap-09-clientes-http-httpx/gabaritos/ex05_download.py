"""Gabarito do exercício 5."""
import httpx


def download(client, url, dest, *, chunk_size=65_536, on_progress=None, resume=True):
    existing = dest.stat().st_size if resume and dest.exists() else 0
    headers = {"Range": f"bytes={existing}-"} if existing else {}
    with client.stream("GET", url, headers=headers) as response:
        if response.status_code == 416:
            return dest.stat().st_size
        response.raise_for_status()
        if response.status_code == 206 and existing:
            mode, done = "ab", existing
            total = int(response.headers["content-range"].rsplit("/", 1)[1]) if "content-range" in response.headers else None
        else:
            mode, done = "wb", 0
            total = int(response.headers["content-length"]) if "content-length" in response.headers else None
        with open(dest, mode) as handle:
            for chunk in response.iter_bytes(chunk_size):
                handle.write(chunk)
                done += len(chunk)
                if on_progress:
                    on_progress(done, total)
    return dest.stat().st_size
