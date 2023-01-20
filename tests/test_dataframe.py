import pytest
import pandas as pd
from memoize.dataframe import memoize_df


def example_func(foo: int):
    df = pd.DataFrame(
        data=range(0, foo)
    )
    return df


def test_memoize():
    wrapped = memoize_df(cache_lifetime_days=None)(example_func)
    print(wrapped(2))
    print(wrapped(3))
    print(wrapped(5))
    print(wrapped(2))
