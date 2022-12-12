import os
import json
import time
import re
from glob import glob
import hashlib
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Callable
from functools import wraps


def _make_key(func_name: str, args: List, kwargs: Dict) -> str:
    """Return SHA-256 hash of JSON stringified args, kwargs, and function name.
    """
    d = kwargs.copy()
    # d['_func_name'] = func_name
    d['_args'] = args
    hl = hashlib.new('sha256')
    hl.update(json.dumps(d, sort_keys=True).encode())
    return f"{func_name}#{hl.hexdigest()}"


def _clean_func_name(fname: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_\-]', '', fname)


def _get_hist_fps(query: str, cache_lifetime_days: int = None) -> List[str]:
    """
    Globs for files in `query` that are <= `cache_lifetime_days` old.
    Returns list of paths sorted in order of most recent to least recent.
    Passing None for `cache_lifetime_days` will use any cache entry regardless
    of timestamp.
    """
    if cache_lifetime_days is None:
        cache_lifetime_days = -1
    re_query = query.replace('*', '(\d{8})')
    dt_grps = list()
    for glob_match in glob(query):
        match = re.match(re_query, glob_match)
        if not match:
            continue
        try:
            item = {
                'fp': glob_match,
                'dt': datetime.strptime(match.groups()[0], '%Y%m%d').date(),
            }
        except Exception as err:
            raise
        dt_grps.append(item)

    fps = [
        file['fp'] for file in
        # Sort filepaths starting with most recent
        sorted(dt_grps, key=(lambda x: x['dt']), reverse=True)
        # Only include files timestamped less than cache_lifetime_days ago
        if ((date.today() - file['dt']) <= timedelta(days=cache_lifetime_days)
            or cache_lifetime_days < 0)
    ]
    return fps


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


def _create_cache(cache_dir: str):
    if os.path.exists(cache_dir):
        if not os.path.isdir(cache_dir):
            raise Exception(f'{cache_dir=} exists but is not a directory')
    else:
        os.makedirs(cache_dir)


def memoize(stub: Optional[str] = None,
            cache_dir: Optional[str] = '/tmp/memoize',
            ext: str = 'json',
            log_func: Callable = print,
            ignore_invalid: bool = True,
            cache_lifetime_days: int = 0) -> Callable:
    """
    Cache results of this function to the file `{cache_dir}/{funcname}_{stub}.{ext}`.
    Read cache entries up to `cache_lifetime_days` days ago if specified; setting
    to None will read from the most recent cache entry.
    Passing `_memoize_force_refresh` as a keyword argument of the wrapped
    function will run the function ignoring the cache.
    """
    # Ensure that cache exists
    _create_cache(cache_dir)
    stub = stub if stub else date.today().strftime('%Y%m%d')

    def add_memoize_dec(func):
        funcname = _clean_func_name(func.__name__)
        fp = os.path.join(cache_dir, f"{funcname}_{stub}.{ext}")
        fp_glob = os.path.join(cache_dir, f"{funcname}_*.{ext}")
        log_func(f"Using cache {fp=} to write results of function {funcname}")

        @wraps(func)
        def memoize_dec(*args, **kwargs):
            hist_fps: List[str] = _get_hist_fps(fp_glob, cache_lifetime_days)
            cache = dict()
            key = _make_key(func.__name__, args, kwargs)
            # Check for a cached result
            if not kwargs.get('_memoize_force_refresh'):
                for hist_fp in hist_fps:
                    cache.update(_read_cache(hist_fp, ignore_invalid))
                    if key in cache:
                        log_func(f"Using cached call from {hist_fp} with {key=}")
                        if hist_fp != fp:
                            # Copy the entire cache from historical entry
                            # to today if necessary
                            with open(fp, 'w') as f:
                                f.write(json.dumps(cache))
                        return cache[key]

            # Else run the function and store cached result
            result = func(*args, **kwargs)
            cache[key] = result
            with open(fp, 'w') as f:
                f.write(json.dumps(cache))
            return result
        return memoize_dec
    return add_memoize_dec

