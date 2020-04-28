import requests
import json
import itunespy
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TALB, TPE1, TIT2, TCON, error


def get_itunes_metadata(vid_url):
    """Get iTunes metadata to add to mp3 file."""

    # oEmbed is a format for allowing an embedded representation
    # of a URL on third party sites.
    oembed_url = "https://www.youtube.com/oembed?url={}&format=json"
    vid_content = requests.get(oembed_url.format(vid_url))
    vid_json = vid_content.json()

    try:
        ITUNES_META = get_from_itunes(vid_json["title"])[0]
        ITUNES_META_JSON = {
            "track_name": ITUNES_META.track_name,
            "album_name": ITUNES_META.collection_name,
            "artist_name": ITUNES_META.artist_name,
            "primary_genre_name": ITUNES_META.primary_genre_name,
            "artwork_url_fullres": ITUNES_META.artwork_url_60.replace(
                "60", "600"
            ),  # manually replace album artwork to 600x600
        }
    except TypeError:  # i.e. no information fetched from get_from_itunes
        return

    def get_album_artwork():
        """Get album artwork from iTunes album artwork url."""
        response = requests.get(ITUNES_META_JSON["artwork_url_fullres"])
        album_img = response.content
        ITUNES_META_JSON["artwork_url_fullres"] = album_img

        return ITUNES_META_JSON

    return get_album_artwork()


def get_from_itunes(song_properties):
    """Download video metadata using itunespy."""
    try:
        song_itunes = itunespy.search_track(song_properties)
        # Before returning convert all the track_time values to minutes.
        for song in song_itunes:
            song.track_time = round(song.track_time / 60000, 2)
        return song_itunes
    except Exception:
        return
