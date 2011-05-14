#!/usr/bin/env python
"""
FCGI Script for Launching Site'n'Co

"""

from flup.server.fcgi import WSGIServer

import sitenco

WSGIServer(sitenco.app).run()
