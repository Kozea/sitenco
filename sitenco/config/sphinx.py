"""
Docs with Sphinx.

"""

import sys
import abc
import os.path
import subprocess

from . import vcs
from .. import DOCS_PATH


class Sphinx(vcs.VCS):
    """Abstract class for project folder tools."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, path, branch='master', url=None):
        path = os.path.join(DOCS_PATH, path)
        super(Sphinx, self).__init__(path, branch, url)


class Git(Sphinx, vcs.Git):
    """Git tool."""
    def update(self):
        self._repository.fetch()
        self._repository.reset('--hard', 'origin/' + self.branch)
        subprocess.check_call(
            ['python3', 'setup.py', 'build_sphinx', '-b', 'dirhtml'],
            cwd=self.path)
