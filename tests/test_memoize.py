import pytest
import os
import json
import tempfile
from memoize import memoize


@pytest.fixture
def temp_cache_dir():
	"""Fixture that provides a temporary cache directory."""
	with tempfile.TemporaryDirectory() as tmpdir:
		yield tmpdir


def test_memoize_basic_caching(temp_cache_dir):
	"""Test that memoize stores and retrieves cached results."""
	call_count = 0

	def expensive_func(x):
		nonlocal call_count
		call_count += 1
		return x ** 2

	wrapped = memoize(cache_dir=temp_cache_dir)(expensive_func)

	# First call should execute the function
	result1 = wrapped(5)
	assert result1 == 25
	assert call_count == 1

	# Second call with same argument should use cache
	result2 = wrapped(5)
	assert result2 == 25
	assert call_count == 1  # Function not called again

	# Different argument should execute function again
	result3 = wrapped(3)
	assert result3 == 9
	assert call_count == 2


def test_memoize_cache_file_created(temp_cache_dir):
	"""Test that memoize creates cache files on disk."""
	def simple_func(x):
		return x * 2

	wrapped = memoize(cache_dir=temp_cache_dir)(simple_func)
	wrapped(10)

	# Check that cache file exists
	cache_files = os.listdir(temp_cache_dir)
	assert len(cache_files) == 1
	assert cache_files[0].startswith('simple_func_')
	assert cache_files[0].endswith('.json')


def test_memoize_cache_file_content(temp_cache_dir):
	"""Test that cache file contains correct data."""
	def test_func(x):
		return {"result": x * 3}

	wrapped = memoize(cache_dir=temp_cache_dir)(test_func)
	wrapped(7)

	# Read cache file directly
	cache_file = [f for f in os.listdir(temp_cache_dir)][0]
	cache_path = os.path.join(temp_cache_dir, cache_file)

	with open(cache_path, 'r') as f:
		cache_data = json.load(f)

	assert isinstance(cache_data, dict)
	assert len(cache_data) == 1
	assert list(cache_data.values())[0] == {"result": 21}


def test_memoize_various_return_types(temp_cache_dir):
	"""Test memoize with various return data types."""
	def return_int(x):
		return int(x)

	def return_str(x):
		return str(x)

	def return_list(x):
		return [x, x * 2, x * 3]

	def return_dict(x):
		return {"value": x, "squared": x ** 2}

	def return_bool(x):
		return x > 0

	def return_none(x):
		return None

	# Test each function
	for func in [return_int, return_str, return_list, return_dict, return_bool, return_none]:
		wrapped = memoize(cache_dir=temp_cache_dir)(func)
		result = wrapped(5)
		# Call again to verify cache works
		cached_result = wrapped(5)
		assert result == cached_result


def test_memoize_with_kwargs(temp_cache_dir):
	"""Test memoize with keyword arguments."""
	call_count = 0

	def func_with_kwargs(x, multiplier=1, offset=0):
		nonlocal call_count
		call_count += 1
		return x * multiplier + offset

	wrapped = memoize(cache_dir=temp_cache_dir)(func_with_kwargs)

	# Call with different kwargs
	result1 = wrapped(5, multiplier=2)
	assert result1 == 10
	assert call_count == 1

	result2 = wrapped(5, multiplier=2)
	assert result2 == 10
	assert call_count == 1  # Cached

	result3 = wrapped(5, multiplier=3)
	assert result3 == 15
	assert call_count == 2  # Different kwargs, different cache key


def test_memoize_persists_across_instances(temp_cache_dir):
	"""Test that cache persists when creating new wrapped instances."""
	def add_func(a, b):
		return a + b

	# First instance
	wrapped1 = memoize(cache_dir=temp_cache_dir)(add_func)
	result1 = wrapped1(3, 4)
	assert result1 == 7

	# Second instance of the same function should use the same cache
	wrapped2 = memoize(cache_dir=temp_cache_dir)(add_func)
	result2 = wrapped2(3, 4)
	assert result2 == 7


def test_memoize_multiple_functions(temp_cache_dir):
	"""Test memoize with multiple different functions."""
	def func_a(x):
		return x + 1

	def func_b(x):
		return x * 2

	wrapped_a = memoize(cache_dir=temp_cache_dir)(func_a)
	wrapped_b = memoize(cache_dir=temp_cache_dir)(func_b)

	result_a = wrapped_a(5)
	result_b = wrapped_b(5)

	assert result_a == 6
	assert result_b == 10

	# Check that separate cache files were created
	cache_files = os.listdir(temp_cache_dir)
	assert len(cache_files) == 2


def test_memoize_complex_nested_types(temp_cache_dir):
	"""Test memoize with complex nested data structures."""
	def complex_func(x):
		return {
			"nested": {
				"list": [1, 2, 3],
				"dict": {"key": "value"},
				"number": x
			},
			"tuple_as_list": [x, x + 1],
		}

	wrapped = memoize(cache_dir=temp_cache_dir)(complex_func)
	result = wrapped(42)
	assert result["nested"]["number"] == 42
	assert result["nested"]["list"] == [1, 2, 3]


def test_memoize_with_multiple_args(temp_cache_dir):
	"""Test memoize with functions that take multiple arguments."""
	call_count = 0

	def multi_arg_func(a, b, c):
		nonlocal call_count
		call_count += 1
		return a + b + c

	wrapped = memoize(cache_dir=temp_cache_dir)(multi_arg_func)

	result1 = wrapped(1, 2, 3)
	assert result1 == 6
	assert call_count == 1

	result2 = wrapped(1, 2, 3)
	assert result2 == 6
	assert call_count == 1  # Cached

	result3 = wrapped(1, 2, 4)
	assert result3 == 7
	assert call_count == 2  # Different args

