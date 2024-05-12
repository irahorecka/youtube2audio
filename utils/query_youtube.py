import re
import urllib

import youtube_dl
from pytube import Playlist
from utils._threading import map_threads


def get_youtube_content(youtube_url, override_error):
    """Str parse YouTube url and call appropriate functions
    to execute url content."""
    if ".com/playlist" in youtube_url:
        url_tuple = get_playlist_video_info(youtube_url)
        # concatenate override_error argument to url_tuple
        url_tuple = tuple((url, override_error) for url in url_tuple)
        video_genr = map_threads(get_video_info, url_tuple)
        video_info = list(video_genr)
    else:
        adj_youtube_url = youtube_url.split("&")[0]  # trim ascii encoding "&"
        # set get_video_info parameter as tuple to comply with multithreading parameter (tuple)
        url_tuple = (adj_youtube_url, override_error)
        video_json = get_video_info(url_tuple)
        video_info = [video_json]

    return video_content_to_dict(video_info)


def get_playlist_video_info(playlist_url):
    """Get url of videos in a YouTube playlist."""
    try:
        playlist = Playlist(playlist_url)
        playlist._video_regex = re.compile(
            r"\"url\":\"(/watch\?v=[\w-]*)"
        )  # important bug fix with recent YouTube update. See https://github.com/get-pytube/pytube3/pull/90
    # thrown if poor internet connection or bad playlist url
    except (urllib.error.URLError, KeyError) as error:
        raise RuntimeError(error)

    try:
        video_urls = tuple(playlist.video_urls)
    except AttributeError as error:
        # if videos were queried unsuccessfully in playlist
        raise RuntimeError(error)

    return video_urls


def get_video_info(args):
    """Get YouTube video metadata."""
    video_url = args[0]
    override_error = args[1]

    ydl_opts = {"ignoreerrors": False, "quiet": True}
    if override_error:
        # silence youtube_dl exceptions by ignoring errors
        ydl_opts = {"ignoreerrors": True, "quiet": True}

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(video_url, download=False)
        return video_info
    # video unavailable or bad url format
    except (youtube_dl.utils.DownloadError, UnicodeError) as error:
        # catch exception here and process error:
        # either load content again or post error label.
        raise RuntimeError(error)


def video_content_to_dict(vid_info_list):
    """Convert YouTube metadata list to dictionary."""
    return {video["title"]: {"id": video["id"], "duration": video["duration"]} for video in vid_info_list if video}
