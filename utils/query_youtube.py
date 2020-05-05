import youtube_dl
from pytube import Playlist
from ._threading import map_threads


def get_youtube_content(youtube_url):
    """Str parse YouTube url and call appropriate functions
    to execute url content."""
    if ".com/playlist" in youtube_url:
        url_tuple = get_playlist_video_urls(youtube_url)
        video_genr = map_threads(get_video_info, url_tuple)
        video_info = list(video_genr)
    else:
        adj_youtube_url = youtube_url.split("&")[0]  # trim ascii encoding &
        video_json = get_video_info(adj_youtube_url)
        video_info = []
        video_info.append(video_json)  # append single video to index-able dtype

    video_dict = video_content_to_dict(video_info)

    return video_dict


def get_playlist_video_urls(playlist_url):
    """Get url of videos in a YouTube playlist."""
    playlist = Playlist(playlist_url)
    vid_tuple = tuple(video for video in playlist.video_urls)

    return vid_tuple


def get_video_info(video_url):
    """Get YouTube video metadata."""
    ydl_opts = {"ignoreerrors": False, "quiet": True}
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(video_url, download=False)
    except youtube_dl.utils.DownloadError:  # video unavailable
        return

    return video_info


def video_content_to_dict(vid_info_list):
    """Convert YouTube metadata list to dictionary."""
    video_dict = {}
    for video in vid_info_list:
        if not video:
            continue
        title = video["title"]
        video_dict[title] = {}
        video_dict[title]["id"] = video["id"]
        video_dict[title]["duration"] = video["duration"]

    return video_dict
