import pytest
import tempfile


@pytest.fixture(scope="function")
def temp_cache_dir():
	"""Fixture that provides a temporary cache directory."""
	with tempfile.TemporaryDirectory() as tmpdir:
		yield tmpdir
