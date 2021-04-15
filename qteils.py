""" Player hand and tile procedures for the game """

import random

from PyQt5.QtCore import (QPointF, Qt, QObject,
                          pyqtProperty, QPropertyAnimation,
                          QSequentialAnimationGroup, QEasingCurve,
                          pyqtSignal)
from PyQt5.QtGui import QPixmap, QTransform, QFont, QBrush
from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsPixmapItem,
                             QGraphicsSimpleTextItem)

import Constants as Cons


# PyQt doesn't support deriving from more than one wrapped class so we use
# composition and delegate the property.
class Pixmap(QObject):
    """ Wrapper class for PixmapItem """

    def __init__(self, pix):
        super(Pixmap, self).__init__()

        self.pixmap_item = QGraphicsPixmapItem(pix)
        self.pixmap_item.setFlag(QGraphicsItem.ItemIsMovable)
        self.pixmap_item.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def __del__(self):
        self.deleteLater()

    def _set_pos(self, pos):
        self.pixmap_item.setPos(pos)

    def _set_opacity(self, op):
        self.pixmap_item.setOpacity(op)

    pos = pyqtProperty(QPointF, fset=_set_pos)  # Position property
    opacity = pyqtProperty(float, fset=_set_opacity)  # Opacity property

    def get_pixmap(self):
        """ Return pixmap item """
        return self.pixmap_item

    def set_pixmap(self, pix):
        """ Return pixmap item """
        self.pixmap_item = QGraphicsPixmapItem(pix)


# Class holding details of player's hand
# List of letters in letters
class Hand(QObject):
    """ Class holds player's hand """

    anim_complete = pyqtSignal()  # Signal for completion of animation

    def __init__(self, letters, player, scene):
        super(Hand, self).__init__()

        self.player = player
        self.letters = letters  # set of letters being used
        self.scene = scene

        self.extra_tiles = []
        self.tilesinplay = []  # tiles being moved
        self.hand = []  # details of hand as (letter, tile) tuple
        self.group = QSequentialAnimationGroup()
        self.group.finished.connect(self.an_end)

    # Get letter details into hand
    # no is 7 if not specified
    # new tiles also held in extra_tiles
    def get_hand(self, num=Cons.NO_HAND):
        """ Get specified number of letters into hand
            - new tiles also held in extra_tiles """
        self.extra_tiles.clear()
        if num > 0 and not self.letters.nomoreletters:
            letters = self.letters.get_letters(num)
            for letter in letters:
                teil = Tile(letter, self.scene)
                self.hand.append([letter, teil, QPointF()])
                self.extra_tiles.append(teil)
        self.set_hand()
        self.draw_hand()

    # Set positions for tiles in rack
    def set_hand(self):
        """ Set positions for tiles in rack """

        tiles = [x[1] for x in self.hand]
        i = 0
        for teil in tiles:
            if self.player == 0:
                xpos = Cons.RACK_XTILE[self.player] + i * Cons.WIDTH
            else:
                xpos = Cons.RACK_XTILE[self.player] + (len(tiles) - 1 - i) * Cons.WIDTH
            teil.rack_pos = QPointF(xpos, Cons.RACK_YTILE)
            self.hand[i][2] = teil.rack_pos
            i += 1

    # Draw all tiles apart from new tiles
    def draw_hand(self):
        """ Draw all tiles apart from new tiles """

        tiles = [h[1] for h in self.hand]
        self.reset_group()
        self.group.finished.connect(self.an_end)
        for teil in tiles:
            if teil in self.extra_tiles:
                self.group.addAnimation(teil.get_tile())
            else:
                teil.draw_tile(teil.rack_pos)
        self.group.start()

    def return_tiles(self, tiles):
        """ Return tiles to rack """

        self.reset_group()
        self.group.finished.connect(self.an_end)
        for teil in tiles:
            self.group.addAnimation(teil.return_tile())
        self.group.start()

    def exchange_tiles(self, tiles):
        """ Exchange tiles for new ones """

        self.reset_group()
        self.group.finished.connect(lambda: self.an_next(tiles))
        for teil in tiles:
            self.group.addAnimation(teil.remove_tile())
        self.group.start()

    def an_next(self, tiles):
        """ Second part of exchange
            Get new tiles """
        no = self.remove_tiles(tiles)
        self.get_hand(no)

    def an_end(self):
        """ Animation completion """
        self.anim_complete.emit()

    def reset_group(self):
        """ Reset Group Animation """
        self.group.clear()
        self.group.finished.disconnect()

    def remove_tiles(self, tiles):
        """ Remove letters used from hand """
        self.hand = [t for t in self.hand if t[1] not in tiles]
        return Cons.NO_HAND - len(self.hand)

    def hand_letters(self):
        """ Return letters in hand """
        return [t[0] for t in self.hand]

    def activate_hand(self, activate):
        """ Activate/deactivate all tiles """
        tiles = [h[1] for h in self.hand]
        for teil in tiles:
            teil.activate(activate)

    def dim_hand(self, activate):
        """ Dim/Undim all tiles in hand """
        tiles = [h[1] for h in self.hand]
        for teil in tiles:
            teil.dim(activate)

    def update_hand(self, remove=None, no=0):
        """ Update hand
            Remove list of tiles in remove
            get required number of new tiles """
        if remove is not None:
            no = self.remove_tiles(remove)
        self.get_hand(no)


# Class of letter tile sprites
class Tile(Pixmap):
    """ Tile class defines on screen tiles """

    anim_complete = pyqtSignal()  # Signal for completion of animation
    sheet = None  # Sprite sheet

    def __init__(self, letter, scene, letfile=r"\scrabble_letters.png"):

        self.alphabet = scene.alphabet
        if type(self).sheet is None:
            type(self).sheet = QPixmap(self.alphabet.lang + letfile)

        # Extract letter tile from sheet, scale to cell size for board
        image = type(self).sheet.copy(self.alphabet.TILE_POSITIONS[letter][0],
                                      self.alphabet.TILE_POSITIONS[letter][1],
                                      Cons.TILE_WIDTH, Cons.TILE_HEIGHT)
        image = image.scaled(Cons.WIDTH, Cons.HEIGHT, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        super(Tile, self).__init__(image)

        type(self).sheet = None
        self.letter = letter
        self.blank_letter = None
        self.rack_pos = QPointF()
        self.pos = QPointF()
        self.txt = None
        self.scene = scene
        self.alphabet = self.scene.alphabet

        self.pixmap_item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.pixmap_item.setTransform(QTransform())
        self.pixmap_item.setAcceptedMouseButtons(Qt.LeftButton)
        self.pixmap_item.setZValue(1000)
        self.pixmap_item.letter = letter
        self.pixmap_item.tile = self
        self.pixmap_item.hide()
        # self.add_to_scene(self.scene)
        self.scene.addItem(self.pixmap_item)
        self.pos = QPointF(0, 0)
        self.animation = None
        self.fade = None

    # Draw at position (QPoint) on screen
    def draw_tile(self, position):
        """ Extract letter tile from sheet, scale to cell size for board
            draw at (xpos, ypos) """
        self.pos = position
        self.pixmap_item.show()

    def get_pos(self):
        """ Return position of tile """
        return self.pixmap_item.pos()

    def set_pos(self, x, y):
        """ Move tile to position (x, y) """
        self.pixmap_item.setPos(x, y)

    def hand_cursor(self):
        """ Change cursor to hand cursor """
        self.pixmap_item.setCursor(Qt.PointingHandCursor)

    def reset_cursor(self):
        """ Change cursor to pointer cursor """
        self.pixmap_item.setCursor(Qt.ArrowCursor)

    def move_tile(self, dur, *args):
        """ Create move tile animation
            *args are time fraction, points in path either as
            (time, QPointF) or (time, x, y) """
        if not self.pixmap_item.isVisible():
            self.pixmap_item.setPos(QPointF(Cons.WINDOW_SIZE[0] / 2 - Cons.WIDTH / 2,
                                            Cons.WINDOW_SIZE[1]))
            self.pixmap_item.show()
        animation = QPropertyAnimation(self, b'pos')
        animation.setDuration(dur)
        for val in args:
            if isinstance(val[1], QPointF):
                point = val[1]
            else:
                point = QPointF(val[1], val[2])
            animation.setKeyValueAt(val[0], point)
        self.animation = animation
        return self.animation

    def activate(self, activate):
        """ Accept mouse presses if activate is True """
        if activate:
            self.pixmap_item.setAcceptedMouseButtons(Qt.LeftButton)
        else:
            self.pixmap_item.setAcceptedMouseButtons(Qt.NoButton)

    def dim(self, activate):
        """ Dim tile if activate is True """
        if activate:
            self.pixmap_item.setOpacity(0.4)
        else:
            self.pixmap_item.setOpacity(1)

    def set_in_board(self):
        """ Set tile in board
            No longer moveable """
        self.pixmap_item.setAcceptedMouseButtons(Qt.NoButton)

    def add_letter(self, letter):
        """ Add small letter to blank tile """

        self.txt = QGraphicsSimpleTextItem(letter, self.pixmap_item)
        self.txt.setFont(QFont("Arial", 14, QFont.DemiBold))
        self.txt.setBrush(QBrush(Qt.darkRed))
        wd, ht = self.txt.boundingRect().width(), self.txt.boundingRect().height()
        self.txt.setPos((Cons.WIDTH - wd) / 2, (Cons.HEIGHT - ht) / 2)

    def get_tile(self):
        """ Move tile from store (bottom centre) to position on rack
            Used in Group Animation """
        return self.move_tile(1000, (0, Cons.WINDOW_SIZE[0] / 2 - Cons.WIDTH / 2,
                                     Cons.WINDOW_SIZE[1]),
                              (0.2, Cons.WINDOW_SIZE[0] / 2 - Cons.WIDTH / 2,
                               self.rack_pos.y()), (1, self.rack_pos))

    def return_tile(self):
        """ Return tile to rack
            Used in Group Animation """
        return self.move_tile(400, (0, self.get_pos()), (1, self.rack_pos))

    def remove_tile(self):
        """ Remove tile from board
            Used in Group Animation """
        return self.move_tile(1000, (0, self.get_pos()),
                              (0.8, Cons.WINDOW_SIZE[0] / 2 - Cons.WIDTH / 2, self.get_pos().y()),
                              (1, Cons.WINDOW_SIZE[0] / 2 - Cons.WIDTH / 2, Cons.WINDOW_SIZE[1]))

    def lift_tile(self):
        """ Used in exchange tiles
            Lift chosen tile to set position above rack """
        self.animation = self.move_tile(100, (0, self.rack_pos),
                                        (1, self.rack_pos + QPointF(0, Cons.TILE_LIFT)))
        self.animation.start()

    def drop_tile(self):
        """ Used in exchange tiles
            Drop chosen tile back into rack """
        self.animation = self.move_tile(100, (0, self.get_pos()), (1, self.rack_pos))
        self.animation.start()

    def name_tile(self, player):
        """ Used in names screen
            Move chosen blank tiles to required position """
        point = QPointF(Cons.INPUT_NAMES[player][0] + Cons.INPUT_NAMES[player][2],
                        Cons.INPUT_NAMES[player][1] + 50)
        self.animation = self.move_tile(100, (0, self.get_pos()), (1, point))
        self.animation.start()

    def return_blank(self):
        """ Used in names screen
            Return tile to position on board """
        self.animation = self.move_tile(400, (0, self.get_pos()), (1, self.rack_pos))
        self.animation.start()

    def unfade(self):
        """ Fade in letter on blank tile """
        self.fade = QPropertyAnimation(self, b'opacity')
        self.fade.setDuration(2000)
        self.fade.setStartValue(0)
        self.fade.setEndValue(1)
        self.fade.setEasingCurve(QEasingCurve.InOutSine)
        self.fade.finished.connect(self._fade_end)
        self.fade.start()

    def _fade_end(self):
        """ end of animation """
        self.anim_complete.emit()

    def hide(self):
        """ Hide tile """
        self.pixmap_item.hide()

    def setZValue(self, val):
        """ set ZValue for image """
        self.pixmap_item.setZValue(val)


# Class defining all letters available in a game
class Letters:
    """ Class for all letters in game """

    def __init__(self, scene):

        self.language = scene.alphabet

        self.letters = self.language.LETTERS[:]

        for _ in range(4):
            random.shuffle(self.letters)

        self.number = len(self.letters)
        self.nomoreletters = False

    # Get no of random letters
    # Delete these from the stock of letters
    def get_letters(self, num):
        """ Get no of random letters if available and remove from bag"""

        if self.nomoreletters:
            return None
        else:
            if num > self.number:
                letters = self.letters
                self.letters.clear()
                self.nomoreletters = True
            else:
                letters = [self.letters.pop(random.randrange(len(self.letters)))
                           for _ in range(num)]
            self.number = len(self.letters)
        return letters

    # Get one random letter
    # Used to start game and not deleted
    def get_random_letter(self):
        """ Get one random letter without removing from bag """

        return random.sample(self.letters, 1)
