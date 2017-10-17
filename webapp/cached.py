from datetime import datetime, timedelta
import os
import thread


class cached(object):
    def __init__(self, *args, **kwargs):
        self.cached_function_responses = {}
        self.default_max_age = kwargs.get("default_cache_max_age", timedelta(seconds=int(os.environ['CACHE_AGE'])))

    def __refresh_function_param(self, func, param, async, *args, **kwargs):
        def do_refresh():
            res = func(*args, **kwargs)
            self.cached_function_responses[func][param] = {'data': res, 'fetch_time': datetime.now()}

        if async:
            thread.start_new_thread(do_refresh, ())
        else:
            do_refresh()

    def __call__(self, func):
        def inner(*args, **kwargs):
            param = args[1]
            max_age = kwargs.get('max_age', self.default_max_age)
            if func not in self.cached_function_responses:
                self.cached_function_responses[func] = {}

            not_cached = not max_age or param not in self.cached_function_responses[func]
            expired_cache = False
            if param in self.cached_function_responses[func]:
                expired_cache = (datetime.now() - self.cached_function_responses[func][param]['fetch_time'] > max_age)
            do_async = (not not_cached) and expired_cache

            if not_cached or expired_cache:
                if 'max_age' in kwargs:
                    del kwargs['max_age']
                self.__refresh_function_param(func, param, do_async, *args, **kwargs)
            return self.cached_function_responses[func][param]['data']

        return inner
