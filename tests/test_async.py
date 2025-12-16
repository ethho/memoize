import pytest
import asyncio
import os
from memoize import memoize


@pytest.mark.asyncio
async def test_memoize_async_basic_caching(temp_cache_dir):
	"""Test that memoize works with async functions."""
	call_count = 0

	async def async_expensive_func(x):
		nonlocal call_count
		call_count += 1
		await asyncio.sleep(0.01)
		return x ** 2

	wrapped = memoize(cache_dir=temp_cache_dir)(async_expensive_func)

	# First call should execute the function
	result1 = await wrapped(5)
	assert result1 == 25
	assert call_count == 1

	# Second call with same argument should use cache
	result2 = await wrapped(5)
	assert result2 == 25
	assert call_count == 1  # Function not called again

	# Different argument should execute function again
	result3 = await wrapped(3)
	assert result3 == 9
	assert call_count == 2


@pytest.mark.asyncio
async def test_memoize_async_cache_file_created(temp_cache_dir):
	"""Test that memoize creates cache files for async functions."""
	async def async_simple_func(x):
		await asyncio.sleep(0.01)
		return x * 2

	wrapped = memoize(cache_dir=temp_cache_dir)(async_simple_func)
	await wrapped(10)

	# Check that cache file exists
	cache_files = os.listdir(temp_cache_dir)
	assert len(cache_files) == 1
	assert cache_files[0].startswith('async_simple_func_')
	assert cache_files[0].endswith('.json')


@pytest.mark.asyncio
async def test_memoize_async_various_return_types(temp_cache_dir):
	"""Test memoize with async functions returning various data types."""
	async def async_return_int(x):
		await asyncio.sleep(0.01)
		return int(x)

	async def async_return_str(x):
		await asyncio.sleep(0.01)
		return str(x)

	async def async_return_list(x):
		await asyncio.sleep(0.01)
		return [x, x * 2, x * 3]

	async def async_return_dict(x):
		await asyncio.sleep(0.01)
		return {"value": x, "squared": x ** 2}

	async def async_return_none(x):
		await asyncio.sleep(0.01)
		return None

	# Test each async function
	for func in [async_return_int, async_return_str, async_return_list, async_return_dict, async_return_none]:
		wrapped = memoize(cache_dir=temp_cache_dir)(func)
		result = await wrapped(5)
		# Call again to verify cache works
		cached_result = await wrapped(5)
		assert result == cached_result


@pytest.mark.asyncio
async def test_memoize_async_with_kwargs(temp_cache_dir):
	"""Test memoize with async functions using keyword arguments."""
	call_count = 0

	async def async_func_with_kwargs(x, multiplier=1, offset=0):
		nonlocal call_count
		call_count += 1
		await asyncio.sleep(0.01)
		return x * multiplier + offset

	wrapped = memoize(cache_dir=temp_cache_dir)(async_func_with_kwargs)

	# Call with different kwargs
	result1 = await wrapped(5, multiplier=2)
	assert result1 == 10
	assert call_count == 1

	result2 = await wrapped(5, multiplier=2)
	assert result2 == 10
	assert call_count == 1  # Cached

	result3 = await wrapped(5, multiplier=3)
	assert result3 == 15
	assert call_count == 2  # Different kwargs, different cache key


@pytest.mark.asyncio
async def test_memoize_async_multiple_args(temp_cache_dir):
	"""Test memoize with async functions that take multiple arguments."""
	call_count = 0

	async def async_multi_arg_func(a, b, c):
		nonlocal call_count
		call_count += 1
		await asyncio.sleep(0.01)
		return a + b + c

	wrapped = memoize(cache_dir=temp_cache_dir)(async_multi_arg_func)

	result1 = await wrapped(1, 2, 3)
	assert result1 == 6
	assert call_count == 1

	result2 = await wrapped(1, 2, 3)
	assert result2 == 6
	assert call_count == 1  # Cached

	result3 = await wrapped(1, 2, 4)
	assert result3 == 7
	assert call_count == 2  # Different args


@pytest.mark.asyncio
async def test_memoize_async_persists_across_instances(temp_cache_dir):
	"""Test that cache persists across multiple async wrapped instances."""
	async def async_add_func(a, b):
		await asyncio.sleep(0.01)
		return a + b

	# First instance
	wrapped1 = memoize(cache_dir=temp_cache_dir)(async_add_func)
	result1 = await wrapped1(3, 4)
	assert result1 == 7

	# Second instance of the same function should use the same cache
	wrapped2 = memoize(cache_dir=temp_cache_dir)(async_add_func)
	result2 = await wrapped2(3, 4)
	assert result2 == 7


@pytest.mark.asyncio
async def test_memoize_async_complex_nested_types(temp_cache_dir):
	"""Test memoize with async functions returning complex nested structures."""
	async def async_complex_func(x):
		await asyncio.sleep(0.01)
		return {
			"nested": {
				"list": [1, 2, 3],
				"dict": {"key": "value"},
				"number": x
			},
			"tuple_as_list": [x, x + 1],
		}

	wrapped = memoize(cache_dir=temp_cache_dir)(async_complex_func)
	result = await wrapped(42)
	assert result["nested"]["number"] == 42
	assert result["nested"]["list"] == [1, 2, 3]

