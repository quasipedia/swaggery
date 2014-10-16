'''Custom responses for specific error codes.'''

import uuid
import inspect
from werkzeug.wrappers import Response

from .logger import log
from .utils import jsonify


HEADERS = [
    ('Access-Control-Allow-Origin', '*'),
    ('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT, PATCH, OPTIONS'),
    ('Access-Control-Allow-Headers', 'Content-Type, api_key, Authorization'),
    ('Content-Type', 'application/json; charset=utf-8'),
]


class AsyncResponse(Response):

    '''Enhance the usual response to support async behaviour.'''

    def __init__(self, payload, *args, **kwargs):
        self.payload = payload
        if inspect.isgenerator(payload):
            super().__init__(payload, *args, direct_passthrough=True, **kwargs)
        else:
            super().__init__(jsonify(payload), *args, **kwargs)

    def stream_array(self, generator):
        '''Helper function to stream content as an array of JSON values.'''
        def chunkify(generator):
            log.debug('Data Stream STARTED')
            yield '['.encode()
            # In order to have commas only after the first value, we take the
            # first value of the generator manually
            try:
                yield jsonify(next(generator)).encode()
            except StopIteration:
                pass
            while True:
                try:
                    bit = next(generator)
                except StopIteration:
                    yield ']'.encode()
                    break
                else:
                    yield ',\n'.encode()
                    yield jsonify(bit).encode()
            log.debug('Data Stream ENDED')
        return chunkify(generator)

    def async(self, environ, start_response):
        start_response(self.status, list(self.headers))
        if inspect.isgenerator(self.payload):
            log.debug('Starting stream response')
            yield from self.stream_array(self.payload)
        else:
            log.debug('Starting monolithic response')
            # The use of self.data over self.payload is due to the need of
            # having an header with the correct lenght information.  A JSON
            # string, for example, has 2 characters '"' wrapping it...
            yield self.data


class BadResponse(AsyncResponse):

    '''Logs an exception and return an ad-hoc response.'''

    def __init__(self, request, exception):
        code = getattr(exception, 'code', 500)  # Default for code breakage
        if code == 500:
            payload = self.process_500(request, exception)
        else:
            msg = exception.description
            log.info('HTTP:{} --- {}'.format(code, msg))
            payload = {'code': code, 'message': msg}
        super().__init__(payload, status=code, headers=HEADERS)

    def process_500(self, request, exception):
        '''Internal server error.'''
        id_ = str(uuid.uuid4())[:6].upper()
        msg = 'Internal server error: 500. Unique error identifier is {}'
        msg = msg.format(id_)
        log.error('HTTP 500 [Message - {}]: {}'.format(id_, msg))
        log.error('HTTP 500 [Arguments - {}]: {}'.format(id_, request.args))
        log.exception('HTTP 500 [Traceback - {}]:'.format(id_))
        return msg


class GoodResponse(AsyncResponse):

    '''Linghtweight wrapper that inject headers and jsonify the output.'''

    def __init__(self, request, respond_exception):
        payload = respond_exception.payload
        status = respond_exception.status
        # TODO: What happens to e.description? See: http://goo.gl/YZ664K
        super().__init__(payload, status=status, headers=HEADERS)
