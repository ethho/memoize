import os
import json
import re
from pathlib import Path
from glob import glob
import hashlib
from datetime import date, datetime, timedelta
from typing import List, Dict, Callable

def _write_dict_to_file(fp: str, d: Dict):
    with open(fp, 'w') as f:
        text = json.dumps(d)
        f.write(text)


def _create_cache_dir(cache_dir: str):
    if os.path.exists(cache_dir):
        if not os.path.isdir(cache_dir):
            raise Exception(f'{cache_dir=} exists but is not a directory')
    else:
        os.makedirs(cache_dir)


def _make_key(func_name: str, args: List, kwargs: Dict, maxlen: int = None) -> str:
    """Return SHA-256 hash of JSON stringified args, kwargs, and function name.
    """
    d = kwargs.copy()
    d['_func_name'] = func_name
    d['_args'] = args
    hl = hashlib.new('sha256')
    hl.update(json.dumps(d, sort_keys=True).encode())
    as_str = hl.hexdigest()
    if maxlen:
        as_str = as_str[:maxlen]
    return as_str


def _clean_func_name(fname: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_\-]', '', fname)


def _get_hist_fps(cache_dir: Path, pattern: str, cache_lifetime_days: int = None) -> List[Path]:
    """
    Globs for files matching pattern in cache_dir that are <= cache_lifetime_days old.
    Returns list of Path objects sorted in order of most recent to least recent.
    """
    if cache_lifetime_days is None:
        cache_lifetime_days = -1

    re_query = re.compile(pattern.replace('*', r'(\d{8})'))
    dt_grps = list()

    for glob_match in cache_dir.glob(pattern):
        match = re.match(re_query, glob_match.name)
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
        sorted(dt_grps, key=(lambda x: x['dt']), reverse=True)
        if ((date.today() - file['dt']) <= timedelta(days=cache_lifetime_days)
            or cache_lifetime_days < 0)
    ]
    return fps


def _use_async(func, log_func: Callable = print) -> bool:
	"""Check if the function is async and asyncio is available"""
	try:
		import asyncio
		return asyncio.iscoroutinefunction(func)
	except (ImportError, NameError):
		log_func("asyncio not available; assuming synchronous function")
	return False