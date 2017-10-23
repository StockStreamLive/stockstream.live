from datetime import datetime, timedelta
import os
import thread
import redis
import web

redis_client = redis.from_url(os.environ.get("REDIS_URL"))


class cached(object):
    def __init__(self, *args, **kwargs):
        self.path_cache_time = {}
        self.default_max_age = kwargs.get("default_cache_max_age", timedelta(seconds=int(os.environ['CACHE_AGE'])))

    def __refresh_function_param(self, func, path, async, *args, **kwargs):
        def do_refresh():
            res = func(*args, **kwargs)
            redis_client.set(path, str(res))
            self.path_cache_time[path] = datetime.now()

        if async:
            thread.start_new_thread(do_refresh, ())
        else:
            do_refresh()

    def __call__(self, func):

        def inner(*args, **kwargs):
            path = web.ctx.get('path')

            max_age = kwargs.get('max_age', self.default_max_age)

            is_cached = redis_client.exists(path)

            expired_cache = False
            if path in self.path_cache_time:
                expired_cache = (datetime.now() - self.path_cache_time[path] > max_age)

            if not is_cached or expired_cache:
                if 'max_age' in kwargs:
                    del kwargs['max_age']
                self.__refresh_function_param(func, path, is_cached, *args, **kwargs)

            return redis_client.get(path)

        return inner
