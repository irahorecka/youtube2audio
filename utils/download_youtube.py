import os
from shutil import copy2
import pytube
import requests
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from mutagen.id3 import ID3, APIC, TALB, TPE1, TIT2, TCON
from moviepy.editor import VideoFileClip


def thread_query_youtube(args):
    """Download video to mp4 then mp3 -- triggered
    by map_threads"""

    yt_link_starter = "https://www.youtube.com/watch?v="
    _, videos_dict = args[0]
    download_path, mp4_path = args[1]
    song_properties = args[2]
    save_as_mp4 = args[3]
    full_link = yt_link_starter + videos_dict["id"]

    def get_youtube_mp4():
        """Write MP4 audio file from YouTube video."""
        try:
            video = pytube.YouTube(full_link)
            stream = video.streams.filter(audio_codec="mp4a.40.2").first()
            mp4_filename = f'{song_properties.get("song")}'
            illegal_char = (
                "?",
                "'",
                '"',
                ".",
                "/",
                "\\",
                "*",
                "^",
                "%",
                "$",
                "#",
                "~",
                "<",
                ">",
                ",",
                ";",
                ":",
                "|",
            )
            # remove illegal characters from song title - otherwise clipped by pytube
            for char in illegal_char:
                mp4_filename = mp4_filename.replace(char, "")
            
            mp4_filename += ".mp4"  # add extension for downstream file recognition
            stream.download(mp4_path, filename=f"{mp4_filename}")
            if save_as_mp4:
                m4a_filename = f'{song_properties.get("song")}.m4a'
                # Copy song from temporary folder to destination
                copy2(
                    os.path.join(mp4_path, mp4_filename),
                    os.path.join(download_path, m4a_filename),
                )
                return set_song_metadata(download_path, song_properties, m4a_filename, True)

            return get_youtube_mp3(mp4_filename)
        except Exception as error:  # not a good Exceptions catch...
            print(f"Error: {str(error)}")  # poor man's logging
            raise RuntimeError from error

    def get_youtube_mp3(mp4_filename):
        """Write MP3 audio file from MP4."""
        mp3_filename = f'{song_properties.get("song")}.mp3'
        print(os.path.join(mp4_path, mp4_filename))
        try:
            video = VideoFileClip(os.path.join(mp4_path, mp4_filename))
            video.audio.write_audiofile(os.path.join(download_path, mp3_filename))
        except Exception as e:
            print(e)
        set_song_metadata(download_path, song_properties, mp3_filename, False)

    return get_youtube_mp4()


def set_song_metadata(directory, song_properties, song_filename, save_as_mp4):
    """Set song metadata."""

    def write_to_mp4():
        """Add metadata to MP4 file."""
        # NOTE Metadata for MP4 will fail to write if any error (esp. with artwork) occurs
        audio = MP4(os.path.join(directory, song_filename))
        audio.tags["\xa9alb"] = song_properties["album"]
        audio.tags["\xa9ART"] = song_properties["artist"]
        audio.tags["\xa9nam"] = song_properties["song"]
        audio.tags["\xa9gen"] = song_properties["genre"]
        # Only add a cover if the response was ok and the header of the
        # response content is that of a JPEG image. Source:
        # https://www.file-recovery.com/jpg-signature-format.htm.
        if valid_artwork():
            audio.tags["covr"] = [MP4Cover(response.content, imageformat=MP4Cover.FORMAT_JPEG)]

        audio.save()

    def write_to_mp3():
        """Add metadata to MP3 file."""
        audio = MP3(os.path.join(directory, song_filename), ID3=ID3)
        audio["TALB"] = TALB(encoding=3, text=song_properties["album"])
        audio["TPE1"] = TPE1(encoding=3, text=song_properties["artist"])
        audio["TIT2"] = TIT2(encoding=3, text=song_properties["song"])
        audio["TCON"] = TCON(encoding=3, text=song_properties["genre"])
        if valid_artwork():
            audio.tags.add(
                APIC(
                    encoding=3,  # 3 is for utf-8
                    mime="image/jpeg",  # image/jpeg or image/png
                    type=3,  # 3 is for the cover image
                    desc="Cover",
                    data=response.content,
                )
            )

        audio.save()

    def valid_artwork():
        """Validate artwork requests response."""
        return response is not None and response.status_code == 200 and response.content[:3] == b"\xff\xd8\xff"

    # TODO Cache the image until program finishes
    try:
        # Get byte data for album artwork url. The first number in the timeout
        # tuple is for the initial connection to the server. The second number
        # is for the subsequent response from the server.
        response = requests.get(song_properties["artwork"], timeout=(1, 5))
    except requests.exceptions.MissingSchema:
        response = None

    if save_as_mp4:
        write_to_mp4()
    else:
        write_to_mp3()
