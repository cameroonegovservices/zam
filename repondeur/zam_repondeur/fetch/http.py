import os
from pathlib import Path

import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from cachecontrol.heuristics import ExpiresAfter


HERE = Path(__file__)
DEFAULT_HTTP_CACHE_DIR = HERE.parent.parent.parent / ".web_cache"
DEFAULT_HTTP_CACHE_DURATION = 10  # minutes

HTTP_CACHE_DIR = os.environ.get("ZAM_HTTP_CACHE_DIR", DEFAULT_HTTP_CACHE_DIR)
HTTP_CACHE_DURATION = os.environ.get(
    "ZAM_HTTP_CACHE_DURATION", DEFAULT_HTTP_CACHE_DURATION
)


session = requests.session()

cached_session = CacheControl(
    session,
    cache=FileCache(HTTP_CACHE_DIR),
    heuristic=ExpiresAfter(minutes=HTTP_CACHE_DURATION),
)
