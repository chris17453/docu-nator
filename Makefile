#.phony: 

quickstart:
	@sphinx-quickstart

clean:
	@rm ./_patch/* -f
	@rm ./_temp/* -f

docstring: clean
	@python -m docu-nator.main --dir docu-nator

patch:
	@./patch.sh