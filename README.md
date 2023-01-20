# memoize.py

This repo contains a decorator factory `memoize` that manages a local file cache of function results.
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

## Memoize Pandas DataFrames

The `memoize_df` decorator caches the `pandas.DataFrame` returned from a function to a CSV file.
The `pandas` module must be installed to use this feature:

```bash
python3 -m pip install pandas
```

The `memoize_df` decorator factory can be used for any function that returns a `pandas.DataFrame`.
While `memoize` stores the results of many calls in one cache file, `memoize_df` stores the DataFrame produced for exactly one call in the cache file.
Also note that DataFrame index will be written to the CSV cache _if and only if_ the index has a non-null `name` attribute.

```python
import pandas as pd
from memoize.dataframe import memoize_df


@memoize_df(cache_dir='/tmp/memoize')
def make_dataframe(foo: int):
    df = pd.DataFrame(data=reversed(range(foo)), index=range(foo), columns=['my_column'])
    df.index.name = 'my_index'
    return df


print(make_dataframe(4))
# Using cache fp='/tmp/memoize/make_dataframe_20230120.csv' to write results of function make_dataframe
#           my_column
# my_index
# 0                 3
# 1                 2
# 2                 1
# 3                 0

print(make_dataframe(3))
# Using cached call from /tmp/memoize/make_dataframe_20230120.csv
#    my_index  my_column
# 0         0          3
# 1         1          2
# 2         2          1
# 3         3          0

print(make_dataframe(4))
# Using cached call from /tmp/memoize/make_dataframe_20230120.csv
#    my_index  my_column
# 0         0          3
# 1         1          2
# 2         2          1
# 3         3          0
```

## License

MIT

## Limitations

Args, kwargs, and function return value must be JSON-serializable if using the `memoize` decorator.
The return value of the wrapped function must be a `pandas.DataFrame` when using the `memoize_df` decorator.
The entire contents of the date-stamped cache file will be read and written on every function call, which may post I/O challenges.