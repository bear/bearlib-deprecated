# -*- coding: utf-8 -*-
"""
:copyright: (c) 2012-2016 by Mike Taylor
:license: CC0 1.0 Universal, see LICENSE for more details.
"""

from bearlib.events import Events


post_url  = "https://bear.im/bearlog/2013/325/indiewebify-and-the-new-site.html"

def test_event_handlers():
    event = Events("./tests/test_event_handlers")

    assert event is not None
    assert len(event.handlers) > 0
    assert 'article' in event.handlers

class test_event_handler_call():
    event = Events("./tests/test_event_handlers")

    event.handle('article', 'post', post_url)
    assert event.handlers['article'].test_results['post'] == post_url
