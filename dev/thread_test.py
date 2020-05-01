import time
import concurrent.futures
import requests


def multi_thread(transform, _iterable):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        streams = executor.map(transform, _iterable, timeout=1)
    return streams


def video_download(args):
    """Download video to mp4 then mp3 -- triggered
    by pool_threads"""
    yt_link_starter = "https://www.youtube.com/watch?v="
    # NOTE: this must have no relation to any self obj
    key_value, videos_dict = args[0]
    download_path, mp4_path = args[1]
    song_properties = args[2]
    full_link = yt_link_starter + videos_dict["id"]

    # TODO: could be strange to create new folder/path in multithread - no collision yet but maybe a source of a bug
    video = YouTube(full_link)  # YOUTUBE IS THE CULPRIT HERE
    # video = requests.get('https://stackoverflow.com/questions/19699165/how-does-the-callback-function-work-in-multiprocessing-map-async')
    print(video)
    stream = video.streams.filter(only_audio=True, audio_codec="mp4a.40.2").first()
    stream.download(mp4_path)

    print(stream)

    # convert generated mp4 files to mp3 -- problem with MacOS where mp4 is twice length of video
    mp4_filename = stream.default_filename  # mp4 full extension
    filename = mp4_filename[:-4]
    mp3_filename = "{}.mp3".format(song_properties["song"])

    subprocess.call(
        [
            "ffmpeg",
            "-i",
            os.path.join(mp4_path, mp4_filename),
            os.path.join(download_path, mp3_filename),
        ]
    )
    set_song_properties(download_path, song_properties, filename)

    return

def time_sleep_1(arg):
    time.sleep(1)
    print(arg)


class Multi():
    def __init__(self):
        self.x = tuple(i for i in range(10))
        self.arg = ((('Yuna Ito   Stuck on you', {'id': 'fmmty1rXzI8', 'duration': '04:23'}), ('/Users/irahorecka/Desktop/Harddrive_Desktop/Python/YouTube2Mp3', '/Users/irahorecka/Desktop/Harddrive_Desktop/Python/YouTube2Mp3/mp4'), {'song': 'Yuna Ito   Stuck on you', 'album': 'Unknown', 'artist': 'Unknown', 'genre': 'Unknown', 'artwork': ''}), (('ここにいるよ（ko ko ni i ru yo)', {'id': 'rpupcoOmsSY', 'duration': '05:27'}), ('/Users/irahorecka/Desktop/Harddrive_Desktop/Python/YouTube2Mp3', '/Users/irahorecka/Desktop/Harddrive_Desktop/Python/YouTube2Mp3/mp4'), {'song': 'ここにいるよ（ko ko ni i ru yo)', 'album': 'Unknown', 'artist': 'Unknown', 'genre': 'Unknown', 'artwork': ''}))

    def run(self):
        multi_thread(video_download, self.arg)
        multi_thread(time_sleep_1, self.x)