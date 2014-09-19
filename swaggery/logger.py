'''Configure and provide a karma-wide logger.

Usage pattern from other modules: "from logger import log".
'''

import logging

# create and configure a log handler
__output_to_stderr = logging.StreamHandler()
__formatter = logging.Formatter(
    '%(asctime)s [ %(levelname)-8s ] - %(message)s - %(pathname)s:%(lineno)s')
__output_to_stderr.setFormatter(__formatter)

# create logger
log = logging.getLogger('swaggery')
log.addHandler(__output_to_stderr)
