# memoize.py

This repo contains a single decorator factory `memoize` that manages a local file cache of function results.
The cache is stored as a JSON file.

## Quick Start

Install using pip:
```bash
python3 -m pip install git+https://github.com/ethho/memoize.git
```

By default, `memoize` stores its cache in `/tmp/memoize/<date>.json`, but this can be overridden by passing optional kwargs to the decorator factory.

```python
from memoize import memoize
from functools import lru_cache


@lru_cache() # Optionally, use with LRU cache to also cache in RAM
# All are optional kwargs
@memoize(stub='my_cache',               # file stub override
         cache_dir='/tmp/my_cache_dir', # cache directory override
         log_func=logger.info           # logging function override, print by default
         ignore_invalid=True)           # ignore cache if not JSON serializable
def my_func(s: str, b: bool = True, opt=None):
    return {"s": s, "b": b, "opt": opt}
```

## License

MIT

## Limitations

Args, kwargs, and function return value must be JSON-serializable.
The entire contents of the date-stamped cache file will be read and written on every function call, which may post I/O challenges.