.DEFAULT_GOAL := help
LAB ?= rest/crapi
export LAB

.PHONY: help list up down logs status

help:
	@printf '%s\n' 'make list' 'make up LAB=rest/crapi' 'make status LAB=rest/crapi' 'make logs LAB=rest/crapi' 'make down LAB=rest/crapi'

list:
	@printf '%s\n' 'rest/crapi  |  REST  |  múltiplas stacks  |  requer importação inicial'
	@if [ -d labs ]; then find labs -name compose.yaml -type f | sed -e 's|^labs/||' -e 's|/compose\.yaml$$||' | sort; fi

up down logs status:
	@sh scripts/lab-compose.sh "$@"
