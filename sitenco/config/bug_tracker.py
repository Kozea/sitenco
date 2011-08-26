"""
Bug tracker tools.

"""

import abc
from docutils import nodes

from .tool import Tool, Role


class BugTracker(Tool):
    """Abstract class for bug tracker tools."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, project_name):
        self.project_name = project_name
        super(BugTracker, self).__init__()

    def update(self):
        """Nothing has to be done to update bug tracker tools."""

    @abc.abstractproperty
    def base_url(self):
        """Base URL of the bug tracker service."""
        raise NotImplementedError

    @property
    def bug_link(self):
        """Link to the bug tracker interface."""
        raise NotImplementedError


class Github(BugTracker):
    """Github bug tracker tool."""
    base_url = 'https://github.com/'

    @property
    def bug_link(self):
        return '%s%s/issues' % (self.base_url, self.project_name)


class Redmine(BugTracker):
    """Redmine bug tracker tool."""
    def __init__(self, project_name, base_url):
        super(Redmine, self).__init__(project_name)
        self._base_url = base_url

    @property
    def base_url(self):
        return self._base_url

    @property
    def bug_link(self):
        return '%sprojects/%s/issues' % (self.base_url, self.project_name)


class BugLink(Role):
    """Link to the bug tracker."""
    def run(self, name, rawtext, text, lineno, inliner, options=None,
            content=None):
        return [nodes.reference('', text, refuri=self.tool.bug_link)], []
