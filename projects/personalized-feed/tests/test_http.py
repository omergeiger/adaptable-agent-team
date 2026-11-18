import socket
import urllib.error

import pytest

from conftest import FakeResponse, http_error
from pfeed import USER_AGENT
from pfeed.http import FetchError, Http


class Script:
    """Opener that plays back a list of responses/exceptions."""

    def __init__(self, *steps):
        self.steps, self.requests = list(steps), []

    def __call__(self, request, timeout):
        self.requests.append((request, timeout))
        step = self.steps.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


def make(*steps, **kw):
    sleeps = []
    opener = Script(*steps)
    return Http(opener=opener, sleep=sleeps.append, **kw), opener, sleeps


def test_sends_user_agent_and_timeout():
    http, opener, _ = make(FakeResponse(b"ok"))
    assert http.fetch("https://x.test/a") == b"ok"
    req, timeout = opener.requests[0]
    assert req.get_header("User-agent") == USER_AGENT == "personalized-feed/0.1"
    assert timeout == 15


@pytest.mark.parametrize("failure", [socket.timeout("t"), http_error(429), http_error(500),
                                     urllib.error.URLError("dns")])
def test_one_retry_with_backoff_then_success(failure):
    http, opener, sleeps = make(failure, FakeResponse(b"ok"), backoff=2.5)
    assert http.fetch("https://x.test/a") == b"ok"
    assert len(opener.requests) == 2 and sleeps == [2.5]


def test_gives_up_after_one_retry():
    http, opener, sleeps = make(http_error(500), http_error(503))
    with pytest.raises(FetchError, match="HTTP 503"):
        http.fetch("https://x.test/a")
    assert len(opener.requests) == 2 and len(sleeps) == 1


def test_timeout_is_fetch_error():
    http, _, _ = make(socket.timeout("t"), socket.timeout("t"))
    with pytest.raises(FetchError, match="timeout"):
        http.fetch("https://x.test/a")


def test_404_is_not_retried():
    http, opener, sleeps = make(http_error(404))
    with pytest.raises(FetchError, match="HTTP 404"):
        http.fetch("https://x.test/a")
    assert len(opener.requests) == 1 and sleeps == []


def test_rejects_non_http_scheme():
    http, opener, _ = make()
    with pytest.raises(FetchError):
        http.fetch("file:///etc/passwd")
    assert opener.requests == []


def test_etag_conditional_request_and_304_reuses_cache():
    http, opener, _ = make(FakeResponse(b"body", {"ETag": '"v1"'}), http_error(304))
    assert http.fetch("https://x.test/a") == b"body"
    assert http.fetch("https://x.test/a") == b"body"
    assert opener.requests[1][0].get_header("If-none-match") == '"v1"'


def test_host_politeness_spaces_requests():
    now = [100.0]
    sleeps = []
    http = Http(opener=Script(FakeResponse(b"1"), FakeResponse(b"2")), sleep=sleeps.append,
                clock=lambda: now[0], host_min_interval={"export.arxiv.org": 3.0})
    http.fetch("https://export.arxiv.org/api/query?a=1")
    now[0] += 1.0
    http.fetch("https://export.arxiv.org/api/query?a=2")
    assert sleeps == [pytest.approx(2.0)]
