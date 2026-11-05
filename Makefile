.PHONY: test eval validate

test:
	python3 -m unittest

eval:
	python3 -m snippets.evaluate

validate: test eval
