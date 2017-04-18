"""
Visitor tests.

"""
from ast import parse
from textwrap import dedent

from hamcrest import (
    assert_that,
    contains,
    empty,
    equal_to,
    has_length,
    is_,
)

from logging_format.violations import (
    PERCENT_FORMAT_VIOLATION,
    STRING_CONCAT_VIOLATION,
    STRING_FORMAT_VIOLATION,
    WARN_VIOLATION,
    WHITELIST_VIOLATION,
)
from logging_format.visitor import LoggingVisitor
from logging_format.whitelist import Whitelist


def test_simple():
    """
    Simple logging statements are fine.

    """
    tree = parse(dedent("""\
        import logging

        logging.info("Hello World!")
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, is_(empty()))


def test_extra():
    """
    Extra dictionary is fine.

    """
    tree = parse(dedent("""\
        import logging

        logging.info(
            "Hello {world}!",
            extra=dict(
              world="World",
            ),
        )
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, is_(empty()))


def test_extra_with_string_format():
    """
    String format is ok within the extra value.

    """
    tree = parse(dedent("""\
        import logging

        logging.info(
            "Hello {world}!",
            extra=dict(
              world="{}".format("World"),
            ),
        )
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, is_(empty()))


def test_extra_with_whitelisted_keyword():
    """
    Extra keyword is ok if in whitelist.

    """
    tree = parse(dedent("""\
        import logging

        logging.info(
            "Hello {world}!",
            extra=dict(
              world="World",
            ),
        )
    """))
    whitelist = Whitelist(group="logging.extra.example")
    visitor = LoggingVisitor(whitelist=whitelist)
    visitor.visit(tree)

    assert_that(whitelist, contains("world"))
    assert_that(visitor.violations, is_(empty()))


def test_extra_with_nont_whitelisted_keyword():
    """
    Extra keyword is not ok if not in whitelist.

    """
    tree = parse(dedent("""\
        import logging

        logging.info(
            "Hello {hello}!",
            extra=dict(
              hello="{}",
            ),
        )
    """))
    whitelist = Whitelist(group="logging.extra.example")
    visitor = LoggingVisitor(whitelist=whitelist)
    visitor.visit(tree)

    assert_that(whitelist, contains("world"))
    assert_that(visitor.violations, has_length(1))
    assert_that(visitor.violations[0][1], is_(equal_to(WHITELIST_VIOLATION.format("hello"))))


def test_extra_with_non_whitelisted_dict_keyword():
    """
    Extra keyword is not ok if not in whiteslist and passed in `{}`

    """
    tree = parse(dedent("""\
        import logging

        logging.info(
            "Hello {hello}!",
            extra={
              "hello": "World!",
            },
        )
    """))
    whitelist = Whitelist(group="logging.extra.example")
    visitor = LoggingVisitor(whitelist=whitelist)
    visitor.visit(tree)

    assert_that(whitelist, contains("world"))
    assert_that(visitor.violations, has_length(1))
    assert_that(visitor.violations[0][1], is_(equal_to(WHITELIST_VIOLATION.format("hello"))))


def test_string_format():
    """
    String formatting is not ok in logging statements.

    """
    tree = parse(dedent("""\
        import logging

        logging.info("Hello {}".format("World!"))
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, has_length(1))
    assert_that(visitor.violations[0][1], is_(equal_to(STRING_FORMAT_VIOLATION)))


def test_format_percent():
    """
    Percent formatting is not ok in logging statements.

    """
    tree = parse(dedent("""\
        import logging

        logging.info("Hello %s" % "World!")
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, has_length(1))
    assert_that(visitor.violations[0][1], is_(equal_to(PERCENT_FORMAT_VIOLATION)))


def test_string_concat():
    """
    String concatenation is not ok in logging statements.

    """
    tree = parse(dedent("""\
        import logging

        logging.info("Hello" + " " + "World!")
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, has_length(2))
    # NB: We could easily decide to report only one of these
    assert_that(visitor.violations[0][1], is_(equal_to(STRING_CONCAT_VIOLATION)))
    assert_that(visitor.violations[1][1], is_(equal_to(STRING_CONCAT_VIOLATION)))


def test_warn():
    """
    Warn is deprecated in place of warning.

    """
    tree = parse(dedent("""\
        import logging

        logging.warn("Hello World!")
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, has_length(1))
    assert_that(visitor.violations[0][1], is_(equal_to(WARN_VIOLATION)))
