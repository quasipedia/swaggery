#! /usr/bin/env python3
import os
import logging
import configparser

from swaggery.application import Swaggery
from swaggery.logger import log

BASE_DIR = os.path.dirname(__file__)
SWAGGER_CONF = os.path.join(BASE_DIR, 'swaggery.ini')


def init():
    '''Initialise a WSGI application to be loaded by uWSGI.'''
    # Load values from config file
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read(SWAGGER_CONF)
    log_level = config.get('application', 'logging_level').upper()
    api_dirs = list(config['apis'])
    do_checks = config.get('application',
                           'disable_boot_checks').lower() == 'false'
    # Set logging level
    log.setLevel(getattr(logging, log_level))
    log.debug('Log level set to {}'.format(log_level))
    # Bootstrap application
    log.debug('Exploring directories: {}'.format(api_dirs))
    application = Swaggery(api_dirs=api_dirs, do_checks=do_checks)
    return application

application = init()
