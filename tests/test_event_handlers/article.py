# -*- coding: utf-8 -*-
"""
:copyright: (c) 2012-2020 by Mike Taylor
:license: CC0 1.0 Universal, see LICENSE for more details.

Test Event Handler
"""

test_results = {
    'post': None
}


def setup():
    pass


def post(postURL):
    test_results['post'] = postURL
