import os
import json
import re
from pathlib import Path
from glob import glob
import hashlib
from datetime import date, datetime, timedelta
from typing import List, Dict, Callable, Optional, Tuple

# EncoderKwargs is a dictionary where the key is a string and the value is a tuple of two callables (encode, decode)
# e.g. {"column_name": (lambda x: x.to_string(), lambda x: x.from_string())}
EncoderKwargs = Dict[str, Tuple[Callable, Callable]]


class Encoders:
    IDENTITY_FUNC = staticmethod(lambda x: x)

    @staticmethod
    def _validate_encoders(encoders: EncoderKwargs):
        try:
            _ = {
                k: (v[0], v[1]) for k, v in encoders.items()
            }
        except Exception as e:
            raise ValueError(f"Invalid encoders provided: {e}")

    def __init__(self, encoders: Optional[EncoderKwargs] = None):
        if encoders is None:
            self.encoders = {}
        else:
            self._validate_encoders(encoders)
            self.encoders = encoders

    def get_encoder(self, key):
        if key not in self.encoders:
            return self.IDENTITY_FUNC
        return self.encoders[key][0] or self.IDENTITY_FUNC
    
    def get_decoder(self, key):
        if key not in self.encoders:
            return self.IDENTITY_FUNC
        return self.encoders[key][1] or self.IDENTITY_FUNC
    
    def encode_value(self, value, key):
        encode_func = self.get_encoder(key)
        return encode_func(value)
    
    def decode_value(self, value, key):
        decode_func = self.get_decoder(key)
        return decode_func(value)
