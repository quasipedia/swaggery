'''Test suite for the introspection module.'''

import os
import json
import unittest
import unittest.mock as mock

from werkzeug.exceptions import NotFound

from .. import introspection as ii
from ...testlib import call_endpoint


class TestModels(unittest.TestCase):

    '''Test that Models are properly populated.'''

    def test_resource_listing_model(self):
        '''ResourceListingModel is properly populated.'''
        self.assertTrue(hasattr(ii.ResourceListingModel, 'schema'))
        for key in ('type', 'properties', 'required'):
            self.assertIn(key, ii.ResourceListingModel.schema)

    def test_api_declaration_model(self):
        '''ApiDeclarationModel is properly populated.'''
        self.assertTrue(hasattr(ii.ApiDeclarationModel, 'schema'))
        for key in ('type', 'properties', 'required'):
            self.assertIn(key, ii.ApiDeclarationModel.schema)


class TestResourceListing(unittest.TestCase):

    '''Test the ResourceListing class.'''

    def test_collect_fragmets(self):
        '''ResourceListing collects fragments from each API.'''
        with mock.patch.object(ii.Introspection, 'get_swagger_fragment') as g:
            call_endpoint(ii.ResourceListing.resource_listing)
        # This test needs to be outside the assertRaises clause, or it will
        # never run!!!
        self.assertEqual(1, g.call_count)


class TestApiDeclaration(unittest.TestCase):

    '''Test the ApiDeclaration class.'''

    def test_extract_models(self):
        '''It is possible to extract all used models from API declaration.'''
        __dir = os.path.dirname(__file__)
        with open(os.path.join(__dir, 'introspect.json')) as file_:
            apis = json.load(file_)['apis']
        expected = {'ResourceListingModel', 'ApiDeclarationModel'}
        models = set([list(a.keys())[0]
                      for a in ii.ApiDeclaration._extract_models(apis)])
        self.assertEquals(expected, models)

    def test_api_declaration_fail_404(self):
        '''Api declaration raises 404 if the resource is invalid.'''
        with self.assertRaises(NotFound):
            call_endpoint(ii.ApiDeclaration.api_declaration, api_path='spam')

    def test_api_declaration_caches(self):
        '''Api declaration caches its results.'''
        expected = call_endpoint(ii.ApiDeclaration.api_declaration,
                                 api_path='introspect')
        actual = ii.ApiDeclaration._ApiDeclaration__cache['introspect']
        self.assertEqual(actual, expected)
        # This line does not serve any other purpose than retrieving the cache
        # once, so that the coverage stats will include that return stmt too...
        call_endpoint(ii.ApiDeclaration.api_declaration, api_path='introspect')

    def test_api_declaration_keys(self):
        '''An API declaration has the minimum compulsory set of items.'''
        min_set = {
            'apiVersion',
            'swaggerVersion',
            'basePath',
            'resourcePath',
            'apis',
            'models',
            'consumes',
            'produces'}
        actual_set = set(call_endpoint(
            ii.ApiDeclaration.api_declaration, api_path='introspect').keys())
        self.assertTrue(min_set.issubset(actual_set))
