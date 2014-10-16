#! /usr/bin/env sh
rm -rf swaggery.egg-info
rm -rf build
rm -rf dist
find -name '*.pyc' -print0 | xargs -0 rm
find -name '__pycache__' | xargs rm -rf
