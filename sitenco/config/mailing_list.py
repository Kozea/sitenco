"""
Mailing list tools.

"""

import abc
from docutils import nodes

from .tool import Tool, Role


class MailingList(Tool):
    """Abstract class for mailing list tools."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, project_name):
        self.project_name = project_name
        super(MailingList, self).__init__()

    def update(self):
        """Nothing has to be done to update mailing list tools."""

    @abc.abstractproperty
    def base_url(self):
        """Base URL of the mailing list service."""
        raise NotImplementedError

    @abc.abstractproperty
    def base_mail_address(self):
        """Base mail adress of the bug tracker service."""
        raise NotImplementedError

    @property
    def archives_url(self):
        """Link to the bug mailing list archives."""
        return self.base_url + self.project_name

    @property
    def mail_address(self):
        """Mail address of the mailing list."""
        return self.project_name + self.base_mail_address


class Librelist(MailingList):
    """Librelist mailing list tool."""
    base_url = 'http://librelist.com/'
    base_mail_address = '@librelist.com'

    @property
    def archives_url(self):
        return '%sbrowser/%s' % (self.base_url, self.project_name)


class MailArchives(Role):
    """Link to the mailing list archives."""
    def run(self, name, rawtext, text, lineno, inliner, options=None,
            content=None):
        return [nodes.reference('', text, refuri=self.tool.archives_url)], []


class MailAddress(Role):
    """Mail address of the mailing list."""
    def run(self, name, rawtext, text, lineno, inliner, options=None,
            content=None):
        address_link = 'mailto:' + self.tool.mail_address
        return [nodes.reference('', text, refuri=address_link)], []
