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


class TestMemoizeDfCustomEncoders:
    class CustomJsonValue:
        def __init__(self, value):
            self.value = value

        def to_json(self):
            return f'{{"value": {self.value}}}'

        @classmethod
        def from_json(cls, s: str):
            import json
            return cls(json.loads(s)["value"])

        def __eq__(self, other):
            return isinstance(other, TestMemoizeDfCustomEncoders.CustomJsonValue) and self.value == other.value

    @pytest.mark.parametrize('ext', ['csv', 'parquet'])
    def test_custom_encoder_decoder_roundtrip(self, ext, temp_cache_dir):
        encoders = {
            "encoded_col": (
                lambda v: v.to_json(),
                lambda v: TestMemoizeDfCustomEncoders.CustomJsonValue.from_json(v),
            )
        }

        def build_df():
            return pd.DataFrame({
                "encoded_col": [self.CustomJsonValue(1), self.CustomJsonValue(2)],
                "plain_col": ["a", "b"],
            })

        wrapped = memoize_df(
            cache_lifetime_days=None,
            ext=ext,
            cache_dir=temp_cache_dir,
            encoders=encoders,
        )(build_df)

        result_first = wrapped()
        assert isinstance(result_first.loc[0, "encoded_col"], self.CustomJsonValue)
        assert result_first.loc[0, "plain_col"] == "a"

        result_cached = wrapped()
        assert isinstance(result_cached.loc[0, "encoded_col"], self.CustomJsonValue)
        assert result_cached.loc[0, "encoded_col"] == self.CustomJsonValue(1)
        assert result_cached.loc[0, "plain_col"] == "a"

    def test_only_specified_columns_are_encoded_decoded_csv(self, temp_cache_dir):
        encoders = {
            "encoded_col": (
                lambda v: v.to_json(),
                lambda v: TestMemoizeDfCustomEncoders.CustomJsonValue.from_json(v),
            )
        }

        def build_df():
            return pd.DataFrame({
                "encoded_col": [self.CustomJsonValue(10)],
                "untouched_col": ["raw-text"],
            })

        wrapped = memoize_df(
            cache_lifetime_days=None,
            ext="csv",
            cache_dir=temp_cache_dir,
            encoders=encoders,
        )(build_df)

        _ = wrapped()
        cached = wrapped()

        assert isinstance(cached.loc[0, "encoded_col"], self.CustomJsonValue)
        assert cached.loc[0, "encoded_col"] == self.CustomJsonValue(10)
        assert cached.loc[0, "untouched_col"] == "raw-text"

    def test_encoder_none_decoder_present_csv(self, temp_cache_dir):
        encoders = {
            "encoded_col": (
                None,
                lambda v: TestMemoizeDfCustomEncoders.CustomJsonValue.from_json(v),
            )
        }

        def build_df():
            return pd.DataFrame({
                "encoded_col": ['{"value": 7}'],
            })

        wrapped = memoize_df(
            cache_lifetime_days=None,
            ext="csv",
            cache_dir=temp_cache_dir,
            encoders=encoders,
        )(build_df)

        cached = wrapped()  # first call writes then returns original
        assert isinstance(cached.loc[0, "encoded_col"], str)

        cached2 = wrapped()  # second call reads and decodes
        assert isinstance(cached2.loc[0, "encoded_col"], self.CustomJsonValue)
        assert cached2.loc[0, "encoded_col"] == self.CustomJsonValue(7)

    def test_decoder_none_encoder_present_csv(self, temp_cache_dir):
        encoders = {
            "encoded_col": (
                lambda v: v.to_json(),
                None,
            )
        }

        def build_df():
            return pd.DataFrame({
                "encoded_col": [self.CustomJsonValue(5)],
            })

        wrapped = memoize_df(
            cache_lifetime_days=None,
            ext="csv",
            cache_dir=temp_cache_dir,
            encoders=encoders,
        )(build_df)

        first = wrapped()
        assert isinstance(first.loc[0, "encoded_col"], self.CustomJsonValue)

        cached = wrapped()
        assert isinstance(cached.loc[0, "encoded_col"], str)
        assert cached.loc[0, "encoded_col"] == '{"value": 5}'

    def test_encoder_and_decoder_none_csv(self, temp_cache_dir):
        encoders = {
            "encoded_col": (
                None,
                None,
            )
        }

        def build_df():
            return pd.DataFrame({
                "encoded_col": ["no-transform"],
            })

        wrapped = memoize_df(
            cache_lifetime_days=None,
            ext="csv",
            cache_dir=temp_cache_dir,
            encoders=encoders,
        )(build_df)

        first = wrapped()
        cached = wrapped()

        assert first.loc[0, "encoded_col"] == "no-transform"
        assert cached.loc[0, "encoded_col"] == "no-transform"
