"""fetch(url) with User-Agent, timeout, one retry with backoff, ETag cache, per-host politeness.

Everything environmental (opener, sleep, clock) is injectable so tests never touch the network.
"""
import socket
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit

from . import USER_AGENT

MAX_BYTES = 5_000_000
# Host politeness from the source catalog: arXiv 1 req / 3 s; GitHub search ~10/min unauthenticated.
HOST_MIN_INTERVAL = {"export.arxiv.org": 3.0, "api.github.com": 6.0}


class FetchError(Exception):
    """A source could not be fetched or parsed. Callers record it and move on; nothing is fabricated."""


class Http:
    def __init__(self, opener=None, sleep=time.sleep, clock=time.monotonic,
                 timeout=15, backoff=2.0, host_min_interval=None):
        self._opener = opener or urllib.request.urlopen
        self._sleep, self._clock = sleep, clock
        self.timeout, self.backoff = timeout, backoff
        self._min_interval = HOST_MIN_INTERVAL if host_min_interval is None else host_min_interval
        self._last_by_host = {}
        self._cache = {}  # url -> (etag, last_modified, body)

    def fetch(self, url):
        if not url.startswith(("https://", "http://")):
            raise FetchError(f"{url}: unsupported URL scheme")
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        cached = self._cache.get(url)
        if cached:
            if cached[0]:
                request.add_header("If-None-Match", cached[0])
            if cached[1]:
                request.add_header("If-Modified-Since", cached[1])
        last_reason = "unknown error"
        for attempt in (1, 2):
            self._be_polite(url)
            try:
                response = self._opener(request, timeout=self.timeout)
                body = response.read(MAX_BYTES)
                self._cache[url] = (response.headers.get("ETag"), response.headers.get("Last-Modified"), body)
                return body
            except urllib.error.HTTPError as e:
                if e.code == 304 and cached:
                    return cached[2]
                last_reason = f"HTTP {e.code}"
                if not (e.code == 429 or e.code >= 500):
                    break  # 4xx other than 429: retrying will not help
            except (TimeoutError, socket.timeout):
                last_reason = "timeout"
            except (urllib.error.URLError, OSError) as e:
                last_reason = f"network error: {getattr(e, 'reason', e)}"
            if attempt == 1:
                self._sleep(self.backoff)
        raise FetchError(f"{url}: {last_reason}")

    def _be_polite(self, url):
        host = urlsplit(url).hostname or ""
        gap = self._min_interval.get(host)
        if gap:
            last = self._last_by_host.get(host)
            if last is not None and self._clock() - last < gap:
                self._sleep(gap - (self._clock() - last))
            self._last_by_host[host] = self._clock()
