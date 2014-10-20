"""
Continuous integration tools.

"""

import abc
import urllib.request

from .tool import Tool


class ContinuousIntegration(Tool):
    """Abstract class for continuous integration tools."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, project_name, base_url):
        self.project_name = project_name
        self.base_url = base_url
        super(ContinuousIntegration, self).__init__()

    def update(self):
        """Nothing has to be done to update continuous integration tools."""


class Jenkins(ContinuousIntegration):
    """Redmine bug tracker tool."""
    def update(self):
        """Update the continuous integration tool."""
        build_url = '%sjob/%s/build?delay=0sec' % (
            self.base_url, self.project_name)
        urllib.request.urlopen(build_url, data=b'')
