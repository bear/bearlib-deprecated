#!/usr/bin/env python

"""
bearlib

:copyright: (c) 2012 by Mike Taylor
:license: MIT, see LICENSE for more details.

"""

VERSION = (0, 6, 0, "")

__author__    = 'bear (Mike Taylor)'
__contact__   = 'bear@bear.im'
__copyright__ = 'Copyright 2012, Mike Taylor'
__site__      = 'https://github.com/bear/bearlib'
__version__   = u'.'.join(map(str, VERSION[0:3])) + u''.join(VERSION[3:])


import os
import sys
import pwd
import grp
import json
import types
import signal
import atexit
import logging


log = logging.getLogger()


def normalizeFilename(filename):
    result = os.path.expanduser(filename)
    result = os.path.abspath(result)
    return result

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
        log.error('Our PID is still active. Exiting')
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

def escXML(text, escape_quotes=False):
    if type(text) != types.UnicodeType:
        if type(text) == types.IntType:
            s = str(text)
        else:
            s = text
        s = list(unicode(s, 'utf-8', 'ignore'))
    else:
        s = list(text)

    cc      = 0
    matches = ('&', '<', '"', '>')

    for c in s:
        if c in matches:
            if c == '&':
                s[cc] = u'&amp;'
            elif c == '<':
                s[cc] = u'&lt;'
            elif c == '>':
                s[cc] = u'&gt;'
            elif escape_quotes:
                s[cc] = u'&quot;'
        cc += 1
    return ''.join(s)

def relativeDelta(td):
    s = ''
    if td.days < 0:
        t = "%s ago"
    else:
        t = "in %s"

    days    = abs(td.days)
    seconds = abs(td.seconds)
    if td.days < 0:
        seconds = 86400 - seconds
    minutes = seconds / 60
    hours   = minutes / 60
    weeks   = days / 7
    months  = days / 30
    years   = days / 365

    if days == 0:
        if seconds < 20:
            s = 'just now'
        elif seconds < 60:
            s = '%d seconds' % seconds
            s = t % s
        elif seconds < 120:
            s = t % 'a minute'
        elif seconds < 3600:
            s = '%d minutes' % minutes
            s = t % s
        elif seconds < 7200:
            s = t % 'an hour'
        elif seconds < 86400:
            s = '%d hours' % hours
            s = t % s
    else:
        if days == 1:
            if td.days < 0:
                if seconds < 60:
                    s = '%d seconds' % seconds
                    s = t % s
                elif seconds < 120:
                    s = t % 'a minute'
                elif seconds < 3600:
                    s = '%d minutes' % minutes
                    s = t % s
                elif seconds < 7200:
                    s = t % 'an hour'
                elif seconds < 86400:
                    s = '%d hours' % hours
                    s = t % s
                else:
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
