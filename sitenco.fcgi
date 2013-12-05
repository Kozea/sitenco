#!/usr/bin/env python3
"""
FCGI Script for Launching Site'n'Co

"""

from flipflop import WSGIServer
import logging

import sitenco

handler = logging.FileHandler('/var/log/sitenco')
sitenco.app.logger.addHandler(handler)
WSGIServer(sitenco.app).run()
