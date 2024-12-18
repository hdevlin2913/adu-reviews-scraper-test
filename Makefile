STANDALONE_ARGS = -f compose/stack.yml
KNOWN_TARGETS = install start stop destroy restart reset logs build.dev build.production format lint
ARGS := $(filter-out $(KNOWN_TARGETS),$(MAKECMDGOALS))
EXEC := /bin/bash

# turn ARGS into do-nothing targets
ifneq ($(ARGS),$(MAKECMDGOALS))
$(eval $(ARGS):;@:)
endif

.PHONY: help
help: ## Show this help information
	@echo "Please use 'make <target>' where <target> is one of the following commands.\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo "Check the Makefile to know exactly what each target is doing."

.PHONY: install
install: ## Bootstrapping the stack
	@cp -i ./config/config.template.toml ./config/prod_config.toml

.PHONY: start
start:  ## Start the stack
	@docker compose ${STANDALONE_ARGS} up -d
	@docker compose ${STANDALONE_ARGS} ps

.PHONY: stop
stop:  ## Stop the stack, keep resources (volumes, networks,...)
	@docker compose ${STANDALONE_ARGS} stop

.PHONY: destroy
destroy:  ## Stop the stack and purge resources (WARN: data will be lost after this)
	@docker compose ${STANDALONE_ARGS} down $(ARGS) -v

.PHONY: ## Restart the stack without purging data (`stop start`)
restart: stop start $(ARGS)

.PHONY: ## Restart the stack and purge the data as well (`destroy start`)
reset: destroy start

.PHONY: logs
logs: ## make logs [service-name]; leave service empty to fetch all servide log
	@docker compose ${STANDALONE_ARGS} logs $(ARGS) -f

.PHONY: build.dev
build.dev: ## Re-build for development environment
	@docker compose ${STANDALONE_ARGS} build

.PHONY: build.production
build.production: ## Build Dockerimage used for Production, require REGISTRY_URL environment variable
	$(eval IMAGE_TAG := $(shell git rev-parse HEAD))
	$(eval TARGET := ${TARGET})
	$(eval IMAGE_URL := ${REGISTRY_URL}/${TARGET}:${IMAGE_TAG})
	@docker build --platform linux/amd64 -f docker/Dockerfile.production -t ${IMAGE_URL} --target ${TARGET} .
	@docker push ${IMAGE_URL}

.PHONY: ps
ps: ## List out all Docker containers of services
	@docker compose ${STANDALONE_ARGS} ps

.PHONY: format
format: ## Format the source code
	@bash ./scripts/format.sh

.PHONY: lint
lint: ## Lint the source code
	@bash ./scripts/lint.sh

.PHONY: exec
exec: ## make exec <service-name> <executable>. E.g: make exec api /bin/bash
	@docker compose ${STANDALONE_ARGS} $(ARGS)
