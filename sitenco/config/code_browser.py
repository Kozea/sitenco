"""
Code browser tools.

"""

import abc
from docutils import nodes

from .tool import Tool, Role


class CodeBrowser(Tool):
    """Abstract class for code browser tools."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, project_name):
        self.project_name = project_name
        super(CodeBrowser, self).__init__()

    def update(self):
        """Nothing has to be done to update code browser tools."""

    @abc.abstractproperty
    def code_link(self, number=10):
        """Link to the code browser interface."""
        raise NotImplementedError


class Github(CodeBrowser):
    """Github code browser tool."""
    base_url = 'https://github.com/'

    @property
    def code_link(self):
        return self.base_url + self.project_name


class CodeLink(Role):
    """List logs as a definition list."""
    def run(self, name, rawtext, text, lineno, inliner, options=None,
            content=None):
        return [nodes.reference('', text, refuri=self.tool.code_link)], []
