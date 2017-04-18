"""
A logging extra keyword argument whitelist.

"""
from pkg_resources import iter_entry_points


class Whitelist(object):
    """
    A pluggable whitelist.

    Uses entry points.

    """
    def __init__(self, group="logging.extra.whitelist"):
        self.legal_keys = {
            legal_key
            for entry_point in iter_entry_points(group)
            for legal_key in entry_point.load()()
        }

    def __iter__(self):
        return iter(self.legal_keys)

    def __contains__(self, key):
        return key in self.legal_keys


def example_whitelist():
    """
    Example whitelist entry point used for testing.

    """
    return ["world"]
