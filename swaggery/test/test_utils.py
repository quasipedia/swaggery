'''Test suite for the utils module.'''

import inspect
import unittest

from werkzeug.exceptions import HTTPException, ImATeapot
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from . import dummymodule as dummy
from .. import utils
from ..models import Model, Void


class Parameters(unittest.TestCase):

    '''Test the resource parameters logic.'''

    types = ('path', 'query', 'body', 'header', 'form')

    def test_existing(self):
        '''All argument types are defined in Ptypes.'''
        for type_ in self.types:
            if not hasattr(utils.Ptypes, type_):
                self.fail('Type {} does not exist!'.format(type_))

    def test_mapped(self):
        '''All argument types but 'path' are mapped to request attributes.'''
        for type_ in self.types:
            if type_ == 'path':
                continue
            type_ = getattr(utils.Ptypes, type_)
            try:
                utils.PTYPE_TO_REQUEST_PROPERTY[type_]
            except KeyError:
                self.fail('Type {} is not mapped!'.format(type_))

    def test_iterable(self):
        '''Ptypes is iterable.'''
        expected = {'path', 'query', 'body', 'header', 'form'}
        self.assertEqual(expected, set(utils.Ptypes))


class MetaClasses(unittest.TestCase):

    '''Test the self-registering class logic.'''

    def test_leaf_registration(self):
        '''Metaclasses register leafs.'''
        registry = dummy.NonLeaf
        self.assertIn(dummy.LeafOne, registry)
        self.assertIn(dummy.LeafTwo, registry)

    def test_skip_nodes(self):
        '''Metaclasses do not register non-leaf classes.'''
        registry = dummy.NonLeaf
        self.assertFalse(dummy.NonLeaf in registry)

    def test_iter(self):
        '''Metaclasses allow to iter over all registered leafs.'''
        expected = {dummy.LeafOne, dummy.LeafTwo}
        actual = set(list(dummy.NonLeaf))
        self.assertEqual(expected, actual)

    def test_string_representation_non_leaf(self):
        '''Non-leaf string representation is a message with the registry.'''
        expected = 'Registered classes of type NonLeaf: LeafOne, LeafTwo'
        self.assertEqual(expected, str(dummy.NonLeaf))

    def test_string_representation_leaf(self):
        '''Leaf string representation is the usual class name.'''
        expected = 'LeafOne'
        self.assertEqual(expected, str(dummy.LeafOne))

    def test_model_metaclass(self):
        '''Models'metaclass maps model names to classes.'''
        expected = dummy.SillyModel
        self.assertEqual(expected, Model.name_to_cls['SillyModel'])


class MapExceptions(unittest.TestCase):

    '''Tests the mapping of HTTP status code onto werkzeug classes.'''

    def test_mapping(self):
        '''Werkzeug HTTPExceptions are mapped correctly.'''
        mapping = utils.map_exception_codes()
        self.assertTrue(all(type(k) == int for k in mapping.keys()))
        self.assertTrue(
            all(isinstance(v, HTTPException)) for v in mapping.values())
        # Random check! :)
        self.assertEqual(mapping[418], ImATeapot)


class SignatureParsing(unittest.TestCase):

    '''Test the introspective logic based on method signatures / docstrings.'''

    def test_return_annotation(self):
        '''Return annotations are correctly parsed.'''
        expected = {
            200: {
                'responseModel': 'string',
                'message': 'Message',
                'code': 200},
            418: {
                'responseModel': 'integer',
                'message': 'I tea',
                'code': 418}}
        actual = utils.parse_return_annotation(dummy.annotated_return)
        self.assertEqual(expected, actual)

    def test_extract_pathvars(self):
        '''It is possible to extract path variables from annotations.'''
        func = dummy.path_var_function
        func.signature = inspect.signature(func)
        expected = {
            'optional': ['optional_value'],
            'mandatory': ['compulsory_value', 'another_compulsory_value']}
        actual = utils.extract_pathvars(func)
        self.assertEqual(expected, actual)

    def test_parse_docstring(self):
        '''It is possible to extract information from the docstring.'''
        expected = ('Summary.', ' First Line Second Line.')
        actual = utils.parse_docstring(dummy.docstring_function)
        self.assertEqual(expected, actual)

    def test_parse_docstring_no_notes(self):
        '''Resources can omit notes in their docstrings.'''
        expected = ('Summary.', '')
        actual = utils.parse_docstring(dummy.docstring_function_no_notes)
        self.assertEqual(expected, actual)


class InjectArgs(unittest.TestCase):

    '''Test the injection of extra arguments into the kwarg.'''

    def test_inject_path(self):
        '''Query arguments are not extracted from path (werkzeug does).'''
        builder = EnvironBuilder(path='/foo/bar')
        request = Request(builder.get_environ())
        expected = {}
        wkargs = {}
        utils.inject_extra_args(dummy.path_func, request, wkargs)
        self.assertEqual(expected, wkargs)

    def test_inject_query(self):
        '''Query arguments are extracted from the request and injected.'''
        builder = EnvironBuilder(path='/?var_one=foo&var_two=bar')
        request = Request(builder.get_environ())
        expected = {'var_one': 'foo', 'var_two': 'bar'}
        wkargs = {}
        utils.inject_extra_args(dummy.query_func, request, wkargs)
        self.assertEqual(expected, wkargs)

    def test_inject_body(self):
        '''Body argument is extracted from the request and injected.'''
        builder = EnvironBuilder(
            data='{"foo": "bar"}',
            method='POST',
            content_type='application/json')
        request = Request(builder.get_environ())
        expected = {'var_one': {'foo': 'bar'}}
        wkargs = {}
        utils.inject_extra_args(dummy.body_func, request, wkargs)
        self.assertEqual(expected, wkargs)

    def test_inject_form(self):
        '''Form arguments are extracted from the request and injected.'''
        builder = EnvironBuilder(
            data={'var_one': 'foo', 'var_two': 'bar'},
            method='POST')
        request = Request(builder.get_environ())
        expected = {'var_one': 'foo', 'var_two': 'bar'}
        wkargs = {}
        utils.inject_extra_args(dummy.form_func, request, wkargs)
        self.assertEqual(expected, wkargs)

    def test_inject_header(self):
        '''Header arguments are extracted from the request and injected.'''
        builder = EnvironBuilder(
            headers=[('Content-Type', 'application/json'),
                     ('var_one', 'foo'),
                     ('var_two', 'bar')])
        request = Request(builder.get_environ())
        expected = {'var_one': 'foo', 'var_two': 'bar'}
        wkargs = {}
        utils.inject_extra_args(dummy.header_func, request, wkargs)
        self.assertEqual(expected, wkargs)


class Jsonify(unittest.TestCase):

    '''Test the jsonify helper function.'''

    def test_return_expected(self):
        '''jsonify return a sorted, indented JSON representation.'''
        payload = {'aaa': 'foo', 'bar': 'spam', 'foobar': 'BDFL'}
        expected = ('{\n    "aaa": "foo", '
                    '\n    "bar": "spam", '
                    '\n    "foobar": "BDFL"\n}')
        self.assertEqual(expected, utils.jsonify(payload))


class FilterAnnotations(unittest.TestCase):

    '''Test the filter_annotations_by_ptype helper function.'''

    def test_that_match(self):
        '''It is possible to filter an annotation by it's Ptypes.'''
        function = dummy.DummyResource.get_verb
        expected = {'param': ('path', Void)}
        actual = utils.filter_annotations_by_ptype(function, utils.Ptypes.path)
        self.assertEqual(expected, actual)

    def test_that_no_match(self):
        '''It is possible to filter an annotation by it's Ptypes.'''
        function = dummy.DummyResource.get_verb
        expected = {}
        actual = utils.filter_annotations_by_ptype(function, utils.Ptypes.body)
        self.assertEqual(expected, actual)
