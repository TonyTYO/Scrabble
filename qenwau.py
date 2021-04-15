""" Initialising procedures to get names and
    player to start """

from PyQt5.QtCore import Qt, QPointF, QRegExp
from PyQt5.QtGui import QColor, QFont, QRegExpValidator
from PyQt5.QtWidgets import (QGraphicsRectItem, QWidget,
                             QLineEdit, QLabel)

import Constants as Cons
import qteils
import qtestun


class Enwau(QWidget):
    """ Get user names and start player """

    def __init__(self, scene):
        super(Enwau, self).__init__()

        self.scene = scene
        self.cells = []
        self.tiles = []
        self.blank = []
        self.n_input = None

        self.letters = qteils.Letters(scene)
        self.msg = qtestun.Msg(self.scene, None)

        # self.show_tiles()
        self.get_grid()
        self.draw_grid()
        self.get_tiles()
        self.msg.general_msg(self.scene.alphabet.QENWAU_MSGS[0])

    def get_grid(self):
        """ Blank grid  with 100 letters for tile choice """

        self.cells = []
        self.tiles = []
        for row in range(Cons.SQUARE_SIZE):
            for col in range(Cons.SQUARE_SIZE):
                self.cells.append([Cons.SQUARE[0] + (Cons.MARGIN + Cons.WIDTH) * col +
                                   Cons.MARGIN, Cons.SQUARE[1] +
                                   (Cons.MARGIN + Cons.HEIGHT) * row + Cons.MARGIN,
                                   Cons.WIDTH, Cons.HEIGHT])
        self.tiles = self.letters.get_letters(100)

    def draw_grid(self):
        """ Draw the grid """

        background_item = QGraphicsRectItem(Cons.SQUARE[0], Cons.SQUARE[1],
                                            Cons.SQUARE[2], Cons.SQUARE[3])
        background_item.setBrush(Qt.black)
        self.scene.addItem(background_item)

        for row in range(Cons.SQUARE_SIZE):
            for col in range(Cons.SQUARE_SIZE):
                cell = row * 10 + col
                square = QGraphicsRectItem(self.cells[cell][0], self.cells[cell][1],
                                           self.cells[cell][2], self.cells[cell][3])
                square.setBrush(QColor(230, 200, 167))
                self.scene.addItem(square)

    def get_tiles(self):
        """ Fill grid with blank tiles
            Each tile has associated letter """

        self.blank = []
        for row in range(Cons.SQUARE_SIZE):
            for col in range(Cons.SQUARE_SIZE):
                cell = row * 10 + col
                self.blank.append(qteils.Tile(" ", self.scene))
                self.blank[cell].draw_tile(QPointF(self.cells[cell][0], self.cells[cell][1]))
                self.blank[cell].letter = self.tiles[cell]
                self.blank[cell].rack_pos = QPointF(self.cells[cell][0], self.cells[cell][1])

    def disable_tiles(self):
        """ Disable mouse buttons for tiles in grid """
        for t in self.blank:
            t.activate(False)

    def enable_tiles(self):
        """ Enable mouse button for tiles in grid """
        for t in self.blank:
            t.activate(True)

    def show_msg(self, text):
        """ Show message """
        self.msg.general_msg(text)

    def show_lbl(self, player):
        """ Label for name input """
        txt = QLabel()
        txt.setStyleSheet("background-color:rgb(230, 200, 167); color : black;")
        txt.move(Cons.INPUT_NAMES[player][0], Cons.INPUT_NAMES[player][1] - 50)
        txt.setFont(QFont("Arial", 18))
        txt.setAlignment(Qt.AlignLeft)
        self.scene.addWidget(txt)
        txt.setText(self.scene.alphabet.QENWAU_MSGS[1]
                    + (self.scene.alphabet.QENWAU_MSGS[2]
                       if player == 0 else self.scene.alphabet.QENWAU_MSGS[3]
                       ) + self.scene.alphabet.QENWAU_MSGS[4])

    def get_names(self):
        """ Input player names """
        self.n_input = {}
        for player in range(0, 2):
            self.show_lbl(player)
            self.n_input[player] = GetInput(self.scene,
                                            (Cons.INPUT_NAMES[player][0],
                                             Cons.INPUT_NAMES[player][1]),
                                            (Cons.SCOREBOARD[player][2],
                                             Cons.INPUT_NAMES[player][3]))
        self.n_input[0].set_focus(True)
        # self.setFocusProxy(self.n_input[player])

    def show_tiles(self):
        """ Show tiles in two files """
        self.cells = []
        for row in range(Cons.SIZE):
            for col in range(Cons.SIZE):
                self.cells.append([Cons.BOARD[0] + (Cons.MARGIN + Cons.WIDTH) * col + Cons.MARGIN,
                                   (Cons.MARGIN + Cons.HEIGHT) * row + Cons.MARGIN, Cons.BOARD[0] +
                                   (Cons.MARGIN + Cons.WIDTH) * col + Cons.MARGIN + Cons.WIDTH,
                                   (Cons.MARGIN + Cons.HEIGHT) * row + Cons.MARGIN + Cons.HEIGHT])
                square = QGraphicsRectItem(Cons.BOARD[0] + (Cons.MARGIN + Cons.WIDTH) * col +
                                           Cons.MARGIN, (Cons.MARGIN + Cons.HEIGHT) * row +
                                           Cons.MARGIN, Cons.WIDTH, Cons.HEIGHT)
                self.scene.addItem(square)
        self.show_alphabet(0, r"\scrabble_letters.png")
        self.show_alphabet(4, r"\xscrabble_letters.png")

    def show_alphabet(self, start, letfile):
        """ Show all tiles in file """
        cell = start * 15
        for let in self.scene.alphabet.ALPHABET:
            tile = qteils.Tile(let, self.scene, letfile)
            tile.draw_tile(QPointF(self.cells[cell][0], self.cells[cell][1]))
            cell += 1


class GetInput(QLineEdit):
    """ Class to get user input """

    def __init__(self, scene, pos, size, parent=None):
        super(GetInput, self).__init__(parent)

        self.scene = scene
        self.bot_left = (pos[0], pos[1] + size[1])
        self.setStyleSheet("""QLineEdit { border: 2px solid gray;
                                          border-radius: 10px;
                                          padding: 0 8px;
                                          background-color:rgba(0, 0, 0, 0);
                                          font: 18pt 'Arial';}""")

        self.setReadOnly(False)
        self.move(pos[0], pos[1])
        self.resize(size[0], size[1])
        validator = QRegExpValidator(QRegExp("^.*$"))
        self.setValidator(validator)
        self.setAutoFillBackground(True)
        widg = self.scene.addWidget(self)
        widg.setZValue(2000)
        if size[0] < widg.minimumWidth():  # min width set at 84
            widg.setMinimumWidth(0)
        self.clear()
        self.show()
        self.setCursorPosition(0)

    def get_text(self, form=None):
        """ Return text in input box formatted as required
            default: no formatting
            u:upper case, l:lower case
            t:title format """

        intext = self.text()
        if form is None:
            return intext
        elif form == "u":
            return intext.upper()
        elif form == "l":
            return intext.lower()
        elif form == "t":
            return intext.title()

    def set_regexpression(self, regexp):
        """ Set regular expression for input format
            regexp as string """

        validator = QRegExpValidator(QRegExp(regexp))
        self.setValidator(validator)

    def set_text(self, text):
        """ Set default text """
        self.clear()
        self.insert(text)

    def set_focus(self, value):
        """ Set or clear focus """

        if value:
            self.setFocus()
        else:
            self.clearFocus()
