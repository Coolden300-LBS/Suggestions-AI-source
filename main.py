# pyside6-designer in terminal to open gui editor
# Suggestions.ui is the main gui file

# -------------------------------------------------------------------------------------
# PSEUDO-CODE:
# start -> load libraries -> set up gui tools -> set up gui elements ->
# -> load film data from .json file -> create gui film card template ->
# -> declare functions -> connect functions to inputs from gui ->
# -> start python application
# -------------------------------------------------------------------------------------



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
movie_items = [] # this one fills up in fill_list function

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

""" Function that adds a movie with parsed data. """
def add_movie(title: str, year: int, genres, moods):
    item = QtWidgets.QListWidgetItem()
    card = MovieCard(title, year, genres, moods)

    item.setSizeHint(card.sizeHint())
    list_widget.addItem(item)
    list_widget.setItemWidget(item, card)

    return item


""" Function that fills movie list in GUI on start. Is not being called anywhere else. """
def fill_list():
    for title, data in FILM_DATA.items():
        item = add_movie(title, data["year"], ", ".join(data["genres"]), ", ".join(data["moods"]))
        movie_items.append((item, data))


""" Function that is being called on each user input in search bars to filter out movies. """
def filter_list():
    
    # refines text to remove any extra signs
    def refine_text(text):
        return str.lower(re.sub(r'[^a-zA-Z0-9\s]', '', text)).split()

    genre_filter = refine_text(genre_input.text())
    mood_filter = refine_text(mood_input.text())

    # if we have any filters typed in, we sort list, otherwise turn on all elements
    if len(genre_filter) + len(mood_filter) > 0:
        for item, data in movie_items:

            visible = False
            found = False

            # looking for matching genre filters
            for gfilter in genre_filter:
                for genre in data["genres"]:
                    if str.find(refine_text(genre), gfilter) == -1:
                        found = True
                        break
                if not found: break
                visible = True

            found = False

            # and same for moods
            """for mfilter in mood_filter:
                for mood in data["moods"]:
                    if str.find(refine_text(mood), mfilter) == -1:
                        found = True
                        break
                if not found: break
                visible = True"""

            item.setHidden(not visible)
    else:
        for item, data in movie_items:
            item.setHidden(False)

# -------------------------------------------------------------------------------------
# input connections
# -------------------------------------------------------------------------------------

genre_input.textEdited.connect(filter_list)
mood_input.textEdited.connect(filter_list)

# -------------------------------------------------------------------------------------
# application run
# -------------------------------------------------------------------------------------

fill_list()
window.show()
sys.exit(app.exec())



# TODO: add more film covers (current stop: Mad Max: Fury Road)   