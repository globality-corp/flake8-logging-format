"""
AST Visitor to identify logging expressions.

"""
from ast import (
    Add,
    keyword,
    iter_child_nodes,
    Mod,
    NodeVisitor,
)


from logging_format.violations import (
    PERCENT_FORMAT_VIOLATION,
    STRING_CONCAT_VIOLATION,
    STRING_FORMAT_VIOLATION,
    WARN_VIOLATION,
    WHITELIST_VIOLATION,
)


LOGGING_LEVELS = {
    "debug",
    "critical",
    "error",
    "info",
    "warn",
    "warning",
}


class LoggingVisitor(NodeVisitor):

    def __init__(self, whitelist=None):
        super(LoggingVisitor, self).__init__()
        self.current_logging_call = None
        self.current_logging_argument = None
        self.current_logging_level = None
        self.current_extra_keyword = None
        self.violations = []
        self.whitelist = whitelist

    def within_logging_statement(self):
        return self.current_logging_call is not None

    def within_logging_argument(self):
        return self.current_logging_argument is not None

    def within_extra_keyword(self, node):
        return self.current_extra_keyword is not None and self.current_extra_keyword != node

    def visit_Call(self, node):
        """
        Visit a function call.

        We expect every logging statement and string format to be a function call.

        """
        # CASE 1: We're in a logging statement
        if self.within_logging_statement():
            if self.within_logging_argument() and self.is_format_call(node):
                self.violations.append((node, STRING_FORMAT_VIOLATION))
                super(LoggingVisitor, self).generic_visit(node)
                return

        logging_level = self.detect_logging_level(node)

        if logging_level and self.current_logging_level is None:
            self.current_logging_level = logging_level

        # CASE 2: We're in some other statement
        if logging_level is None:
            super(LoggingVisitor, self).generic_visit(node)
            return

        # CASE 3: We're entering a new logging statement
        self.current_logging_call = node

        if logging_level == "warn":
            self.violations.append((node, WARN_VIOLATION))

        for index, child in enumerate(iter_child_nodes(node)):
            if index == 1:
                self.current_logging_argument = child
            if index > 1 and isinstance(child, keyword) and child.arg == "extra":
                self.current_extra_keyword = child

            super(LoggingVisitor, self).visit(child)

            self.current_logging_argument = None
            self.current_extra_keyword = None

        self.current_logging_call = None
        self.current_logging_level = None

    def visit_BinOp(self, node):
        """
        Process binary operations while processing the first logging argument.

        """
        if self.within_logging_statement() and self.within_logging_argument():
            # handle percent format
            if isinstance(node.op, Mod):
                self.violations.append((node, PERCENT_FORMAT_VIOLATION))
            # handle string concat
            if isinstance(node.op, Add):
                self.violations.append((node, STRING_CONCAT_VIOLATION))
        super(LoggingVisitor, self).generic_visit(node)

    def visit_Dict(self, node):
        """
        Process dict arguments.

        """
        if self.should_check_whitelist(node):
            for key in node.keys:
                if key.s in self.whitelist or key.s.startswith("debug_"):
                    continue
                self.violations.append((self.current_logging_call, WHITELIST_VIOLATION.format(key.s)))

        super(LoggingVisitor, self).generic_visit(node)

    def visit_keyword(self, node):
        """
        Process keyword arguments.

        """
        if self.should_check_whitelist(node):
            if node.arg not in self.whitelist and not node.arg.startswith("debug_"):
                self.violations.append((self.current_logging_call, WHITELIST_VIOLATION.format(node.arg)))
        super(LoggingVisitor, self).generic_visit(node)

    def detect_logging_level(self, node):
        """
        Heuristic to decide whether an AST Call is a logging call.

        """
        try:
            if node.func.value.id == "warnings":
                return None
            # NB: We could also look at the argument signature or the target attribute
            if node.func.attr in LOGGING_LEVELS:
                return node.func.attr
        except AttributeError:
            pass
        return None

    def is_format_call(self, node):
        """
        Does a function call use format?

        """
        try:
            return node.func.attr == "format"
        except AttributeError:
            return False

    def should_check_whitelist(self, node):
        return all(
            (
                self.current_logging_level != 'debug',
                self.within_logging_statement(),
                self.within_extra_keyword(node),
                self.whitelist is not None,
            )
        )
