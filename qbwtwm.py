""" Define all buttons and the game state machine """

import sys
from PyQt5.QtCore import (QRectF, Qt, QState, QFinalState, QStateMachine,
                          pyqtSignal, QObject, QPoint)
from PyQt5.QtGui import (QPixmap, QLinearGradient, QPainterPath)
from PyQt5.QtWidgets import (QGraphicsWidget, QGraphicsItem,
                             QGraphicsRectItem, QStyle)
from PyQt5.QtTest import QTest

import Constants as Cons
import qstates


class Button(QGraphicsWidget):
    """ Defines standard buttons """

    pressed = pyqtSignal()  # signal for button pressed

    def __init__(self, pixmap, size, parent=None):
        super(Button, self).__init__(parent)

        self._pix = pixmap.scaled(30, 30, Qt.KeepAspectRatio)
        self.setAcceptHoverEvents(True)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.size = size
        self.persistent = True

    def boundingRect(self):
        """ Return bounding rectangle """
        return QRectF(-1 * self.size, -1 * self.size, 2 * self.size, 2 * self.size)

    def shape(self):
        """ Return shape as path """
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def paint(self, painter, option, _widget=None):
        """ Paint button """
        down = option.state & QStyle.State_Sunken
        r = self.boundingRect()

        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        if option.state & QStyle.State_MouseOver:
            color_0 = Qt.white
        else:
            color_0 = Qt.lightGray

        color_1 = Qt.darkGray
        if down:
            color_0, color_1 = color_1, color_0

        grad.setColorAt(0, color_0)
        grad.setColorAt(1, color_1)

        painter.setPen(Qt.darkGray)
        painter.setBrush(grad)
        painter.drawEllipse(r)

        color_0 = Qt.darkGray
        color_1 = Qt.lightGray
        if down:
            color_0, color_1 = color_1, color_0

        grad.setColorAt(0, color_0)
        grad.setColorAt(1, color_1)

        painter.setPen(Qt.NoPen)
        painter.setBrush(grad)

        if down:
            painter.translate(2, 2)
        painter.drawEllipse(r.adjusted(5, 5, -5, -5))
        painter.drawPixmap(-self._pix.width() / 2, -self._pix.height() / 2,
                           self._pix)

    def mousePressEvent(self, _ev):
        """ Emit pressed signal and redraw on mouse press """
        self.pressed.emit()
        self.update()

    def mouseReleaseEvent(self, _ev):
        """ Redraw on mouse release """
        self.update()

    # -------------------------------------------------------------------------
    # Move mouse and click button for computer player
    def pc_mouse_click(self, scene, x, y):
        """ Move cursor to button and simulate a click """
        scene.move_reconnect(self.on_move_complete)  # Cursor move completed signal
        scene.mouse_move(x, y)

    def on_move_complete(self, scene, x, y):
        """ Simulate click on the button """
        QTest.mouseMove(scene.parent, QPoint(x, y))
        QTest.mousePress(scene.parent, Qt.LeftButton, delay=1000)
        self.pressed.emit()
        self.update()
        QTest.mouseRelease(scene.parent, Qt.LeftButton, delay=2000)
        self.update()


class Setbuttons(QObject):
    """ Setup all buttons for the game """

    def __init__(self, scene):
        super(Setbuttons, self).__init__()

        self.scene = scene
        self.buttons = {}  # Register of buttons as {name: button}

        buttonParent = QGraphicsRectItem()
        buttonParent.persistent = True

        self.playButton, self.acceptButton, self.passButton = None, None, None
        self.challengeButton, self.exchangeButton, self.quitButton = None, None, None
        self.nextButton, self.backButton, self.endButton, self.newButton = None, None, None, None

        self.setup_buttons(buttonParent)
        self.set_button_pos()
        # self.reset_tips()
        self.scene.addItem(buttonParent)
        buttonParent.setScale(0.75)
        buttonParent.setPos(200, 200)
        buttonParent.setZValue(65)

    def setup_buttons(self, button_parent):
        """ Define buttons """

        # Buttons for playing screen
        self.playButton = Button(QPixmap('tiles/tick.png'), Cons.LARGE_BUTTON, button_parent)
        self._add_button("playButton", self.playButton)
        self.acceptButton = Button(QPixmap('tiles/next.png'), Cons.LARGE_BUTTON, button_parent)
        self._add_button("acceptButton", self.acceptButton)
        self.passButton = Button(QPixmap('tiles/pass.png'), Cons.SMALL_BUTTON, button_parent)
        self._add_button("passButton", self.passButton)
        self.challengeButton = Button(QPixmap('tiles/query.png'), Cons.SMALL_BUTTON, button_parent)
        self._add_button("challengeButton", self.challengeButton)
        self.exchangeButton = Button(QPixmap('tiles/exchange.png'), Cons.SMALL_BUTTON, button_parent)
        self._add_button("exchangeButton", self.exchangeButton)
        self.quitButton = Button(QPixmap('tiles/quit.png'), Cons.SMALL_BUTTON, button_parent)
        self._add_button("quitButton", self.quitButton)

        # Accept button for entry screens
        self.nextButton = Button(QPixmap('tiles/next.png'), Cons.LARGE_BUTTON, button_parent)
        self._add_button("nextButton", self.nextButton)

        # Buttons for end screen
        self.backButton = Button(QPixmap('tiles/back.png'), Cons.SMALL_BUTTON, button_parent)
        self._add_button("backButton", self.backButton)
        self.endButton = Button(QPixmap('tiles/quit.png'), Cons.LARGE_BUTTON, button_parent)
        self._add_button("endButton", self.endButton)
        self.newButton = Button(QPixmap('tiles/restart.png'), Cons.SMALL_BUTTON, button_parent)
        self._add_button("newButton", self.newButton)

    def _add_button(self, name, button):
        """ Register button in dictionary """
        self.buttons[name] = button

    def set_button_pos(self):
        """ Set default button positions """
        self.backButton.setPos(Cons.BACK_BUTTON, Cons.BUTTON_Y)
        self.endButton.setPos(Cons.END_BUTTON, Cons.BUTTON_Y)
        self.newButton.setPos(Cons.NEW_BUTTON, Cons.BUTTON_Y)

        self.playButton.setPos(Cons.PLAY_BUTTON, Cons.BUTTON_Y)
        self.acceptButton.setPos(Cons.ACCEPT_BUTTON, Cons.BUTTON_Y)
        self.passButton.setPos(Cons.PASS_BUTTON, Cons.BUTTON_Y)
        self.challengeButton.setPos(Cons.CHALLENGE_BUTTON, Cons.BUTTON_Y)
        self.exchangeButton.setPos(Cons.EXCHANGE_BUTTON, Cons.BUTTON_Y)
        self.quitButton.setPos(Cons.QUIT_BUTTON, Cons.BUTTON_Y)

        self.nextButton.setPos(Cons.NEXT_BUTTON, Cons.BUTTON_Y)

    def reset_tips(self):
        """ Set tooltip text to correct language """
        self.playButton.setToolTip(self.scene.alphabet.TOOLTIPS["play"])
        self.acceptButton.setToolTip(self.scene.alphabet.TOOLTIPS["accept"])
        self.passButton.setToolTip(self.scene.alphabet.TOOLTIPS["pass"])
        self.challengeButton.setToolTip(self.scene.alphabet.TOOLTIPS["challenge"])
        self.exchangeButton.setToolTip(self.scene.alphabet.TOOLTIPS["exchange"])
        self.quitButton.setToolTip(self.scene.alphabet.TOOLTIPS["quit"])
        self.nextButton.setToolTip(self.scene.alphabet.TOOLTIPS["next"])
        self.backButton.setToolTip(self.scene.alphabet.TOOLTIPS["back"])
        self.endButton.setToolTip(self.scene.alphabet.TOOLTIPS["end"])
        self.newButton.setToolTip(self.scene.alphabet.TOOLTIPS["new"])


# noinspection PyUnresolvedReferences
class SetupMachine(QStateMachine):
    """ Setup game state machine """

    action_complete = pyqtSignal()  # emitted when action completed
    time_out = pyqtSignal()  # emitted on clock timeout
    try_again = pyqtSignal()  # emitted if repeat action required
    not_valid = pyqtSignal()  # emitted if turn invalid
    end_game = pyqtSignal()  # emitted to end game
    players_complete = pyqtSignal()  # emitted when players set up
    radio_complete = pyqtSignal(int, int)  # emitted when radio button clicked

    def __init__(self, scene):
        super(SetupMachine, self).__init__()

        self.st_code = qstates.States(scene, self)

        buttons = scene.buttons.buttons

        self.rootState = None
        self.languageState, self.loadState, self.instructState = None, None, None
        self.nameState, self.setplayersState, self.tileState = None, None, None
        self.checkState, self.setupState, self.startState = None, None, None
        self.playState, self.blankState, self.acceptState = None, None, None
        self.passState, self.challengeState, self.exchangeState = None, None, None
        self.endState, self.quitState = None, None

        self.set_states()
        self.set_signal_transitions()
        self.set_button_transitions(buttons)
        states = self.assign_name()
        self.assign_visibility(states, buttons)
        self.assign_enabled(states, buttons)
        self.set_structure()
        self.set_connections()
        self.start()  # start state machine

    def set_states(self):
        """ Create state machine states """

        self.rootState = QState()
        # Initial setup states
        self.languageState = QState(self.rootState)
        self.loadState = QState(self.rootState)
        self.instructState = QState(self.rootState)
        self.nameState = QState(self.rootState)
        self.setplayersState = QState(self.rootState)
        self.tileState = QState(self.rootState)
        self.checkState = QState(self.rootState)
        self.setupState = QState(self.rootState)
        # Wait state between turns
        self.startState = QState(self.rootState)
        # Playing states
        self.playState = QState(self.rootState)
        self.blankState = QState(self.rootState)
        self.acceptState = QState(self.rootState)
        self.passState = QState(self.rootState)
        self.challengeState = QState(self.rootState)
        self.exchangeState = QState(self.rootState)
        self.endState = QState(self.rootState)
        # End state
        self.quitState = QFinalState()

    def set_signal_transitions(self):
        """ pyqtSignal transitions from states """

        self.loadState.addTransition(self.action_complete, self.instructState)
        self.setplayersState.addTransition(self.players_complete, self.tileState)
        self.checkState.addTransition(self.action_complete, self.setupState)
        self.checkState.addTransition(self.try_again, self.tileState)
        self.setupState.addTransition(self.action_complete, self.startState)
        self.blankState.addTransition(self.not_valid, self.playState)
        self.blankState.addTransition(self.try_again, self.blankState)
        self.blankState.addTransition(self.action_complete, self.acceptState)
        self.acceptState.addTransition(self.action_complete, self.startState)
        self.passState.addTransition(self.action_complete, self.startState)
        self.challengeState.addTransition(self.action_complete, self.startState)
        self.rootState.addTransition(self.end_game, self.endState)

    def set_button_transitions(self, buttons):
        """ Button transitions from states """

        self.languageState.addTransition(buttons["nextButton"].pressed, self.loadState)
        self.instructState.addTransition(buttons["nextButton"].pressed, self.nameState)
        self.nameState.addTransition(buttons["nextButton"].pressed, self.setplayersState)
        self.tileState.addTransition(buttons["nextButton"].pressed, self.checkState)
        self.acceptState.addTransition(buttons["challengeButton"].pressed,
                                       self.challengeState)
        self.rootState.addTransition(buttons["playButton"].pressed, self.playState)
        self.rootState.addTransition(buttons["passButton"].pressed, self.passState)
        self.rootState.addTransition(buttons["exchangeButton"].pressed,
                                     self.exchangeState)
        self.playState.addTransition(buttons["acceptButton"].pressed, self.blankState)
        self.exchangeState.addTransition(buttons["acceptButton"].pressed, self.acceptState)
        self.rootState.addTransition(buttons["quitButton"].pressed, self.endState)
        self.endState.addTransition(buttons["backButton"].pressed, self.startState)
        self.endState.addTransition(buttons["endButton"].pressed, self.quitState)
        self.endState.addTransition(buttons["newButton"].pressed, self.nameState)

    def assign_name(self):
        """ Assign name to property 'state' for each state """

        states = {}
        self.rootState.assignProperty(self, "state", "root")
        states["root"] = self.rootState
        self.languageState.assignProperty(self, "state", "language")
        states["language"] = self.languageState
        self.loadState.assignProperty(self, "state", "load")
        states["load"] = self.loadState
        self.instructState.assignProperty(self, "state", "instruct")
        states["instruct"] = self.instructState
        self.nameState.assignProperty(self, "state", "name")
        states["name"] = self.nameState
        self.setplayersState.assignProperty(self, "state", "setplayers")
        states["setplayers"] = self.setplayersState
        self.tileState.assignProperty(self, "state", "tiles")
        states["tiles"] = self.tileState
        self.checkState.assignProperty(self, "state", "check")
        states["check"] = self.checkState
        self.setupState.assignProperty(self, "state", "setup")
        states["setup"] = self.setupState
        self.startState.assignProperty(self, "state", "start")
        states["start"] = self.startState
        self.playState.assignProperty(self, "state", "play")
        states["play"] = self.playState
        self.blankState.assignProperty(self, "state", "blank")
        states["blank"] = self.blankState
        self.acceptState.assignProperty(self, "state", "accept")
        states["accept"] = self.acceptState
        self.passState.assignProperty(self, "state", "pass")
        states["pass"] = self.passState
        self.challengeState.assignProperty(self, "state", "challenge")
        states["challenge"] = self.challengeState
        self.exchangeState.assignProperty(self, "state", "exchange")
        states["exchange"] = self.exchangeState
        self.endState.assignProperty(self, "state", "end")
        states["end"] = self.endState
        return states

    @staticmethod
    def assign_visibility(states, buttons):
        """ Assign visibility property for each button in each state """

        visibility = {"language": ["nextButton"],
                      "load": [],
                      "instruct": ["nextButton"],
                      "name": ["nextButton"],
                      "tiles": ["nextButton"],
                      "start": ["playButton", "acceptButton", "passButton", "challengeButton",
                                "exchangeButton", "quitButton"],
                      "play": ["playButton", "acceptButton", "passButton", "challengeButton",
                               "exchangeButton", "quitButton"],
                      "blank": ["playButton", "acceptButton", "passButton", "challengeButton",
                                "exchangeButton", "quitButton"],
                      "accept": ["playButton", "acceptButton", "passButton", "challengeButton",
                                 "exchangeButton", "quitButton"],
                      "pass": ["playButton", "acceptButton", "passButton", "challengeButton",
                               "exchangeButton", "quitButton"],
                      "exchange": ["playButton", "acceptButton", "passButton", "challengeButton",
                                   "exchangeButton", "quitButton"],
                      "challenge": ["playButton", "acceptButton", "passButton", "challengeButton",
                                    "exchangeButton", "quitButton"],
                      "end": ["newButton", "endButton", "backButton"]}

        for name, state in states.items():
            button_list = []
            if name in visibility:
                button_list = visibility[name]
            for k, b in buttons.items():
                if k in button_list:
                    state.assignProperty(b, "visible", "True")
                else:
                    state.assignProperty(b, "visible", "False")

    @staticmethod
    def assign_enabled(states, buttons):
        """ Assign enabled property for each button in each state """

        enabled = {"language": ["nextButton"],
                   "load": [],
                   "instruct": ["nextButton"],
                   "name": ["nextButton"],
                   "tiles": ["nextButton"],
                   "start": ["playButton", "quitButton"],
                   "play": ["acceptButton", "passButton", "exchangeButton"],
                   "accept": ["challengeButton"],
                   "pass": ["playButton"],
                   "exchange": ["acceptButton"],
                   "end": ["newButton", "endButton", "backButton"]}

        for name, state in states.items():
            button_list = []
            if name in enabled:
                button_list = enabled[name]
            for k, b in buttons.items():
                if k in button_list:
                    state.assignProperty(b, "enabled", "True")
                else:
                    state.assignProperty(b, "enabled", "False")

    def set_structure(self):
        """ Set initial anf final states """

        self.addState(self.rootState)
        self.addState(self.quitState)
        self.setInitialState(self.rootState)
        self.rootState.setInitialState(self.languageState)
        self.finished.connect(self.end_m)

    def set_connections(self):
        """ Set enter and exit connections for states """

        self.languageState.entered.connect(self.st_code.s_enter_language)
        self.languageState.exited.connect(self.st_code.s_exit_language)
        self.loadState.entered.connect(self.st_code.s_enter_load)
        self.instructState.entered.connect(self.st_code.s_enter_instruct)
        self.nameState.entered.connect(self.st_code.s_enter_name)
        self.setplayersState.entered.connect(self.st_code.s_enter_setplayers)
        self.setplayersState.exited.connect(self.st_code.s_exit_setplayers)
        self.tileState.entered.connect(self.st_code.s_enter_tile)
        self.checkState.entered.connect(self.st_code.s_enter_check)
        self.setupState.entered.connect(self.st_code.s_enter_setup)
        self.startState.entered.connect(self.st_code.s_enter_start)
        self.playState.entered.connect(self.st_code.s_enter_play)
        self.playState.exited.connect(self.st_code.s_exit_play)
        self.blankState.entered.connect(self.st_code.s_enter_blank)
        self.acceptState.entered.connect(self.st_code.s_enter_accept)
        self.passState.entered.connect(self.st_code.s_enter_pass)
        self.challengeState.entered.connect(self.st_code.s_enter_challenge)
        self.exchangeState.entered.connect(self.st_code.s_enter_exchange)
        self.endState.entered.connect(self.st_code.s_enter_end)
        self.endState.exited.connect(self.st_code.s_exit_end)

    @staticmethod
    def end_m():
        """ State machine quit """

        sys.exit(0)
