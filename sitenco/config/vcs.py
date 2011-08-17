"""
Version control management tools.

"""

import abc
import brigit
from docutils import nodes
from docutils.parsers.rst import directives

from .tool import Tool, Directive


class VCS(Tool):
    """Abstract class for VCS tools."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, path, branch, url=None):
        self.path = path
        self.branch = branch
        super(VCS, self).__init__()

    @abc.abstractmethod
    def log(self, number=10):
        """List of :class:`Commit` items."""
        raise NotImplementedError


class Git(VCS):
    """Git tool."""
    def __init__(self, path, branch='master', url=None):
        self._repository = brigit.Git(path)
        super(Git, self).__init__(path, branch)

    def log(self, number=10):
        commits = "%s~%i..%s" % (self.branch, number, self.branch)
        return self._repository.pretty_log(commits)

    def update(self):
        self._repository.fetch()


class Log(Directive):
    """List logs as a definition list."""
    option_spec = {'number': directives.nonnegative_int}

    def run(self):
        children = []
        for item in self.tool.log():
            children.append(nodes.term(text=item['hash']))
            children.append(
                nodes.definition('', nodes.paragraph(text=item['message'])))
        definition_list = nodes.definition_list('', *children)
        return [definition_list]
