# YouTube2Mp3
A desktop application to download YouTube videos as annotated MP3 files.
<hr>

### Using the application

<p align="center">
<img src=https://i.imgur.com/s4sMi9q.png alt="YouTube to MP3"
    width=800>
</p>

Paste a YouTube playlist or video URL and load its content onto the table. Click "iTunes annotate" to provide annotation hints to your videos and make edits to the table as you need. Choose a download folder, download your videos, and just like that, you have nicely annotated MP3 files.

This application uses PyQT5 to provide the user interface and multithreading to run parallel requests and tasks. The backend uses the iTunes API to suggest song annotations, the YouTube API to download the video content, and FFMPEG to convert MP4 files to MP3.
<hr>

### Running the application

1) Download ```ffmpeg```
2) Clone GitHub repository
3) ```pip install -r requirements.txt```
4) ```python main.py```

Check <b>Troubleshooting</b> if you encounter any trouble running / using the application or downloading MP3 files. If undocumented exceptions occur, please file issue in <a href="https://github.com/irahorecka/YouTube2Mp3/issues">issues</a>.
<hr>

### Download ```ffmpeg```

There are several options to install ```ffmpeg``` depending on your OS.

1) Using homebrew
    - Downloading homebrew: 
    <a href="https://docs.brew.sh/Homebrew-on-Linux">Linux</a>,
    <a href="https://docs.brew.sh/Installation">macOS</a>
    -  ```brew install ffmpeg```
2) Through ffmpeg.org
    - <a href="https://www.ffmpeg.org/download.html#build-linux">Linux</a>,
    <a href="https://www.ffmpeg.org/download.html#build-mac">macOS</a>,
    <a href="https://www.ffmpeg.org/download.html#build-windows">Windows</a>
    
<hr>

### Troubleshooting

1) If the script completes instantly without downloading your video(s), you are probably experiencing an ```SSL: CERTIFICATE_VERIFY_FAIL``` exception. This fails to instantiate ```pytube.Youtube```, thus failing the download prematurely.

    To troubleshoot this (if you're using macOS), go to Macintosh HD > Applications > Python3.6 folder (or whatever version of python you're using) > double click on ```Install Certificates.command``` file. This should do the trick.



