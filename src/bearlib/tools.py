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
    return os.path.abspath(os.path.expanduser(filename))


def baseDomain(domain, includeScheme=True):
    """Return only the network location portion of the given domain
    unless includeScheme is True
    """
    result = ''
    url = urlparse(domain)
    if includeScheme:
        if len(url.scheme) > 0:
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


def _pluralize(template, value):
    s = ''
    if round(value) > 1:
        s = 's'
    return template.format(value, s)


def _zeroDays(seconds, template):
    if seconds < 20:
        return 'just now'
    if seconds < 60:
        return template.format(_pluralize('{:.0f} second{}', seconds))
    if seconds < 120:
        return template.format('a minute')
    if seconds < 3600:
        return template.format(_pluralize('{:.0f} minute{}', seconds / 60))
    if seconds < 7200:
        return template.format('an hour')
    return template.format(_pluralize('{:.0f} hour{}', seconds / 3600))


def relativeDelta(td):
    s = ''
    days = abs(td.days)
    seconds = abs(td.seconds)
    if td.days < 0:
        seconds = 86400 - seconds
        t = "{} ago"
    else:
        t = "in {}"
    if days > 28:
        start = datetime.datetime.now()
        end = start + td
        months = (abs(end.year - start.year) * 12) + (end.month - start.month)
    if days == 0:
        s = _zeroDays(seconds, t)
    else:
        if days == 1:
            if td.days < 0:
                if seconds < 86400:
                    s = _zeroDays(seconds, t)
                else:
                    s = 'yesterday'
            else:
                s = 'tomorrow'
        elif days < 7:
            s = t.format(_pluralize('{:.0f} day{}', days))
        elif days < 31:
            s = t.format(_pluralize('{:.0f} week{}', days / 7))
        elif days < 365:
            s = t.format(_pluralize('{:.0f} month{}', months))
        else:
            s = t.format(_pluralize('{:.0f} year{}', months / 12))
    return s
