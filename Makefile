black:
	rm -rf ./__pycache__ ./utils/__pycache__ ./ui/__pycache__
	black --line-length 120 ./*.py ./utils/*.py ./tests/*.py ./ui/yt2mp3.py 

flake:
	flake8 ./*.py ./utils/*.py ./tests/*.py

pylint:
	pylint ./*.py ./utils/*.py ./tests/*.py