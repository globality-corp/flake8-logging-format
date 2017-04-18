"""
Test whitelist.

"""
from hamcrest import assert_that, contains

from logging_format.whitelist import Whitelist


def test_whitelist():
    whitelist = Whitelist(group="logging.extra.example")
    assert_that(whitelist.legal_keys, contains("world"))
