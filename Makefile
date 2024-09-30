.PHONY: check
check: check-format lint

.PHONY: check-format
check-format: ## Dry-run code formatter
	poetry run black ./limeprompt/ --check
	poetry run isort ./limeprompt/ --profile black --check

.PHONY: lint
lint: ## Run linter
	poetry run pylint limeprompt/

.PHONY: format
format: ## Run code formatter
	poetry run black ./limeprompt/
	poetry run isort ./limeprompt/ --profile black

.PHONY: check-lockfile
check-lockfile: ## Compares lock file with pyproject.toml
	poetry lock --check

.PHONY: test
test: ## Run the test suite
	poetry run pytest -vv -s ./tests

.PHONY: publish
publish:
	poetry build
	poetry publish