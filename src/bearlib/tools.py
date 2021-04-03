# -*- coding: utf-8 -*-
"""
:copyright: (c) 2012-2021 by Mike Taylor
:license: CC0 1.0 Universal, see LICENSE for more details.
"""
import os
import logging
import datetime
from urllib.parse import urlparse


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
    url = urlparse(domain)
    if includeScheme:
        result = '%s://' % url.scheme
    if len(url.netloc) == 0:
        result += url.path
    else:
        result += url.netloc
    return result


def pidWrite(pidFile):
    os.umask(0o77)  # set umask for pid
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

    try:
        os.kill(pid, 0)
        return True
    except OSError:
        s = 'pid %d for %s found.' % (pid, pidFile)
        logging.warning(s)
        return False


def escXML(text, escape_quotes=False):
    if not isinstance(text, str):
        if isinstance(text, int):
            s = str(text)
        else:
            s = text
        s = list("%s" % str(s))
    else:
        s = list(text)

    cc = 0
    matches = ('&', '<', '"', '>')

    for c in s:
        if c in matches:
            if c == '&':
                s[cc] = '&amp;'
            elif c == '<':
                s[cc] = '&lt;'
            elif c == '>':
                s[cc] = '&gt;'
            elif escape_quotes:
                s[cc] = '&quot;'
        cc += 1
    return ''.join(s)


def _zeroDays(seconds):
    if seconds < 20:
        return 'just now'
    if seconds < 60:
        return '%d seconds' % seconds
    if seconds < 120:
        return 'a minute'
    if seconds < 3600:
        return '%d minutes' % (seconds / 60)
    if seconds < 7200:
        return 'an hour'
    return '%d hours' % (seconds / 3600)


def relativeDelta(td):
    s = ''
    days = abs(td.days)
    seconds = abs(td.seconds)
    if td.days < 0:
        seconds = 86400 - seconds
        t = "%s ago"
    else:
        t = "in %s"
    if days > 28:
        start = datetime.datetime.now()
        end = start + td
        months = (abs(end.year - start.year) * 12) + (end.month - start.month)
        print(abs(end.year - start.year))
        print(abs(end.year - start.year) * 12)
        print(end.month - start.month)
        print(months)

    if days == 0:
        s = t % _zeroDays(seconds)
    else:
        if days == 1:
            if td.days < 0:
                if seconds < 86400:
                    s = t % _zeroDays(seconds)
                else:
                    s = 'yesterday'
            else:
                s = 'tomorrow'
        elif days < 7:
            s = t % f'{days} days'
        elif days < 31:
            s = t % f'{days / 7} weeks'
        elif days < 365:
            s = t % f'{months} months'
        else:
            s = t % f'{td.years} years'
    return s
