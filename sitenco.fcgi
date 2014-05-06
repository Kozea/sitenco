#!/usr/bin/env python3
"""
FCGI Script for Launching Site'n'Co

"""

from flipflop import WSGIServer
import logging

import sitenco

log_handler = logging.FileHandler('/var/log/sitenco')
mail_handler = logging.SMTPHandler(
    'mail.keleos.fr', 'sitenco@kozea.fr', ['sitenco@kozea.fr'],
    'Error in Site’n’co')
sitenco.app.logger.addHandler(log_handler)
sitenco.app.logger.addHandler(mail_handler)
WSGIServer(sitenco.app).run()
