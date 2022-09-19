import os
import json
import time
import hashlib
from datetime import date
from typing import List, Dict, Optional, Callable
from functools import wraps


def _make_key(func_name: str, args: List, kwargs: Dict) -> str:
    """Return SHA-256 hash of JSON stringified args, kwargs, and function name.
    """
    d = kwargs.copy()
    d['_func_name'] = func_name
    d['_args'] = args
    hl = hashlib.new('sha256')
    hl.update(json.dumps(d, sort_keys=True).encode()) 
    return hl.hexdigest()


def memoize(stub: Optional[str] = None,
            cache_dir: Optional[str] = '/tmp/memoize',
            ext: str = 'json',
            log_func: Callable = print,
            ignore_invalid: bool = True) -> Callable:
    # Ensure that cache exists
    if os.path.exists(cache_dir):
        if not os.path.isdir(cache_dir):
            raise Exception(f'{cache_dir=} exists but is not a directory')
    else:
        os.makedirs(cache_dir)
    stub = stub if stub else date.today().strftime('%Y%m%d') 
    fp = os.path.join(cache_dir, f"{stub}.{ext}")

    def add_memoize_dec(func):
        log_func(f"Using cache {fp=} for function {func.__name__}")
        @wraps(func)
        def memoize_dec(*args, **kwargs):
            cache = dict()
            key = _make_key(func.__name__, args, kwargs)
            # Check for a cached result
            if os.path.isfile(fp) and not kwargs.get('_memoize_force_refresh'):
                start = time.time()
                with open(fp, 'rb') as f:
                    try:
                        cache = json.load(f)
                    except json.decoder.JSONDecodeError as err:
                        if ignore_invalid:
                            cache = dict()
                        else:
                            raise
                if not isinstance(cache, dict):
                    breakpoint()
                    raise TypeError(f"Cache at {fp=} could not be deserialized to dictionary")
                if key in cache:
                    return cache[key]
                log_func(f"read from cache took {(time.time() - start):0.2f} seconds")
            
            # Else run the function and store cached result
            result = func(*args, **kwargs)
            start = time.time()
            cache[key] = result
            with open(fp, 'w') as f:
                text = json.dumps(cache)
                f.write(text)
            log_func(f"write to cache took {(time.time() - start):0.2f} seconds")
            return result
        return memoize_dec
    return add_memoize_dec

