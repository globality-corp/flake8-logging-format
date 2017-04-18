"""
Defined violations

"""


STRING_FORMAT_VIOLATION = "G001 Logging statement uses string.format()"
STRING_CONCAT_VIOLATION = "G003 Logging statement uses '+'"

PERCENT_FORMAT_VIOLATION = "G002 Logging statement uses '%'"

WARN_VIOLATION = "G010 Logging statement uses 'warn' instead of 'warning'"

WHITELIST_VIOLATION = "G100 Logging statement uses non-whitelisted extra keyword argument: {}"
