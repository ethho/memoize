from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, ListAttribute, NumberAttribute, DynamicMapAttribute
)


class CacheEntryValue(DynamicMapAttribute):
    pass


class CacheEntryModel(Model):
    class Meta:
        table_name = 'memoize-cache'

    key = UnicodeAttribute(hash_key=True)
    date = UnicodeAttribute(range_key=True)
	value = CacheEntryValue()
