# pyside6-designer in terminal to open editor

import json, sys, re
from PySide6 import QtWidgets, QtGui
from PySide6.QtUiTools import QUiLoader
from pathlib import Path

FOLDER_PATH = str(Path(__file__).resolve().parent) + "/"

# -------------------------------------------------------------------------------------
# gui tools setup
# -------------------------------------------------------------------------------------

app = QtWidgets.QApplication(sys.argv)
loader = QUiLoader()
window = loader.load(f"{FOLDER_PATH}Suggestions.ui")

# -------------------------------------------------------------------------------------
# gui elements setup
# -------------------------------------------------------------------------------------

genre_input = window.findChild(QtWidgets.QLineEdit, "genre_preferences")
mood_input = window.findChild(QtWidgets.QLineEdit, "mood_preferences")
list_widget = window.findChild(QtWidgets.QListWidget, "film_list")

# -------------------------------------------------------------------------------------
# film data setup
# -------------------------------------------------------------------------------------

DATA_PATH = f"{FOLDER_PATH}film_data.json"
with open(DATA_PATH, "r", encoding="utf-8") as file:
    FILM_DATA = json.load(file)

# -------------------------------------------------------------------------------------
# create film card for list manually with code 
# (I couldn't find a way to make a visual template that can be ctrl+c ctld-v by script)
# -------------------------------------------------------------------------------------

class MovieCard(QtWidgets.QWidget):
    def __init__(self, title: str, year: int, genres, moods):
        super().__init__()

        layout = QtWidgets.QHBoxLayout(self)

        # film cover on the left
        self.image = QtWidgets.QLabel()
        self.image.setFixedSize(60, 90)

        # add image cover (if exists)
        simplified_title = str.lower(re.sub(r'[^a-zA-Z0-9\s]', '', title))
        image_path = f"{FOLDER_PATH}FilmCovers/{simplified_title}"
        if Path(image_path).exists:
            pixmap = QtGui.QPixmap(image_path)
            self.image.setPixmap(pixmap.scaled(60, 90))

        # container widget for text layout
        text_widget = QtWidgets.QWidget()
        text_layout = QtWidgets.QVBoxLayout(text_widget)

        # labels
        self.title = QtWidgets.QLabel(f"{title} ({year})")
        self.genres = QtWidgets.QLabel(f"Genres: {genres}")
        self.moods = QtWidgets.QLabel(f"Moods: {moods}")

        text_layout.addWidget(self.title)
        text_layout.addWidget(self.genres)
        text_layout.addWidget(self.moods)

        # add widget (NOT layout)
        layout.addWidget(self.image)
        layout.addWidget(text_widget)

# -------------------------------------------------------------------------------------
# functions
# -------------------------------------------------------------------------------------

def add_movie(title: str, year: int, genres, moods):
    item = QtWidgets.QListWidgetItem()
    card = MovieCard(title, year, genres, moods)

    item.setSizeHint(card.sizeHint())
    list_widget.addItem(item)
    list_widget.setItemWidget(item, card)

def filter_list():
    
    def clear_input(input):
        return str.lower(re.sub(r'[^a-zA-Z0-9\s]', '', input)).split()

    genres = clear_input(genre_input.text())
    moods = clear_input(mood_input.text())

    list_widget.clear()
    for title, data in FILM_DATA.items():
        add_movie(title, data["year"], ", ".join(data["genres"]), ", ".join(data["moods"]))

# -------------------------------------------------------------------------------------
# input connections
# -------------------------------------------------------------------------------------

genre_input.textEdited.connect(filter_list)
mood_input.textEdited.connect(filter_list)

# -------------------------------------------------------------------------------------
# application run
# -------------------------------------------------------------------------------------

filter_list()
window.show()
sys.exit(app.exec())



# TODO: add more stuff to data and sorting algorithm