[default]
all: format lint type test

# Fetch ATP Tour live matches once and print a terminal summary
tour-once:
    uv run atptour --level tour --once

# Fetch ATP Challenger live matches once and print a terminal summary
challenger-once:
    uv run atptour --level challenger --once

# Fetch ATP Tour and Challenger live matches once and print terminal summaries
all-once:
    uv run atptour --level all --once

# Watch ATP Tour live matches, polling every 15 seconds
watch-tour:
    uv run atptour --level tour

# Watch ATP Challenger live matches, polling every 15 seconds
watch-challenger:
    uv run atptour --level challenger

# Watch ATP Tour and Challenger live matches, polling every 15 seconds
watch-all:
    uv run atptour --level all

# Format code using ruff
format:
    uv run ruff format

# Lint code using ruff
lint:
    uv run ruff check --fix

# Type checking using ty
type:
    uv run ty check

# Run tests using pytest with coverage
test:
    uv run pytest -v -s --cov=src tests

# Build and publish the package to PyPI
publish:
    uv build
    uv publish
