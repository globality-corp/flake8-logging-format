# flake8-logging-format

Flake8 extension to validate (lack of) logging format strings


## What's This?

Python [logging](https://docs.python.org/3/library/logging.html#logging.Logger.debug) supports a special `extra` keyword
for passing a dictionary of user-defined attributes to include in a logging event. One way to ensure consistency and
rigor in logging is to **always** use `extra` to pass non-constant data and, therefore, to **never** use format strings,
concatenation, or other similar techniques to construct a log string.

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


## Extra Whitelist

As a further level of rigor, we can enforce that `extra` dictionaries only use keys from a well-known whitelist.

Usage:

     flake8 --enable-extra-whitelist

The built-in `Whitelist` supports plugins using `entry_points` with a key of `"logging.extra.whitelist"`. Each
registered entry point must be a callable that returns an iterable of string.

In some cases you may want to log sensitive data only in debugging senarios.  This is supported in 2 ways:
1. We do not check the logging.extra.whitelist for lines logged at the `debug` level
2. You may also prefix a keyword with 'debug\_' and log it at another level.  You can safely assume these will be
   filtered out of shipped logs.

## Violations Detected

 -  `G001` Logging statements should not use `string.format()` for their first argument
 -  `G002` Logging statements should not use `%` formatting for their first argument
 -  `G003` Logging statements should not use `+` concatenation for their first argument
 -  `G004` Logging statements should not use `f"..."` for their first argument (only in Python 3.6+)
 -  `G010` Logging statements should not use `warn` (use `warning` instead)
 -  `G100` Logging statements should not use `extra` arguments unless whitelisted
 -  `G200` Logging statements should not include the exception in logged string (use `exception` or `exc_info=True`)
 -  `G201` Logging statements should not use `error(..., exc_info=True)` (use `exception(...)` instead)
 -  `G202` Logging statements should not use redundant `exc_info=True` in `exception` 

These violations are disabled by default. To enable them for your project, specify the code(s) in your `setup.cfg`:

    [flake8]
    enable-extensions=G
