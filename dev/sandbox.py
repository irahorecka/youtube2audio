from pytube import YouTube, Playlist
import youtube_dl
from _threading import map_threads
import time

from functools import partial


def timer(method):
    def wrapper(*args, **kwargs):
        t0 = time.time()
        method(*args, **kwargs)
        t1 = time.time()
        print("%.2f" % (t1 - t0))

    return wrapper


# @timer
# def run(playlist_url):
#     '''ydl_opts = {"ignoreerrors": True, "quiet": True}
#     videos_dict = dict()
#     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#         playlist_dict = ydl.extract_info(
#             playlist_url, download=False
#         )'''
#     playlist = Playlist(playlist_url)
#     print('Number of videos in playlist: %s' % len(playlist.video_urls))
#     print(playlist.video_urls)
#     vid_tup = tuple(video for video in playlist.video_urls)

#     x = map_threads(thread_this, vid_tup)


def thread_this(url):
    ydl_opts = {"ignoreerrors": True, "quiet": True}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ab = ydl.extract_info(url, download=False)  # time
    return ab

    # video = YouTube(url)
    # print(video.title)
    # print(video.video_id)


# @timer
def run_playlist(playlist_url):
    playlist = Playlist(playlist_url)
    print("Number of videos in playlist: %s" % len(playlist.video_urls))
    print(playlist.video_urls)
    vid_tup = tuple(video for video in playlist.video_urls)

    ab = map_threads(thread_this, vid_tup)
    vid_dict = {}
    for i in list(ab):
        title = i["title"]
        vid_dict[title] = {}
        vid_dict[title]["id"] = i["id"]
        vid_dict[title]["duration"] = i["duration"]

    print(vid_dict)


if __name__ == "__main__":
    # run('https://www.youtube.com/playlist?list=PLFIhsqj9dojq97bzw4fapbWsmIm37KtO2')
    run_playlist(
        "https://www.youtube.com/playlist?list=PLFIhsqj9dojq97bzw4fapbWsmIm37KtO2"
    )
    # print(ab)
