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


## Extra Whitelist

As a further level of rigor, we can enforce that `extra` dictionaries only use keys from a well-known whitelist.

Usage:

     flake8 --enable-extra-whitelist

The built-in `Whitelist` supports plugins using `entry_points` with a key of `"logging.extra.whitelist"`. Each
registered entry point must be a callable that returns an iterable of string.


## Violations Detected

 -  `G001` Logging statements should not use `string.format()` for their first argument
 -  `G002` Logging statements should not use `%` formatting for their first argument
 -  `G003` Logging statements should not use `+` concatenation for their first argument
 -  `G010` Logging statements should not use `warn` (use `warning` instead)
 -  `G100` Logging statements should not use `extra` arguments unless whitelisted
