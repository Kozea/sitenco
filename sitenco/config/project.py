"""
Project folder tools.

"""

import abc
import os.path

from . import vcs
from .. import PATH


class Project(vcs.VCS):
    """Abstract class for project folder tools."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, path, branch='website', url=None):
        path = os.path.join(PATH, path)
        super(Project, self).__init__(path, branch, url)


class Git(Project, vcs.Git):
    """Git tool."""
    def update(self):
        self._repository.fetch()
        self._repository.reset('--hard', 'origin/' + self.branch)
