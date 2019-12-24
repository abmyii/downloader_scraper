import logging
import xxhash

from collections import OrderedDict


def fail_custom_msg(exec_func, fail_func):
    """
    Raise with custom message on error. Having fail as lambda ensures that text
    isn't loaded until execution (or never), reducing memory usage.
    """
    try:
        return exec_func()
    except Exception as exception:
        logging.error(fail_func())
        raise exception


def hash_int(string):
    return xxhash.xxh32(string).intdigest() % 10**8


def NoNoneOrderedDict(kv):
    # Returns an OrderedDict with no None keys
    ordered = OrderedDict(kv)
    for key, value in kv:
        if value is None:
            ordered.pop(key)
    return ordered


# https://stackoverflow.com/a/35177483
class LoggingHandler:
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(self.__class__.__name__)
