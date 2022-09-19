# memoize.py

This repo contains a single decorator factory `memoize` that stores its cache as a flat JSON file.

## Quick Start

By default, `memoize` stores its cache in `/tmp/memoize/<date>.json`, but this can be overridden by passing optional kwargs to the decorator factory.

```python
from memoize import memoize
from functools import lru_cache

# All are optional kwargs
@memoize(stub='my_cache',               # file stub override
		 cache_dir='/tmp/my_cache_dir', # cache directory override
	  	 log_func=logger.info           # logging function override, print by default
		 ignore_invalid=True            # ignore cache if not JSON serializable
		 )
# Optionally, use with LRU cache for in memory caching
@lru_cache()
def my_func(s: str, b: bool = True, opt=None):
	return {
		"s": s,
		"b": b,
		"opt": opt
	}
```

## License

MIT

## Limitations

Args, kwargs, and function return value must be JSON-serializable.