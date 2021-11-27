black: ## Black format every python file to line length 120
	find . -type f -name "*.py" | xargs black --line-length=120;
	find . -type f -name "*.py" | xargs absolufy-imports;
	make clean;

flake8: ## Flake8 every python file
	find . -type f -name "*.py" -a | xargs flake8;

pylint: ## Pylint every python file
	find . -type f -name "*.py" -a | xargs pylint;

clean: ## Remove pycache
	find . -type d -name "__pycache__" | xargs rm -r;
	find . -type f -name ".DS_Store" | xargs rm;
