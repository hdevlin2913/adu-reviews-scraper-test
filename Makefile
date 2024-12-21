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

.PHONY: seed_input
seed_input: ## Create a default INPUT.json file
	@mkdir -p ./storage/key_value_stores/default
	@echo '{' > ./storage/key_value_stores/default/INPUT.json
	@echo '   "type": "",' >> ./storage/key_value_stores/default/INPUT.json
	@echo '   "params": {' >> ./storage/key_value_stores/default/INPUT.json
	@echo '       "query": [],' >> ./storage/key_value_stores/default/INPUT.json
	@echo '       "max_places_page": null,' >> ./storage/key_value_stores/default/INPUT.json
	@echo '       "max_reviews_page": null' >> ./storage/key_value_stores/default/INPUT.json
	@echo '   },' >> ./storage/key_value_stores/default/INPUT.json
	@echo '   "useApifyProxy": false' >> ./storage/key_value_stores/default/INPUT.json
	@echo '}' >> ./storage/key_value_stores/default/INPUT.json
