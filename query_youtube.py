import os
import subprocess
import requests
import youtube_dl
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TALB, TPE1, TIT2, TCON
from pytube import YouTube


def get_playlist_videos(playlist_url):
    """ Main function, gets all the playlist videos data."""
    ydl_opts = {"ignoreerrors": True, "quiet": True}
    videos_dict = dict()
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        playlist_dict = ydl.extract_info(
            playlist_url, download=False
        )  # time consuming spot -- cannot thread
        for video in playlist_dict["entries"]:
            try:
                title = video.get("title")
            except Exception as error:  # If video title is unavailable don't add it to the dict
                print(error)
                continue
            videos_dict[title] = dict()
            videos_dict[title]["id"] = video.get("id")
            videos_dict[title]["duration"] = seconds_to_mmss(video.get("duration"))

        return videos_dict


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


def seconds_to_mmss(seconds):
    """Returns a string in the format of mm:ss."""
    min = seconds // 60
    sec = seconds % 60
    if min < 10:
        min_str = "0" + str(min)
    else:
        min_str = str(min)
    if sec < 10:
        sec_str = "0" + str(sec)
    else:
        sec_str = str(sec)

    return min_str + ":" + sec_str
