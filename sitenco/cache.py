"""
Cache mechanisms.

"""
from flask import g, Response


CACHE = {}


class cache(object):
    """Decorator caching pages."""
    def __init__(self, rule):
        self.rule = rule
        self.__name__ = rule.__name__

    def __call__(self, **kwargs):
        key = g.project_name, self.rule, tuple(
            (key, kwargs[key]) for key in sorted(kwargs.keys()))

        if key in CACHE:
            content = CACHE[key]['content']
            mimetype = CACHE[key]['mimetype']
        else:
            answer = self.rule(**kwargs)
            if isinstance(answer, Response):
                content = answer.data
                mimetype = answer.mimetype
            else:
                content = answer
                mimetype = 'text/html'
            self.set_cache(key, {'content': content, 'mimetype': mimetype})

        return Response(content, mimetype=mimetype)

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
