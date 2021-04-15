""" Enter and exit procedures for all states
    in game state machine """

import os
import subprocess
from PyQt5.QtCore import Qt, QObject, QPointF, pyqtSlot, QTimer
from PyQt5.QtWidgets import (QTextEdit, QFrame, QVBoxLayout,
                             QGraphicsPixmapItem, QPushButton)
from PyQt5.QtGui import QPixmap

import Constants as Cons
import qcloc
import qenwau
import qchwaraewr as qch
import qbwrdd
import qteils
import qtestun
import qgeiriau
import qalphabet


class States(QObject):
    """ Class holding all entry and exit actions for states """

    def __init__(self, scene, machine):
        super(States, self).__init__()

        self.scene = scene
        self.machine = machine
        self.result = (None,)  # Passes values between states
        # as tuple (description, value)
        # Holds the error if state exited on error
        self.start = None  # Holds instance of get names screen
        self.current_state = None  # Holds current state - used to get
        # previous state (before it is reset)
        self.letters = None  # Set of playing letters
        self.players = scene.get_players()

        self.clock = qcloc.DigitalClock(self.scene)  # Digital min/sec count up timer
        self.countdown = qcloc.DigitalClock(self.scene, 5)  # Digital min/sec count down timer
        # time_out signal emitted
        # after 5 secs

        self.final_scores = qtestun.Finalscores(self.scene, self.players)
        self.checker = None  # Forms and checks all words formed on board
        self.turn = None  # Present turn as [(word, score, valid(T/F)]
        self.active_tiles = ActiveTiles(self.scene)  # Holds details of all active tiles
        self.player = -1  # Current player (0/1)

        self.no_pc = 0  # No of computer players

    # -------------------------------------------------------------------------
    def s_enter_language(self):
        """ Enter initial state to get language """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)

        back_pix = QPixmap('tiles/scrabble.jpg')
        back_pix = back_pix.scaled(Cons.WINDOW_SIZE[0], Cons.WINDOW_SIZE[1],
                                   Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        back_pix = QGraphicsPixmapItem(back_pix)
        back_pix.setOpacity(0.9)
        self.scene.addItem(back_pix)

        # Get list of all available languages and their sub-directories
        # Set self.result to default (button 0, list of sub-directories)
        langs = self._get_langs("__init__.py")
        self.result = (0, [lst[0] for lst in langs])
        block = QFrame()
        block.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout()
        layout.setSpacing(20)
        ex = qch.Radiobuttons("Dewiswch Iaith\nChoose Language",
                              "wedyn cliciwch y botwm isod\nthen click button below",
                              [lst[1] for lst in langs], self)
        ex.set_frame(True)
        ex.set_default(0)
        self.machine.radio_complete.connect(self._get_language)
        lang_utils = QPushButton("Click here for Language Utilities\n"
                                 "Cliciwch yma am y Defnydd-debau Iaith")
        lang_utils.setStyleSheet("background-color: rgb(230, 200, 167);"
                                 "border-style: solid; border-radius: 6;"
                                 "border-color: #636363; border: 1px solid gray;"
                                 "font-family: 'Arial'; font-size: 16px;"
                                 "min-height: 48px;")
        lang_utils.clicked.connect(self._lang_clicked)
        layout.addWidget(ex)
        layout.addWidget(lang_utils)
        block.setLayout(layout)
        proxy = self.scene.addWidget(block)
        proxy.setPos(Cons.WINDOW_SIZE[0] / 2 - ex.width() / 2, Cons.WINDOW_SIZE[1] / 2 - ex.height() / 2)
        proxy.show()

    @staticmethod
    def _lang_clicked():
        """ Launch language utilities """
        path = os.getcwd()
        prog = path + "\\createGADDAG.py"
        _ = subprocess.Popen(["python", prog])

    @staticmethod
    def _get_name(fname):
        """ Get name and active state of language in subdirectory """
        with open(fname, "rt", encoding='utf-8') as f:
            line = f.readline()
            if line.strip():
                line = line.split()
                return line[1], ("active" in line[2].lower())

    def _get_langs(self, file):
        """ Get list of available active languages by searching subdirectories
            Returns list of tuples (sub-directory, language name)"""
        langs = []
        for root, _, files in os.walk(r'.'):  # root, dirs, files
            if file in files and 'alphabet.py' in files:
                drc = os.path.basename(root)
                entry, active = self._get_name(drc + r'\alphabet.py')
                if active and not any(tu[1] == entry for tu in langs):
                    langs.append((drc, entry))
        return langs

    def _get_language(self, button):
        """ Set self.result to chosen language for game
            by replacing first entry with button number """
        if button < 0:
            button = 0
        self.result = (button, self.result[1])

    def s_exit_language(self):
        """ Set alphabet for language choice and exit state """

        self.scene.alphabet = qalphabet.Alphabet(self.result[1][self.result[0]])
        self.machine.radio_complete.disconnect()
        self.scene.buttons.reset_tips()
        self.letters = qteils.Letters(self.scene)  # Set of playing letters
        # based on language choice
        self.result = (None,)  # Reset self.result

    # -------------------------------------------------------------------------
    def s_enter_load(self):
        """ Enter state to load word check """

        word_check = self.scene.alphabet.WORD_CHECK
        self.checker = qgeiriau.Words(self.scene)  # Word checker and scorer
        # based on language choice
        if isinstance(word_check, list) or (isinstance(word_check, str)
                                            and not word_check.lower().endswith(".p")):
            self._end_action()

    def end_load(self):
        """ end of loading """
        self._end_action()

    # -------------------------------------------------------------------------
    def s_enter_instruct(self):
        """ Enter state to show instructions """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        print("DEBUG", self.scene.alphabet.lang)
        qch.Player.reset_players()
        self._clear_scene()
        inst = QTextEdit()
        inst.setReadOnly(True)
        inst.setLineWidth(5)
        inst.setMidLineWidth(5)
        inst.setFrameShape(QFrame.Panel)
        inst.setFrameShadow(QFrame.Sunken)
        inst.move(50, 0)
        inst.resize(Cons.WINDOW_SIZE[0] - 100, Cons.WINDOW_SIZE[1] - 100)
        inst.setAutoFillBackground(True)
        inst.setStyleSheet("background-color:rgb(230, 200, 167);")
        inst.proxy = self.scene.addWidget(inst)
        inst.proxy.setZValue(2000)
        inst.proxy.hide()
        with open(self.scene.alphabet.lang + r"\Instructions.html") as myfile:  # read html from file
            text = "".join(line.strip() for line in myfile)
        text = text[text.index("<"):]  # replace marker with
        inst.setHtml(text)
        inst.proxy.show()

    # -------------------------------------------------------------------------
    def s_enter_name(self):
        """ Enter name state to get names """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        qch.Player.reset_players()
        self._clear_scene()
        if self.scene.players:
            for player in range(0, 2):
                self.scene.players[player].clear_scoreboard()
        self.start = qenwau.Enwau(self.scene)
        if self.scene.alphabet.pc_player():
            self.start.show_msg(self.scene.alphabet.QSTATES_MSGS[22])
        else:
            self.start.show_msg(self.scene.alphabet.QSTATES_MSGS[23])
        self.start.disable_tiles()
        self.start.get_names()

    # -------------------------------------------------------------------------
    def s_enter_setplayers(self):
        """ Enter setplayers state to set up players """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)

        self.no_pc = 0
        # As from init() self.player points to same dict as self.scene.players no need to update
        for player in range(0, 2):
            self.scene.players[player] = qch.Player(self.scene, self.letters, self,
                                                    self.start.n_input[player].get_text("t"))
            self.players[player].set_anim_complete_slot(self._end_action)

            if self.players[player].name == "":
                self.players[player].name = self.scene.alphabet.QCHWARAEWR_MSGS[0]
                self.players[player].name += "_" + str(player + 1)
                self.start.n_input[player].set_text(self.players[player].name)

            if self.players[player].name == "Pc" and self.scene.alphabet.PC_VOCAB:
                self.no_pc += 1
                if self.no_pc == 1:
                    self.players[player].name = self.scene.alphabet.PC_NAME
                    self.start.n_input[player].set_text(self.players[player].name)
                elif self.no_pc == 2:
                    self.players[0].name = self.scene.alphabet.PC_NAME + "_1"
                    self.players[1].name = self.scene.alphabet.PC_NAME + "_2"
                    self.start.n_input[0].set_text(self.players[0].name)
                    self.start.n_input[1].set_text(self.players[1].name)
                self.players[player].get_pc_player()

        if self.no_pc == 0:
            self.machine.players_complete.emit()

    @pyqtSlot(int)
    def end_state(self, no_loaded):
        """ Check for end of process """
        print("DEBUG end_state", self.no_pc, no_loaded)
        if no_loaded == self.no_pc:
            self.machine.players_complete.emit()
        else:
            self.start.show_msg(self.scene.alphabet.QSTATES_MSGS[20])

    def s_exit_setplayers(self):
        """ Exit """
        self.result = (None,)
        for player in range(0, 2):
            print("DEBUG", self.players[player].no, self.players[player].name,
                  self.players[player].pc)

    # -------------------------------------------------------------------------
    def s_enter_tile(self):
        """ Enter choose tile state
            Reentered if error """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        pc_player = []
        for player in range(0, 2):
            if self.players[player].pc:
                pc_player.append(player)
        self.start.enable_tiles()

        player = self._get_player(pc_player)
        self._ask_player(player)
        self.players[player].get_start_tile(self.start, self.countdown)

        if (self.result[0] is not None and self.result[0] == "number"
                and (self.result[1] + self.result[2]) == 1):
            if self.result[1] == 0:
                player = 0
            elif self.result[2] == 0:
                player = 1
            print("DEBUG player", player)
            self._ask_player(player)
            self.result = (None,)

        if self.result[0] is not None:
            for t in self.active_tiles.active:
                t.return_blank()
            self.active_tiles.clear()
            if self.result[0] == "number":
                self.start.show_msg(self.scene.alphabet.QSTATES_MSGS[0])
            elif self.result[0] == "same":
                self.active_tiles.hide_newt()
                self.start.show_msg(self.scene.alphabet.QSTATES_MSGS[1])
            player = self._get_player(pc_player)
            self._ask_player(player)
            QTimer.singleShot(2000, lambda: self._ask_player(player))

    @staticmethod
    def _get_player(pc_player):
        """ Get player no """
        if len(pc_player) == 1:
            return (pc_player[0] + 1) % 2
        return 0

    def _ask_player(self, player):
        """ Show message and get player to choose tile """
        self.start.show_msg(self.players[player].name + " - "
                            + self.scene.alphabet.QSTATES_MSGS[21])
        self.players[player].get_start_tile(self.start, self.countdown)

    # -------------------------------------------------------------------------
    def s_enter_check(self):
        """ Enter check state
            Return to tile state if error
            Unfade tiles """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)

        self.result = (None,)
        left = self.active_tiles.get_left()
        right = self.active_tiles.get_right()
        if not left or not right or len(left) != 1 or len(right) != 1:
            self.result = ("number", len(left), len(right))
            self.scene.machine.try_again.emit()
        else:
            letters = self.active_tiles.get_letters()
            if all(let == letters[0] for let in letters):
                self.result = ("same",)
            tiles = self.active_tiles.get_left()
            tiles.extend(self.active_tiles.get_right())
            for index in range(2):
                tiles[index].setZValue(1000)
                tiles[index].name_tile(index)
                newt = qteils.Tile(tiles[index].letter, self.scene)
                newt.draw_tile(QPointF(Cons.INPUT_NAMES[index][0] + Cons.INPUT_NAMES[index][2],
                                       Cons.INPUT_NAMES[index][1] + 50))
                newt.anim_complete.connect(lambda: self._end_fade(tiles))
                self.active_tiles.add_newt(newt)
            for t in self.active_tiles.newt:
                t.unfade()

    @pyqtSlot()
    def _end_fade(self, tiles):
        """ If tiles the same return to tile state
            else set players """

        letters = self.active_tiles.get_letters()
        if all(let == letters[0] for let in letters):
            self.result = ("same",)
        else:
            self.player = 0
            if (self.scene.alphabet.to_index(tiles[0].letter)
                    > self.scene.alphabet.to_index(tiles[1].letter)):
                self.player = 1
            if tiles[self.player].letter == " ":
                msg = self.scene.alphabet.QSTATES_MSGS[3]
            else:
                msg = (tiles[self.player].letter.upper() + self.scene.alphabet.QSTATES_MSGS[4]
                       + tiles[self._not_player()].letter.upper() + "<br>")
            self.start.show_msg(msg + self.players[self.player].name
                                + self.scene.alphabet.QSTATES_MSGS[5])
        self.countdown.reconnect(self._end_wait)
        self.countdown.hidden(1)

    @pyqtSlot()
    def _end_wait(self):
        """ Return to tile state if error 'same'
            else emit action_complete """

        if self.result[0] == "same":
            self.scene.machine.try_again.emit()
        else:
            self.scene.machine.action_complete.emit()

    # -------------------------------------------------------------------------
    def s_enter_setup(self):
        """ Enter setup state
            Initialise game """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self._clear_scene()
        board = qbwrdd.Board(self.scene)
        board.draw_board()
        # self.letters.letters = self.letters.letters[:len(self.letters.letters)//4]

        self.player = (self.player + 1) % 2  # Switch player (will be switched back in start)
        for i in range(2):
            self.players[i].get_hand()  # Emits action_complete at end

    # -------------------------------------------------------------------------
    def s_enter_start(self):
        """ Enter start state
            Wait for play - Return here after each turn """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        if self.result[0] is None:
            self._set_players()
        self.result = (None,)
        self.players[self.player].message.show_msg(self.scene.alphabet.QSTATES_MSGS[17])
        self.players[self.player].start_turn(self.countdown)

    # -------------------------------------------------------------------------
    def s_enter_play(self):
        """ Enter play state """

        state = self.current_state
        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state, state)
        if state != "blank":
            self._hide_scoreboards()
            self._hide_messages()
            self.active_tiles.clear()
            self.players[self.player].activate(True)
            self.clock.setPos(Cons.TIMER_POS[self.player], Cons.TIMER_Y)
            self.clock.show()
            self.clock.reset()

        self.players[self.player].play_turn(self.countdown)

    def s_exit_play(self):
        """ Exit play state """

        self.clock.stop()
        self.active_tiles.update()

    # -------------------------------------------------------------------------
    def s_enter_blank(self):
        """ Enter blank state """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)

        self.turn = self.checker.get_wordscore(self.active_tiles.get_word())
        print("DEBUG turn", self.turn)
        if self.turn[0][1] < 0:
            self._print_error_msg(self.turn[0][1])
            self.scene.machine.not_valid.emit()
        else:
            if self.result[0] is None:
                # self.active_tiles.update()
                print("DEBUG letters", self.active_tiles.get_letters())
                self.players[self.player].set_anim_complete_slot(self._end_anim)
                self.players[self.player].return_tiles(self.active_tiles.off_tiles)
            else:
                self.players[self.player].message.show_msg(self.scene.alphabet.QSTATES_MSGS[6])
                self._get_blank_letters()

    @pyqtSlot()
    def _end_anim(self):
        """ All played tiles not on board returned """

        if not self.active_tiles.blanks:
            self.scene.machine.action_complete.emit()
        else:
            self.players[self.player].message.show_msg(self.scene.alphabet.QSTATES_MSGS[7])
            self._get_blank_letters()

    def _get_blank_letters(self):
        """ Deal with blank tiles """

        blet = {}
        bpos = []
        for ind, tile in enumerate(self.active_tiles.board_tiles):
            if tile.letter.strip() == "":
                tile.dim(True)
                blet[ind] = qenwau.GetInput(self.scene,
                                            (tile.get_pos().x(), tile.get_pos().y()),
                                            (Cons.WIDTH, Cons.HEIGHT))
                blet[ind].set_regexpression("^[a-zA-Z]$")
                blet[ind].returnPressed.connect(lambda: self.blanks_set(blet))
                blet[ind].raise_()
                bpos.append([ind, tile.get_pos().x(), tile.get_pos().y()])

        if all(coord[2] == bpos[0][2] for coord in bpos):
            bx = sorted(bpos, key=lambda pos: pos[1])
            blet[bx[0][0]].setFocus()
        else:
            by = sorted(bpos, key=lambda pos: pos[2])
            blet[by[0][0]].setFocus()

        self.players[self.player].get_blanks(blet, self.countdown)

    @pyqtSlot()
    def blanks_set(self, blet):
        """ Set letters on tiles
            set error if any missing
            and return to start of state"""

        self.result = (None,)
        for key, val in blet.items():
            tile = self.active_tiles.board_tiles[key]
            tile.letter = val.get_text("l").strip()
            if tile.letter != "":
                tile.dim(False)
                val.hide()
                tile.add_letter(tile.letter.upper())
            else:
                self.result = ("missing",)

        if self.result[0] is None:
            self.scene.machine.action_complete.emit()
        else:
            self.scene.machine.try_again.emit()

    # -------------------------------------------------------------------------
    def s_enter_accept(self):
        """ Enter accept state """

        state = self.current_state
        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state, state)

        if state == "exchange":
            self.players[self.player].exchange_tiles(self.active_tiles.active)
        else:
            self.turn = self.checker.get_wordscore(self.active_tiles.get_word())
            for teil in self.active_tiles.board_tiles:
                teil.set_in_board()
            self.players[self.player].score_board.show_words(self.turn, False,
                                                             len(self.active_tiles.board_tiles))
            self._hide_messages()
            self.clock.hide()
            self.players[self._not_player()].message.show_msg(self.scene.alphabet.QSTATES_MSGS[8])
            self.countdown.setPos(Cons.TIMER_POS[self._not_player()], Cons.TIMER_Y)
            self.countdown.reconnect(self._nochallenge)
            self.countdown.reset()

    @pyqtSlot()
    def _nochallenge(self):
        """ No challenge made or incorrect """

        self.players[self._not_player()].message.hide()
        self._endchallenge(False)

    # -------------------------------------------------------------------------
    def s_enter_challenge(self):
        """ Enter challenge state
            Check and respond """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)

        print("DEBUG turn", self.turn)
        self.turn, html_error = self.checker.check_words(self.turn)
        if html_error:
            self.players[self._not_player()].message.show_msg(self.scene.alphabet.QSTATES_MSGS[18])
            self.countdown.reconnect(self._nochallenge)
            self.countdown.hidden()
        else:
            self.countdown.stop()
            self.players[self.player].score_board.show_words(self.turn, True,
                                                             len(self.active_tiles.board_tiles))
            self.players[self.player].set_anim_complete_slot(self._end_action)
            no_errors = sum(1 for word in self.turn if not word[2])
            if no_errors == 0:
                self.players[self._not_player()].message.show_msg(
                    self.scene.alphabet.QSTATES_MSGS[9])
                self.countdown.reconnect(self._challenge_fail)
                self.countdown.hidden()
            else:
                self.players[self._not_player()].message.show_msg(
                    str(no_errors) + (self.scene.alphabet.QSTATES_MSGS[10] if no_errors == 1
                                      else self.scene.alphabet.QSTATES_MSGS[11])
                    + self.scene.alphabet.QSTATES_MSGS[12])

                self.players[self.player].message.show_msg(self.scene.alphabet.QSTATES_MSGS[13])
                self.countdown.reconnect(self._challenge_success)
                self.countdown.hidden()

    @pyqtSlot()
    def _challenge_success(self):
        """ Return tiles to hand if challenge succeeds """

        if self.active_tiles.blanks:
            for tile in self.active_tiles.blanks:
                tile.letter = " "
                tile.txt.hide()
        self.players[self.player].return_tiles(self.active_tiles.board_tiles)

    @pyqtSlot()
    def _challenge_fail(self):
        """ Return tiles to hand if challenge succeeds """

        self._endchallenge(True)

    def _endchallenge(self, challenge):
        """ Process player if no challenge or failed challenge """

        self.countdown.hide()
        self.players[self.player].set_anim_complete_slot(self._no_letters)
        for teil in self.active_tiles.board_tiles:
            teil.set_in_board()
        self.checker.set_letters(self.active_tiles.get_word())
        self.players[self.player].update_score(self.turn, len(self.active_tiles.board_tiles))
        self.players[self.player].totals.show_totals()
        self.players[self.player].update_hand(self.active_tiles.board_tiles)
        if self.letters.nomoreletters and not self.players[self.player].get_letters():
            self.players[self.player].message.show_msg(self.scene.alphabet.QSTATES_MSGS[14])
            self.countdown.reconnect(self._endgame)
            self.countdown.hidden()
        elif self.letters.nomoreletters:
            self.players[self.player].message.show_msg(self.scene.alphabet.QSTATES_MSGS[15])
        if challenge:
            self.player = self._not_player()

    @pyqtSlot()
    def _endgame(self):
        """ Signal to end game """

        self.scene.machine.end_game.emit()

    @pyqtSlot()
    def _no_letters(self):
        """ Signal to end game """

        if self.letters.nomoreletters:
            self.countdown.setPos(Cons.TIMER_POS[self.player], Cons.TIMER_Y)
            self.countdown.reconnect(self._end_action)
            self.countdown.hidden(0)
        else:
            self._end_action()

    # -------------------------------------------------------------------------
    def s_enter_pass(self):
        """ Enter pass state
            Return all tiles in play """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self.players[self.player].return_tiles(self.active_tiles.active)
        self.active_tiles.clear()

    # -------------------------------------------------------------------------
    def s_enter_exchange(self):
        """ Enter exchange state
            All work done in graphics scene and accept state """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self.players[self.player].return_tiles(self.active_tiles.active)
        self.active_tiles.clear()
        self.players[self.player].message.show_msg(self.scene.alphabet.QSTATES_MSGS[16])

        self.players[self.player].play_exchange(self.countdown)

    # -------------------------------------------------------------------------
    def s_enter_end(self):
        """ Enter end state
            Confirm quit then
            Show final scores and quit """

        self.current_state = self.machine.property("state")
        print("DEBUG", self.current_state)
        self._hide_messages()
        self._hide_scoreboards()
        scores = [self.players[0].score, self.players[1].score]
        hands = [self.checker.val_letters(self.players[0].get_letters()),
                 self.checker.val_letters(self.players[1].get_letters())]
        finals = [self.players[0].score - hands[0], self.players[1].score - hands[1]]
        for player in range(2):
            if not self.players[player].get_letters:
                finals[player] = finals[player] + hands[(player + 1) % 2]
        winner = finals.index(max(finals))
        if finals[0] == finals[1]:
            winner = scores.index(max(scores))
        self.final_scores.show_scores(hands, finals, winner)

    def s_exit_end(self):
        """ Exit end state """
        self.final_scores.hide()
        self.result = ("end",)

    # -------------------------------------------------------------------------

    def _clear_scene(self):
        """ Clear graphics items from scene
            Items with attribute 'persistent' set not cleared """

        for item in self.scene.items():
            if not hasattr(item, 'persistent'):
                self.scene.removeItem(item)

    def _set_players(self):
        """ Initialise all player settings for next turn """

        self.clock.hide()
        self.countdown.hide()
        self._hide_messages()
        self._hide_scoreboards()
        self.players[self.player].activate(False)
        self.player = (self.player + 1) % 2
        self.players[self.player].activate(False)

    def _not_player(self):
        """ Return player not presently playing """

        return (self.player + 1) % 2

    def _hide_scoreboards(self):
        """ Clear all scoreboards """

        for player in range(0, 2):
            self.players[player].score_board.hide()

    def _hide_messages(self):
        """ Clear all player messages """

        for player in range(0, 2):
            self.players[player].message.hide()

    def _print_error_msg(self, error_no):
        """ Print error message """

        error_msg = {-1: self.scene.alphabet.ERROR_MSGS[0],
                     -2: self.scene.alphabet.ERROR_MSGS[1],
                     -3: self.scene.alphabet.ERROR_MSGS[2],
                     -4: self.scene.alphabet.ERROR_MSGS[3],
                     -5: self.scene.alphabet.ERROR_MSGS[4],
                     -6: self.scene.alphabet.ERROR_MSGS[5]}
        self.players[self.player].message.show_msg(error_msg[error_no])

    @pyqtSlot()
    def _end_action(self):
        """ Emit end of action signal """

        self.scene.machine.action_complete.emit()


class ActiveTiles:
    """ Class holding data on active tiles """

    def __init__(self, scene):
        """ Initialize data structure """

        self.scene = scene
        self.active = self.scene.active
        self.board_tiles = None
        self.off_tiles = None
        self.blanks = None
        self.letters = None
        self.newt = []

    def clear(self):
        """ Clear active tiles """

        self.scene.active.clear()

    def update(self):
        """ Process to get tiles on and off the board
            and list of letters and board positions (letter, (row, col)) """

        self.board_tiles = [t for t in self.active if -1 not in self.convert(t.get_pos(), True)]
        self.off_tiles = [t for t in self.active if t not in self.board_tiles]
        self.blanks = [t for t in self.board_tiles if t.letter.strip() == ""]

    def get_word(self):
        """ Return list of letters and board positions (letter, (row, col)) """
        word = [(t.letter, self.convert(t.get_pos(), True), t in self.blanks)
                for t in self.board_tiles]
        return word

    def get_letters(self):
        """ Return list of active letters only """

        return [t.letter for t in self.active]

    def get_board_letters(self):
        """ Return list of board letters only """

        return [t.letter for t in self.board_tiles]

    def get_left(self):
        """ Return list of tiles off to the left of board """

        self.update()
        return [t for t in self.active if self.convert(t.get_pos(), False)[1] < 3]

    def get_right(self):
        """ Return list of tiles off to the right of board """

        self.update()
        return [t for t in self.active if self.convert(t.get_pos(), False)[1] > 11]

    def add_newt(self, tile):
        """ Letter tiles used in game start """

        self.newt.append(tile)

    def hide_newt(self):
        """ Hide letter tiles """

        for t in self.newt:
            t.hide()
        self.newt.clear()

    @staticmethod
    def convert(value, board):
        """ convert tile coordiates to board (row, col) """

        (row, col) = ((value.y() - Cons.MARGIN) // (Cons.MARGIN + Cons.HEIGHT),
                      (value.x() - Cons.BOARD[0] - Cons.MARGIN) // (Cons.MARGIN + Cons.WIDTH))
        if board and (row < 0 or col < 0 or row > 14 or col > 14):
            return -1, -1
        return int(row), int(col)
