"""
Cache mechanisms.

"""

from flask import g, current_app


CACHE = {}


class cache(object):
    """Decorator caching pages."""
    def __init__(self, rule):
        self.rule = rule
        self.__name__ = rule.__name__

    def __call__(self, **kwargs):
        key = g.project_name, self.rule, tuple(
            (key, kwargs[key]) for key in sorted(kwargs.keys()))

        response = CACHE.get(key)
        if not response:
            response = current_app.make_response(self.rule(**kwargs))
            self.set_cache(key, response)

        return response

    def set_cache(self, key, value):
        CACHE[key] = value


class clean_cache(object):
    """Decorator cleaning the cache."""
    def __init__(self, rule):
        self.rule = rule
        self.__name__ = rule.__name__

    def __call__(self, **kwargs):
        CACHE.clear()
        return self.rule(**kwargs)
