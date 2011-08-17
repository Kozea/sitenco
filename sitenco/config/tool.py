"""
Base tool class.

"""

import abc
from docutils.parsers.rst import (
    directives as rest_directives, Directive as RestDirective)


class Tool(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update(self):
        """Update the data managed by the tool."""
        raise NotImplementedError


class Directive(RestDirective):
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = False
    tool_dict = None
    tool = None

    def run(self):
        if self.arguments:
            self.tool = self.tool_dict[self.arguments[0]]
        else:
            # TODO: say "that's bad" in logs
            self.tool = self.tool_dict.values()[0]
