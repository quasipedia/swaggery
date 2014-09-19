'''Test suite for the flowcontrol module.'''

import unittest

from ..flowcontrol import Respond


class TestRespond(unittest.TestCase):

    '''Test the Win exception.'''

    def test_raise(self):
        '''Instantiating a Win exception also raises it.'''
        with self.assertRaises(Respond):
            Respond(200, 'Dummy Payload')

    def test_arguments_full(self):
        '''A payload is saved in the Respond exception, if given.'''
        try:
            Respond(200, 'Dummy Payload')
        except Respond as e:
            self.assertEqual('Dummy Payload', e.payload)

    def test_arguments_no_payload(self):
        '''Payload is set to None in the Respond exception, if not given.'''
        try:
            Respond(200)
        except Respond as e:
            self.assertIsNone(e.payload)
