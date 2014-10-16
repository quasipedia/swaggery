#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''A Lord Vetinari clock API.'''

from time import strftime, localtime, time
from random import randint
from uwsgi import async_sleep as sleep

from swaggery.keywords import *


class TickStream(Model):

    '''A stream of clock ticks.'''

    schema = {
        'type': 'array',
        'items': {'type': 'string'}
    }


class LordVetinari(Api):

    '''The API of Lord Vetinari.'''

    version = '1.0.0'
    path = 'vetinari'


class Clock(Resource):

    '''The world-famous irregular and yet accurate clock.'''

    api = LordVetinari
    subpath = 'ticks/<length>/<style>'
    _styles = {'compact': '%H:%M:%S', 'extended': '%a, %d %b %Y %H:%M:%S'}

    @operations('GET')
    def ticks(
            cls, request,
            length: (Ptypes.path, Integer('Duration of the stream, in seconds.')),
            style: (Ptypes.path, String('Tick style.', enum=['compact', 'extended']))
        ) -> [
            (200, 'Ok', TickStream),
            (400, 'Invalid parameters')
        ]:
        '''A streaming Lord Vetinari clock...'''
        try:
            length = int(length)
            style = cls._styles[style]
        except (ValueError, KeyError):
            Respond(400)
        def vetinari_clock():
            start = time()
            while time() - start <= length:
                sleep(randint(25, 400) / 100)
                yield strftime(style, localtime())
        Respond(200, vetinari_clock())
