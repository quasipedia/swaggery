'''Test suite for the testlib module.'''

import unittest

from .. import testlib as tl
from ..api import operations
from ..flowcontrol import Respond


class DummyResource(object):

    @operations('GET', 'POST')
    def dummy_endpoint(cls, request, foo, bar, spam) -> [(200, 'Ok')]:
        Respond(200, foo + bar + spam)

    @operations('GET', 'POST')
    def dummy_generator_endpoint(
            cls, request, foo, bar, spam) -> [(200, 'Ok')]:
        Respond(200, (x for x in (foo, bar, spam)))


class TestFunctions(unittest.TestCase):

    '''Test a few random helper functions.'''

    def test_call_endpoint_objest(self):
        '''test_enpoint bypasses wrapper implementation details (object).'''
        kwargs = {'foo': 1, 'bar': 2, 'spam': 3}
        expected = 6
        actual = tl.call_endpoint(DummyResource.dummy_endpoint, **kwargs)
        self.assertEqual(expected, actual)

    def test_call_endpoint_generator(self):
        '''test_enpoint bypasses wrapper implementation details (generator).'''
        kwargs = {'foo': 1, 'bar': 2, 'spam': 3}
        expected = [1, 2, 3]
        actual = tl.call_endpoint(
            DummyResource.dummy_generator_endpoint, **kwargs)
        self.assertEqual(expected, actual)
