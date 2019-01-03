"""
Visitor tests.

"""
from ast import parse
from sys import version_info
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
    FSTRING_VIOLATION,
    WARN_VIOLATION,
    WHITELIST_VIOLATION,
    EXCEPTION_VIOLATION,
    ERROR_EXC_INFO_VIOLATION,
    REDUNDANT_EXC_INFO_VIOLATION,
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


def test_extra_with_not_whitelisted_keyword():
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


def test_debug_ok_with_not_whitelisted_keyword():
    """
    Extra keyword is ok for debug if not in whitelist.

    """
    tree = parse(dedent("""\
        import logging

        logging.debug(
            "Hello {goodbye}!",
            extra=dict(
              goodbye="{}",
            ),
        )
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


def test_debug_prefix_ok_with_not_whitelisted_keyword():
    """
    Extra keyword is ok if prefix 'debug_'.

    """
    tree = parse(dedent("""\
        import logging

        logging.info(
            "Hello {debug_hello}!",
            extra=dict(
              debug_hello="{}",
            ),
        )
    """))
    whitelist = Whitelist(group="logging.extra.example")
    visitor = LoggingVisitor(whitelist=whitelist)
    visitor.visit(tree)

    assert_that(whitelist, contains("world"))
    assert_that(visitor.violations, is_(empty()))


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


def test_debug_string_format():
    """
    String formatting is not ok in logging statements.

    """
    tree = parse(dedent("""\
        import logging

        logging.debug("Hello {}".format("World!"))
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


def test_fstring():
    """
    F-Strings are not ok in logging statements.

    """
    if version_info >= (3, 6):
        tree = parse(dedent("""\
            import logging
            name = "world"
            logging.info(f"Hello {name}")
        """))
        visitor = LoggingVisitor()
        visitor.visit(tree)

        assert_that(visitor.violations, has_length(1))
        assert_that(visitor.violations[0][1], is_(equal_to(FSTRING_VIOLATION)))


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


def test_warnings():
    """
    Warnings library is forgiven.

    """
    tree = parse(dedent("""\
        import warnings

        warnings.warn("Hello World!")
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, is_(empty()))


def test_exception_standard():
    """
    In an except block, exceptions should be logged using .exception().

    """
    tree = parse(dedent("""\
        import logging

        try:
            pass
        except Exception:
            logging.exception('Something bad has happened')
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, is_(empty()))


def test_exception_warning():
    """
    In an except block, logging exceptions using exc_info=True is ok.

    """
    tree = parse(dedent("""\
        import logging

        try:
            pass
        except Exception:
            logging.warning('Something bad has happened', exc_info=True)
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, is_(empty()))


def test_exception_attribute_as_main_arg():
    """
    In an except block, passing an exception attribute into logging as main argument is ok.

    """
    tree = parse(dedent("""\
            import logging

            class CustomException(Exception):
                def __init__(self, custom_arg):
                    self.custom_arg = custom_arg

            try:
                pass
            except CustomException as e:
                logging.error(e.custom_arg)
        """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, is_(empty()))


def test_exception_attribute_as_formatting_arg():
    """
    In an except block, passing an exception attribute into logging as a formatting argument is ok.

    """
    tree = parse(dedent("""\
        import logging

        class CustomException(Exception):
            def __init__(self, custom_arg):
                self.custom_arg = custom_arg

        try:
            pass
        except CustomException as e:
            logging.error('Custom exception has occurred: %s', e.custom_arg)
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, is_(empty()))


def test_exception_attribute_in_extra():
    """
    In an except block, passing an exception attribute into logging as a value of extra dict is ok.

    """
    tree = parse(dedent("""\
        import logging

        class CustomException(Exception):
            def __init__(self, custom_arg):
                self.custom_arg = custom_arg

        try:
            pass
        except CustomException as e:
            logging.error('Custom exception has occurred: {custom_arg}', extra=dict(custom_arg=e.custom_arg))
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, is_(empty()))


def test_exception_as_main_arg():
    """
    In an except block, passing the exception into logging as main argument is not ok.

    """
    tree = parse(dedent("""\
        import logging

        try:
            pass
        except Exception as e:
            logging.exception(e)
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, has_length(1))
    assert_that(visitor.violations[0][1], is_(equal_to(EXCEPTION_VIOLATION)))


def test_exception_as_formatting_arg():
    """
    In an except block, passing the exception into logging as a formatting argument is not ok.

    """
    tree = parse(dedent("""\
        import logging

        try:
            pass
        except Exception as e:
            logging.exception('Exception occurred: %s', str(e))
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, has_length(1))
    assert_that(visitor.violations[0][1], is_(equal_to(EXCEPTION_VIOLATION)))


def test_exception_in_extra():
    """
    In an except block, passing the exception into logging as a value of extra dict is not ok.

    """
    tree = parse(dedent("""\
        import logging

        try:
            pass
        except Exception as e:
            logging.exception('Exception occurred: {exc}', extra=dict(exc=e))
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, has_length(1))
    assert_that(visitor.violations[0][1], is_(equal_to(EXCEPTION_VIOLATION)))


def test_nested_exception():
    """
    In a nested except block, using the exception from an outer except block is not ok.

    """
    tree = parse(dedent("""\
        import logging

        try:
            pass
        except Exception as e1:
            try:
                pass
            except Exception as e2:
                logging.exception(e1)
            logging.exception(e1)
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, has_length(2))
    assert_that(visitor.violations[0][1], is_(equal_to(EXCEPTION_VIOLATION)))
    assert_that(visitor.violations[1][1], is_(equal_to(EXCEPTION_VIOLATION)))


def test_error_exc_info():
    """
    .error(..., exc_info=True) should not be used in favor of .exception(...).

    """

    tree = parse(dedent("""\
        import logging

        logging.error('Hello World', exc_info=True)
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, has_length(1))
    assert_that(visitor.violations[0][1], is_(equal_to(ERROR_EXC_INFO_VIOLATION)))


def test_exception_exc_info():
    """
    .exception(..., exc_info=True) is redundant.

    """

    tree = parse(dedent("""\
        import logging

        logging.exception('Hello World', exc_info=True)
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, has_length(1))
    assert_that(visitor.violations[0][1], is_(equal_to(REDUNDANT_EXC_INFO_VIOLATION)))


def test_app_log():
    """
    Detect nested loggers.

    """
    tree = parse(dedent("""\
        import logging

        class TestApp(object):

            def __init__(self, logger: logging.Logger, child=None):
                self.log = logger
                self.child = child

        app_name = "test-app"
        logger = logging.getLogger(app_name)

        app = TestApp(logger)

        logger = logging.getLogger("child1")
        app.child = TestApp(logger)

        app.log.info(f"Hello World for {app_name}")
        app.child.log.debug(f"Hello World for {app_name}")
        try:
            raise Exception("Another test")
        except Exception as exp:
            app.log.exception("Something bad has happened")
    """))
    visitor = LoggingVisitor()
    visitor.visit(tree)

    assert_that(visitor.violations, has_length(1))
    assert_that(visitor.violations[0][1], is_(equal_to(FSTRING_VIOLATION)))
