# YouTube2Mp3
A desktop application to download YouTube videos as annotated MP3 files.
<br>
<p align="left">
<img src=https://i.imgur.com/wUwfptG.png alt="YouTube to MP3"
    width=800>
</p>
<hr>

## Using the application
Paste a YouTube playlist or video URL and load its content. Make edits to the table as you need, and click "iTunes annotate" to provide annotation hints to your videos. Choose a download folder, download your videos, and just like that, you have nicely annotated MP3 files.

This application uses PyQT5 to provide the user interface and multithreading to execute calls asynchronously. The backend uses the iTunes API to suggest song annotations, the YouTube API to download the video content as MP4 audio files, and FFMPEG to convert MP4 to MP3.

Watch the <a href="https://www.youtube.com/watch?v=z_aymV1H1Ro&feature=youtu.be">video demo</a> for more information.
<hr>

## Running the application

1) Download ```ffmpeg```
2) Clone GitHub repository
3) ```pip install -r requirements.txt```
4) ```python main.py```

Check <b>Troubleshooting</b> if you encounter any trouble running / using the application or downloading MP3 files. If undocumented exceptions occur, please file issue in <a href="https://github.com/irahorecka/YouTube2Mp3/issues">issues</a>.
<hr>

## Download ```ffmpeg```

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

## Troubleshooting

1) If the script completes instantly without downloading your video(s), you are probably experiencing an ```SSL: CERTIFICATE_VERIFY_FAIL``` exception. This fails to instantiate ```pytube.Youtube```, thus failing the download prematurely.

    To troubleshoot this (if you're using macOS), go to Macintosh HD > Applications > Python3.6 folder (or whatever version of python you're using) > double click on ```Install Certificates.command``` file. This should do the trick.
