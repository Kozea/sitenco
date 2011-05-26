#!/usr/bin/env python
# Too bad: this file must be separated from the main script, as Sphinx uses
# docutils its own way, redefining functions for its own use, making Site'n'Co
# fail with some docutils functions such as directives.

import os
from sphinx.application import Sphinx


SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECTS_PATH = os.path.join(SITE_ROOT, 'projects')


for project in os.listdir(PROJECTS_PATH):
    api = os.path.join(SITE_ROOT, 'projects', project, 'api')
    if os.path.isdir(api):
        outdir = os.path.join(api, os.pardir, 'static', 'api')
        doctreedir = os.path.join(outdir, '.doctrees')
        Sphinx(api, api, outdir, doctreedir, 'html').build()
