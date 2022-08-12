import json
from json.decoder import JSONDecodeError

from .conf import MODE, CACHE_FILE
from .exceptions import CacheDataCorrupted


class TFSCache:
    """
    Cache management
    """
    def __init__(self):
        self.meta = {}
        self.cache = {}
        if MODE == 'lazy':
            self._load_cache()

    def _load_cache(self):
        """
        Read cache file and parse meta/cache data if file exists
        """
        try:
            with open(CACHE_FILE, 'rb') as fd:
                raw_data = json.loads(fd.read()).decode('utf-8')
                self.meta = raw_data['meta']
                self.cache = raw_data['cache']
        except JSONDecodeError:
            raise CacheDataCorrupted(f'Cache file {CACHE_FILE} incorrect, '
                                     f'remove it and try again!')
        except FileNotFoundError:
            pass

    def _persistence_cache(self):
        """
        Create/Update cache file
        """
        with open(CACHE_FILE, 'wb') as fd:
            raw_data = json.dumps({
                'meta': self.meta,
                'cache': self.cache
            }, ensure_ascii=False).encode('utf-8')
            fd.write(raw_data)
