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

    Native datatypes are all defined in Swaggery, so the final user will never
    have to create new ones.

    Custom datatypes only need a class attribute (schema) defining their JSON
    schema.
    '''

    schema = None
    native_type = False

    def __init__(self, description, **kwargs):
        self._description = description
        err_msg = 'Parameter "{}" invalid for type "{}"'
        for pname in kwargs.keys():
            if pname not in self._allowed_extra_params:
                raise ValueError(err_msg.format(pname, self.name))
        self.extra_params = kwargs

    @classproperty
    def name(cls):
        '''Return the name of the model as to be used in swagger.'''
        return cls.native_type or cls.__name__

    @classproperty
    def model(cls):
        '''Return the Model to be insertend in the swagger declaration.'''
        if cls.native:
            raise RuntimeError('Trying to get the model for a native type.')
        return {cls.__name__: cls.schema}

    def describe(self):
        '''Provide a dictionary with information describing itself.'''
        description = {
            'description': self._description,
            'type': self.name,
        }
        description.update(self.extra_params)
        return description

# ############################# #
# NATIVE JSON-SCHEMA DATA TYPES #
# ############################# #


class Void(Model):

    '''None objects.'''

    native_type = 'void'
    _allowed_extra_params = ('defaultValue', 'format')


class Integer(Model):

    '''Integer numbers.'''

    native_type = 'integer'
    _allowed_extra_params = ('defaultValue', 'format')


class Float(Model):

    '''Floating point numbers.'''

    native_type = 'float'
    _allowed_extra_params = ('defaultValue', 'format', 'minimum', 'maximum')


class String(Model):

    '''Unicode strings.'''

    native_type = 'string'
    _allowed_extra_params = ('defaultValue', 'format', 'enum')


class Boolean(Model):

    '''Boolean.'''

    native_type = 'boolean'
    _allowed_extra_params = ('defaultValue', 'format')


class Date(Model):

    '''Dates.'''

    native_type = 'date'
    _allowed_extra_params = ('defaultValue', 'format')


class DateTime(Model):

    '''DateTimes.'''

    native_type = 'date-time'
    _allowed_extra_params = ('defaultValue', 'format')


# ############################# #
# CUSTOM JSON-SCHEMA DATA TYPES #
# ############################# #


class List(Model):

    '''Lists.'''

    schema = {'type': 'array'}


class Set(Model):

    '''Sets.'''

    schema = {'type': 'array', 'uniqueItems': True}
