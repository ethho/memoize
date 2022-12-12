from typing import List, Dict, Any
from .models import CacheEntryModel


class DDBCacher(object):
    
    def __init__(self, create_table=True):
        CacheEntryModel.create_table()
        print(f"")
        # super(name, self).__init__()

    def find_key(self, key, cache_lifetime_days):
        keycond = CacheEntryModel.date >= date_lower_bound
        return CacheEntryModel.query(key, keycond, consistent_read=True)

ddb_cacher = DDBCacher()