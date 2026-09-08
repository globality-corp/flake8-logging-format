"""
A logging extra keyword argument whitelist.

"""
from importlib.metadata import entry_points


class Whitelist:
    """
    A pluggable whitelist.

    Uses entry points.

    """
    def __init__(self, group="logging.extra.whitelist"):
        self.legal_keys = {
            legal_key
            for entry_point in entry_points().select(group=group)
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
