import os
import shutil
import sys
import time
from functools import partial
import requests
from PyQt5.QtCore import QThread, QPersistentModelIndex, pyqtSignal
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QTableWidgetItem
from ytpd_beta import Ui_MainWindow as UiMainWindow
from _threading import map_threads
from query_itunes import thread_query_itunes
from query_youtube import thread_query_youtube, get_playlist_videos


class UrlLoading(QThread):
    """ Loads the videos data from playlist in another thread."""

    countChanged = pyqtSignal(dict, bool)

    def __init__(self, playlist_link, parent=None):
        QThread.__init__(self, parent)
        self.playlist_link = playlist_link

    def run(self):
        """ Main function, gets all the playlist videos data, emits the info dict"""
        try:
            videos_dict = get_playlist_videos(self.playlist_link)
            self.countChanged.emit(videos_dict, True)
        except Exception as error:
            print(error)
            self.countChanged.emit({}, False)


class MainPage(QMainWindow, UiMainWindow):
    def __init__(self, parent=None):
        super(MainPage, self).__init__(parent)
        self.setupUi(self)
        # Hide the fetching data label, error label, and revert button
        self.url_fetching_data_label.hide()
        self.url_error_label.hide()
        self.revert_annotate.hide()
        # Connect the delete video button with the remove_selected_items fn.
        self.remove_from_table_button.clicked.connect(self.remove_selected_items)
        # Connect song property setter buttons.
        self.set_album.clicked.connect(partial(self.set_column_val, column_index=1))
        self.set_artist.clicked.connect(partial(self.set_column_val, column_index=2))
        self.set_genre.clicked.connect(partial(self.set_column_val, column_index=3))
        self.set_artwork.clicked.connect(partial(self.set_column_val, column_index=4))
        # Buttons connection with the appropriate functions
        self.url_load_button.clicked.connect(self.url_loading_button_click)
        self.download_button.clicked.connect(self.download_button_click)
        self.download_path.clicked.connect(self.get_file_dir)
        self.itunes_annotate.clicked.connect(self.itunes_annotate_click)
        self.revert_annotate.clicked.connect(self.default_annotate_table)
        self.video_table.cellClicked.connect(self.artwork_display)
        # Input changes in video property text box to appropriate cell.
        self.change_video_info_input.clicked.connect(self.change_cell)
        # Exit application
        self.cancel_button.clicked.connect(self.close)
        # Get the desktop path, set folder name, full download path, set label.
        self.download_dir = os.path.dirname(
            os.path.abspath(__file__)
        )  # base :: no-selection download dir
        self.download_folder_select.setText(
            "Folder: ../{}".format([i for i in self.download_dir.split("/")][-1])
        )

    def url_loading_button_click(self):
        """ Reads input data from url_input and creates an instance of the UrlLoading thread """
        self.videos_dict = dict()  # Clear videos_dict upon reloading new playlist.
        playlist_url = self.url_input.text()  # Get the input text

        self.url_fetching_data_label.show()  # Show the loading label
        self.url_error_label.hide()  # Hide the error label if the input is a retry
        self.calc = UrlLoading(playlist_url)  # Pass in the input text
        self.calc.countChanged.connect(
            self.url_loading_finished
        )  # connect with the changing variables
        self.calc.start()

    def url_loading_finished(self, videos_dict, executed):
        """ Retrieves data from thread at the end, updates the list"""
        # First entry of self.videos_dict in MainPage class
        self.videos_dict = videos_dict
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

    def default_annotate_table(self):
        """Default table annotation to video title in song columns"""
        for index, key in enumerate(self.videos_dict):
            self.video_table.setItem(index, 0, QTableWidgetItem(key))  # part of QWidget
            self.video_table.setItem(index, 1, QTableWidgetItem("Unknown"))
            self.video_table.setItem(index, 2, QTableWidgetItem("Unknown"))
            self.video_table.setItem(index, 3, QTableWidgetItem("Unknown"))
            self.video_table.setItem(index, 4, QTableWidgetItem(""))
        self.revert_annotate.hide()
        self.itunes_annotate.show()

    def itunes_annotate_click(self):
        """Get YouTube video url."""
        query_iter = (
            (row_index, key_value)
            for row_index, key_value in enumerate(self.videos_dict.items())
        )
        itunes_query = map_threads(thread_query_itunes, query_iter)
        itunes_query_tuple = tuple(itunes_query)

        for row_index, ITUNES_META_JSON in itunes_query_tuple:
            self.populate_itunes_meta(row_index, ITUNES_META_JSON)

        self.itunes_annotate.hide()
        self.revert_annotate.show()

    def populate_itunes_meta(self, row_index, ITUNES_META_JSON):
        """Provide iTunes annotation guess based on video title"""
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
            artwork_name, artwork_index = "", 4
        self.video_table.setItem(row_index, song_index, QTableWidgetItem(song_name))
        self.video_table.setItem(row_index, album_index, QTableWidgetItem(album_name))
        self.video_table.setItem(row_index, artist_index, QTableWidgetItem(artist_name))
        self.video_table.setItem(row_index, genre_index, QTableWidgetItem(genre_name))
        self.video_table.setItem(
            row_index, artwork_index, QTableWidgetItem(artwork_name)
        )

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
        playlist_properties = self.get_playlist_properties()

        self.download_button.setEnabled(False)
        self.downloaded_label.setText("Downloading...")
        self.down = DownloadingVideos(
            self.videos_dict, self.download_dir, playlist_properties
        )
        self.down.start()
        # TODO: Fix this below -- be able to reflect emission
        self.downloaded_label = self.down.downloadCount

    def change_cell(self):
        """Change selected cell value to value in self.video_info_input."""
        row = self.video_table.currentIndex().row()
        column = self.video_table.currentIndex().column()
        video_info_input_value = self.video_info_input.text()
        self.video_table.setItem(row, column, QTableWidgetItem(video_info_input_value))

    def get_playlist_properties(self):
        """Get video information from self.video_table
        to reflect to downloaded MP3 metadata."""
        playlist_properties = []
        for row_index, key_value in enumerate(self.videos_dict.items()):
            song_properties = {}
            song_properties["song"] = self.get_row_text(
                self.video_table.item(row_index, 0)
            ).replace(
                "/", "-"
            )  # will be filename -- change illegal char to legal - make func
            song_properties["album"] = self.get_row_text(
                self.video_table.item(row_index, 1)
            )
            song_properties["artist"] = self.get_row_text(
                self.video_table.item(row_index, 2)
            )
            song_properties["genre"] = self.get_row_text(
                self.video_table.item(row_index, 3)
            )
            song_properties["artwork"] = self.get_row_text(
                self.video_table.item(row_index, 4)
            )

            playlist_properties.append(
                song_properties
            )  # this assumes that dict will be ordered like list

        return playlist_properties

    @staticmethod
    def get_row_text(cell_item):
        """Get text of cell value, if empty return empty str."""
        try:
            cell_item = cell_item.text()
            return cell_item
        except AttributeError:
            cell_item = ""
            return cell_item

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

    def __init__(self, videos_dict, download_path, playlist_properties, parent=None):
        QThread.__init__(self, parent)
        self.videos_dict = videos_dict
        self.download_path = download_path
        self.playlist_properties = playlist_properties

    def run(self):
        """ Main function, downloads videos by their id while emitting progress data"""
        # Download
        mp4_path = os.path.join(self.download_path, "mp4")
        try:
            os.mkdir(mp4_path)
        except FileExistsError:
            pass

        time0 = time.time()
        video_properties = (
            (key_value, (self.download_path, mp4_path), self.playlist_properties[index])
            for index, key_value in enumerate(
                self.videos_dict.items()
            )  # dict is naturally sorted in iteration
        )
        map_threads(thread_query_youtube, video_properties)
        shutil.rmtree(mp4_path)  # remove mp4 dir
        time1 = time.time()

        delta_t = time1 - time0
        print(delta_t)
        # TODO: allow proper emission of below func
        self.downloadCount.emit(f"Download time: {'%.2f' % delta_t} seconds")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainPage()
    widget.show()
    sys.exit(app.exec_())
