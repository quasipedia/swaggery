'''A collection of utility for the Swaggery framework.'''
import json
import inspect
from textwrap import dedent

import werkzeug.exceptions as exceptions


class Enumerator(type):

    '''Metaclass for iterating over the attributes of a class.'''

    def __init__(cls, name, bases, nmspc):
        super(Enumerator, cls).__init__(name, bases, nmspc)
        cls.__cls = cls

    def __iter__(cls):
        for attribute in dir(cls.__cls):
            if not attribute.startswith("_"):
                yield getattr(cls.__cls, attribute)


class Ptypes(metaclass=Enumerator):

    '''Param types "enumerator-compatible" class.'''

    # This should be ported to an Enum() instance, when python 3.4 will be out.
    # The unusual construct used here is for compatibility with PEP 435
    path = 'path'
    query = 'query'
    body = 'body'
    header = 'header'
    form = 'form'


# Used to extract parameters from the request object
PTYPE_TO_REQUEST_PROPERTY = {
    Ptypes.query: 'args',
    Ptypes.body: 'data',
    Ptypes.header: 'headers',
    Ptypes.form: 'form',
}


class classproperty(object):

    '''An helper class to allow for classproperty decorators.'''

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class RegisterLeafClasses(type):

    '''Metaclass for keeping track of generic leaf classes.'''

    def __init__(cls, name, bases, nmspc):
        super(RegisterLeafClasses, cls).__init__(name, bases, nmspc)
        if not hasattr(cls, 'registry'):
            cls.registry = set()
        cls.registry.add(cls)
        cls.registry -= set(bases)  # Remove base classes

    def __iter__(cls):
        return iter(cls.registry)

    def __str__(cls):
        if cls in cls.registry:
            return cls.__name__
        template = 'Registered classes of type {}: {}'
        return template.format(
            cls.__name__, ", ".join(sorted([rgst.__name__ for rgst in cls])))


class RegisterLeafModels(RegisterLeafClasses):

    '''Metaclass for keeping track of Module leaf classes.'''

    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)
        if not hasattr(cls, 'name_to_cls'):
            cls.name_to_cls = {}
        cls.name_to_cls[cls.name] = cls
        # For native types we want to map both the Model class name and the
        # native name (e.g.: both "string" and "String")
        if cls.native_type:
            cls.name_to_cls[cls.__name__] = cls
        for base in bases:  # Remove base classes
            try:
                del cls.name_to_cls[base.name]
            except (KeyError, AttributeError):
                pass


def map_exception_codes():
    '''Helper function to intialise CODES_TO_EXCEPTIONS.'''
    werkex = inspect.getmembers(exceptions, lambda x: getattr(x, 'code', None))
    return {e.code: e for _, e in werkex}


def parse_return_annotation(callback):
    '''Parses the annotation return tuples. Ruturn a dictinary {code: info}.'''
    # This has been implemented as a function as the parsing need to be
    # accessible from a decorator used on the function's class method
    responses = {}
    for data in callback.__annotations__['return']:
        tmp = dict(zip(('code', 'message', 'responseModel'), data))
        rm = tmp.get('responseModel', None)  # "None" can be omitted!
        tmp['responseModel'] = rm.name if rm else 'void'
        responses[tmp['code']] = tmp
    return responses


def extract_pathvars(callback):
    '''Extract the path variables from an Resource operation.

    Return {'mandatory': [<list-of-pnames>], 'optional': [<list-of-pnames>]}
    '''
    mandatory = []
    optional = []
    # We loop on the signature because the order of the parameters is
    # important, and signature is an OrderedDict, while annotations is a
    # regular dictionary
    for pname in callback.signature.parameters.keys():
        try:
            anno = callback.__annotations__[pname]
        except KeyError:  # unannotated params, like "cls" or "request"
            continue
        if anno[0] != Ptypes.path:
            continue
        # At this point we are only considering path variables, but
        # we have to generate different (present/absent) if these
        # parameters have a default.
        if callback.signature.parameters[pname].default == inspect._empty:
            mandatory.append(pname)
        else:
            optional.append(pname)
    return {'mandatory': mandatory, 'optional': optional}


def parse_docstring(whatever_has_docstring):
    '''Parse a docstring into a semmary (first line) and notes (rest of it).'''
    try:
        summary, notes = whatever_has_docstring.__doc__.split('\n', 1)
        notes = dedent(notes).replace('\n', ' ')
    except ValueError:
        summary = whatever_has_docstring.__doc__.strip()
        notes = ''
    return summary, notes


def inject_extra_args(callback, request, kwargs):
    '''Inject extra arguments from header, body, form.'''
    # TODO: this is a temporary pach, should be managed via honouring the
    # mimetype in the request header....
    annots = dict(callback.__annotations__)
    del annots['return']
    for param_name, (param_type, _) in annots.items():
        if param_type == Ptypes.path:
            continue  # Already parsed by werkzeug
        elif param_type == Ptypes.body:
            value = getattr(request, PTYPE_TO_REQUEST_PROPERTY[param_type])
            # TODO: The JSON conversion should be dependant from request
            # header type, really...
            value = json.loads(value.decode('utf-8'))
        else:
            get = lambda attr: getattr(request, attr).get(param_name, None)
            value = get(PTYPE_TO_REQUEST_PROPERTY[param_type])
        if value is not None:
            kwargs[param_name] = value


def jsonify(payload):
    '''A helper function to consistently format the output of the API.'''
    # This is a HOPEFULLY temporary fix, while waiting to properly honour the
    # consumes/produces fields of the API description
    return json.dumps(payload, indent=4, sort_keys=True)


def filter_annotations_by_ptype(function, ptype):
    '''Filter an annotation by only leaving the parameters of type "ptype".'''
    ret = {}
    for k, v in function.__annotations__.items():
        if k == 'return':
            continue
        pt, _ = v
        if pt == ptype:
            ret[k] = v
    return ret
