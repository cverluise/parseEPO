.PHONY: clean requirements.txt docs/src/

requirements.txt:
	poetry export -f requirements.txt > requirements.txt

docs/src/:
	cp -r eda/plots/ docs/src/
