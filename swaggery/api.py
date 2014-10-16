'''Provide support for a plugin-style resource system.

Because of the swagger architecture, three base classes are defined: Api,
Resource and Model.  Api works as a "collector" for all resources operating on
the same data.  These resources share the same base URL fragment of their Api.
Models are data-type descriptor (used for both input and output).

There are two main concepts Swaggery architecture heavily relies on.

The first if the use of metaclasses for registering resources in a "plugin-
style" [i.e. it is sufficient to write an Api/Resource class to have it
discovered and loaded].

The second is the use of introspection to generate swagger-compliant API
documentation.  This is such that code for interfacing to it can be auto-
generated with swagger tools.
'''

import re
import json
import inspect

from werkzeug.routing import Rule

from . import utils
from .logger import log
from .flowcontrol import Respond
from .responses import BadResponse, GoodResponse

__SWAGGER_VERSION__ = '1.2'


CODES_TO_EXCEPTIONS = utils.map_exception_codes()


class Api(object, metaclass=utils.RegisterLeafClasses):

    '''An API is a collector for Resources operating on the same data.

    A valid API provides the following class attributes:
      - version: the current version of the api (string)
      - path: the path frgament common to all resources
      - description: a short description of what the API is all about
    '''

    swagger_version = __SWAGGER_VERSION__

    __description = None
    private = False

    @classmethod
    def get_swagger_fragment(cls):
        '''Return the swagger-formatted fragment for the Resource Listing.'''
        return {
            'path': '/{}'.format(cls.path),
            'description': cls.description
        }

    @utils.classproperty
    def description(cls):
        if cls.__description is None:
            cls.__description = utils.parse_docstring(cls)[0]
        return cls.__description


class Resource(object, metaclass=utils.RegisterLeafClasses):

    '''An Resource correspond to a specific path with zero or more opertations.

    A valid Resource provides the following class attributes..
      - api: the Api the Resource belongs to (determine the leading path).
      - subpath: a werkzeug-formatted URL rule string to be joined to the root
                 api URL.  This can be omitted or set to an empty string if the
                 resource is the root of the API.
      - description: a short description of what the resource does.

    Classmethods for any of the HTTP methods (get, post, put...)
    '''

    api = None
    subpath = None
    private = False

    __callbacks = None
    __description = None
    __endpoint_path = None
    __swagger_fragment = None
    __implemented_methods = None

    @classmethod
    def parse_signature(cls, function):
        '''Parses the signature of a method and its annotations to swagger.

        Return a dictionary {arg_name: info}.
        '''
        annotations = function.__annotations__.copy()
        del annotations['return']
        result = []
        for param_name, (param_type, param_obj) in annotations.items():
            sig_param = function.signature.parameters[param_name]
            result.append({
                'paramType': param_type,
                'name': param_name,
                'description': param_obj.description,
                'dataType': param_obj.name,
                'required': sig_param.default is inspect.Parameter.empty,
            })
        return result

    @classmethod
    def get_swagger_fragment(cls):
        '''Return the swagger-formatted fragment for the Resource Listing.'''
        if cls.__swagger_fragment:
            return cls.__swagger_fragment
        cls.__swagger_fragment = {
            'path': cls.endpoint_path.replace('<', '{').replace('>', '}'),
            'description': cls.description,
            'operations': cls.get_resource_operations(),
        }
        return cls.__swagger_fragment

    @classmethod
    def get_resource_operations(cls):
        '''Return the swagger-formatted method descriptions'''
        operations = []
        for http, callback in cls.implemented_methods.items():
            # Parse docstring
            summary, notes = utils.parse_docstring(callback)
            # Parse return annotations
            responses = utils.parse_return_annotation(callback)
            ok_result_model = responses[200]['responseModel']
            operations.append({
                'method': http,
                'nickname': callback.__name__,
                'type': ok_result_model,
                'parameters': cls.parse_signature(callback),
                'summary': summary.strip(),
                'notes': notes.strip(),
                'responseMessages': list(responses.values())
            })
        return operations

    @classmethod
    def get_routing_tuples(cls):
        '''A generator of (rule, callback) tuples.'''
        for callback in cls.callbacks:
            ep_name = '{}.{}'.format(cls.api.__name__, callback.__name__)
            yield (Rule(cls.endpoint_path,
                        endpoint=ep_name,
                        methods=callback.swagger_ops),
                   callback)

    @utils.classproperty
    def description(cls):
        '''A textual description of the resource.'''
        if cls.__description is None:
            cls.__description = utils.parse_docstring(cls)[0]
        return cls.__description

    @utils.classproperty
    def callbacks(cls):
        '''Return all the methods that are actually a request callback.'''
        if cls.__callbacks is not None:
            return cls.__callbacks
        cls.__callbacks = []
        for mname in dir(cls):
            # Avoid recursion by excluding all methods of this prototype class
            if mname in dir(Resource):
                continue
            callback = getattr(cls, mname)
            if not hasattr(callback, 'swagger_ops'):
                continue
            cls.__callbacks.append(callback)
        return cls.__callbacks

    @utils.classproperty
    def endpoint_path(cls):
        if cls.__endpoint_path is not None:
            return cls.__endpoint_path
        bits = ['', cls.api.path]
        if cls.subpath is not None:
            bits.append(cls.subpath)
        cls.__endpoint_path = '/'.join(bits)
        return cls.__endpoint_path

    @utils.classproperty
    def implemented_methods(cls):
        '''Return a mapping of implemented HTTP methods vs. their callbacks.'''
        if cls.__implemented_methods:
            return cls.__implemented_methods
        cls.__implemented_methods = {}
        for method in cls.callbacks:
            for op in getattr(method, 'swagger_ops'):
                cls.__implemented_methods[op] = method
        return cls.__implemented_methods


def operations(*operations):
    '''Decorator for marking Resource methods as HTTP operations.

    This decorator does a number of different things:
        - It transfer onto itself docstring and annotations from the decorated
          method, so as to be "transparent" with regards to introspection.
        - It tranform the method so as to make it a classmethod.
        - It invokes the method within a try-except condition, so as to
          intercept and populate the Fail(<code>) conditions.'''
    def decorator(method):
        def wrapper(cls, request, start_response, **kwargs):
            result_cache = []
            try:
                yield from method(cls, request, **kwargs)
            except Respond as e:
                # Inject messages as taken from signature
                status = e.status
                msg = utils.parse_return_annotation(method)[status]['message']
                if status / 100 == 2:  # All 2xx HTTP codes
                    e.description = msg
                    raise e
                else:  # HTTP Errors --> use werkzeug exceptions
                    raise CODES_TO_EXCEPTIONS[status](msg)
        # Add operation-specific attributes to the method.
        method.swagger_ops = operations
        method.signature = inspect.signature(method)
        method.source = inspect.getsource(method)
        method.path_vars = utils.extract_pathvars(method)
        # "Backport" the method introspective attributes to the wrapper.
        wrapper.__name__ = method.__name__
        wrapper.__doc__ = method.__doc__
        wrapper.__annotations__ = method.__annotations__
        wrapper.swagger_ops = method.swagger_ops
        wrapper.signature = method.signature
        wrapper.source = method.source
        wrapper.path_vars = method.path_vars
        return classmethod(wrapper)
    return decorator
