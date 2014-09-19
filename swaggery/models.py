'''A collection of Models (Data Structures) for the Swaggery framework.

The Model subclasses - differently than Api and Resource descendants - can be
instantiated in signature annotations.  This is such that each response can
hold an individual description of the returned data.

All the business logic is however delegated entirely to the class (precisely
as for Api and Resource classes).
'''

from .utils import RegisterLeafModels, classproperty


class Model(object, metaclass=RegisterLeafModels):

    '''Models describe the data structure which go through the interface.

    A Model class can either map a json-schema native data type (see: json-
    schema.org) or a custom one.

    Native datatypes are all defined in Swaggery, so the final user will never have
    to create new ones.

    Custom datatypes only need a class attribute (schema) defining their JSON
    schema.
    '''

    native = False
    schema = None

    def __init__(self, description):
        self._description = description

    @classproperty
    def name(cls):
        '''Return the name of the model as to be used in swagger.'''
        return cls.native or cls.__name__

    @classproperty
    def model(cls):
        '''Return the Model to be insertend in the swagger declaration.'''
        if cls.native:
            raise RuntimeError('Trying to get the model for a native type.')
        return {cls.__name__: cls.schema}

    @property
    def description(self):
        '''Return the textual description of the instance of the Model.'''
        return self._description


# ############################# #
# NATIVE JSON-SCHEMA DATA TYPES #
# ############################# #


class Void(Model):

    '''None objects.'''

    native = 'void'


class Integer(Model):

    '''Integer numbers.'''

    native = 'integer'


class Float(Model):

    '''Floating point numbers.'''

    native = 'float'


class String(Model):

    '''Unicode strings.'''

    native = 'string'


class Boolean(Model):

    '''Boolean.'''

    native = 'boolean'


class Date(Model):

    '''Dates.'''

    native = 'date'


class DateTime(Model):

    '''DateTimes.'''

    native = 'date-time'


# ############################# #
# CUSTOM JSON-SCHEMA DATA TYPES #
# ############################# #


class List(Model):

    '''Lists.'''

    schema = {'type': 'array'}


class Set(Model):

    '''Sets.'''

    schema = {'type': 'array', 'uniqueItems': True}
