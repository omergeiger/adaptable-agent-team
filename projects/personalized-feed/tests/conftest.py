import io
import urllib.error
from pathlib import Path

import pytest

FIX = Path(__file__).parent / "fixtures"


def fixture_bytes(name):
    return (FIX / name).read_bytes()


class FakeHttp:
    """Stands in for pfeed.http.Http: returns canned bytes or raises. Records URLs. No network."""

    def __init__(self, body=b"", error=None):
        self.body, self.error, self.urls = body, error, []

    def fetch(self, url):
        self.urls.append(url)
        if self.error:
            raise self.error
        return self.body


class FakeResponse:
    def __init__(self, body=b"", headers=None):
        self.body, self.headers = body, headers or {}

    def read(self, n=-1):
        return self.body if n < 0 else self.body[:n]


def http_error(code, url="https://x.test/"):
    return urllib.error.HTTPError(url, code, "err", {}, io.BytesIO(b""))


@pytest.fixture
def fx():
    return fixture_bytes
