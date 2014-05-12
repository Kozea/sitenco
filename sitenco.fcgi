#!/usr/bin/env python3
"""
FCGI Script for Launching Site'n'Co

"""

from flipflop import WSGIServer
from logging import FileHandler
from logging.handlers import SMTPHandler


import sitenco

log_handler = FileHandler('/var/log/sitenco')
mail_handler = SMTPHandler(
    'mail.kozea.fr', 'sitenco@kozea.fr', ['sitenco@kozea.fr'],
    'Error in Site’n’co')
sitenco.app.logger.addHandler(log_handler)
sitenco.app.logger.addHandler(mail_handler)
WSGIServer(sitenco.app).run()
