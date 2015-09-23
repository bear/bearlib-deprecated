#!/usr/bin/env python

import os
import datetime
import unittest

from bearlib.tools import normalizeFilename, relativeDelta


class TestNormalize(unittest.TestCase):
    def runTest(self):
        cwd   = os.getcwd()
        home  = os.environ['HOME']

        assert normalizeFilename('foo.txt')   == os.path.join(cwd,  'foo.txt')
        assert normalizeFilename('~/foo.txt') == os.path.join(home, 'foo.txt')
        assert normalizeFilename('./foo.txt') == os.path.join(cwd,  'foo.txt')

class TestRelativeDelta(unittest.TestCase):
    def runTest(self):
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
        assert relativeDelta(datetime.timedelta(2))        == 'in 2 days'
        assert relativeDelta(datetime.timedelta(8))        == 'in 1 weeks'
        assert relativeDelta(datetime.timedelta(40))       == 'in 1 months'
