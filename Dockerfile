FROM --platform=linux/amd64 python:3.8-slim-bullseye

######################
# Tool Installation ##
######################

RUN : \
  && apt-get update \
  && apt-get install \
  -y --no-install-recommends \
  git \
  vim \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

#######################
## Application Setup ##
#######################

# Install Requirements
RUN pip install -U pip

COPY pyproject.toml pyproject.toml
COPY dev-requirements.txt dev-requirements.txt
COPY requirements.txt requirements.txt
RUN pip install -r dev-requirements.txt -r requirements.txt

# Copy in the application files and install fideslib locally
COPY . /fideslib
WORKDIR /fideslib
RUN pip install -e ".[all]"

# Immediately flush to stdout, globally
ENV PYTHONUNBUFFERED=TRUE
