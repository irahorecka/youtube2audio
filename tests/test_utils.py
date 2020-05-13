"""Test functions in utils/ directory"""
import os
import sys
import unittest

# get base directory and import util files
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import _threading, download_youtube, query_itunes, query_youtube


class testThreading(unittest.TestCase):
    """Test utils/_threading.py"""

    def setUp(self):
        import time

    def example_func_for_threading(self, value):
        """Example function for testing threading"""
        value_sum_one = value + 1

        return value_sum_one

    def test_threading(self):
        """Test _threading.map_threads for proper threading functionality"""
        iterable = [i for i in range(500)]
        total_value_sum_one = _threading.map_threads(
            self.example_func_for_threading, iterable
        )
        self.assertEqual(len(list(total_value_sum_one)), 500)


class testYouTubeQuery(unittest.TestCase):
    """Test utils/youtube_query.py"""

    def setUp(self):
        self.playlist_url = (
            "https://www.youtube.com/playlist?list=PL-UWPlRIl68oSg7qsGbVRh56bsdCbDLiU"
        )
        self.video_url = "https://www.youtube.com/watch?v=ixGrA0dQKeI&list=PL-UWPlRIl68oSg7qsGbVRh56bsdCbDLiU&index=2&t=0s"
        self.video_info_list = [
            {"title": "Test1", "id": 1, "duration": 100},
            {"title": "Test2", "id": 2, "duration": 200},
        ]

    def test_get_youtube_playlist_content_false_override(self):
        """Test query_youtube.get_youtube_content with false error override
        for a playlist url"""
        override_error = False
        try:
            youtube_video_dict = query_youtube.get_youtube_content(
                self.playlist_url, override_error
            )
        except RuntimeError:  # successfully threw RuntimeError
            youtube_video_dict = {}
            pass
        self.assertIsInstance(youtube_video_dict, dict)

    def test_get_youtube_video_content_false_override(self):
        """Test query_youtube.get_youtube_content with false error override
        for a video url"""
        override_error = False
        try:
            youtube_video_dict = query_youtube.get_youtube_content(
                self.video_url, override_error
            )
        except RuntimeError:
            youtube_video_dict = {}
            pass
        self.assertIsInstance(youtube_video_dict, dict)

    def test_get_youtube_playlist_content_true_override(self):
        """Test query_youtube.get_youtube_content with error override
        for a playlist url"""
        override_error = True
        youtube_video_dict = query_youtube.get_youtube_content(
            self.playlist_url, override_error
        )
        self.assertIsInstance(youtube_video_dict, dict)

    def test_get_youtube_video_content_true_override(self):
        """Test query_youtube.get_youtube_content with error override
        for a video url"""
        override_error = True
        youtube_video_dict = query_youtube.get_youtube_content(
            self.video_url, override_error
        )
        self.assertIsInstance(youtube_video_dict, dict)

    def test_get_playlist_video_info(self):
        """Test fetching individual urls in a playlist url"""
        youtube_playlist_videos_tuple = query_youtube.get_playlist_video_info(
            self.playlist_url
        )
        self.assertIsInstance(youtube_playlist_videos_tuple, tuple)

    def test_get_video_info_false_override(self):
        """Test getting video information with false error override"""
        override_error = False
        args = (self.video_url, override_error)
        try:
            video_info = query_youtube.get_video_info(args)
        except RuntimeError:
            video_info = {}
        self.assertIsInstance(video_info, dict)

    def test_get_video_info_true_override(self):
        """Test getting video information with error override"""
        override_error = True
        args = (self.video_url, override_error)
        video_info = query_youtube.get_video_info(args)
        self.assertIsInstance(video_info, dict)

    def test_video_content_to_dict(self):
        """Test a list of video info dictionaries is successfully converted
        to a dict type"""
        video_list_to_dict = query_youtube.video_content_to_dict(self.video_info_list)
        self.assertIsInstance(video_list_to_dict, dict)


class testiTunesQuery(unittest.TestCase):
    """Test utils/itunes_query.py"""

    def setUp(self):
        # threading is accomplished in main.py
        self.youtube_video_key_value = (
            "Bob Marley - Blackman Redemption",
            {"id": "KlmPOxwoC6Y", "duration": 212},
        )
        self.row_index = 0
        self.video_url_for_oembed = "https://www.youtube.com/watch?v=KlmPOxwoC6Y"

    def test_thread_query_itunes(self):
        """Test accurate parsing of youtube video url to retrieve
        iTunes metadata."""
        args = (self.row_index, self.youtube_video_key_value)
        itunes_return_arg = query_itunes.thread_query_itunes(args)
        return_row_index = itunes_return_arg[0]
        return_itunes_json = itunes_return_arg[1]

        self.assertEqual(return_row_index, 0)
        self.assertIsInstance(return_itunes_json, dict)

    def test_get_itunes_metadata(self):
        """Test retrieving iTunes metadata as a high level function"""
        itunes_meta_data = query_itunes.get_itunes_metadata(self.video_url_for_oembed)
        self.assertIsInstance(itunes_meta_data, dict)

    def test_oembed_title_non_url(self):
        """Test converting a non-url string to oembed. Should raise
        TypeError"""
        with self.assertRaises(TypeError):
            query_itunes.oembed_title("invalid_url")

    def test_oembed_title_url(self):
        """Test the conversion of a youtube video url to an oembed format
        for simple extraction of video information."""
        video_title = query_itunes.oembed_title(self.video_url_for_oembed)
        self.assertIsInstance(video_title, str)

    def test_query_itunes(self):
        """Test low level function to fetch iTunes metadata based on the
        youtube video title."""
        youtube_video_title = self.youtube_video_key_value[0]
        itunes_query_results = query_itunes.query_itunes(youtube_video_title)
        self.assertIsInstance(itunes_query_results, list)


class testYouTubeDownload(unittest.TestCase):
    """Test utils/download_youtube.py"""

    def setUp(self):
        self.mp3_args_for_thread_query_youtube = (
            ("No Time This Time - The Police", {"id": "nbXACcsTn84", "duration": 198}),
            (
                "/Users/irahorecka/Desktop/Harddrive_Desktop/Python/YouTube2Audio/tests",
                "/Users/irahorecka/Desktop/Harddrive_Desktop/Python/YouTube2Audio/tests/mp4",
            ),
            {
                "song": "No Time This Time",
                "album": "Reggatta de Blanc (Remastered)",
                "artist": "The Police",
                "genre": "Rock",
                "artwork": "https://is2-ssl.mzstatic.com/image/thumb/Music128/v4/21/94/c7/2194c796-c7f0-2c4b-2f94-ac247bab22a5/source/600x600bb.jpg",
            },
            False,
        )
        self.mp4_args_for_thread_query_youtube = (
            ("No Time This Time - The Police", {"id": "nbXACcsTn84", "duration": 198}),
            (
                "/Users/irahorecka/Desktop/Harddrive_Desktop/Python/YouTube2Audio/tests",
                "/Users/irahorecka/Desktop/Harddrive_Desktop/Python/YouTube2Audio/tests/mp4",
            ),
            {
                "song": "No Time This Time",
                "album": "Reggatta de Blanc (Remastered)",
                "artist": "The Police",
                "genre": "Rock",
                "artwork": "https://is2-ssl.mzstatic.com/image/thumb/Music128/v4/21/94/c7/2194c796-c7f0-2c4b-2f94-ac247bab22a5/source/600x600bb.jpg",
            },
            True,
        )
        self.mp3_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "No Time This Time.mp3"
        )
        self.m4a_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "No Time This Time.m4a"
        )

    def test_get_youtube_mp4(self):
        """Test download of mp4 file (m4a) using the setUp var above"""
        download_youtube.thread_query_youtube(self.mp4_args_for_thread_query_youtube)
        assert os.path.exists(self.m4a_file_path) == True
        os.remove(self.m4a_file_path)  # remove generated m4a file

    def test_get_youtube_mp3(self):
        """Test download of mp3 file (mp3) using the setUp var above"""
        download_youtube.thread_query_youtube(self.mp3_args_for_thread_query_youtube)
        assert os.path.exists(self.mp3_file_path) == True
        os.remove(self.mp3_file_path)  # remove generated mp3 file

    def tearDown(self):
        import shutil

        shutil.rmtree(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "mp4")
        )  # remove mp4 dir

    # TODO: add tests for mp3 and mp4 annotations -- above tests are for high-level functions.


if __name__ == "__main__":
    unittest.main()
