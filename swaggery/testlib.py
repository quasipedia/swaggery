'''Utilities to facilitate testing of Swaggery APIs.'''

from inspect import isgenerator
import unittest.mock as mock

from .flowcontrol import Respond


def call_endpoint(endpoint, request=None, start_response=None, **kwargs):
    '''Call an endpoint as if it were a regular function.

    Notably, this utility function:
    - Creates arguments required by the wrapper "on the fly" (unless passed).
    - Intercept the Win exception and extract the data from it.
    - Return an object or a list of objects, rather than a generator.
    '''
    request = request or mock.MagicMock()
    start_response = start_response or mock.MagicMock()
    try:
        list(endpoint(request, start_response, **kwargs))
    except Respond as e:
        pl = e.payload
        if isgenerator(pl):
            return list(pl)
        return pl
