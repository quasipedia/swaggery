'''A bougus API used for testing the checker functionality.'''

from swaggery.keywords import *


# #############################################################################
# API(s)
# #############################################################################

class BogusApi(Api):

    '''A concurrent demo API.'''

    version = '1.0.0'
    path = 'bogus'


# #############################################################################
# ENDPOINTS
# #############################################################################

class ResourceA(Resource):

    '''Async endpoint that should work.'''

    api = BogusApi
    subpath = None

    @operations('GET')
    def endpoint_a(cls, request) -> [(200, 'Ok', String)]:
        '''Perform an always succeeding task.'''
        Respond(200, msg)

    @operations('GET')
    def endpoint_b(cls, request):
        '''Perform an always succeeding task.'''
        Respond(200, msg)

    @operations('POST')
    def endpoint_c(
            cls, request, foo: (Ptypes.path, Void('No result'))) -> [
            (200, 'Ok', String)]:
        '''Perform an always succeeding task.'''
        Respond(404)
        Respond(200, msg)
