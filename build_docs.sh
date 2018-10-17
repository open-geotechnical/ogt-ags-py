#!/bin/bash

mkdir ./docs/_static/
cp ./static/images/favicon.* ./docs/_static/
cp ./static/images/logo.* ./docs/_static/
cp ./static/images/logo-small.* ./docs/_static/


sphinx-build -a  -b html ./docs/ ./public/
