#!/usr/bin/env sh
nosetests -v --with-coverage --cover-package swaggery --cover-inclusive --cover-erase $@
