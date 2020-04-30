# YouTube2Mp3
A desktop application to convert YouTube videos to annotated MP3 files.


### Troubleshooting

1) If you download your playlist and the script completes instantly, you are probably experiencing a SSL: CERTIFICATE_VERIFY_FAIL error. This fails the instanciation of pytube.Youtube. To troubleshoot this (if you're using macOS), go to Macintosh HD > Applications > Python3.6 folder (or whatever version of python you're using) > double click on "Install Certificates.command" file.

2) Install ffmpeg via ```brew install ffmpeg```

