#!/usr/bin/env python

import os, sys
import unittest

from bearlib.events import Events


post_url  = "https://bear.im/bearlog/2013/325/indiewebify-and-the-new-site.html"

class TestEventConfig(unittest.TestCase):
    def runTest(self):
        event = Events("./tests/test_event_handlers")

        assert event is not None
        assert len(event.handlers) > 0
        assert 'article' in event.handlers

class TestEventHandlerCalls(unittest.TestCase):
    def runTest(self):
        event = Events("./tests/test_event_handlers")

        event.handle('article', 'post', post_url)
        assert event.handlers['article'].test_results['post'] == post_url
