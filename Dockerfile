FROM --platform=linux/amd64 python:3.8-slim-buster

######################
# Tool Installation ##
######################

RUN apt-get update
RUN apt-get install -y \
    git \
    vim

#######################
## Application Setup ##
#######################

# Install Requirements
RUN pip install -U pip

COPY dev-requirements.txt dev-requirements.txt
RUN pip install -r dev-requirements.txt

# Copy in the application files and install fideslib locally
COPY . /fideslib
WORKDIR /fideslib
RUN pip install -e ".[all]"

# Immediately flush to stdout, globally
ENV PYTHONUNBUFFERED=TRUE
