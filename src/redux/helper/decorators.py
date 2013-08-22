import functools

# :SEE: http://wiki.python.org/moin/PythonDecoratorLibrary/#Alternate_memoize_as_nested_functions
def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]

    return memoizer


def post_hookable(cls):
    cls.post_hook()
    return cls