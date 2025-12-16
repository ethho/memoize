import pytest
import pandas as pd
from memoize.dataframe import memoize_df


def example_func(foo: int):
    df = pd.DataFrame(
        data=range(0, foo)
    )
    return df


@pytest.mark.parametrize('ext', ['csv', 'parquet'])
def test_memoize(ext, temp_cache_dir):
    wrapped = memoize_df(cache_lifetime_days=None, ext=ext, cache_dir=temp_cache_dir)(example_func)
    print(wrapped(2))
    print(wrapped(3))
    print(wrapped(5))
    print(wrapped(2))
