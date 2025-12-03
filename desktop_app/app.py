import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLineEdit, 
                             QListWidget, QMainWindow, QListWidgetItem, QPushButton, 
                             QHBoxLayout, QFileDialog, QMessageBox, QProgressBar, QLabel)
from PyQt6.QtCore import Qt, QMimeData, QUrl, QThread, pyqtSignal
from PyQt6.QtGui import QDrag, QShortcut, QKeySequence, QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from searcher import SampleSearcher
from indexer import IndexerBackend
import ctypes

myappid = 'mycompany.myproduct.subproduct.version'
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

class IndexingWorker(QThread):
    finished = pyqtSignal(int)
    progress = pyqtSignal(int) 
    status_update = pyqtSignal(str)

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
    
    def run(self):
        self.status_update.emit("Loading Indexer models...")
        indexer = IndexerBackend()

        def callback_bridge(percentage):
            self.progress.emit(percentage)

        self.status_update.emit(f"Starting indexing on {self.folder_path}")
        try:
            count = indexer.run_indexing(self.folder_path, progress_callback=callback_bridge)
        except Exception as e:
            self.status_update.emit(f"FATAL INDEXING ERROR: {e}")
            count = 0
        self.finished.emit(count)

class SampleList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)

    def wsl_to_windows_path(self, wsl_path):
        if wsl_path.startswith("/mnt/"):
            parts = wsl_path.split('/')
            drive_letter = parts[2]    # 'c'
            rest_of_path = "\\".join(parts[3:])
            windows_path = f"{drive_letter.upper()}:\\{rest_of_path}"
            return windows_path
        return wsl_path
    
    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return   
        
        raw_path = item.data(Qt.ItemDataRole.UserRole)
        print(f"Ruta Linux: {raw_path}")
        win_path_backslashes = self.wsl_to_windows_path(raw_path)
        win_path_forward_slashes = win_path_backslashes.replace("\\", "/")
        final_url_string = f"file:///{win_path_forward_slashes}"
        url = QUrl(final_url_string)
        print(f"URL Final: {url.toString()}")

        mime_data  = QMimeData()
        mime_data.setUrls([url])

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.CopyAction)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Sample Searcher")
        basedir = os.path.dirname(__file__)
        icon_path = os.path.join(basedir, "icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.resize(500, 700)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        try: 
            self.engine = SampleSearcher()
            print("DB Loaded succesfuly")
            db_exists = True
        except FileNotFoundError:
            print("No DB found. Waiting for user to index.")
            self.engine = None
            db_exists = False

        #Audio Setup
        self.audio_ouput = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_ouput)
        self.audio_ouput.setVolume(0.8)

        main_layout = QVBoxLayout()

        #Indexing Boutton
        self.top_bar = QHBoxLayout()
        self.btn_index = QPushButton("📂 Add Samples Folder")
        self.btn_index.clicked.connect(self.open_folder_dialog)
        self.top_bar.addWidget(self.btn_index)
        main_layout.addLayout(self.top_bar)

        #Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Initializing....")
        self.status_label.setStyleSheet("font-size: 10pt; color: #555;")
        main_layout.addWidget(self.status_label)

        #Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Describe Sound: ")
        self.search_bar.returnPressed.connect(self.do_search)

        if not db_exists:
            self.search_bar.setPlaceholderText("Please index a folder first to search...")
            self.search_bar.setEnabled(False)
            self.status_label.setText("Ready to index. Please select a folder.")
        else:
            self.search_bar.setPlaceholderText("Describe Sound: ")
            self.status_label.setText("Engine Loaded. Ready.")
        main_layout.addWidget(self.search_bar)

        #Result List
        self.result_list = SampleList()
        self.result_list.itemClicked.connect(self.play_preview)
        main_layout.addWidget(self.result_list)

        self.stop_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        self.stop_shortcut.activated.connect(self.stop_audio)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def update_status_label(self, message):
        self.status_label.setText(message)

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Sample Folder")
        if folder:
            reply = QMessageBox.question(self, 'Index Folder', 
                                         f"Do you want to index:\n{folder}\n\nThis may take a while.",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.start_indexing(folder)

    def start_indexing(self, folder):
        self.btn_index.setEnabled(False)
        self.search_bar.setEnabled(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.status_label.setText("Indexing started...")

        self.worker = IndexingWorker(folder)
        self.worker.finished.connect(self.indexing_finished)
        self.worker.progress.connect(self.update_progress_bar)
        self.worker.status_update.connect(self.update_status_label)
        self.worker.start()

    def update_progress_bar(self, val):
        self.progress_bar.setValue(val)
        self.status_label.setText(f"Indexing...%")

    def indexing_finished(self, count):
        self.progress_bar.hide()
        self.btn_index.setEnabled(True)
        self.search_bar.setEnabled(True)
        QMessageBox.information(self, "Done", f"Indexing complete!\nProcessed {count} new files.")
        self.status_label.setText("Reloading Eninge...")
        try: 
            self.engine = SampleSearcher()
            self.search_bar.setPlaceholderText("Describe Sound: ")
            self.search_bar.setEnabled(True)
            self.search_bar.setFocus()
            self.status_label.setText(f"Engine ready! Processed {count} new files.")
            QMessageBox.information(self, "Done", f"Indexing complete!\nProcessed {count} new files.")
        except Exception as e:
            self.status_label.setText(f"FATAL ERROR: Could not load DB. {e}")
            QMessageBox.critical(self, "Error", f"Could not load database: {e}")

    def play_preview(self, item):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path.startswith("/mnt/"):
            file_path = self.result_list.wsl_to_windows_path(file_path)

        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.player.play()

    def stop_audio(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.stop()

    def do_search(self):
        if self.engine is None:
            return
        query = self.search_bar.text()
        results = self.engine.search(query, top_k=15)
        self.result_list.clear()

        for item in results:
            filename = item['filename']
            full_path = item['route']
            list_item = QListWidgetItem(filename)
            list_item.setData(Qt.ItemDataRole.UserRole, full_path)
            self.result_list.addItem(list_item)

# Dark Theme
STYLESHEET = """
QMainWindow {
    background-color: #2b2b2b;
}

QLabel {
    color: #cccccc;
    font-family: 'Segoe UI', sans-serif;
}

QLineEdit {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 5px;
    color: #ffffff;
    padding: 8px;
    font-size: 14px;
}

QLineEdit:focus {
    border: 1px solid #006bb3;
}

QListWidget {
    background-color: #1e1e1e;
    border: none;
    color: #dddddd;
    font-size: 13px;
    outline: none;
}

QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #2a2a2a;
}

QListWidget::item:selected {
    background-color: #007acc;
    color: white;
}

QListWidget::item:hover {
    background-color: #333333;
}

QPushButton {
    background-color: #006bb3;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #005c99;
}

QPushButton:pressed {
    background-color: #004c80;
}

QProgressBar {
    border: 1px solid #444;
    border-radius: 3px;
    text-align: center;
    background-color: #2e2e2e;
    color: white;
}

QProgressBar::chunk {
    background-color: #006bb3;
    width: 20px;
}
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())