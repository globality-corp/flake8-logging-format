"""
Defined violations

"""


STRING_FORMAT_VIOLATION = "G001 Logging statement uses string.format()"
STRING_CONCAT_VIOLATION = "G003 Logging statement uses '+'"

PERCENT_FORMAT_VIOLATION = "G002 Logging statement uses '%'"

FSTRING_VIOLATION = "G004 Logging statement uses f-string"

WARN_VIOLATION = "G010 Logging statement uses 'warn' instead of 'warning'"

WHITELIST_VIOLATION = "G100 Logging statement uses non-whitelisted extra keyword argument: {}"

EXCEPTION_VIOLATION = "G200 Logging statement uses exception in arguments"

ERROR_EXC_INFO_VIOLATION = "G201 Logging: .exception(...) should be used instead of .error(..., exc_info=True)"
REDUNDANT_EXC_INFO_VIOLATION = "G202 Logging statement has redundant exc_info"
