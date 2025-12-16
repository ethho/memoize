import pytest
import asyncio
import pandas as pd
from pandas.testing import assert_frame_equal
from memoize.dataframe import memoize_df


def example_func(foo: int):
    df = pd.DataFrame(
        data=range(0, foo)
    )
    return df


async def async_example_func(foo: int):
    """Async version of example_func that returns a DataFrame."""
    await asyncio.sleep(0.01)
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


@pytest.mark.asyncio
@pytest.mark.parametrize('ext', ['csv', 'parquet'])
async def test_memoize_async_basic(ext, temp_cache_dir):
    """Test that memoize_df works with async functions returning DataFrames."""
    call_count = 0

    async def async_expensive_func(x):
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.01)
        return pd.DataFrame({"value": [x, x * 2, x * 3]})

    wrapped = memoize_df(cache_lifetime_days=None, ext=ext, cache_dir=temp_cache_dir)(async_expensive_func)

    # First call should execute the function
    result1 = await wrapped(5)
    assert isinstance(result1, pd.DataFrame)
    assert len(result1) == 3
    assert call_count == 1

    # Second call with same argument should use cache
    result2 = await wrapped(5)
    assert isinstance(result2, pd.DataFrame)
    assert_frame_equal(result1, result2)
    assert call_count == 1  # Function not called again

    # Different argument should execute function again
    result3 = await wrapped(3)
    assert isinstance(result3, pd.DataFrame)
    assert len(result3) == 3
    assert call_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize('ext', ['csv', 'parquet'])
async def test_memoize_async_persists_across_instances(ext, temp_cache_dir):
    """Test that memoize_df cache persists across multiple async wrapped instances."""
    async def async_add_func(a, b):
        await asyncio.sleep(0.01)
        return pd.DataFrame({"result": [a + b]})

    # First instance
    wrapped1 = memoize_df(cache_lifetime_days=None, ext=ext, cache_dir=temp_cache_dir)(async_add_func)
    result1 = await wrapped1(3, 4)
    assert isinstance(result1, pd.DataFrame)
    assert result1["result"][0] == 7

    # Second instance of the same function should use the same cache
    wrapped2 = memoize_df(cache_lifetime_days=None, ext=ext, cache_dir=temp_cache_dir)(async_add_func)
    result2 = await wrapped2(3, 4)
    assert isinstance(result2, pd.DataFrame)
    assert_frame_equal(result1, result2)


@pytest.mark.asyncio
async def test_memoize_async_with_example_func(temp_cache_dir):
    """Test memoize_df with async version of example_func."""
    call_count = 0

    async def counting_async_example_func(foo: int):
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.01)
        df = pd.DataFrame(data=range(0, foo))
        return df

    wrapped = memoize_df(cache_lifetime_days=None, ext='csv', cache_dir=temp_cache_dir)(counting_async_example_func)

    # First calls with different values
    result1 = await wrapped(2)
    assert len(result1) == 2
    assert call_count == 1

    result2 = await wrapped(3)
    assert len(result2) == 3
    assert call_count == 2

    result3 = await wrapped(5)
    assert len(result3) == 5
    assert call_count == 3

    # Repeated call should use cache
    result4 = await wrapped(2)
    assert len(result4) == 2

    # Verify the cached result has the same data (allowing for column type differences from CSV)
    assert list(result1[result1.columns[0]]) == list(result4[result4.columns[0]])
    assert call_count == 3  # Not incremented
