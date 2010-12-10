#!/usr/bin/env python

import kraken
import os
import json

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECTS_PATH = os.path.join(SITE_ROOT, 'projects')
CONFIG = {}

import controllers
import helpers
import kalamarsite
from local import LOCAL


class Site(kraken.site.Site):
    """Site'n'Co Kraken Site."""
    def __init__(self, site_root=SITE_ROOT, template_root='views',
                 kalamar_site=None, secret_key=None, fallback_on_template=True):
        super(Site, self).__init__(
            site_root, template_root, kalamar_site, secret_key,
            fallback_on_template)
        self.register_controllers(controllers)

    def prehandle(self, request):
        LOCAL.site = self
        LOCAL.project_name = request.host.split('.')[-2]
        LOCAL.variables = CONFIG[LOCAL.project_name].copy()
        LOCAL.variables.update(
            {'project_name': LOCAL.project_name, 'helpers': helpers,
             'request': request})

    
for project in os.listdir(PROJECTS_PATH):
    config_path = os.path.join(PROJECTS_PATH, project, 'configuration')
    CONFIG[project] = json.load(open(config_path))


if __name__ == '__main__':
    kraken.runserver(Site())
