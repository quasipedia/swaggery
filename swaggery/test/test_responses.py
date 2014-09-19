'''Test suite for the responses module.'''

import json
import unittest

import unittest.mock as mock
from werkzeug.exceptions import InternalServerError, BadRequest

from ..responses import AsyncResponse, BadResponse, GoodResponse, HEADERS
from .. import responses


class TestAsync(unittest.TestCase):

    '''Test the Asyncronous response abstract class.'''

    def test_init(self):
        '''Payload is jsonified at instantiation, if it is not a generator.'''
        data = {'foo': 'bar'}
        r = AsyncResponse(data)
        self.assertEqual(data, json.loads(r.data.decode()))

    def test_stream_array(self):
        '''A generator payload's outcome, is an array of jsonified objects.'''
        data = (letter for letter in 'SPAM')
        r = AsyncResponse(data)
        expected = b'["S",\n"P",\n"A",\n"M"]'
        start_response = mock.MagicMock
        self.assertEqual(expected, b''.join(r.async(None, start_response)))

    def test_stream_empty_array(self):
        '''An empty generator payload's outcome, is a json empty array.'''
        data = (letter for letter in '')
        r = AsyncResponse(data)
        expected = b'[]'
        start_response = mock.MagicMock
        self.assertEqual(expected, b''.join(r.async(None, start_response)))

    def test_async_objects(self):
        '''A single-object response iterate once.'''
        data = {'foo': 'bar'}
        r = AsyncResponse(data)
        start_response = mock.MagicMock
        for n, bit in enumerate(r.async(None, start_response)):
            pass
        self.assertEqual(0, n)

    def test_async_generators(self):
        '''A generator response iterate several times.'''
        data = (letter for letter in 'SPAM')
        r = AsyncResponse(data)
        start_response = mock.MagicMock
        for n, bit in enumerate(r.async(None, start_response)):
            pass
        self.assertGreater(n, 1)


class TestBad(unittest.TestCase):

    '''Test the BadRespsonse class.'''

    def test_500(self):
        '''HTTP 500 responses get special logging.'''
        exception = InternalServerError('SPAM')
        # When python 3.4 is out this should be changed to self.assertLogs
        with mock.patch.object(responses, 'log') as lg:
            # This silly try/raise/except is due to the fact that log.exception
            # requires an exception context that is created only when the
            # exception is actually raised (not simply instantiated)
            try:
                raise exception
            except InternalServerError:
                BadResponse(mock.MagicMock(), exception)
        self.assertEqual(2, lg.error.call_count)
        self.assertEqual(1, lg.exception.call_count)

    def test_others(self):
        '''HTTP (non 500) bad resoponses get logged.'''
        exception = BadRequest('SPAM')
        # When python 3.4 is out this should be changed to self.assertLogs
        with mock.patch.object(responses, 'log') as lg:
            # This silly try/raise/except is due to the fact that log.exception
            # requires an exception context that is created only when the
            # exception is actually raised (not simply instantiated)
            try:
                raise exception
            except BadRequest:
                BadResponse(mock.MagicMock(), exception)
        self.assertEqual(1, lg.info.call_count)

    def test_headers(self):
        '''A bad response has the headers properly set.'''
        request = mock.MagicMock()
        exception = BadRequest('SPAM')
        r = BadResponse(request, exception)
        for header in HEADERS:
            self.assertIn(header, list(r.headers))


class TestGood(unittest.TestCase):

    '''Test the GoodResponse class.'''

    def test_headers(self):
        '''A good response has the headers properly set.'''
        r = GoodResponse(None, mock.MagicMock(status=200, payload=None))
        for header in HEADERS:
            self.assertIn(header, list(r.headers))
