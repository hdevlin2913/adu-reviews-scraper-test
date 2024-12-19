STANDALONE_ARGS = -f compose/stack.yml
KNOWN_TARGETS = start stop destroy restart reset logs build.dev
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
	@echo "\nCheck the Makefile to know exactly what each target is doing."

.PHONY: start
start:
	@docker compose ${STANDALONE_ARGS} up

.PHONY: stop
stop:
	@docker compose ${STANDALONE_ARGS} stop

.PHONY: destroy
destroy:
	@docker compose ${STANDALONE_ARGS} down -v

.PHONY: ## Restart the stack without purging data
restart: stop start

.PHONY: ## Restart the stack and purge the data as well
reset: destroy start

.PHONY: logs
logs:
	@docker compose ${STANDALONE_ARGS} logs $(ARGS) -f

.PHONY: build.dev
build.dev: ## Re-build for development environment
	@docker compose ${STANDALONE_ARGS} build

.PHONY: ps
ps: ## Re-build for development environment
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
