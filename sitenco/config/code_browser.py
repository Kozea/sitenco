"""
Code browser tools.

"""

import abc
from docutils import nodes
from flask import request

from .tool import Tool, Role, Directive


class CodeBrowser(Tool):
    """Abstract class for code browser tools."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, project_name, ribbon=None):
        self.project_name = project_name
        self.ribbon = ribbon
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
    """GitHub code browser tool."""
    base_url = 'https://github.com/'


class Gitorious(CodeBrowser):
    """Gitorious code browser tool."""
    base_url = 'https://gitorious.org/'


class Redmine(CodeBrowser):
    """Redmine code browser tool."""
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


class Editable(Directive):
    """Add a link to page source."""
    def run(self):
        # TODO: fix the link for code browsers other than GitHub
        content = (
            '<aside class="editable">'
            '<a id="editable" title="Edit this page" href="%s">'
            'Edit this page</a></aside>' % (
                self.tool.code_link + '/tree/website/pages/' +
                request.path.strip('/') + '.rst'))
        return [nodes.raw('', content, format='html')]
