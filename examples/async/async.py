'''A demo designed to showcase the concurrent capabilities of Swaggery.'''

from uuid import uuid4
from random import randint

from swaggery.keywords import *

MAX_LOOP_DURATION = 50  # Set the max CPU-bound delay for all the endpoints


# #############################################################################
# MODELS
# #############################################################################

class FibonacciFragment(Model):

    '''A fragment of the Fibonacci series.'''

    schema = {
        'type': 'array',
        'items': {'type': 'integer'}
    }


# #############################################################################
# API(s)
# #############################################################################

class Async(Api):

    '''A concurrent demo API.'''

    version = '1.0.0'
    path = 'async'


# #############################################################################
# ENDPOINTS
# #############################################################################

class AlwaysWin(Resource):

    '''Async endpoint that should work.'''

    api = Async
    subpath = 'always-ok'

    @operations('GET')
    def always_win(cls, request) -> [(200, 'Ok', String)]:
        '''Perform an always succeeding task.'''
        task_id = uuid4().hex.upper()[:5]
        log.info('Starting always OK task {}'.format(task_id))
        for i in range(randint(0, MAX_LOOP_DURATION)):
            yield
        log.info('Finished always OK task {}'.format(task_id))
        msg = 'I am finally done with task {}!'.format(task_id)
        Respond(200, msg)


class AlwaysFail(Resource):

    '''Async endpoint that should return Error messages.'''

    api = Async
    subpath = 'always-ko'

    @operations('GET')
    def always_fail(cls, request) -> [
            (200, 'Ok', String),
            (406, 'Not Acceptable', Void)]:
        '''Perform an always failing task.'''
        task_id = uuid4().hex.upper()[:5]
        log.info('Starting always FAILING task {}'.format(task_id))
        for i in range(randint(0, MAX_LOOP_DURATION)):
            yield
        Respond(406)
        Respond(200, 'Foobar')


class AlwaysCrash(Resource):

    '''Async endpoint that should crash while running.'''

    api = Async
    subpath = 'always-crash'

    @operations('GET')
    def always_crash(cls, request) -> [(200, 'Ok', String)]:
        '''Perform an always crashing task.'''
        task_id = uuid4().hex.upper()[:5]
        log.info('Starting always CRASHING task {}'.format(task_id))
        for i in range(randint(0, MAX_LOOP_DURATION)):
            yield
        1 / 0
        Respond(200, 'Foobar')


class Fibonacci(Resource):

    '''A deliberatly slow Fibonacci generator: showcase streaming replies.'''

    api = Async
    subpath = 'fibonacci/<limit>'

    @operations('GET')
    def fibonacci(cls, request,
                  limit: (Ptypes.path,
                          Integer('Upper limit of the series'))) -> [
            (200, 'Ok', FibonacciFragment)]:
        '''Return Fibonacci sequence whose last number is <= limit.'''
        def fibonacci_generator():
            last_two = (0, 1)
            while last_two[1] <= limit:
                log.debug('Fibonacci number generated: {}'.format(last_two[1]))
                yield last_two[1]
                last_two = last_two[1], sum(last_two)
        log.info('Starting Fibonacci generation, max: {}'.format(limit))
        limit = int(limit)
        Respond(200, fibonacci_generator())


class QueryEcho(Resource):

    '''Async endpoint echoing the query parameters.'''

    api = Async
    subpath = 'query-echo'

    @operations('GET')
    def query_echo(cls, request,
                   foo: (Ptypes.query, String('A query parameter'))) -> [
            (200, 'Ok', String)]:
        '''Echo the query parameter.'''
        log.info('Echoing query param, value is: {}'.format(foo))
        for i in range(randint(0, MAX_LOOP_DURATION)):
            yield
        msg = 'The value sent was: {}'.format(foo)
        Respond(200, msg)


class BodyEcho(Resource):

    '''Async endpoint echoing the body parameter.'''

    api = Async
    subpath = 'body-echo'

    @operations('POST')
    def body_echo(cls, request,
                  foo: (Ptypes.body, String('A body parameter'))) -> [
            (200, 'Ok', String)]:
        '''Echo the body parameter.'''
        log.info('Echoing body param, value is: {}'.format(foo))
        for i in range(randint(0, MAX_LOOP_DURATION)):
            yield
        msg = 'The value sent was: {}'.format(foo)
        Respond(200, msg)


class HeaderEcho(Resource):

    '''Async endpoint echoing the header parameters.'''

    api = Async
    subpath = 'header-echo'

    @operations('GET')
    def header_echo(cls, request,
                    api_key: (Ptypes.header, String('API key'))) -> [
            (200, 'Ok', String)]:
        '''Echo the header parameter.'''
        log.info('Echoing header param, value is: {}'.format(api_key))
        for i in range(randint(0, MAX_LOOP_DURATION)):
            yield
        msg = 'The value sent was: {}'.format(api_key)
        Respond(200, msg)


class FormEcho(Resource):

    '''Async endpoint echoing the form parameters.'''

    api = Async
    subpath = 'form-echo'

    @operations('POST')
    def form_echo(cls, request,
                  foo: (Ptypes.form, String('A form parameter'))) -> [
            (200, 'Ok', String)]:
        '''Echo the form parameter.'''
        log.info('Echoing form param, value is: {}'.format(foo))
        for i in range(randint(0, MAX_LOOP_DURATION)):
            yield
        msg = 'The value sent was: {}'.format(foo)
        Respond(200, msg)
