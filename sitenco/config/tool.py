"""
Base tool classes.

"""

import abc
from flask import g
from docutils.parsers.rst import Directive as RestDirective


class Tool(object):
    """Abstract class for external tools."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update(self):
        """Update the data managed by the tool."""
        raise NotImplementedError


class Element(object):
    """Abstract class for ReST elements."""
    __metaclass__ = abc.ABCMeta

    @property
    def tool(self):
        """Tool related to the element."""
        tool_type = self.__class__.__module__.split('.')[-1]
        return g.config.tools[tool_type]


class Directive(RestDirective, Element):
    """Abstract class for ReST directives."""
    __metaclass__ = abc.ABCMeta

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = False

    def run(self):
        """Method run each time a directive is called."""
        raise NotImplementedError


class Role(Element):
    """Abstract class for ReST roles."""
    __metaclass__ = abc.ABCMeta

    def run(self, name, rawtext, text, lineno, inliner, options=None,
            content=None):
        """Method run each time a role is called."""
        raise NotImplementedError
