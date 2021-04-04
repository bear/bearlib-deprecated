# -*- coding: utf-8 -*-
"""
:copyright: (c) 2012-2020 by Mike Taylor
:license: CC0 1.0 Universal, see LICENSE for more details.
"""

import os
import datetime
import tempfile
from bearlib.tools import normalizeFilename, relativeDelta, baseDomain
from bearlib.tools import pidWrite, pidRead, pidClear, isRunning


def test_normalize():
    cwd   = os.getcwd()
    home  = os.environ['HOME']

    assert normalizeFilename('foo.txt')   == os.path.join(cwd,  'foo.txt')
    assert normalizeFilename('~/foo.txt') == os.path.join(home, 'foo.txt')
    assert normalizeFilename('./foo.txt') == os.path.join(cwd,  'foo.txt')


def test_relativeDelta():
    assert relativeDelta(datetime.timedelta(0,   10))  == 'just now'
    assert relativeDelta(datetime.timedelta(0,   50))  == 'in 50 seconds'
    assert relativeDelta(datetime.timedelta(0,  100))  == 'in a minute'
    assert relativeDelta(datetime.timedelta(0, 3000))  == 'in 50 minutes'
    assert relativeDelta(datetime.timedelta(0, 7000))  == 'in an hour'
    assert relativeDelta(datetime.timedelta(0, 8000))  == 'in 2 hours'

    assert relativeDelta(datetime.timedelta(0,   -50)) == '50 seconds ago'
    assert relativeDelta(datetime.timedelta(0,  -100)) == 'a minute ago'
    assert relativeDelta(datetime.timedelta(0, -3000)) == '50 minutes ago'
    assert relativeDelta(datetime.timedelta(0, -7000)) == 'an hour ago'
    assert relativeDelta(datetime.timedelta(0, -8000)) == '2 hours ago'

    assert relativeDelta(datetime.timedelta(1))        == 'tomorrow'
    assert relativeDelta(datetime.timedelta(-1))       == 'yesterday'
    assert relativeDelta(datetime.timedelta(2))        == 'in 2 days'
    assert relativeDelta(datetime.timedelta(8))        == 'in 1 week'
    assert relativeDelta(datetime.timedelta(15))       == 'in 2 weeks'
    assert relativeDelta(datetime.timedelta(40))       == 'in 1 month'
    assert relativeDelta(datetime.timedelta(120))      == 'in 4 months'
    assert relativeDelta(datetime.timedelta(360))      == 'in 11 months'
    assert relativeDelta(datetime.timedelta(370))      == 'in 1 year'


def test_baseDomain():
    urls = [
        "http://bear.im",
        "http://bear.im/bearlog",
        "http://bear.im/bearlog?param=value",
    ]

    for url in urls:
        assert baseDomain(url)                       == "http://bear.im"
        assert baseDomain(url, includeScheme=False)  == "bear.im"
    assert baseDomain("bear.im/bearlog") == "bear.im/bearlog"


def test_pid_routines():
    try:
        pidfilename = tempfile.mkstemp()[1]
        pid = os.getpid()

        pidWrite(pidfilename)
        assert pidRead(pidfilename)       == pid
        assert pidRead('fake/pid/file')   == -1
        assert isRunning('fake/pid/file') is False

        # because we are using the pid of the testing process
        # pidClear() should not do anything as the process is active
        pidClear(pidfilename)
        assert os.path.exists(pidfilename)
    finally:
        os.remove(pidfilename)
