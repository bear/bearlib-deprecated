# -*- coding: utf-8 -*-
"""
:copyright: (c) 2012-2015 by Mike Taylor
:license: MIT, see LICENSE for more details.
"""

import os
import types
from urlparse import urlparse


def normalizeFilename(filename):
    """Take a given filename and return the normalized version of it.
    Where ~/ is expanded to the full OS specific home directory and all
    relative path elements are resolved.
    """ 
    result = os.path.expanduser(filename)
    result = os.path.abspath(result)
    return result

def baseDomain(domain, includeScheme=True):
    """Return only the network location portion of the given domain
    unless includeScheme is True
    """
    result = ''
    url    = urlparse(domain)
    if includeScheme:
        result = '%s://' % url.scheme
    if len(url.netloc) == 0:
        result += url.path
    else:
        result += url.netloc
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
