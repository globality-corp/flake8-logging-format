"""
Flake8 entry point.

"""


__version__ = "0.1.0"


class LoggingFormatValidator(object):
    name = "logging-format"
    version = __version__

    def __init__(self, tree, filename):
        self.tree = tree

    def run(self):
        # XXX: inspect the AST
        if True:
            pass
        else:
            yield 0, 0, "foo bar", type(self)
