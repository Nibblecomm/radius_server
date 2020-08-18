import hashlib
import json
import redis
import sys
import inspect
import os

from config import REDIS_URL
from logger import exception

rs = redis.Redis.from_url(REDIS_URL)


def cache_data(obj_type, ttl=600):
    def func_warp1(func):
        def func_wrap2(*args, **kargs):
            sig = _mk_cache_sig(*args, **kargs)
            key = "%s:%s" % (func.__name__, sig)
            data_json = rs.get(key)
            if data_json is not None:
                obj_inst = obj_type()
                obj_inst.from_dict(json.loads(data_json))
                return obj_inst
            obj_inst = func(*args, **kargs)
            if obj_inst is not None:
                data_json = json.dumps(obj_inst.to_dict())
                try:
                    rs.set(key, data_json, ex=ttl)
                except:
                    exception("Exception while trying to set {key} to {data_json}".format(key=key, data_json=data_json))
            return obj_inst

        return func_wrap2

    return func_warp1


def _mk_cache_sig(*args, **kargs):
    src_data = repr(args) + repr(kargs)
    m = hashlib.md5(src_data.encode('utf-8'))
    sig = m.hexdigest()
    return sig


