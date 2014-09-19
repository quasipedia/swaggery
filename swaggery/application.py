
import os
import sys
import pkgutil
from importlib import import_module

from werkzeug.routing import Map
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException

from .api import Resource
from .utils import inject_extra_args
from .logger import log
from .responses import GoodResponse, BadResponse
from .flowcontrol import Respond
from .checker import main as check_and_load

# The Swagger interface is implemented itself as an API, so we always want to
# import it.  The import happens as a module (rather than from a directory) so
# as to be sure the version associated to the code being run is used [and not
# the installed version of "swaggery"]
from .introspection import introspection

# Note that the following is the version of Swaggery, not of the APIs (to be set
# in each API module) nor of the swagger specifications (set in "api.py)".
__VERSION__ = '1.0.0'


class Swaggery(object):

    '''The main Application object.'''

    def __init__(self, api_dirs, do_checks=True):
        self._register_resources(api_dirs, do_checks)
        if not do_checks:
            log.warning('Skipping sanity checks for all APIs')
        self._mount_resources()

    def _register_resources(self, api_dirs, do_checks):
        '''Register all Apis, Resources and Models with the application.'''
        msg = 'Looking-up for APIs in the following directories: {}'
        log.debug(msg.format(api_dirs))
        if do_checks:
            check_and_load(api_dirs)
        else:
            msg = 'Loading module "{}" from directory "{}"'
            for loader, mname, _ in pkgutil.walk_packages(api_dirs):
                sys.path.append(os.path.abspath(loader.path))
                log.debug(msg.format(mname, loader.path))
                import_module(mname)

    def _mount_resources(self):
        '''Mount all registered resources onto the application.'''
        rules = []
        self.callback_map = {}
        for ep in Resource:
            for rule, callback in ep.get_routing_tuples():
                log.debug('Path "{}" mapped to "{}"'.format(
                    rule.rule, rule.endpoint))
                rules.append(rule)
                self.callback_map[rule.endpoint] = callback
        self.url_map = Map(rules)

    def _get_coroutine(self, request, start_response):
        '''Try to dispapch the request and get the matching coroutine.'''
        adapter = self.url_map.bind_to_environ(request.environ)
        resource, kwargs = adapter.match()
        callback = self.callback_map[resource]
        inject_extra_args(callback, request, kwargs)
        return callback(request, start_response, **kwargs)

    def __call__(self, environ, start_response):
        request = Request(environ)
        url = request.url
        try:
            log.debug('Attempting to dispatch {}'.format(url))
            coroutine = self._get_coroutine(request, start_response)
            log.debug('Dispatching of {} SUCCEDED!'.format(url))
            yield from coroutine
        except Respond as e:  # Only good responses are still of this class
            log.debug('Intercepted a Respond exception')
            response = GoodResponse(request, e)
        except HTTPException as e:
            log.debug('Intercepted an HTTPException')
            response = BadResponse(request, e)
        except Exception as e:
            msg = 'Intercepted an Exception of type "{}". Message was: "{}"'
            log.error(msg.format(e.__class__.__name__, e))
            response = BadResponse(request, e)
        yield from response.async(environ, start_response)
