# -*- coding: utf-8 -*-
"""
:copyright: (c) 2012-2015 by Mike Taylor
:license: MIT, see LICENSE for more details.
"""

import os
import sys
import pwd
import grp
import json
import types
import signal
import atexit
import logging


_ourPath = os.getcwd()
_ourName = os.path.splitext(os.path.basename(sys.argv[0]))[0]

def shutdownLogging():
    logging.shutdown()

def Logs(loggername, echo=True, debug=False, chatty=False, loglevel=logging.INFO, logfile=None, logpath=None, fileHandler=None):
    """Initialize logging
    """
    log = logging.getLogger(loggername)

    if fileHandler is None:
        if logfile is None:
            logFilename = _ourName
        else:
            logFilename = logfile

        if '.log' not in logFilename:
            logFilename = '%s.log' % logFilename

        if logpath is not None:
            logFilename = os.path.join(logpath, logFilename)

        _handler   = logging.FileHandler(logFilename)
        _formatter = logging.Formatter('%(asctime)s %(levelname)-7s %(message)s')

        _handler.setFormatter(_formatter)
        log.addHandler(_handler)
        # logging.fileHandler = _handler
    else:
        log.addHandler(fileHandler)
        # logging.fileHandler = fileHandler

    if echo:
        echoHandler = logging.StreamHandler()
        if chatty:
            echoFormatter = logging.Formatter('%(asctime)s %(levelname)-7s %(processName)s[%(process)d]: %(message)s')
        else:
            echoFormatter = logging.Formatter('%(asctime)s %(levelname)-7s %(message)s')
        echoHandler.setFormatter(echoFormatter)
        log.addHandler(echoHandler)

    if debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(loglevel)

    atexit.register(shutdownLogging)
