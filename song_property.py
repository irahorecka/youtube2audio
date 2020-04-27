import requests
import json
import itunespy
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, TCOM, TCON, TDRC
from PIL import Image
from io import BytesIO
import os

song_dir = os.path.join(os.getcwd(), 'Another Summer')
os.chdir(song_dir)

def get_from_itunes(SONG_NAME):
    """Try to download the metadata using itunespy."""
    # Try to get the song data from itunes
    try:
        SONG_INFO = itunespy.search_track(SONG_NAME)
        # Before returning convert all the track_time values to minutes.
        for song in SONG_INFO:
            song.track_time = round(song.track_time / 60000, 2)
        return SONG_INFO
    except Exception:
        pass

def get_metadata(url):
    # KEY https://www.youtube.com/oembed?url={}&format=json
    URL_KEY = "https://www.youtube.com/oembed?url={}&format=json"
    content = requests.get(URL_KEY.format(url))
    json_content = content.json()

    # print(json_content)

    SONG_META = get_from_itunes(json_content['title'])[0]
    SONG_META_JSON = {
        'track_name': SONG_META.track_name,
        'artist_name': SONG_META.artist_name,
        'album_name': SONG_META.collection_name,
        'primary_genre_name': SONG_META.primary_genre_name,
        'artwork_url_fullres': SONG_META.artwork_url_60.replace('60', '600'), # manually replace album artwork to 600x600
    }

    return SONG_META_JSON

def get_song_properties(url):
    SONG_META_JSON = get_metadata(url)
    response = requests.get(SONG_META_JSON['artwork_url_fullres'])
    img = response.content
    SONG_META_JSON['artwork_url_fullres'] = img
    return SONG_META_JSON

if __name__ == '__main__':
    dear_breeze_url = 'https://www.youtube.com/watch?v=mOhaWdKI42E&list=OLAK5uy_m7J5sA6lRSaZ-8Ozc0TnLHA1lck46wHRg&index=3&t=0s'
    SONG_META_JSON = get_song_properties(dear_breeze_url)
    file_mp3 = "DEAR BREEZE.mp3"

    audio = MP3(os.path.join(song_dir, file_mp3), ID3=ID3)    
    audio.tags.add(
        APIC(
            encoding=3, # 3 is for utf-8
            mime='image/jpeg', # image/jpeg or image/png
            type=3, # 3 is for the cover image
            desc=u'Cover',
            data=SONG_META_JSON['artwork_url_fullres']
        )
    )
    audio["TALB"] = TALB(encoding=3, text=SONG_META_JSON['album_name'])
    audio["TPE1"] = TPE1(encoding=3, text=SONG_META_JSON['artist_name'])
    audio["TIT2"] = TIT2(encoding=3, text=SONG_META_JSON['track_name'])
    audio["TCON"] = TCON(encoding=3, text=SONG_META_JSON['primary_genre_name'])
    audio.save()

# SONG_META = {
#     'artist_name': 
# }

# """
# Python module to search gaana.com using their API.
# Uses api.gaana.com to get search results.
# """

# # import requests

# # Define the base url
# base_url = "http://api.gaana.com/?type=search&subtype=search_song&key={}&token=b2e6d7fbc136547a940516e9b77e5990&format=JSON"

# SONG = []


# class GaanaSongs():
#     """Class to store gaana song tags."""

#     def __init__(self, SONG):
#         """SONG is supposed to be a dict."""
#         self.track_name = SONG['track_title']
#         self.release_date = SONG['release_date']
#         self.artist_name = SONG['artist'][0]['name']
#         self.collection_name = SONG['album_title']
#         self.primary_genre_name = SONG['gener'][0]['name']
#         self.track_number = '1'
#         self.artwork_url_100 = SONG['artwork_large']
#         self.track_time = self._convert_time(SONG['duration'])

#     def _convert_time(self, duration):
#         in_min = int(duration)
#         in_time = int(in_min / 60) + (0.01 * (in_min % 60))
#         return in_time


# def searchSong(querry, lim=40):
#     """Nanan."""
#     url = base_url.format(querry)
#     r = requests.get(url)
#     data = r.json()
#     data = data['tracks']
#     SONG_TUPLE = []

#     for i in range(0, len(data)):
#         song_obj = GaanaSongs(data[i])
#         SONG_TUPLE.append(song_obj)

#     return SONG_TUPLE


# if __name__ == '__main__':
#     q = "Breathe in the Air"
#     dat = searchSong(q)
#     for i in range(0, len(dat)):
#         print(dat[i].collection_name)