"""
Flake8 entry point.

"""
from logging_format.visitor import LoggingVisitor
from logging_format.whitelist import Whitelist


__version__ = "0.6.0"


class LoggingFormatValidator(object):
    name = "logging-format"
    version = __version__
    enable_extra_whitelist = False

    def __init__(self, tree, filename):
        self.tree = tree

    @classmethod
    def add_options(cls, parser):
        parser.add_option("--enable-extra-whitelist", action="store_true")

    @classmethod
    def parse_options(cls, options):
        cls.enable_extra_whitelist = options.enable_extra_whitelist

    def run(self):
        whitelist = None

        if LoggingFormatValidator.enable_extra_whitelist:
            whitelist = Whitelist()

        visitor = LoggingVisitor(whitelist=whitelist)
        visitor.visit(self.tree)

        for node, reason in visitor.violations:
            yield node.lineno, node.col_offset, reason, type(self)
