.PHONY: help  # List phony targets
help:
	@cat "Makefile" | grep '^.PHONY:' | sed -e "s/^.PHONY:/- make/"

.PHONY: start  # Start application
start:
	uv run --prerelease=allow --group dev streamlit run src/main.py

.PHONY: clean  # Clean development environment
clean:
	rm -rf .venv
