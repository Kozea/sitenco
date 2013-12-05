#!/usr/bin/env python3
"""
FCGI Script for Launching Site'n'Co

"""

from flup.server.fcgi import WSGIServer
import logging

import sitenco

handler = logging.FileHandler('/var/log/sitenco')
sitenco.app.logger.addHandler(handler)
WSGIServer(sitenco.app).run()
