'''Dummy functions to be used for testing.'''

from ..utils import RegisterLeafClasses
from ..keywords import *


# #############################################################################
# SWAGGER CALLING
# #############################################################################

class SwaggeryCallingResource(object):

    @operations('GET')
    def test(cls, request, exception_class, status) -> [
            (200, "OK", Void),
            (404, "KO", Void)]:
        def generator():
            yield
            if status == 200:
                exception_class(status, 'Payload')
            raise exception_class(status)
        return generator()


# #############################################################################
# OPERATIONS TESTING
# #############################################################################

class OperationsClass(object):

    def foo(cls, bar: 'bar') -> [(404, "KO", Void)]:
        '''BDFL'''
        Respond(404)


# #############################################################################
# API TESTING
# #############################################################################

class DummyAPI(Api):

    '''This should be the description.

    This should be eliminated.'''

    path = 'dummyapi'


# #############################################################################
# RESOURCE TESTING
# #############################################################################

class DummyResource(Resource):

    '''A dummy resource.

    Very interesting notes.'''

    api = DummyAPI
    subpath = 'dummyres/<param>'

    @operations('GET')
    def get_verb(cls, request,
                 param: (Ptypes.path, Void)) -> [(200, 'Ok', Void)]:
        '''A dummy GET endpoint.

        Notes to the dummy endpoint.'''
        Respond(200, 'GET Success!')

    @operations('POST')
    def post_verb(cls, request,
                 param: (Ptypes.path, Void)) -> [(200, 'Ok', Void)]:
        '''A dummy POST endpoint.

        Notes to the dummy endpoint.'''
        Respond(200, 'POST Success!')

    @classmethod
    def i_am_not_an_endpoint():
        pass


# #############################################################################
# SIGNATURE PARSING
# #############################################################################


def annotated_return() -> [
        (200, 'Message', String),
        (418, 'I tea', Integer)]:
    pass


def path_var_function(
        noise,
        more_noise,
        still_noise: (Ptypes.body, String('Nothing so see here')),
        compulsory_value: (Ptypes.path, String('foo')),
        another_compulsory_value: (Ptypes.path, String('BDFL')),
        optional_value: (Ptypes.path, String('bar'))='spam',
        extra_noise: (Ptypes.header, Integer('just noise...'))='ignore me'):
    pass


def docstring_function():
    '''Summary.

    First Line
    Second Line.'''


def docstring_function_no_notes():
    '''Summary.'''


# #############################################################################
# METACLASSES
# #############################################################################

class SelfRegistering(object, metaclass=RegisterLeafClasses):

    pass


class NonLeaf(SelfRegistering):

    pass


class LeafOne(NonLeaf):

    pass


class LeafTwo(NonLeaf):

    pass


class SillyModel(Model):

    schema = {}


# #############################################################################
# INJECTION
# #############################################################################

def path_func(
        noise, more_noise,
        var_one: (Ptypes.path, String('Variable one')),
        var_two: (Ptypes.path, String('Variable two'))) -> [
            (200, 'Ok', Void)
        ]:
    pass


def query_func(
        noise, more_noise,
        var_one: (Ptypes.query, String('Variable one')),
        var_two: (Ptypes.query, String('Variable two'))) -> [
            (200, 'Ok', Void)
        ]:
    pass


def body_func(
        noise, more_noise,
        var_one: (Ptypes.body, String('Variable one'))) -> [
            (200, 'Ok', Void)
        ]:
    pass


def header_func(
        noise, more_noise,
        var_one: (Ptypes.header, String('Token one')),
        var_two: (Ptypes.header, String('Token two'))) -> [
            (200, 'Ok', Void)
        ]:
    pass


def form_func(
        noise, more_noise,
        var_one: (Ptypes.form, String('Name of something')),
        var_two: (Ptypes.form, String('Value of something'))) -> [
            (200, 'Ok', Void)
        ]:
    pass
