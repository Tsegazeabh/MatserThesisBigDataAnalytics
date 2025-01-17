# DjuliAPIpython

Python API for djuli

## Installing dependencies
Python version: >= 3.9
1. Install dependencies. (A python environment is recommended)
    > pip install -r requirements.txt
1. If the host isn't Windows (required for DT6 files decode)
    For Linux:
        > apt-get update
        > apt-get install --no-install-recommends --assume-yes wine
        > apt-get update
        > apt-get install --no-install-recommends --assume-yes wine32

## Run project
> python src/main.py

## Run unit tests
> pytest

## Create docker image
1. Create master pull-request

1. Build docker container
docker build .

1. Check the image code


1. Verify that the docker image can run properly (Change the image code)


1. Tag the container (Remember to change the version id and the docker image code)


1. Push the container (Remember to change the version id)


1. Update Cloud Run djuli-python project



# Use GCloud to build the container
> gcloud builds submit

## Update Requirements
pip freeze
