import requests
import json
import itunespy


def get_itunes_metadata(vid_url):
    """Get iTunes metadata to add to mp3 file."""
    vid_title = oembed_title(vid_url)
    try:
        ITUNES_META = get_from_itunes(vid_title)[0]
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
        ITUNES_META_JSON["artwork_bytes_fullres"] = album_img

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


def oembed_title(vid_url):
    """Get YouTube video title information if input str
    is a url - else return input descriptor str from
    get_itunes_metadata."""
    if vid_url.startswith("https://"):
        # oEmbed is a format for allowing an embedded representation
        # of a URL on third party sites.
        oembed_url = "https://www.youtube.com/oembed?url={}&format=json"
        vid_content = requests.get(oembed_url.format(vid_url))
        vid_json = vid_content.json()
        vid_title = vid_json["title"]
        return vid_title
    else:
        raise TypeError("vid_url must be a URL string.")
