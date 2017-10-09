from datetime import datetime, timedelta
import os


class cached(object):
    def __init__(self, *args, **kwargs):
        self.cached_function_responses = {}
        self.default_max_age = kwargs.get("default_cache_max_age", timedelta(seconds=int(os.environ['CACHE_AGE'])))

    def __call__(self, func):
        def inner(*args, **kwargs):
            max_age = kwargs.get('max_age', self.default_max_age)
            if not max_age or func not in self.cached_function_responses or (datetime.now() - self.cached_function_responses[func]['fetch_time'] > max_age):
                if 'max_age' in kwargs: del kwargs['max_age']
                res = func(*args, **kwargs)
                self.cached_function_responses[func] = {'data': res, 'fetch_time': datetime.now()}
            return self.cached_function_responses[func]['data']
        return inner
