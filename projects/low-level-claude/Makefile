command=docker

image="llm-lite"
container="shared-box"

repl:
	@python server/repl.py

run:
	@$(command) run -dit --name $(container) $(image) bash

build:
	@$(command) build -t $(image) .

exec:
	@$(command) exec -it shared-box bash

clean:
	@$(command) rm -f $$(docker ps -aq) || true