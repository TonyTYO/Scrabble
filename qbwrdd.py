# pylint: disable=locally-disabled,no-member,no-name-in-module,invalid-name
""" Sets up the game playboard """

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem

import Constants as Cons
import qteils


class Board:
    """ Setup the board for the game """

    def __init__(self, scene):
        self.scene = scene
        self.cells = []
        self.checker = self.scene.states.checker
        self.letters = qteils.Letters(scene)
        self.players = self.scene.get_players()
        self.buttons = None
        self.background_item = None

    def draw_board(self):
        """ Draw playing board with two racks """

        # Dictionary of colours
        colours = {".": Cons.NORMAL_COLOUR, "T": Cons.TRIPLEWORD_COLOUR,
                   "D": Cons.DOUBLEWORD_COLOUR, "t": Cons.TRIPLELETTER_COLOUR,
                   "d": Cons.DOUBLELETTER_COLOUR}

        self.background_item = QGraphicsRectItem(Cons.BOARD[0], Cons.BOARD[1],
                                                 Cons.BOARD[2], Cons.BOARD[3])
        self.background_item.setBrush(Qt.black)
        self.scene.addItem(self.background_item)

        for row in range(Cons.SIZE):
            for col in range(Cons.SIZE):
                self.cells.append([Cons.BOARD[0] + (Cons.MARGIN + Cons.WIDTH) * col + Cons.MARGIN,
                                   (Cons.MARGIN + Cons.HEIGHT) * row + Cons.MARGIN, Cons.BOARD[0] +
                                   (Cons.MARGIN + Cons.WIDTH) * col + Cons.MARGIN + Cons.WIDTH,
                                   (Cons.MARGIN + Cons.HEIGHT) * row + Cons.MARGIN + Cons.HEIGHT])
                square = QGraphicsRectItem(Cons.BOARD[0] + (Cons.MARGIN + Cons.WIDTH) * col +
                                           Cons.MARGIN, (Cons.MARGIN + Cons.HEIGHT) * row +
                                           Cons.MARGIN, Cons.WIDTH, Cons.HEIGHT)
                col = colours[self.checker.grid[row][col]]
                square.setBrush(QColor(col[0], col[1], col[2]))
                self.scene.addItem(square)
        self.add_racks()

    def add_racks(self):
        """ Draw racks that hold tiles """

        rack_img = QPixmap('tiles\\rack.png')
        for i in range(2):
            rack = QGraphicsPixmapItem(rack_img)
            self.scene.addItem(rack)
            rack.setPos(Cons.RACK_POS[i], Cons.RACK_Y)

        for player in range(2):
            self.players[player].totals.show()
            self.players[player].totals.show_totals()
