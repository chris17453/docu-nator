#.phony: 

quickstart:
	@sphinx-quickstart

clean:
	@rm ./_patch/* -f
	@rm ./_temp/* -f

docstring: clean
	@python -m .src.main --dir src

patch:
	@./patch.sh