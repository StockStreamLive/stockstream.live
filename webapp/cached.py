from datetime import datetime, timedelta
from css_html_js_minify import html_minify
import os
import threading
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
            page = str(res)
            page = html_minify(page)
            redis_client.set(path, page)
            self.path_cache_time[path] = datetime.now()

        if async:
            threading.Thread(target=do_refresh).start()
        else:
            do_refresh()

    def __call__(self, func):

        def inner(*args, **kwargs):
            path = web.ctx.get('path')

            max_age = kwargs.get('max_age', self.default_max_age)

            is_cached = redis_client.exists(path)

            reload_cache = True
            if path in self.path_cache_time:
                reload_cache = (datetime.now() - self.path_cache_time[path] > max_age)
            else:
                self.path_cache_time[path] = datetime.now()

            if not is_cached or reload_cache:
                if 'max_age' in kwargs:
                    del kwargs['max_age']
                self.__refresh_function_param(func, path, is_cached, *args, **kwargs)

            return redis_client.get(path)

        return inner
