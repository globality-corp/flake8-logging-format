# flake8-logging-format

Flake8 extension to validate (lack of) logging format strings


## What's This?

Python [logging](https://docs.python.org/3/library/logging.html#logging.Logger.debug) supports a special `extra` keyword
for passing a dictionary of user-defined attributes to include in a logging event. One way to ensure consistency and
rigor in logging is to **always** use `extra` to pass non-constant data and, therefore, to **never** use format strings,
concatenation, or other similar to construct a log string.

In other words, do this:

    logger.info(
        "Hello {world}",
        extra=dict(
            world="Earth"
        )
    )

Instead of:

    logger.info(
        "Hello {world}".format(world=Earth)
    )
