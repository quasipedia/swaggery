Swaggery
========

A python3 framework to code self-documenting RESTful API's according to the
[swagger 2.0](https://swagger.io) specifications.

At present, serving the **application via uWSGI is a requirement** as this is
presently the only WSGI server to provide support for the `yeld from` syntax.

As soon as [native support for `asyncio` will become stable]
(http://uwsgi-docs.readthedocs.org/en/latest/asyncio.html), Swaggery will be
refactored to use that (hopefully universal, and thus supported by other WSGI
servers) mechanism.



Quick Start
-----------

After having installed the dependencies in the virtual environment, you will
have to create your own `swaggery.ini` file.

A template can be found at `/templates/swaggery.ini`.  After you have done,
just type:

    uwsgi swaggery.ini



Stuff that needs to be documented
---------------------------------

  - Use sphinx
  - Return mechanism (Fail vs. return)
  - How testing is easy
  - Only one callback for each HTTP (REST)
  - Request is passed as a courtesy, but shouldn't be used for business logic
  - Ptypes
  - Streaming answers
  - swaggery.ini file
  - testlib
  - Subpath
  - Checker



Creating your own API
---------------------

Swaggery APIs are created by subclassing 3 main "abstract" classes:

### Model ###

Models define the data strcutures used by the API.  Since Swaggery is based on
JSON-schema, the native datatypes are readily available in the `models.py`
module (where the abstract `Model` class also lives).

Models are referenced in the Endpoint method signatures, so they need to be
declared (or imported) before defining any Endpoint, as they will be avaluated
at import time.

Model classes have a single class attribute called "schema" which must conform
to JSON schema syntax (see: [here](http://json-schema.org/) and
[here](https://github.com/wordnik/swagger-core/wiki/datatypes)).

#### Planned features: ####

  - The schema provided is automatically used to validate data supplied in
    the request.
  - A specific command-line flag will allow to also check the result provided
    by the API conforms to the schema.


### Api ###

APIs are just lightweight containers grouping related resources.  Since they do
not perform any particular type of operation, their declaration is
straighforward:

    class ZombieManipulation(Api):

        '''A beautiful API allowing to manipulate zombies.'''

        version = '1.0.0'
        path = 'zombies'


### Resources ###

Resources are "entities" that can be manipulated atomically.  They are mapped
to a single, unique URL/endpoint.  And the manipulation happens via HTTP verbs.
The URL can be either _static_ (`/zombies`) or _dynamic_ (`/zombies/{id}`),
were the `{id}` part means the ID value is a variable supplied by the client.

Operations on the entities are performed by calling the endpoint with the
appropriate HTTP method/verb.  For example you might issue a `GET` on
`/zombies/666` and the server might return the strength, stamina, and max
velocity of the zombie #666.  Alternatively you might `POST` to the same URL,
adding either a form or a body to the request, with the strength, stamina and
max velocity of a zombie to be newly created.

Back to Swaggery...

A Resoruce is implemented by subclassing the `Resource` class.  Operations are
implented as class methods, decorated with the `operations` function.

Class methods need to be fully annotated, and have a docstring, to make
possible for Swaggery to instrospect them correctly.  For example:

    class AddVectors(Resource):

        '''Single vector operations.'''

        api = Calculator
        subpath = 'vector'

        @operations('POST')
        def length(
                cls, request,
                vector: (Ptypes.body,
                         Vector('The vector to analyse.'))) -> [
                (200, 'Ok', Float),
                (400, 'Wrong vector format')]:
            '''Return the modulo of a vector.'''
            <your-code-here>

Will be rendered as the following swagger description:

    {
        "description": "Single vector operations.", 
        "operations": [
            {
                "method": "POST", 
                "nickname": "length", 
                "notes": "", 
                "parameters": [
                    {
                        "dataType": "Vector", 
                        "description": "The vector to analyse.", 
                        "name": "vector", 
                        "paramType": "body", 
                        "required": true
                    }
                ], 
                "responseMessages": [
                    {
                        "code": 200, 
                        "message": "Ok", 
                        "responseModel": "float"
                    }, 
                    {
                        "code": 400, 
                        "message": "Wrong vector format", 
                        "responseModel": "void"
                    }
                ], 
                "summary": "Return the modulo of a vector.", 
                "type": "float"
            }
        ], 
        "path": "/calc/vector"
    }

See the full example int the `examples/calculator` folder.



FAQ
---

**Where is the Python 2.X compatible version?**
Support for python 2.x series **cannot** be provided as the library heavily
relies on function annotation, which has been introduced in python 3.0 as well
as from the `yield from` syntax introduced in v 3.3.

