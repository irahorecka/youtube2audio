import os
import subprocess
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TALB, TPE1, TIT2, TCON
from pytube import YouTube
from ._threading import map_threads


def thread_query_youtube(args):
    """Download video to mp4 then mp3 -- triggered
    by map_threads"""
    yt_link_starter = "https://www.youtube.com/watch?v="
    # NOTE: this must have no relation to any self obj
    key_value, videos_dict = args[0]
    download_path, mp4_path = args[1]
    song_properties = args[2]
    full_link = yt_link_starter + videos_dict["id"]

    def get_youtube_mp4():
        """Write MP4 audio file from YouTube video."""
        try:
            video = YouTube(full_link)
            stream = video.streams.filter(
                only_audio=True, audio_codec="mp4a.40.2"
            ).first()
            stream.download(mp4_path)

            return get_youtube_mp3(stream)
        except Exception as error:
            print(error)  # poor man's logging
            raise Exception

    def get_youtube_mp3(stream):
        """Write MP3 audio file from MP4."""
        mp4_filename = stream.default_filename  # mp4 full extension
        mp3_filename = "{}.mp3".format(song_properties["song"])

        subprocess.call(
            [
                "ffmpeg",
                "-i",
                os.path.join(mp4_path, mp4_filename),
                os.path.join(download_path, mp3_filename),
            ]
        )
        set_mp3_metadata(download_path, song_properties, mp3_filename)

    return get_youtube_mp4()


def set_mp3_metadata(directory, song_properties, mp3_filename):
    """Set song metadata to MP3 file."""
    # get byte format for album artwork url
    response = requests.get(song_properties["artwork"])
    artwork_img = response.content

    audio = MP3(os.path.join(directory, mp3_filename), ID3=ID3)
    audio.tags.add(
        APIC(
            encoding=3,  # 3 is for utf-8
            mime="image/jpeg",  # image/jpeg or image/png
            type=3,  # 3 is for the cover image
            desc="Cover",
            data=artwork_img,
        )
    )
    audio["TALB"] = TALB(encoding=3, text=song_properties["album"])
    audio["TPE1"] = TPE1(encoding=3, text=song_properties["artist"])
    audio["TIT2"] = TIT2(encoding=3, text=song_properties["song"])
    audio["TCON"] = TCON(encoding=3, text=song_properties["genre"])

    audio.save()
