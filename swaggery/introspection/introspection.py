'''Provide support for introspection into the API (swagger-format).'''

import json
import os.path

from werkzeug.exceptions import NotFound

from swaggery.keywords import *


class ResourceListingModel(Model):

    '''The model of the resource listing, inferred from examples.'''

    __dir = os.path.dirname(__file__)
    with open(os.path.join(__dir, 'resource-listing.json')) as file_:
        schema = json.load(file_)


class ApiDeclarationModel(Model):

    '''The model of the api declaration, taken from: http://goo.gl/C2kbwC'''

    __dir = os.path.dirname(__file__)
    with open(os.path.join(__dir, 'api-declaration-schema.json')) as file_:
        schema = json.load(file_)


class Introspection(Api):

    '''Swagger support for Swaggery API.'''

    version = '1.0.0'
    path = 'introspect'
    private = True


class ResourceListing(Resource):

    '''Resource listing (show all APIs + descrpiption path).'''

    api = Introspection

    @operations('GET')
    def resource_listing(cls, request) -> [(200, 'Ok', ResourceListingModel)]:
        '''Return the list of all available resources on the system.

        Resources are filtered according to the permission system, so querying
        this resource as different users may bare different results.'''
        apis = [api.get_swagger_fragment() for api in Api if not api.private]
        Respond(200, {
            'apiVersion': cls.api.version,
            'swaggerVersion': cls.api.swagger_version,
            'apis': apis
        })


class ApiDeclaration(Resource):

    '''API description (show all possible data for each resource).'''

    api = Introspection
    subpath = '<api_path>'

    __cache = {}

    @classmethod
    def _extract_models(cls, apis):
        '''An helper function to extract all used models from the apis.'''
        # TODO: This would probably be much better if the info would be
        # extracted from the classes, rather than from the swagger
        # representation...
        models = set()
        for api in apis:
            for op in api.get('operations', []):
                models.add(op['type'])
                for param in op.get('parameters', []):
                    models.add(param.get('type', 'void'))
                for msg in op['responseMessages']:
                    models.add(msg.get('responseModel', 'void'))
        # Convert from swagger name representation to classes
        models = map(lambda m: Model.name_to_cls[m], models)
        ret = {}
        for model in models:
            if model.native_type:
                continue
            obj = model.schema.copy()
            obj['id'] = model.name
            ret[model.name] = obj
        return ret

    @operations('GET')
    def api_declaration(
            cls, request,
            api_path: (Ptypes.path,
                       String('The path for the info on the resource.'))) -> [
            (200, 'Ok', ApiDeclarationModel),
            (404, 'Not a valid resource.')]:
        '''Return the complete specification of a single API.

        Resources are filtered according to the permission system, so querying
        this resource as different users may bare different results.
        '''
        if api_path in cls.__cache:
            Respond(200, cls.__cache[api_path])
        # Select the resources belonging to this API
        resources = tuple(filter(lambda ep: ep.api.path == api_path, Resource))
        if not resources:
            Respond(404)
        apis = [r.get_swagger_fragment() for r in resources if not r.private]
        cls.__cache[api_path] = {
            'apiVersion': cls.api.version,
            'swaggerVersion': cls.api.swagger_version,
            'basePath': request.url_root[:-1],  # Remove trailing slash
            'resourcePath': '/{}'.format(api_path),
            'apis': apis,
            'models': cls._extract_models(apis),
            'consumes': ['application/json'],
            'produces': ['application/json']
        }
        Respond(200, cls.__cache[api_path])
