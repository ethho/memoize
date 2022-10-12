import pytest
from memoize import memoize


def test_memoize():
	test_func = lambda x: {"float": x**2, "bool": False, "null": None, "string": "foobar"}
	wrapped = memoize(cache_lifetime_days=None)(test_func)
	print(wrapped(2.))
	print(wrapped(3.))
	print(wrapped(5.))
	print(wrapped(2.))