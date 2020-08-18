from gevent.lock import BoundedSemaphore
import hashlib
import arrow
from collections import OrderedDict

class Cache():
    '''Creates a dict that expires after max_age_seconds

    '''
    def __init__(self,max_age_seconds=5):
        self.age       = max_age_seconds
        self.semaphore = BoundedSemaphore()
        self.entries   = {}

    def get(self, key): 
        with self.semaphore:
            item = self.entries.get(key)   
            expiry = arrow.utcnow().timestamp - self.age
            if item:
                if item[1] > expiry:                    
                    return item[0]
                else:
                    del self.entries[key]
                    return None
            else:
                return None

    def set(self, key, value): 
        with self.semaphore:
            self.entries[key] = (value,arrow.utcnow().timestamp)
    
    def delete(self, key):
        with self.semaphore:
            try:
                del self.entries[key]
            except KeyError as k:
                pass
        return

    def exists(self, key):
        """ Return True if the dict has a key, else return False. """
        with self.semaphore:
            item = self.entries.get(key)   
            expiry = arrow.utcnow().timestamp - self.age
            if item:
                if item[1] > expiry:
                    return True
                else:
                    del self.entries[key]
                    return False
            else:
                return False


online_cache = Cache()

user_cache = Cache()

nas_cache = Cache()

stat_cache = Cache()

_cache = Cache()

def cache_data(category='all'):
    def func_warp1(func):
        def func_wrap2(*args, **kargs):
            sig = _mk_cache_sig(*args, **kargs)
            key = "%s:%s:%s"%(category,func.__name__, sig)
            data = _cache.get(key)
            if data is not None:
                return data
            data = func(*args, **kargs)
            if data is not None:
                _cache.set(key,data)
            return data
        return func_wrap2
    return func_warp1

def _mk_cache_sig(*args, **kargs):
    src_data = repr(args) + repr(kargs)
    m = hashlib.md5(src_data.encode('utf-8'))
    sig = m.hexdigest()
    return sig


 