"""Test Event Handler
"""

test_results = { 'post': None
               }

def setup():
    pass

def post(postURL):
    test_results['post'] = postURL
