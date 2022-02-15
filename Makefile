.DEFAULT_GOAL := help

####################
# CONSTANTS
####################

# Image Names & Tags
IMAGE_NAME := fideslib
IMAGE := $(IMAGE_NAME):local

# Run in Compose
RUN = docker run --rm $(IMAGE)
RUN_IT = docker run --rm -it $(IMAGE) /bin/bash

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
	@$(RUN) black --check src

# The order of dependent targets here is intentional
check-all: build black pylint mypy xenon pytest
	@echo "Running formatter, linter, typechecker and tests..."

mypy:
	@$(RUN) mypy --ignore-missing-imports src

pylint:
	@$(RUN) pylint src

pytest:
	@$(RUN) pytest -x -m unit

xenon:
	@$(RUN) xenon . \
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
