from datetime import datetime, timedelta
import os


class cached(object):
    def __init__(self, *args, **kwargs):
        self.cached_function_responses = {}
        self.default_max_age = kwargs.get("default_cache_max_age", timedelta(seconds=int(os.environ['CACHE_AGE'])))

    def __call__(self, func):
        def inner(*args, **kwargs):
            param = args[1] if len(args) > 1 else args[0]
            max_age = kwargs.get('max_age', self.default_max_age)
            if func not in self.cached_function_responses:
                self.cached_function_responses[func] = {}
            if not max_age or param not in self.cached_function_responses[func] or (datetime.now() - self.cached_function_responses[func][param]['fetch_time'] > max_age):
                if 'max_age' in kwargs:
                    del kwargs['max_age']
                res = func(*args, **kwargs)
                self.cached_function_responses[func][param] = {'data': res, 'fetch_time': datetime.now()}
            return self.cached_function_responses[func][param]['data']
        return inner
