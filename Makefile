unit-tests:
	@pytest
unit-tests-cov:
	@pytest --cov=src --cov-report term-missing --cov-report=html
unit-tests-cov-fail:
	@pytest --cov=cython_extensions --cov-report term-missing --cov-report=html --cov-fail-under=80
clean-cov:
	@rm -rf .coverage
	@rm -rf htmlcov
	@rm -rf pytest.xml
	@rm -rf pytest-coverage.txt
docs-build: ## build documentation locally
	@mkdocs build

docs-deploy: ## build & deploy documentation to "gh-pages" branch
	@mkdocs gh-deploy -m "docs: update documentation" -v --force
