'''An API collection with coding mistakes.

This module is used by the test_checker one to verify coding errors are
detected correctly.  It also contains non-Api non-Resources classes to test
the checking infrastracture per se.
'''

from ..keywords import *
from ..checker import Checker


class DummyChecker(Checker):

    '''A dummy checker used to unit-test the Checker class itself.'''

    def check_dummy(self, foo, bar):
        pass

    def check_trouble_one(self, foo, bar):
        return ['Trouble 1 detected.']

    def check_trouble_two(self, foo, bar):
        return ['Trouble 2a detected.', 'Trouble 2b detected.']

    def this_is_a_non_check_method(self):
        pass


class ApiOk(object):

    '''An API.'''

    version = '1.0.0'
    path = 'apiok'


class ApiKo(object):

    pass


class NotAModel(object):

    def __init__(self, msg):
        pass


class ResourceWithKoMethods(object):

    '''A Resources class whose methods are bogus.'''

    api = ApiOk
    subpath = 'methods-ko'

    @operations('POST')
    def no_docstring(
        cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 'Ok', Void),
            (404, 'Not Found', Void)]:
        if False:
            Respond(404)
        Respond(200, 'GET Success!')

    @operations('POST')
    def no_return_types(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))):
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'GET Success!')

    @operations('POST')
    def wrong_return_types(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> String:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'GET Success!')

    @operations('POST')
    def wrong_return_type_tuples(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 204, 'Ok', Void),
            (404, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'GET Success!')

    @operations('POST')
    def undeclared_codes(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (404, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'GET Success!')

    @operations('POST')
    def unused_codes(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 'Ok', Void),
            (400, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(400)

    @operations('POST')
    def mismatching_codes(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 'Ok', Void),
            (404, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(400)
        Respond(202)

    @operations('POST')
    def param_types_classes(
            cls, request,
            foo: (Ptypes.path, String),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 'Ok', Void),
            (404, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'GET Success!')

    @operations('POST')
    def return_types_instances(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 'Ok', Void),
            (404, 'Not Found', String('The result'))]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'GET Success!')

    @operations('POST')
    def multiple_bodies(
            cls, request,
            foo: (Ptypes.body, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 'Ok', Void),
            (404, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'GET Success!')

    @operations('POST')
    def optional_path(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.path, String('A parameter'))='spam') -> [
            (200, 'Ok', Void),
            (404, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'GET Success!')

    @operations('POST')
    def param_types_no_model(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, NotAModel('A parameter'))) -> [
            (200, 'Ok', Void),
            (404, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'GET Success!')

    @operations('POST')
    def return_types_no_model(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 'Ok', Void),
            (404, 'Not Found', NotAModel)]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'GET Success!')

    @operations('POST')
    def params_no_tuple(
            cls, request,
            foo: 'A parameter',
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 'Ok', Void),
            (404, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'GET Success!')

    @operations('POST')
    def params_no_ptype(
            cls, request,
            foo: ('Type: path', String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 'Ok', Void),
            (404, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'GET Success!')

    @operations('POST')
    def ok_method(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 'Ok', Void),
            (404, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'GET Success!')


class ResourceWithConflictingPaths(Resource):

    '''A Resources class whose methods are bogus.'''

    api = ApiOk
    subpath = 'conflicting-paths/<foo>'

    @operations('POST')
    def method_one(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 'Ok', Void),
            (404, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'POST Success!')

    @operations('POST')
    def method_two(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            spam: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 'Ok', Void),
            (404, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'POST Success!')


class ResourceWithGoodPaths(Resource):

    '''A Resources class whose methods are bogus.'''

    api = ApiOk
    subpath = 'good-paths/<foo>'

    @operations('GET')
    def method_one(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 'Ok', Void),
            (404, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'GET Success!')

    @operations('POST')
    def method_two(
            cls, request,
            foo: (Ptypes.path, String('A parameter')),
            bar: (Ptypes.body, String('A parameter'))) -> [
            (200, 'Ok', Void),
            (404, 'Not Found', Void)]:
        '''<placeholder>'''
        if False:
            Respond(404)
        Respond(200, 'POST Success!')
