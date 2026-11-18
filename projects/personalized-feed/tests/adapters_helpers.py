import json

from conftest import FakeHttp
from pfeed.adapters import hn


def hn_candidate_for(target_url, points=50):
    hit = {"objectID": "1", "title": "Some story", "url": target_url, "points": points,
           "num_comments": 3, "author": "a", "created_at": "2026-11-18T00:00:00Z"}
    return hn.fetch(FakeHttp(json.dumps({"hits": [hit]}).encode()), url="https://x.test/")[0]
