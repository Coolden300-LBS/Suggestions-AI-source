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
from PySide6 import QtWidgets, QtGui, QtCore
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

        # store values in card
        self.movie_title = title
        self.movie_year = year
        self.movie_genres = genres
        self.movie_moods = moods

        layout = QtWidgets.QHBoxLayout(self)

        # film cover on the left
        self.image = QtWidgets.QLabel()
        self.image.setFixedSize(60, 90)

        # add image cover (if exists)
        simplified_title = str.lower(re.sub(r'[^a-zA-Z0-9\s]', '', title))
        image_path = f"{FOLDER_PATH}FilmCovers/{simplified_title}"
        #if Path(image_path).exists:
        pixmap = QtGui.QPixmap(image_path)
        self.image.setPixmap(pixmap.scaled(60, 90))

        # container widget for text layout
        text_widget = QtWidgets.QWidget()
        text_layout = QtWidgets.QVBoxLayout(text_widget)

        # labels
        self.title = QtWidgets.QLabel(f"{title} ({year})")
        self.genres = QtWidgets.QLabel(f"Genres: {genres}")
        self.moods = QtWidgets.QLabel(f"Moods: {moods}")

        # make genres and moods wrap so they take up less space
        self.genres.setWordWrap(True)
        self.moods.setWordWrap(True)

        text_layout.addWidget(self.title)
        text_layout.addWidget(self.genres)
        text_layout.addWidget(self.moods)

        # add container for buttons and create buttons
        button_widget = QtWidgets.QWidget()
        button_layout = QtWidgets.QVBoxLayout(button_widget)

        self.like_button = QtWidgets.QPushButton()
        self.dislike_button = QtWidgets.QPushButton()

        # connect events to buttons
        self.like_button.clicked.connect(self.on_like)
        self.dislike_button.clicked.connect(self.on_dislike)

        # make buttons round
        button_size = 40

        for button in [self.like_button, self.dislike_button]:
            button.setFixedSize(button_size, button_size)
            button.setStyleSheet(f"""
                QPushButton {{
                    border-radius: {button_size // 2}px;
                }}
            """)

        # add thumb up/down icons
        self.like_button.setIcon( QtGui.QIcon(f"{FOLDER_PATH}Assets/like.png") )
        self.dislike_button.setIcon( QtGui.QIcon(f"{FOLDER_PATH}Assets/dislike.png") )

        # set icon size
        self.like_button.setIconSize(QtCore.QSize(24, 24))
        self.dislike_button.setIconSize(QtCore.QSize(24, 24))

        # add buttons to layout with separator inbetween to set them up and down
        button_layout.addWidget(self.like_button)
        button_layout.addStretch()
        button_layout.addWidget(self.dislike_button)

        button_widget.setFixedWidth(50) # to prevent from large rectangular box

        # add all the widgets (NOT layout)
        layout.addWidget(self.image)
        layout.addWidget(text_widget, 1)
        layout.addWidget(button_widget)

    def on_like(self):
        print(f"{self.movie_title} is LIKED BY BILLIONS!")

    def on_dislike(self):
        print("Dislike")

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
    
    """ Removes any extra signs from text. Outputs string. """
    def refine_text(text):
        return str.lower(re.sub(r'[^a-zA-Z0-9\s]', '', text))

    genre_filter = refine_text(genre_input.text()).split()
    mood_filter = refine_text(mood_input.text()).split()

    # if we have any filters typed in, we sort list, otherwise turn on all elements
    if len(genre_filter) + len(mood_filter) > 0:
        for item, data in movie_items:

            required_matches = 0
            matches = 0

            # looking for matching genre filters
            required_matches = len(genre_filter)
            for gfilter in genre_filter:
                for genre in data["genres"]:
                    if str.find(refine_text(genre), gfilter) > -1:
                        matches += 1

            # if check didn't pass, hide card and proceed to next one
            if matches < required_matches:
                item.setHidden(True)
                continue

            print(required_matches)
            print(matches)

            # reset matches!
            matches = 0

            # do similar check for moods
            required_matches = len(mood_filter)
            for mfilter in mood_filter:
                for mood in data["moods"]:
                    if str.find(refine_text(mood), mfilter) > -1:
                        matches += 1

            # ~//~
            if matches < required_matches:
                item.setHidden(True)
                continue

            # after all the checks passed we can enable card
            item.setHidden(False)
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



""" 
TODO:   - (done) fix sorting algorithm. Current issue: sorts through all genre/mood items and tries to see if all they match to single filter
        - (done) fix that when more than 1 filter is present it will find suggestions where at least one of those filters present and not 2 
        at the same time (eg "drama" filter = films those have "drama", "drama sci-fi" = films with drama and films with sci-fi, WRONG, should
        be = only films with both drama and sci-fi)
        - (done) add like/dislike button to films
        - (done) make sure buttons are working
        - (done) fix buttons position and ugly looking
        
        - make points system for genres and moods
        - make picked films with most points appear upper in list, while ones with lesser points go down
        - when new filter consists of one letter it tends to add other films to list (?)
        - add more film covers (current stop: Mad Max: Fury Road)
"""