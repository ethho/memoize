import os
import json
from datetime import date
from typing import List, Optional, Callable
from functools import wraps
from .utils import _clean_func_name, _get_hist_fps, _make_key, _create_cache_dir, _write_dict_to_file, _use_async

def _read_cache(fp: str, ignore_invalid: bool = True):
    cache = dict()
    try:
        with open(fp, 'rb') as f:
            cache = json.load(f)
    except json.decoder.JSONDecodeError as err:
        if ignore_invalid:
            cache = dict()
        else:
            raise
    if not isinstance(cache, dict):
        raise TypeError(f"Cache at {fp} could not be deserialized to dictionary")
    return cache


def memoize(
    stub: Optional[str] = None,
    cache_dir: Optional[str] = '/tmp/memoize',
    ext: str = 'json',
    log_func: Callable = print,
    cache_lifetime_days: int = 0
) -> Callable:
    """
    Cache results of this function to the file `{cache_dir}/{funcname}_{stub}.{ext}`.
    Read cache entries up to `cache_lifetime_days` days ago if specified; setting
    to None will read from the most recent cache entry.
    """
    # Ensure that cache exists
    _create_cache_dir(cache_dir)
    stub = stub if stub else date.today().strftime('%Y%m%d')

    def add_memoize_dec(func):
        funcname = _clean_func_name(func.__name__)
        fp = os.path.join(cache_dir, f"{funcname}_{stub}.{ext}")
        fp_glob = os.path.join(cache_dir, f"{funcname}_*.{ext}")
        log_func(f"Using cache {fp=} to write results of function {funcname}")

        if not _use_async(func, log_func):
            @wraps(func)
            def memoize_dec(*args, **kwargs):
                cache = dict()
                key = _make_key(func.__name__, args, kwargs)
                # Check for a cached result
                if not kwargs.get('_memoize_force_refresh'):
                    hist_fps: List[str] = _get_hist_fps(fp_glob, cache_lifetime_days)
                    for hist_fp in hist_fps:
                        cache.update(_read_cache(hist_fp))
                        if key in cache:
                            log_func(f"Using cached call from {hist_fp} with {key=}")
                            if hist_fp != fp:
                                # Copy the entire cache from historical entry
                                # to today if necessary
                                _write_dict_to_file(fp, cache)
                            return cache[key]

                # Else run the function and store cached result
                result = func(*args, **kwargs)
                cache[key] = result
                _write_dict_to_file(fp, cache)
                return result
            return memoize_dec
        else:
            # Same function as memoize_dec except for the await

            @wraps(func)
            async def async_memoize_dec(*args, **kwargs):
                cache = dict()
                key = _make_key(func.__name__, args, kwargs)
                # Check for a cached result
                if not kwargs.get('_memoize_force_refresh'):
                    hist_fps: List[str] = _get_hist_fps(fp_glob, cache_lifetime_days)
                    for hist_fp in hist_fps:
                        cache.update(_read_cache(hist_fp))
                        if key in cache:
                            log_func(f"Using cached call from {hist_fp} with {key=}")
                            if hist_fp != fp:
                                # Copy the entire cache from historical entry
                                # to today if necessary
                                _write_dict_to_file(fp, cache)
                            return cache[key]

                # Else run the function and store cached result
                result = await func(*args, **kwargs)
                cache[key] = result
                _write_dict_to_file(fp, cache)
                return result
            return async_memoize_dec
    return add_memoize_dec

