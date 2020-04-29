import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TALB, TPE1, TIT2, TCON, error
import requests
import shutil
import subprocess
import sys
import time
import concurrent.futures
from functools import partial
import youtube_dl
from pytube import YouTube
from PyQt5.QtCore import QThread, QPersistentModelIndex, pyqtSignal
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from ytpd_beta import Ui_MainWindow as UiMainWindow
from itunes_annotate import get_itunes_metadata


def seconds_to_mmss(seconds):
    """Function:
    Returns a string in the format of mm:ss"""
    min = seconds // 60
    sec = seconds % 60
    if min < 10:
        min_str = "0" + str(min)
    else:
        min_str = str(min)
    if sec < 10:
        sec_str = "0" + str(sec)
    else:
        sec_str = str(sec)
    return min_str + ":" + sec_str


class UrlLoading(QThread):
    """ Loads the videos data from playlist in another thread."""

    countChanged = pyqtSignal(dict, bool)

    def __init__(self, playlist_link, parent=None):
        QThread.__init__(self, parent)
        self.playlist_link = playlist_link

    def run(self):
        """ Main function, gets all the playlist videos data, emits the info dict"""
        ydl_opts = {"ignoreerrors": True, "quiet": True}
        videos_dict = dict()
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                playlist_dict = ydl.extract_info(
                    self.playlist_link, download=False
                )  # time consuming spot -- cannot thread
                for video in playlist_dict["entries"]:
                    try:
                        title = video.get("title")
                    except:  # If video title is unavailable don't add it to the dict
                        continue
                    videos_dict[title] = dict()
                    videos_dict[title]["id"] = video.get("id")
                    videos_dict[title]["duration"] = seconds_to_mmss(
                        video.get("duration")
                    )
                self.countChanged.emit(videos_dict, True)
        except:
            self.countChanged.emit({}, False)


class MainPage(QMainWindow, UiMainWindow):
    def __init__(self, parent=None):
        super(MainPage, self).__init__(parent)
        self.setupUi(self)
        # Hide the fetching data label and the error label, shows up when its loading, invalid url
        self.url_fetching_data_label.hide()
        self.url_error_label.hide()
        # Seting the videos dict. and connecting the delete video button with the remove_selected_items fn.
        self.remove_from_table_button.clicked.connect(self.remove_selected_items)
        self.set_album.clicked.connect(partial(self.set_column_val, column_index=1))
        self.set_artist.clicked.connect(partial(self.set_column_val, column_index=2))
        self.set_genre.clicked.connect(partial(self.set_column_val, column_index=3))
        self.set_artwork.clicked.connect(partial(self.set_column_val, column_index=4))
        self.videos_dict = dict()
        # Buttons Connection with the appropriate functions
        self.url_load_button.clicked.connect(self.url_loading_button_click)
        self.download_button.clicked.connect(self.download_button_click)
        self.download_path.clicked.connect(self.get_file_dir)
        self.itunes_annotate.clicked.connect(self.itunes_annotate_table)
        self.revert_annotate.clicked.connect(self.default_annotate_table)
        self.video_table.cellClicked.connect(self.artwork_display)
        # Hide buttons
        self.revert_annotate.hide()
        # Get the desktop path, set folder name, full download path, set label.
        self.download_dir = os.path.dirname(
            os.path.abspath(__file__)
        )  # base no-selection download dir
        self.download_folder_select.setText(
            "Folder: ../{}".format([i for i in self.download_dir.split("/")][-1])
        )

    # Input url threading

    def url_loading_button_click(self):
        """ Reads input data from url_input and creates an instance of the UrlLoading thread """
        self.videos_dict = dict()  # Clear the dict
        self.url_fetching_data_label.show()  # Show the loading label
        self.url_error_label.hide()  # Hide the error label if the input is a retry
        playlist_url = self.url_input.text()  # Get the input text
        self.calc = UrlLoading(playlist_url)  # Pass in the input text
        self.calc.countChanged.connect(
            self.url_loading_finished
        )  # connect with the changing variables
        self.calc.start()

    def url_loading_finished(self, videos_dict, executed):
        # First entry of self.videos_dict in MainPage class
        self.videos_dict = videos_dict
        """ Retrieves data from thread at the end, updates the list"""
        self.url_fetching_data_label.hide()  # Hide the loading label as it has finished loading
        if executed:  # If it was executed successfully
            self.default_annotate_table()
        else:
            self.url_error_label.show()  # Show the error label

    def artwork_display(self, row, column):
        """Display selected artwork and self.video_info_input on Qpixmap widget."""
        # artwork
        try:
            artwork_file = self.video_table.item(row, 4).text()
            response = requests.get(artwork_file)
            artwork_img = response.content
            qt_artwork_img = QtGui.QImage()
            qt_artwork_img.loadFromData(artwork_img)
            self.album_artwork.setPixmap(QtGui.QPixmap.fromImage(qt_artwork_img))
        except (
            AttributeError,
            requests.exceptions.MissingSchema,
        ):  # i.e. selected empty cell or cell has non-url str
            self.album_artwork.setPixmap(QtGui.QPixmap("default_artwork.png"))

        # self.video_info_input
        try:
            self.video_info_input.setText(self.video_table.item(row, column).text())
        except AttributeError:
            self.video_info_input.setText("")

        self.album_artwork.setScaledContents(True)
        self.album_artwork.setAlignment(QtCore.Qt.AlignCenter)

    def itunes_annotate_table(self):
        """Get YouTube video url."""
        yt_link_starter = "https://www.youtube.com/watch?v="
        for row_index, key_value in enumerate(self.videos_dict.items()):
            url_id = key_value[1]["id"]
            vid_url = yt_link_starter + url_id
            self.set_itunes_meta(vid_url, row_index)
        self.itunes_annotate.hide()
        self.revert_annotate.show()

    def set_itunes_meta(self, vid_url, row_index):
        """Provide iTunes annotation guess based on video title"""
        ITUNES_META_JSON = get_itunes_metadata(vid_url)
        try:
            song_name, song_index = ITUNES_META_JSON["track_name"], 0
            album_name, album_index = ITUNES_META_JSON["album_name"], 1
            artist_name, artist_index = ITUNES_META_JSON["artist_name"], 2
            genre_name, genre_index = ITUNES_META_JSON["primary_genre_name"], 3
            artwork_name, artwork_index = ITUNES_META_JSON["artwork_url_fullres"], 4
        except TypeError:
            song_name, song_index = (
                self.video_table.item(row_index, 0).text(),
                0,
            )  # get video title
            album_name, album_index = "Unknown", 1
            artist_name, artist_index = "Unknown", 2
            genre_name, genre_index = "Unknown", 3
            artwork_name, artwork_index = "default_artwork.png", 4
        self.video_table.setItem(row_index, song_index, QTableWidgetItem(song_name))
        self.video_table.setItem(row_index, album_index, QTableWidgetItem(album_name))
        self.video_table.setItem(row_index, artist_index, QTableWidgetItem(artist_name))
        self.video_table.setItem(row_index, genre_index, QTableWidgetItem(genre_name))
        self.video_table.setItem(
            row_index, artwork_index, QTableWidgetItem(artwork_name)
        )

    def default_annotate_table(self):
        """Default table annotation to video title in song columns"""
        for index, key in enumerate(self.videos_dict):
            self.video_table.setItem(index, 0, QTableWidgetItem(key))  # part of QWidget
            self.video_table.setItem(index, 1, QTableWidgetItem("Unknown"))
            self.video_table.setItem(index, 2, QTableWidgetItem("Unknown"))
            self.video_table.setItem(index, 3, QTableWidgetItem("Unknown"))
            self.video_table.setItem(index, 4, QTableWidgetItem("default_artwork.png"))
        self.revert_annotate.hide()
        self.itunes_annotate.show()

    def get_file_dir(self):
        """Fetch download file path"""
        self.download_dir = QFileDialog.getExistingDirectory(
            self, "Open folder", os.path.dirname(os.path.abspath(__file__))
        )
        # set nearby names
        self.download_folder_select.setText(
            "Folder: ../{}".format(
                "/".join([i for i in self.download_dir.split("/")][-2:])
            )
        )

    def set_column_val(self, column_index):
        """Set cell content in album, artist, genre, and artwork
        columns based on cell selection or selected cell content."""
        rows = self.video_table.rowCount()
        try:
            for row_index in range(rows):
                item = self.video_table.item(
                    row_index, 0
                )  # get value from col 0 ('song')
                if item and item.text():
                    self.video_table.setItem(
                        row_index,
                        column_index,
                        QTableWidgetItem(self.video_info_input.text()),
                    )  # part of QWidget
        except AttributeError:  # i.e. empty self.video_info_input
            pass

    def download_button_click(self):
        """ Executes when the button is clicked """
        self.download_button.setEnabled(False)
        self.downloaded_label.setText("Downloading...")
        self.down = DownloadingVideos(
            self.videos_dict, self.download_dir
        )  # Pass in the dict
        self.down.start()
        # TODO: Fix this below -- be able to reflect emission
        self.downloaded_label = self.down.downloadCount

    def remove_selected_items(self):
        """Removes the selected items from self.videos_table and self.videos_dict.
        Table widget updates -- multiple row deletion capable."""
        index_list = []
        video_list = [key_value for key_value in self.videos_dict.items()]
        for model_index in self.video_table.selectionModel().selectedRows():
            row = model_index.row()
            index = QPersistentModelIndex(model_index)
            index_list.append(index)
            current_key = video_list[row][0]
            del self.videos_dict[current_key]  # remove row item from self.videos_dict

        for index in index_list:
            self.video_table.removeRow(index.row())


class DownloadingVideos(QThread):
    """ Download all videos from the videos_dict using the id, todo fix some bugs"""

    downloadCount = pyqtSignal(str)  # downloaded, number_of_videos, finished

    def __init__(self, videos_dict, download_path, parent=None):
        QThread.__init__(self, parent)
        self.videos_dict = videos_dict
        self.download_path = download_path

    def run(self):
        """ Main function, downloads videos by their id while emitting progress data"""

        # Download
        number_of_videos = len(self.videos_dict)
        failed_download = list()
        time0 = time.time()

        video_properties = (
            ((key, value), self.download_path)
            for key, value in self.videos_dict.items()
        )
        streams = download_threads(video_download, video_properties)
        shutil.rmtree(os.path.join(self.download_path, "mp4"))  # remove mp4 from dir

        time1 = time.time()

        delta_t = time1 - time0
        print(delta_t)
        self.downloadCount.emit(f"Download time: {'%.2f' % delta_t} seconds")


def download_threads(transform, iterable):
    # TODO: look into partial issue with deadlock
    with concurrent.futures.ThreadPoolExecutor() as executor:
        streams = executor.map(transform, iterable, timeout=1)
    return streams


def video_download(args):
    yt_link_starter = "https://www.youtube.com/watch?v="
    # NOTE: this must have no relation to any self obj
    key_value, videos_dict = args[0]
    download_path = args[1]
    full_link = yt_link_starter + videos_dict["id"]

    try:
        # TODO: could be strange to create new folder/path in multithread - no collision yet but maybe a source of a bug
        mp4_path = os.path.join(download_path, "mp4")
        video = YouTube(full_link)
        stream = video.streams.filter(only_audio=True, audio_codec="mp4a.40.2").first()
        stream.download(mp4_path)

        # convert generated mp4 files to mp3 -- problem with MacOS where mp4 is twice length of video
        mp4_filename = stream.default_filename  # mp4 full extension
        mp3_filename = "{}.mp3".format(mp4_filename[:-4])
        filename = mp4_filename[:-4]

        subprocess.call(
            [
                "ffmpeg",
                "-i",
                os.path.join(mp4_path, mp4_filename),
                os.path.join(download_path, mp3_filename),
            ]
        )
        set_song_properties(download_path, full_link, filename)

        return
    except:
        pass


def set_song_properties(directory, vid_url, vid_name):
    # TODO: look at table for annotated information to query to iTunes for appropriate metadatas
    """Set song properties to MP3 file."""
    file_mp3 = f"{vid_name}.mp3"
    ITUNES_META_JSON = get_itunes_metadata(vid_url)

    audio = MP3(os.path.join(directory, file_mp3), ID3=ID3)
    audio.tags.add(
        APIC(
            encoding=3,  # 3 is for utf-8
            mime="image/jpeg",  # image/jpeg or image/png
            type=3,  # 3 is for the cover image
            desc="Cover",
            data=ITUNES_META_JSON["artwork_bytes_fullres"],
        )
    )
    audio["TALB"] = TALB(encoding=3, text=ITUNES_META_JSON["album_name"])
    audio["TPE1"] = TPE1(encoding=3, text=ITUNES_META_JSON["artist_name"])
    audio["TIT2"] = TIT2(encoding=3, text=ITUNES_META_JSON["track_name"])
    audio["TCON"] = TCON(encoding=3, text=ITUNES_META_JSON["primary_genre_name"])
    audio.save()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainPage()
    widget.show()
    sys.exit(app.exec_())
