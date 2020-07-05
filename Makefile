black:
	rm -rf ./__pycache__ ./utils/__pycache__ ./ui/__pycache__
	black ./main.py ./utils/download_youtube.py ./utils/pytube_patch.py ./utils/query_itunes.py ./utils/query_youtube.py ./utils/timeout.py ./ui/yt2mp3.py ./tests/test_qt_defaults.py ./tests/test_utils.py

flake:
	flake8 ./main.py ./utils/download_youtube.py ./utils/pytube_patch.py ./utils/query_itunes.py ./utils/query_youtube.py ./utils/timeout.py ./ui/yt2mp3.py ./tests/test_qt_defaults.py ./tests/test_utils.py