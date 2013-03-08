#!/usr/bin/env python

"""
bearlib

:copyright: (c) 2012 by Mike Taylor
:license: BSD, see LICENSE for more details.

"""

VERSION = (0, 5, 2, "alpha")

__author__    = 'bear (Mike Taylor)'
__contact__   = 'bear@bear.im'
__copyright__ = 'Copyright 2012, Mike Taylor'
__license__   = 'BSD 2-Clause'
__site__      = 'https://github.com/bear/bearlib'
__version__   = u'.'.join(map(str, VERSION[0:3])) + u''.join(VERSION[3:])


import os
import sys
import pwd
import grp
import types
import signal
import logging

from optparse import OptionParser
from ConfigParser import SafeConfigParser


_ourPath = os.getcwd()
log      = logging.getLogger('babble')

def pidWrite(pidFile):
    os.umask(077) # set umask for pid

    with open(pidFile, "w") as f:
        f.write(str(os.getpid()))

def pidRead(pidFile):
    try:
        with open(pidFile, 'r') as f:
            return int(f.read())
    except IOError:
        return -1

def pidClear(pidFile):
    if not isRunning(pidFile):
        if os.path.exists(pidFile):
            os.remove(pidFile)

def isRunning(pidFile):
    pid = pidRead(pidFile)

    if pid == -1:
        return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            log.warn('pid %d for %s found.' % (pid, pidFile))
            return False

def shutdownHandler(signal, frame):
    log.info('shutdown requested')
    sys.exit(0)

def daemonize(config):
    if not hasattr(config, 'pidfile'):
        raise Exception('pidfile is a required configuration item')
    if not hasattr(config, 'uid'):
        raise Exception('uid is a required configuration item')
    if not hasattr(config, 'gid'):
        raise Exception('gid is a required configuration item')

    if isRunning(config.pidfile):
        log.error('Babble is still running. Exiting')
        sys.exit(1)
    else:
        if os.fork() == 0:
            os.setsid()

            signal.signal(signal.SIGHUP, signal.SIG_IGN)

            pid = os.fork()

            if pid != 0:
                os._exit(0)
            else:
                pidClear(config.pidfile)
                pidWrite(config.pidfile)
        else:
            os._exit(0)

    signal.signal(signal.SIGINT,  shutdownHandler)
    signal.signal(signal.SIGTERM, shutdownHandler)

    if os.getuid() != 0:
        return

    uid = pwd.getpwnam(config.uid).pw_uid
    gid = grp.getgrnam(config.gid).gr_gid

    os.setgroups([])

    os.setgid(gid)
    os.setuid(uid)

    os.umask(077)

def relativeDelta(td):
    s = ''
    if td.days < 0:
        t = "%s ago"
    else:
        t = "in %s"

    days    = abs(td.days)
    seconds = abs(td.seconds)
    minutes = seconds / 60
    hours   = minutes / 60
    weeks   = days / 7
    months  = days / 30
    years   = days / 365

    if days == 0:
        if seconds < 20:
            s = 'just now'
        if seconds < 60:
            s = '%d seconds' % seconds
            s = t % s
        if seconds < 120:
            s = t % 'a minute'
        if seconds < 3600:
            s = '%d minutes' % minutes
            s = t % s
        if seconds < 7200:
            s = t % 'an hour'
        if seconds < 86400:
            s = '%d hours' % hours
            s = t % s
    else:
        if days == 1:
            if td.days < 0:
                s = 'yesterday'
            else:
                s = 'tomorrow'
        elif days < 7:
            s = '%d days' % days
            s = t % s
        elif days < 31:
            s = '%d weeks' % weeks
            s = t % s
        elif days < 365:
            s = '%d months' % months
            s = t % s
        else:
            s = '%d years' % years
            s = t % s

    return s

class bConfig():
    def __init__(self):
        self.options = None
        self.args    = None

    def parseCommandLine(self):
        _config = { 'config':  ('-c', '--config',  'babble.cfg', 'Configuration Filename (optionally w/path'),
                    'debug':   ('-d', '--debug',   False,        'Enable Debug?'),
                    'logpath': ('-l', '--logpath', '.',          'Path where log file is to be written'),
                    'logfile': ('',   '--logfile', 'babble.log', 'log filename'),
                    'daemon':  ('',   '--daemon',  False,        'fork into a daemon?'),
                  }

        parser = OptionParser()

        for key in _config:
            shortCmd, longCmd, defaultValue, helpText = _config[key]

            if type(defaultValue) is types.BooleanType:
                parser.add_option(shortCmd, longCmd, dest=key, action='store_true', default=defaultValue, help=helpText)
            else:
                parser.add_option(shortCmd, longCmd, dest=key, default=defaultValue, help=helpText)

        (self.options, self.args) = parser.parse_args()

        for key in _config:
            setattr(self, key, getattr(self.options, key))

    def loadConfigFile(self):
        if os.path.isfile(self.config):
            cfg = SafeConfigParser()
            cfg.readfp(open(self.config))

            for section in cfg.sections():
                for key, value in cfg.items(section):
                    if section == 'babble':
                        setattr(self, key, value)
                    else:
                        if not hasattr(self, section):
                            setattr(self, section, bConfig())

                        setattr(getattr(self, section), key, value)

def bLogs(config):
    if config.logfile is not None:
        handler       = logging.FileHandler(os.path.join(config.logpath, config.logfile))
        fileFormatter = logging.Formatter('%(asctime)s %(levelname)-7s %(processName)s: %(message)s')

        handler.setFormatter(fileFormatter)
        log.addHandler(handler)
        log.fileHandler = handler

    if config.debug:
        log.setLevel(logging.DEBUG)
        log.info('debug logging is enabled')
    else:
        log.setLevel(logging.INFO)
