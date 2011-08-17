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
    __metaclass__ = abc.ABCMeta

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = False
    tool = None

    def run(self):
        """Method run each time a directive is called."""
        raise NotImplementedError
