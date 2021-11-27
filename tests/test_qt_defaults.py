"""Test default (static) state of the application upon boot."""
import os
import sys
import unittest
from PyQt5.QtWidgets import QApplication

# get directory to main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main

app = QApplication(sys.argv)


class testMain(unittest.TestCase):
    """Test the main GUI for default properties."""

    def setUp(self):
        self.form = main.MainPage()

    def test_video_table_defaults(self):
        """Test default content of self.video_table -- should be empty"""
        row_count = 250
        column_count = 5
        self.assertEqual(self.form.video_table.rowCount(), row_count)
        self.assertEqual(self.form.video_table.columnCount(), column_count)

        # ensure empty table upon start
        for row in range(row_count):
            for column in range(column_count):
                self.assertEqual(self.form.video_table.item(row, column), None)

    def test_user_input_defaults(self):
        """Test default inputs for users."""
        default_download_dir = self.form._get_parent_current_dir(self.form.download_dir)
        self.assertEqual(self.form.download_folder_select.text(), default_download_dir)
        self.assertEqual(self.form.url_input.text(), "")
        self.assertEqual(self.form.video_info_input.text(), "")

    def test_button_labels(self):
        """Test default button labels on GUI"""
        self.assertEqual(self.form.cancel_button.text(), "Cancel")
        self.assertEqual(self.form.change_video_info_input.text(), "Replace")
        self.assertEqual(self.form.change_video_info_input_all.text(), "Replace all")
        self.assertEqual(self.form.download_button.text(), "Download")
        self.assertEqual(self.form.download_path.text(), "Select")
        self.assertEqual(self.form.itunes_annotate.text(), "Ask butler")
        self.assertEqual(self.form.revert_annotate.text(), "Go back")
        self.assertEqual(self.form.save_as_mp3_box.text(), "MP3")
        self.assertEqual(self.form.save_as_mp4_box.text(), "MP4")
        self.assertEqual(self.form.url_load_button.text(), "Load")

    def test_label_labels(self):
        """Test default labels on GUI"""
        self.assertEqual(self.form.download_folder_label.text(), "Download folder")
        self.assertEqual(self.form.download_status.text(), "")
        self.assertEqual(self.form.enter_playlist_url_label.text(), "Playlist or video URL")
        self.assertEqual(self.form.save_filetype.text(), "Save as:")
        self.assertEqual(self.form.title_label.text(), "YouTube to Audio")
        self.assertEqual(self.form.url_fetching_data_label.text(), "Loading...")
        self.assertEqual(self.form.url_error_label.text(), "Could not get URL. Try again.")
        self.assertEqual(self.form.url_poor_connection.text(), "Poor internet connection.")
        self.assertEqual(self.form.url_reattempt_load_label.text(), "Reattempting load...")

    def test_artwork_label(self):
        """Test default artwork label"""
        self.assertEqual(self.form.album_artwork.text(), "")

    def test_hyperlink_label(self):
        """Test default label on source code hyperlink"""
        self.assertEqual(
            self.form.credit_url.text(),
            '<a href="https://github.com/irahorecka/YouTube2Mp3">source code</a>',
        )


if __name__ == "__main__":
    unittest.main()
