# flake8-logging-format

Flake8 extension to validate (lack of) logging format strings


## What's This?

Python [logging](https://docs.python.org/3/library/logging.html#logging.Logger.debug) supports a special `extra` keyword
for passing a dictionary of user-defined attributes to include in a logging event. One way to ensure consistency and
rigor in logging is to **always** use `extra` to pass non-constant data and, therefore, to **never** use format strings,
concatenation, or other similar techniques to construct a log string.

In other words, do this:

```python
logger.info(
    "Hello {world}",
    extra=dict(
        world="Earth"
    )
)
```

Instead of:

```python
logger.info(
    "Hello {world}".format(world=Earth)
)
```

## Extra Whitelist

As a further level of rigor, we can enforce that `extra` dictionaries only use keys from a well-known whitelist.

Usage:

```bash
flake8 --enable-extra-whitelist
```

The built-in `Whitelist` supports plugins using `entry_points` with a key of `"logging.extra.whitelist"`. Each
registered entry point must be a callable that returns an iterable of string.

In some cases you may want to log sensitive data only in debugging scenarios.  This is supported in 2 ways:
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
 -  `G101` Logging statement should not use `extra` arguments that clash with LogRecord fields
 -  `G200` Logging statements should not include the exception in logged string (use `exception` or `exc_info=True`)
 -  `G201` Logging statements should not use `error(..., exc_info=True)` (use `exception(...)` instead)
 -  `G202` Logging statements should not use redundant `exc_info=True` in `exception`

These violations are disabled by default. To enable them for your project, specify the code(s) in your `setup.cfg`:

```ini
[flake8]
enable-extensions=G
```

## Motivation

Our motivation has to do with balancing the needs of our team and those of our customers.
On the one hand, developers and front-line support should be able to look at application logs. On the other hand, our customers don't want their data shared with anyone, including internal employees.

The implementation approaches this in two ways:

1. By trying to prevent the use of string concatenation in logs (vs explicit variable passing in the standard logging `extra` dictionary)

2. By providing an (optional) mechanism for whitelisting which field names may appear in the `extra` dictionary

Naturally, this _does not_ prevent developers from doing something like:

```python
extra=dict(
    user_id=user.name,
)
```

but then avoiding a case like this falls back to other processes around pull-requests, code review and internal policy.
