#! /usr/bin/env python3
'''A code linter/checker for user-defined APIs.

This module will try to detect common errors that might be done while coding
an API, such as forgetting to define a path, or defining optional path
parameters, or...

Usage:
    checker.py <API-DIRECTORY> ...

It is possible to perform the checks on multiple directories at once.
'''

import os
import re
import sys
import pkgutil
import inspect
from importlib import import_module

from docopt import docopt

from . import utils
from .logger import log
from .keywords import *


# A regex that can extract HTTP status codes from source code of a method.
HTTP_STATUSES_REGEX = re.compile(r'Respond\( *(\d\d\d)')


class Checker(object):

    '''An abstract class that allow for defining checks as methods.

    Each check should have the same signature, so that `check_all` can iterate
    over them.  Checks follow an unix-like convention of returning a value that
    evaluate to False if the for no error conditions, and a value evaluating
    to True (namely a list of error messages) if such conditions arise.
    '''

    @property
    def checks(self):
        '''Return the list of all check methods.'''
        condition = lambda a: a.startswith('check_')
        return (getattr(self, a) for a in dir(self) if condition(a))

    def __call__(self, *args, **kwargs):
        '''Perform all checks in the Checker class.'''
        err_messages = []
        for ch in self.checks:
            msgs = ch(*args, **kwargs)
            if msgs:
                err_messages.extend(msgs)
        for em in err_messages:
            log.critical(em)
        return err_messages


class ApiChecker(Checker):

    '''A checker for the Api class.'''

    def check_has_docstring(self, api):
        '''An API class must have a docstring.'''
        if not api.__doc__:
            msg = 'The Api class "{}" lacks a docstring.'
            return [msg.format(api.__name__)]

    def check_has_version(self, api):
        '''An API class must have a `version` attribute.'''
        if not hasattr(api, 'version'):
            msg = 'The Api class "{}" lacks a `version` attribute.'
            return [msg.format(api.__name__)]

    def check_has_path(self, api):
        '''An API class must have a `path` attribute.'''
        if not hasattr(api, 'path'):
            msg = 'The Api class "{}" lacks a `path` attribute.'
            return [msg.format(api.__name__)]


class ResourceMethodChecker(Checker):

    '''A checker for individual methods in the Resource class.'''

    def check_docstring(self, method):
        '''All methods should have a docstring.'''
        mn = method.__name__
        if method.__doc__ is None:
            return ['Missing docstring for method "{}"'.format(mn)]

    def check_return_types(self, method):
        '''Return types must be correct, their codes must match actual use.'''
        mn = method.__name__
        retanno = method.__annotations__.get('return', None)
        # Take a look at the syntax
        if not retanno:
            return ['Missing return types for method "{}"'.format(mn)]
        if not isinstance(retanno, (list, tuple)):
            msg = 'Return annotation for method "{}" not tuple nor list'
            return [msg.format(mn)]
        if (any(map(lambda t: not isinstance(t, (list, tuple)), retanno)) or
                any(map(lambda t: not (2 <= len(t) <= 3), retanno))):
            msg = ('Return values series for "{}" should be composed of '
                   '2 or 3-items tuples (code, msg, type).')
            return [msg.format(mn)]
        errors = []
        # Take a look at the codes
        declared = set([t[0] for t in retanno])
        actual = set(int(s)
                     for s in HTTP_STATUSES_REGEX.findall(method.source))
        if declared != actual:
            if declared.issubset(actual):
                msg = 'Method {} returns undeclared codes: {}.'
                errors.append(msg.format(mn, actual - declared))
            elif actual.issubset(declared):
                msg = 'Method {} declares codes {} that are never used.'
                errors.append(msg.format(mn, declared - actual))
            else:
                msg = 'Declared {} and Used {} codes mismatch.'
                errors.append(msg.format(declared, actual))
        # Take a look at the types
        ret_with_types = filter(lambda t: len(t) == 3, retanno)
        msg = 'Method {} return type for code {} must be class (not instance).'
        msg_mod = 'Method {} return type for code {} must subclass from Model.'
        for code, _, type_ in ret_with_types:
            try:
                if Model not in type_.__bases__:
                    errors.append(msg_mod.format(mn, code))
            except AttributeError:
                errors.append(msg.format(mn, code))
        return errors

    def check_params_types(self, method):
        '''Types in argument annotations must be instances, not classes.'''
        mn = method.__name__
        annos = dict(method.__annotations__)
        errors = []
        # Take a look at the syntax
        msg_tuple = 'Parameter {} in method {} is not annotated with a tuple.'
        msg_ptype = 'Parameter {} in method {} is not a valid Ptype.'
        msg_mod = 'Type for param {} in method {} must descend from Model.'
        msg_cls = 'Type for param {} in method {} must be instance (not class)'
        bodies = []
        for pname, anno in annos.items():
            if pname == 'return':
                continue
            elif len(anno) != 2:
                errors.append(msg_tuple.format(pname, mn))
            else:
                param_type, value_type = anno
                if param_type not in Ptypes:
                    errors.append(msg_ptype.format(pname, mn))
                elif param_type == 'body':
                    bodies.append(pname)
                elif param_type == 'path':
                    default = method.signature.parameters[pname].default
                    if default is not inspect._empty:
                        msg = ('Path prameter {} in method {} has a default '
                               'value ({}) that would make it optional (which '
                               'is wrong!)')
                        errors.append(msg.format(pname, mn, default))
                if hasattr(value_type, '__bases__'):
                    errors.append(msg_cls.format(pname, mn))
                elif Model not in value_type.__class__.__bases__:
                    errors.append(msg_mod.format(pname, mn))
        # Only one body parameter!
        if len(bodies) > 1:
            msg = 'Too many "Ptypes.body" params {} for method {} (max=1).'
            errors.append(msg.format(bodies, mn))
        return errors


class ResourceChecker(Checker):

    '''A checker for the Resource class.'''

    path_params_regex = re.compile(r'<(.*?)>')

    def check_path_consistency(self, resource):
        '''Path arguments must be consistent for all methods.'''
        msg = ('Method "{}" path variables {}) do not conform with the '
               'resource subpath declaration ({}).')
        errors = []
        # If subpath is not set, it will be detected by another checker
        if resource.subpath is None:
            return errors
        declared = sorted(self.path_params_regex.findall(resource.subpath))
        for callback in resource.callbacks:
            actual = sorted(utils.filter_annotations_by_ptype(
                callback, Ptypes.path))
            if declared == actual:
                continue
            errors.append(msg.format(
                '{}.{}'.format(resource.__name__, callback.__name__),
                actual, resource.subpath))
        return errors

    def check_no_multiple_handlers(self, resource):
        '''The same verb cannot be repeated on several endpoints.'''
        seen = []
        errors = []
        msg = 'HTTP verb "{}" associated to more than one endpoint in "{}".'
        for method in resource.callbacks:
            for op in getattr(method, 'swagger_ops'):
                if op in seen:
                    errors.append(msg.format(op, resource.__name__))
                else:
                    seen.append(op)
        return errors

    def check_methods(self, resource):
        '''Iteratively check all methods (endpoints) in the Resource.'''
        checker = ResourceMethodChecker()
        errors = []
        for callback in resource.callbacks:
            new_errors = checker(callback)
            if new_errors:
                errors.extend(new_errors)
        return errors


def main(directories):
    '''Perform all checks on the API's contained in `directory`.'''
    msg = 'Checking module "{}" from directory "{}" for coding errors.'
    api_checker = ApiChecker()
    resource_checker = ResourceChecker()
    errors = []
    modules = []
    for loader, mname, _ in pkgutil.walk_packages(directories):
        sys.path.append(os.path.abspath(loader.path))
        log.info(msg.format(mname, loader.path))
        modules.append(mname)
        import_module(mname)
    for api in Api:
        if api.__module__.split('.')[-1] not in modules:
            continue
        log.debug('Anlysing Api class: {}'.format(api.__name__))
        errors.extend(api_checker(api))
    for res in Resource:
        if res.__module__.split('.')[-1] not in modules:
            continue
        log.debug('Anlysing Resource class: {}'.format(res.__name__))
        errors.extend(resource_checker(res))
    else:
        log.info('All modules tested, no problem detected.')
    return errors

# TODO: Add a checker class for Models.


if __name__ == '__main__':
    from logging import INFO
    arguments = docopt(__doc__)
    log.setLevel(INFO)
    errors = main(arguments['<API-DIRECTORY>'])
