# YouTube2Mp3
A desktop application to convert YouTube videos to annotated MP3 files.

### Running the application

1) Clone GitHub repository
2) ```pip install -r requirements.txt```
3) ```python main.py```

Check <b>Troubleshooting</b> if you encounter any trouble running / using the application or downloading MP3 files. If undocumented exceptions occur, please file issue in <a href="https://github.com/irahorecka/YouTube2Mp3/issues">issues</a>.

### Troubleshooting

1) If the script completes instantly without downloading your video(s), you are probably experiencing an ```SSL: CERTIFICATE_VERIFY_FAIL``` exception. This fails to instantiate ```pytube.Youtube```, thus failing the download prematurely.

    To troubleshoot this (if you're using macOS), go to Macintosh HD > Applications > Python3.6 folder (or whatever version of python you're using) > double click on "Install Certificates.command" file. This should do the trick.

2) Install ffmpeg via ```brew install ffmpeg```



