.DEFAULT_GOAL := fideslib

####################
# CONSTANTS
####################

# Image Names & Tags
IMAGE_NAME := fideslib
IMAGE := $(IMAGE_NAME):local

# Run in Compose
RUN = docker run --rm $(IMAGE)
RUN_IT = docker run \
	--rm -it $(IMAGE) \
	/bin/bash

####################
# Dev
####################

fideslib: build
	@$(RUN_IT)

####################
# Docker
####################

build:
	docker build --tag $(IMAGE) .

####################
# CI
####################

black:
	@$(RUN) black --check fideslib tests

# The order of dependent targets here is intentional
check-all: build check-install black pylint mypy xenon pytest
	@echo "Running formatter, linter, typechecker and tests..."

check-install:
	@$(RUN) python -c "import fideslib; from fideslib import oauth"

mypy:
	@$(RUN) mypy .

pylint:
	@$(RUN) pylint fideslib tests

pytest:
	@$(RUN) pytest

xenon:
	@$(RUN) xenon fideslib \
	--max-absolute B \
	--max-modules B \
	--max-average A

####################
# Utils
####################

.PHONY: clean
clean:
	@echo "Cleaning project temporary files and installed dependencies..."
	@docker system prune -a --volumes
	@echo "Clean complete!"
