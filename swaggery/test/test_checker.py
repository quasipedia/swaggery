'''Tests for the checker module.'''

import os
import unittest
import unittest.mock as mock

from . import troubles as trb
from .. import checker as ckr


class TestChecker(unittest.TestCase):

    '''Tests for the Checker abstract class.'''

    def test_collection(self):
        '''Methods starting with 'check_' are considered checks.'''
        dc = trb.DummyChecker()
        expected = {dc.check_dummy, dc.check_trouble_one, dc.check_trouble_two}
        self.assertEqual(expected, set(dc.checks))

    def test_running_all(self):
        '''Calling a checker object perform all checks, return error list.'''
        dc = trb.DummyChecker()
        expected = {
            'Trouble 1 detected.',
            'Trouble 2a detected.',
            'Trouble 2b detected.'}
        self.assertEqual(expected, set(dc(1, 2)))


class TestApiChecker(unittest.TestCase):

    '''Test the ApiChecker class.'''

    def test_ok(self):
        '''A perfect Api class passes all checks.'''
        ac = ckr.ApiChecker()
        self.assertFalse(ac(trb.ApiOk))

    def test_ko(self):
        '''A troublesome Api class raises all relevant messages.'''
        ac = ckr.ApiChecker()
        self.assertEqual(3, len(ac(trb.ApiKo)))


class TestResourceMethodChecker(unittest.TestCase):

    '''Test the ResourceMethodChecker class.'''

    def check(self, method_name):
        '''An helper function to keep syntax concise in tests.'''
        method = getattr(trb.ResourceWithKoMethods, method_name)
        return ckr.ResourceMethodChecker()(method)

    def assertSingleFailure(self, method_name):
        result = self.check(method_name)
        self.assertEqual(1, len(result))

    def test_ok(self):
        '''A perfect Resource method passes all checks.'''
        self.assertFalse(self.check('ok_method'))

    def test_missing_docstring(self):
        '''Resource methods without docstrings are illegal.'''
        self.assertSingleFailure('no_docstring')

    def test_return_type_exists(self):
        '''Resource methods without return types are illegal.'''
        self.assertSingleFailure('no_return_types')

    def test_return_type_types(self):
        '''Resource methods return types must be lists or tuples.'''
        self.assertSingleFailure('wrong_return_types')

    def test_return_type_formats(self):
        '''Length of Resource methods lists/tuples must be 2-3.'''
        self.assertSingleFailure('wrong_return_type_tuples')

    def test_respond_codes_undeclared(self):
        '''Returned codes must have been declared.'''
        self.assertSingleFailure('undeclared_codes')

    def test_respond_codes_unused(self):
        '''Declared codes must be used.'''
        self.assertSingleFailure('unused_codes')

    def test_respond_codes_mistmatching(self):
        '''Respond codes must match signature declaration.'''
        self.assertSingleFailure('mismatching_codes')

    def test_param_types_are_instances(self):
        '''Types in argument annotations are instances, not classes.'''
        self.assertSingleFailure('param_types_classes')

    def test_param_types_descend_from_model(self):
        '''Types in argument annotations descend from Model.'''
        self.assertSingleFailure('param_types_no_model')

    def test_return_types_are_classes(self):
        '''Types in return annotations are classes, not instances.'''
        self.assertSingleFailure('return_types_instances')

    def test_return_types_descend_from_model(self):
        '''Types in return annotations descend from Model.'''
        self.assertSingleFailure('return_types_no_model')

    def test_unique_body_variable(self):
        '''No more than one body variable can be declared.'''
        self.assertSingleFailure('multiple_bodies')

    def test_no_optional_path_parameters(self):
        '''Path parameters cannot be optional.'''
        self.assertSingleFailure('optional_path')

    def test_parameters_are_tuples(self):
        '''Parameters must be annotated with a tuple.'''
        self.assertSingleFailure('params_no_tuple')

    def test_parameters_is_ptype(self):
        '''Parameters first annoatation must be in Ptype.'''
        self.assertSingleFailure('params_no_ptype')


class TestResourceChecker(unittest.TestCase):

    '''Tests for the ResourceChecker class.'''

    checker = ckr.ResourceChecker()

    def test_consistent_path_ok(self):
        '''All paths in a Resource must be the same (Ok).'''
        checker = self.checker.check_path_consistency
        resource = trb.ResourceWithGoodPaths
        expected = []
        self.assertEqual(expected, checker(resource))

    def test_consistent_path_ko(self):
        '''All paths in a Resource must be the same (Ko).'''
        checker = self.checker.check_path_consistency
        resource = trb.ResourceWithConflictingPaths
        expected = ['Method "ResourceWithConflictingPaths.method_two" path '
                    'variables [\'foo\', \'spam\']) do not conform with the '
                    'resource subpath declaration (conflicting-paths/<foo>).']
        self.assertEqual(expected, checker(resource))

    def test_run_checks_on_methods(self):
        '''Checking a Resource will check all its methods too.'''
        resource = trb.ResourceWithGoodPaths
        expected = [((resource.method_one, ), ), ((resource.method_two, ), )]
        with mock.patch.object(ckr, 'ResourceMethodChecker') as mock_ckr:
            self.checker.check_methods(resource)
            actual = mock_ckr().call_args_list
            self.assertEqual(expected, actual)

    def test_no_multiple_handlers_ok(self):
        '''HTTP methods must appear only once per endpoint (Ok).'''
        checker = self.checker.check_no_multiple_handlers
        resource = trb.ResourceWithGoodPaths
        expected = []
        self.assertEqual(expected, checker(resource))

    def test_no_multiple_handlers_ko(self):
        '''HTTP methods must appear only once per endpoint (Ko).'''
        checker = self.checker.check_no_multiple_handlers
        resource = trb.ResourceWithConflictingPaths
        expected = ['HTTP verb "POST" associated to more than one endpoint '
                    'in "ResourceWithConflictingPaths".']
        self.assertEqual(expected, checker(resource))


class TestMain(unittest.TestCase):

    '''Tests for the main() function.'''

    base_dir = os.path.dirname(__file__)

    def get_dir(self, subdir):
        '''Helper function that returns the real path relative to this file.'''
        path = os.path.join(self.base_dir, subdir)
        return os.path.realpath(path)

    def test_ok(self):
        '''Testing a module with a correctly coded API bears no result.'''
        self.assertEqual([], ckr.main([self.get_dir('../../examples/async')]))

    def test_ko(self):
        '''Testing a module with code errors bears a list of them.'''
        expected = {
            'Missing return types for method "endpoint_b"',
            'Method endpoint_c returns undeclared codes: {404}.',
            'HTTP verb "GET" associated to more than one endpoint in '
            '"ResourceA".'}
        self.assertEqual(expected, set(ckr.main([self.get_dir('bogusapi')])))
