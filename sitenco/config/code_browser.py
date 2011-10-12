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
    def base_url(self):
        """Base URL of the code browser service."""
        raise NotImplementedError

    @property
    def code_link(self):
        """Link to the code browser interface."""
        return self.base_url + self.project_name


class Github(CodeBrowser):
    """Github code browser tool."""
    base_url = 'https://github.com/'


class Gitorious(CodeBrowser):
    """Github code browser tool."""
    base_url = 'https://gitorious.org/'


class Redmine(CodeBrowser):
    """Github code browser tool."""
    def __init__(self, project_name, base_url):
        super(Redmine, self).__init__(project_name)
        self._base_url = base_url

    @property
    def base_url(self):
        return self._base_url


class CodeLink(Role):
    """Link tag to the code browser."""
    def run(self, name, rawtext, text, lineno, inliner, options=None,
            content=None):
        return [nodes.reference('', text, refuri=self.tool.code_link)], []
