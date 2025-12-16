import os
from datetime import date
from typing import List, Optional, Callable
from functools import wraps
try:
    import pandas as pd
except ImportError:
    raise Exception(
        f"Could not import module pandas. To use the `memoize.dataframe` "
        f"module, please install pandas:\n\n"
        f'pip install --install-option="--extras-require=dataframe" git+https://github.com/ethho/memoize.git'
    )

from .utils import _clean_func_name, _get_hist_fps, _make_key, _create_cache_dir, _use_async

def _read(ext: str, fp: str) -> pd.DataFrame:
    """Reads DataFrame from CSV file at `fp`."""
    if ext == 'csv':
        return pd.read_csv(fp)
    elif ext == 'parquet':
        return pd.read_parquet(fp)
    else:
        raise Exception(f"Unsupported file extension {ext=}")


def _write(ext: str, fp: str, df: pd.DataFrame):
    if ext == 'csv':
        write_index = bool(df.index.name)
        return df.to_csv(fp, index=write_index)
    elif ext == 'parquet':
        if not pd.api.types.is_object_dtype(df.columns.dtype):
            print(f"WARNING: Converting column names to string dtype")
            df.columns = df.columns.astype(str)
        return df.to_parquet(fp)
    else:
        raise Exception(f"Unsupported file extension {ext=}")


def memoize_df(
    stub: Optional[str] = None,
    cache_dir: Optional[str] = '/tmp/memoize',
    ext: str = 'csv',
    log_func: Callable = print,
    cache_lifetime_days: int = 0
) -> Callable:
    """
    Cache the DataFrame returned by this function to
    `{cache_dir}/{funcname}_{stub}.{ext}`.
    Read cache entries up to `cache_lifetime_days` days ago if specified; setting
    to None will read from the most recent cache entry.
    """
    # Ensure that cache exists
    _create_cache_dir(cache_dir)
    stub = stub if stub else date.today().strftime('%Y%m%d')

    def add_memoize_dec(func):
        funcname = _clean_func_name(func.__name__)

        if not _use_async(func, log_func):
            @wraps(func)
            def memoize_dec(*args, **kwargs):
                key = _make_key(func.__name__, args, kwargs, maxlen=7)
                fp = os.path.join(cache_dir, f"{funcname}_{key}_{stub}.{ext}")
                log_func(f"Using cache {fp=} to write results of function {funcname}")
                fp_glob = os.path.join(cache_dir, f"{funcname}_{key}_*.{ext}")
                if not kwargs.get('_memoize_force_refresh'):
                    hist_fps: List[str] = _get_hist_fps(fp_glob, cache_lifetime_days)
                    for hist_fp in hist_fps:
                        log_func(f"Using cached call from {hist_fp}")
                        return _read(ext, hist_fp)

                # Else run the function and store cached result
                result = func(*args, **kwargs)

                if not isinstance(result, pd.DataFrame):
                    raise Exception(
                        f"Failed to write return value of function '{funcname}' to CSV file. "
                        f"Expected a pandas.DataFrame, received {type(result)}."
                    )
                _write(ext, fp, result)
                return result
            return memoize_dec
        else:
            # Same function as memoize_dec except for the await

            @wraps(func)
            async def async_memoize_dec(*args, **kwargs):
                key = _make_key(func.__name__, args, kwargs, maxlen=7)
                fp = os.path.join(cache_dir, f"{funcname}_{key}_{stub}.{ext}")
                log_func(f"Using cache {fp=} to write results of function {funcname}")
                fp_glob = os.path.join(cache_dir, f"{funcname}_{key}_*.{ext}")
                if not kwargs.get('_memoize_force_refresh'):
                    hist_fps: List[str] = _get_hist_fps(fp_glob, cache_lifetime_days)
                    for hist_fp in hist_fps:
                        log_func(f"Using cached call from {hist_fp}")
                        return _read(ext, hist_fp)

                # Else run the function and store cached result
                result = await func(*args, **kwargs)

                if not isinstance(result, pd.DataFrame):
                    raise Exception(
                        f"Failed to write return value of function '{funcname}' to CSV file. "
                        f"Expected a pandas.DataFrame, received {type(result)}."
                    )
                _write(ext, fp, result)
                return result
            return async_memoize_dec
    return add_memoize_dec

