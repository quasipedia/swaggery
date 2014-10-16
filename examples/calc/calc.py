'''A silly demo API to showcase Swaggery's capabilities.'''

from math import sqrt

from swaggery.keywords import *


# #############################################################################
# MODELS
# #############################################################################

class Vector(Model):

    '''Vector (2 or 3 dimensional).'''

    schema = {
        'type': 'object',
        'properties': {
            'x': {
                'type': 'float'
            },
            'y': {
                'type': 'float'
            },
            'z': {
                'type': 'float',
            }
        },
        'required': ['x', 'y']
    }


# #############################################################################
# API(s)
# #############################################################################

class Calculator(Api):

    '''A basic calculator for demoing Swaggery's capabilities.'''

    version = '1.0.0'
    path = 'calculator'


# #############################################################################
# ENDPOINTS
# #############################################################################

class TwoNumbers(Resource):

    '''Perform operations on two numbers.'''

    api = Calculator
    subpath = 'op/<operation>/<first>/<second>'

    @operations('GET')
    def two_numbers(
            cls, request,
            operation: (Ptypes.path,
                        String('One of the 4 arithmetic operations.',
                                enum=['add', 'sub', 'mul', 'div'])),
            first: (Ptypes.path,
                    Float('The first operand.')),
            second: (Ptypes.path,
                     Float('The second operand.'))) -> [
            (200, 'Ok', Float),
            (400, 'Wrong number format or invalid operation'),
            (422, 'NaN')]:
        '''Any of the four arithmetic operation on two numbers.'''
        log.info('Performing {} on {} and {}'.format(operation, first, second))
        try:
            first = float(first)
            second = float(second)
        except ValueError:
            Respond(400)
        if operation == 'add':
            Respond(200, first + second)
        elif operation == 'sub':
            Respond(200, first - second)
        elif operation == 'mul':
            Respond(200, first * second)
        elif operation == 'div':
            if second == 0:
                Respond(422)
            Respond(200, first / second)
        else:
            Respond(400)


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
        log.info('Computing the length of vector {}'.format(vector))
        try:
            Respond(200, sqrt(vector['x'] ** 2 +
                              vector['y'] ** 2 +
                              vector.get('z', 0) ** 2))
        except ValueError:
            Respond(400)
