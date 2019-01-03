"""
AST Visitor to identify logging expressions.

"""
from sys import version_info

from ast import (
    Add,
    Call,
    keyword,
    iter_child_nodes,
    Mod,
    Name,
    NodeVisitor,
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

if version_info >= (3, 6):
    from ast import FormattedValue


LOGGING_LEVELS = {
    "debug",
    "critical",
    "error",
    "exception",
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
        self.current_except_names = []
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

        self.check_exc_info(node)

        for index, child in enumerate(iter_child_nodes(node)):
            if index == 1:
                self.current_logging_argument = child
            if index >= 1:
                self.check_exception_arg(child)
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

        if self.should_check_extra_exception(node):
            for value in node.values:
                self.check_exception_arg(value)

        super(LoggingVisitor, self).generic_visit(node)

    def visit_JoinedStr(self, node):
        """
        Process f-string arguments.

        """
        if version_info >= (3, 6):
            if self.within_logging_statement():
                if any(isinstance(i, FormattedValue) for i in node.values):
                    if self.within_logging_argument():
                        self.violations.append((node, FSTRING_VIOLATION))
                        super(LoggingVisitor, self).generic_visit(node)

    def visit_keyword(self, node):
        """
        Process keyword arguments.

        """
        if self.should_check_whitelist(node):
            if node.arg not in self.whitelist and not node.arg.startswith("debug_"):
                self.violations.append((self.current_logging_call, WHITELIST_VIOLATION.format(node.arg)))

        if self.should_check_extra_exception(node):
            self.check_exception_arg(node.value)

        super(LoggingVisitor, self).generic_visit(node)

    def visit_ExceptHandler(self, node):
        """
        Process except blocks.

        """
        name = self.get_except_handler_name(node)
        if not name:
            super(LoggingVisitor, self).generic_visit(node)
            return

        self.current_except_names.append(name)
        super(LoggingVisitor, self).generic_visit(node)
        self.current_except_names.pop()

    def detect_logging_level(self, node):
        """
        Heuristic to decide whether an AST Call is a logging call.

        """
        try:
            if self.get_id_attr(node.func.value) == "warnings":
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

    def should_check_extra_exception(self, node):
        return all(
            (
                self.within_logging_statement(),
                self.within_extra_keyword(node),
                len(self.current_except_names) > 0,
            )
        )

    def get_except_handler_name(self, node):
        """
        Helper to get the exception name from an ExceptHandler node in both py2 and py3.

        """
        name = node.name
        if not name:
            return None

        if version_info < (3,):
            return name.id
        return name

    def get_id_attr(self, value):
        """Check if value has id attribute and return it.

        :param value: The value to get id from.
        :return: The value.id.
        """
        if not hasattr(value, "id") and hasattr(value, "value"):
            value = value.value
        return value.id

    def is_bare_exception(self, node):
        """
        Checks if the node is a bare exception name from an except block.

        """
        return isinstance(node, Name) and node.id in self.current_except_names

    def is_str_exception(self, node):
        """
        Checks if the node is the expression str(e) or unicode(e), where e is an exception name from an except block

        """
        return (
            isinstance(node, Call)
            and isinstance(node.func, Name)
            and node.func.id in ('str', 'unicode')
            and node.args
            and self.is_bare_exception(node.args[0])
        )

    def check_exception_arg(self, node):
        if self.is_bare_exception(node) or self.is_str_exception(node):
            self.violations.append((self.current_logging_call, EXCEPTION_VIOLATION))

    def check_exc_info(self, node):
        """
        Reports a violation if exc_info keyword is used with logging.error or logging.exception.

        """
        if self.current_logging_level not in ('error', 'exception'):
            return

        for kw in node.keywords:
            if kw.arg == 'exc_info':
                if self.current_logging_level == 'error':
                    violation = ERROR_EXC_INFO_VIOLATION
                else:
                    violation = REDUNDANT_EXC_INFO_VIOLATION
                self.violations.append((node, violation))
