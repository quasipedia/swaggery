'''Test suite for the application module.'''

import os
import json
import unittest
import unittest.mock as mock

from .. import application as app
from ..flowcontrol import Respond
from .dummymodule import SwaggeryCallingResource


THIS_DIR = os.path.dirname(__file__)
ASYNC_API_DIR = os.path.realpath(
    os.path.join(THIS_DIR, '..', '..', 'examples', 'async'))


class TestSwaggeryMethods(unittest.TestCase):

    '''Test the Swaggery class' regular methods.'''

    @mock.patch.object(app.Swaggery, '_mount_resources', mock.MagicMock())
    def test_register_resources(self):
        '''Registering resources equals importing their modules.'''
        with mock.patch.object(app, 'import_module') as mock_import:
            app.Swaggery([ASYNC_API_DIR])
            mock_import.assert_called_once_with('async')

    def test_mount_resources(self):
        '''Mounting builds the route mapping and register with werzeug.'''
        with mock.patch.object(app, 'Map') as mock_map:
            instance = app.Swaggery([ASYNC_API_DIR])
            registered_keys = len([k for k in instance.callback_map.keys()
                                   if k.startswith('Async')])
            self.assertLess(7, registered_keys)
            self.assertEqual(1, mock_map.call_count)

    @mock.patch.object(app.Swaggery, '_register_resources', mock.MagicMock())
    @mock.patch.object(app.Swaggery, '_mount_resources', mock.MagicMock())
    def test_get_coroutine(self):
        '''URL is routed to a coroutine that gets initialised too.'''
        application = app.Swaggery(['spam'], False)
        # Test objects
        mock_cb = mock.MagicMock()
        mock_url_map = mock.MagicMock()
        mock_environ = mock.MagicMock()
        mock_start_response = mock.MagicMock()
        kwargs = {}
        # Behaviorus
        mock_url_map.bind_to_environ().match.return_value = ('foo', kwargs)
        application.url_map = mock_url_map
        application.callback_map = {'foo': mock_cb}
        # Tests
        with mock.patch.object(app, 'inject_extra_args') as mock_inject:
            application._get_coroutine(mock_environ, mock_start_response)
        mock_inject.assert_called_once_with(mock_cb, mock_environ, kwargs)
        mock_cb.assert_called_once_with(mock_environ, mock_start_response)


class TestSwaggeryCalling(unittest.TestCase):

    '''Test the Swaggery class' __call__ method.'''

    @mock.patch.object(app, 'Request', mock.MagicMock())
    @mock.patch.object(app.Swaggery, '_register_resources', mock.MagicMock())
    @mock.patch.object(app.Swaggery, '_mount_resources', mock.MagicMock())
    @mock.patch.object(app.Swaggery, '_get_coroutine')
    def _run_test_call(self, exception_class, status, tester, mock_getco):
        '''Helper function to run a call mocking the hell out of it.'''
        mock_getco.return_value = SwaggeryCallingResource.test(
            mock.MagicMock(),
            mock.MagicMock(),
            exception_class=exception_class,
            status=status)
        application = app.Swaggery(['spam'], False)(None, mock.MagicMock())
        while True:
            value = next(application)
            if value:
                tester(value)
                break

    def test_call_win(self):
        '''Calling the application can yield a valid Win response.'''
        expected = 'Payload'
        tester = lambda v: self.assertEqual(expected, json.loads(v.decode()))
        self._run_test_call(Respond, 200, tester)

    def test_call_fail(self):
        '''Calling the application can yield a valid Fail response.'''
        expected = {'code': 404, 'message': 'KO'}
        tester = lambda v: self.assertEqual(expected, json.loads(v.decode()))
        self._run_test_call(Respond, 404, tester)

    def test_call_ok(self):
        '''Calling the application can yield a valid Crash response.'''
        tester = lambda v: v.startswith(b'Internal server error: 500.')
        self._run_test_call(RuntimeError, None, tester)
