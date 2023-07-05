#!/bin/bash 

if [ $2 == "dev" ]; then
  pip freeze | grep $1 >> requirements-dev.txt
else
  pip freeze | grep $1 >> requirements.txt
fi