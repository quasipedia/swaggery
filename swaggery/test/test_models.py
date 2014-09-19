'''Test suite for the models module.'''

import inspect
import unittest

from .. import models as mm


class TestBaseClass(unittest.TestCase):

    '''Test the Model base class' methods.'''

    classes = [c for n, c in inspect.getmembers(mm, inspect.isclass)
               if issubclass(c, mm.Model)]

    def test_name_native(self):
        '''A native model's name is its native JSON schema keyword'''
        for cls in self.classes:
            if cls.native:
                self.assertEqual(cls.native, cls.name)

    def test_name_non_native(self):
        '''A non-native model's name is its class name.'''
        for cls in self.classes:
            if not cls.native:
                self.assertEqual(cls.__name__, cls.name)

    def test_schema_native(self):
        '''Trying to get the schema of a native model raises an exception.'''
        for cls in self.classes:
            if cls.native:
                with self.assertRaises(RuntimeError):
                    cls.model

    def test_schema_non_native(self):
        '''It is possible to retrieve the model/schema of non-native models.'''
        for cls in self.classes:
            if not cls.native:
                self.assertEqual(1, len(cls.model))
                self.assertEqual(dict, type(cls.model))

    def test_description(self):
        '''Instantiated models have a description.'''
        test_string = 'Random description.'
        for cls in self.classes:
            instance = cls(test_string)
            self.assertEqual(test_string, instance.description)
