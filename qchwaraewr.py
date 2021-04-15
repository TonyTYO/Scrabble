""" Defines player in game """

from random import randint

from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, QPointF
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QGroupBox,
                             QButtonGroup, QRadioButton, QLabel, QWidget)
from PyQt5.QtGui import QFont

import qteils
import qtestun
import scmoves
import Constants as Cons


class Player:
    """ Class provides all information
        for a player """

    no = 0  # provides unique player number

    def __init__(self, scene, letters, smachine, name=None):

        self.scene = scene
        self.smachine = smachine

        self.name = name  # player name
        self.no = Player.no  # player number
        Player.no += 1  # increment to next number

        self.hand = qteils.Hand(letters, self.no, scene)
        self.hand.anim_complete.connect(self.end_anim)  # default slot required
        # before use of disconnect()
        self.score = 0  # current score

        self.score_board = qtestun.Scoreboard(self.scene, self)
        self.totals = qtestun.Totals(self.scene, self)
        self.message = qtestun.Msg(self.scene, self)
        self.score_board.hide()
        self.totals.hide()
        self.message.hide()

        self.pc = False  # True for computer player
        self.pc_play = None  # Computer player class
        self.word = None  # Current word for pc

    @classmethod
    def reset_players(cls):
        """ Reset number count to 0 """
        cls.no = 0

    def clear_scoreboard(self):
        """ Remove scoreboard """
        self.scene.removeItem(self.totals.proxy)

    def update_score(self, words, no_tiles):
        """ Add total words score to players total """
        self.score += sum([w[1] for w in words])
        if no_tiles == Cons.NO_HAND:
            self.score += 50

    def get_letters(self):
        """ Return list of letters in hand """
        return self.hand.hand_letters()

    def set_anim_complete_slot(self, slot):
        """ Set slot for anim_complete signal from hand """
        self.hand.anim_complete.disconnect()
        self.hand.anim_complete.connect(slot)

    def get_hand(self):
        """ Get initial hand """
        self.hand.get_hand()

    def activate(self, active):
        """ Sets hand as active or not active
            Inactive tiles are dimmed """
        self.hand.activate_hand(active)
        self.hand.dim_hand(not active)

    def update_hand(self, tiles):
        """ Update hand after turn
            Remove tiles and get new ones """
        self.hand.update_hand(tiles)

    def return_tiles(self, tiles):
        """ Return tiles to rack """
        self.hand.return_tiles(tiles)

    def exchange_tiles(self, tiles):
        """ Exchange chosen tiles for new ones """
        self.hand.exchange_tiles(tiles)

    def end_anim(self):
        """ Default slot for animation  signal """
        pass

    # -------------------------------------------------------------------------
    # Player routines that check for computer player

    def get_start_tile(self, start, clock):
        """ Choose tile at start
            Nearest to A starts
            clock: countdown sec timer """

        if self.pc:
            clock.setPos(0, 0)
            clock.reconnect(lambda: self._pc_choose_tile(start))
            clock.hidden(1)

    def start_turn(self, clock):
        """ Players turn - click Play button """
        if self.pc:
            clock.setPos(0, 0)
            clock.reconnect(lambda: self._click_button(self.scene.buttons.playButton,
                                                       Cons.PLAY_CLICK_X))
            clock.hidden(1)

    def play_turn(self, clock):
        """ Players turn - start after delay """
        if self.pc:
            clock.setPos(0, 0)
            clock.reconnect(self.continue_play)
            clock.hidden(1)

    def continue_play(self):
        """ Players turn """
        rack = [t[0] for t in self.hand.hand]
        print("DEBUG rack", rack)
        self.word = self.pc_play.update_state(rack)
        print("DEBUG chwaraewr", self.word)
        if self.word is None:
            if self.is_low_freq():
                self._click_button(self.scene.buttons.exchangeButton, Cons.EXCHANGE_CLICK_X)
            else:
                self._click_button(self.scene.buttons.passButton, Cons.PASS_CLICK_X)
        else:
            self._pc_play_word()

    def get_blanks(self, blanks, clock):
        """ Enter blank letters """
        if self.pc:
            clock.setPos(0, 0)
            clock.reconnect(lambda: self._pc_enter_blanks(blanks, clock))
            clock.hidden(2)

    def play_exchange(self, clock):
        """ Exchange letters """
        if self.pc:
            clock.setPos(0, 0)
            clock.reconnect(self._pc_exchange_letters)
            clock.hidden(2)

    def is_low_freq(self):
        """ Check for low frequency use letters in hand """
        letts = self.hand.hand_letters()
        l_frequencies = self.scene.alphabet.LETTER_FREQUENCIES
        freq_lst = [(let, l_frequencies.get(let, 100))
                    for let in letts]  # 100 default for blank
        freq = 3
        return any(t[1] < freq for t in freq_lst)

    # -------------------------------------------------------------------------
    # Computer player routines

    def _pc_choose_tile(self, start):
        """ Choose tile at random in names screen
            and move off board on player's side """

        while True:
            tile_no = randint(0, Cons.SQUARE_SIZE - 1) * 10 + randint(0, Cons.SQUARE_SIZE - 1)
            tile = start.blank[tile_no]
            tile_pos = tile.get_pos() + QPointF(Cons.WIDTH / 2, Cons.HEIGHT / 2)
            if tile not in self.scene.active:
                break
        endx = 200 + 800 * self.no
        endy = 500
        self._goto_tile(tile, (int(tile_pos.x()), int(tile_pos.y())), (endx, endy))

    def _goto_tile(self, tile, start, end):
        """ Take mouse to required tile """
        x, y = start
        endx, endy = end
        self.scene.move_reconnect(lambda: self._tile_move(tile, endx, endy))
        self.scene.mouse_move(x, y)

    def _tile_move(self, tile, endx, endy):
        """ Pick up tile and move off grid """
        self.scene.parent.setCursor(Qt.PointingHandCursor)
        self.scene.move_reconnect(self._move_complete)
        self.scene.tile_move(tile, endx, endy)
        self.scene.active.append(tile)

    def _move_complete(self):
        """ Goto and press Next button """
        self.scene.parent.setCursor(Qt.ArrowCursor)
        self._click_button(self.scene.buttons.nextButton, Cons.NEXT_CLICK_X)

    # --------------------------------------------------
    def _pc_play_word(self):
        """ Computer player play word """
        print("DEBUG word", self.word)
        rack = list(self.hand.hand)
        groupIter = iter(self.word[2])
        self._place_tile(rack, groupIter)

    def _place_tile(self, rack, iterlist):
        """ Computer player place tiles """
        group = next(iterlist, None)
        if group is not None:
            print("DEBUG group", group)
            letter, (row, col), _ = group
            print("DEBUG tiles before", [t[0] for t in rack])
            if letter in [t[0] for t in rack]:
                tiletupl = next(t for t in rack if t[0] == letter)
            else:
                tiletupl = next(t for t in rack if t[0] == ' ')
            rack.remove(tiletupl)
            print("DEBUG tiles after", [t[0] for t in rack])
            tile = tiletupl[1]
            tile_pos = tile.get_pos()
            endx = Cons.BOARD[0] + (Cons.MARGIN + Cons.WIDTH) * col + Cons.MARGIN
            endy = (Cons.MARGIN + Cons.HEIGHT) * row + Cons.MARGIN
            end = (endx, endy)
            self.scene.move_reconnect(lambda: self._move_tile(tile, end, rack, iterlist))
            self.scene.mouse_move(tile_pos.x(), tile_pos.y())
        else:
            self._click_button(self.scene.buttons.acceptButton, Cons.ACCEPT_CLICK_X)

    def _move_tile(self, tile, end, rack, iterlist):
        """ Computer player move tile to position """
        endx, endy = end
        self.scene.parent.setCursor(Qt.PointingHandCursor)
        self.scene.move_reconnect(lambda: self._place_complete(tile, rack, iterlist))
        self.scene.tile_move(tile, endx, endy)

    def _place_complete(self, tile, rack, iterlist):
        """ Computer player place tile on board """
        self.scene.parent.setCursor(Qt.ArrowCursor)
        self._set_tile(tile)
        self._place_tile(rack, iterlist)

    def _set_tile(self, tile):
        """ Computer player set tile in position """
        self.scene.active.append(tile)
        collisions = tile.pixmap_item.collidingItems()
        if collisions:
            x, y = self._process_collisions(tile, collisions)
            if x is not None:
                tile.set_pos(x, y)

    # --------------------------------------------------
    def _pc_enter_blanks(self, blanks, clock):
        """ Computer player enter letters for blanks """
        print("DEBUG word", self.word)
        clock.reconnect(lambda: self._enter_letters(blanks, groupIter, clock))
        groupIter = iter(blanks.items())
        self._enter_letters(blanks, groupIter, clock)

    def _enter_letters(self, blanks, iterlist, clock):
        """ Computer player enter letters """
        group = next(iterlist, None)
        if group is not None:
            indx, ledit = group
            ledit.setFocus()
            lett = self.word[2][indx][0]
            print("DEBUG lett", self.word[2], indx, lett)
            if lett:
                self.scene.move_reconnect(lambda: self._put_letter(lett, ledit, clock))
                self.scene.mouse_move(ledit.bot_left[0], ledit.bot_left[1])
        else:
            self.smachine.blanks_set(blanks)

    @staticmethod
    def _put_letter(lett, ledit, clock):
        """ Computer player insert letter on tile """
        ledit.insert(lett[0])
        clock.hidden(1)

    # --------------------------------------------------
    def _pc_exchange_letters(self):
        """ Computer player exchange letters """
        rack = list(self.hand.hand)
        letts = self.hand.hand_letters()
        freq = [(let, self.pc_play.l_frequencies.get(let, 100)) for let in letts]  # 100 default for blank
        sort_freq = sorted(freq, key=lambda x: x[1])
        freq = 3
        low_freq = [t[0] for t in sort_freq if t[1] < freq]
        groupIter = iter(low_freq)
        self._xplace_tile(rack, groupIter)

    def _xplace_tile(self, rack, iterlist):
        """ Computer player nudge chosen tiles """
        letter = next(iterlist, None)
        tiletupl = None
        if letter is not None:
            print("DEBUG group", letter)
            if letter in [t[0] for t in rack]:
                tiletupl = next(t for t in rack if t[0] == letter)
            rack.remove(tiletupl)
            tile = tiletupl[1]
            tile_pos = tile.get_pos()
            self._xpickup_tile(tile, (tile_pos.x(), tile_pos.y()), rack, iterlist)
        else:
            self._click_button(self.scene.buttons.acceptButton, Cons.ACCEPT_CLICK_X)

    def _xpickup_tile(self, tile, pos, rack, iterlist):
        """ Computer player move to tile """
        x, y = pos
        self.scene.move_reconnect(lambda: self._xmove_tile(tile, rack, iterlist))
        self.scene.mouse_move(x, y)

    def _xmove_tile(self, tile, rack, iterlist):
        """ Computer player nudge tile up from rack """
        tile.lift_tile()
        self.scene.active.append(tile)
        QTimer.singleShot(1000, lambda: self._xplace_tile(rack, iterlist))

    # --------------------------------------------------
    def _click_button(self, button, xpos):
        """ Move mouse to button and click it """

        button.pc_mouse_click(self.scene, xpos, Cons.CLICK_Y)

    # --------------------------------------------------

    def _process_collisions(self, tile, collisions):
        """ Jump tile to nearest board cell """

        rects = [r.rect() for r in collisions if isinstance(r, QGraphicsRectItem)]
        rects = [[r.x(), r.y(), r.width(), r.height()] for r in rects
                 if r.width() == Cons.WIDTH and r.height() == Cons.HEIGHT]
        pos = tile.get_pos()
        tilerect = [pos.x(), pos.y(), Cons.WIDTH, Cons.HEIGHT]
        overlaps = [self.scene.overlap(tilerect, r) for r in rects]
        if overlaps:
            index = max(range(len(overlaps)), key=overlaps.__getitem__)
            return rects[index][0], rects[index][1]
        return None, None

    # --------------------------------------------------

    def get_pc_player(self):
        """ Get details and load computer player """
        self.pc = True

        if len(self.scene.alphabet.rb_text) == 1:
            self._load_player(0)
        else:
            self.smachine.start.show_msg(self.scene.alphabet.QSTATES_MSGS[20])
            radio_dict = (Radiobuttons(self.scene.alphabet.PC_RB_TITLE,
                                       "",
                                       self.scene.alphabet.rb_text,
                                       self.smachine), None)
            radio_dict[0].set_frame(False)
            radio_dict[0].set_ID(self.no)
            radio_dict = (radio_dict[0], self.scene.addWidget(radio_dict[0]))
            radio_dict[1].setPos(Cons.INPUT_NAMES[self.no][0] - 10,
                                 Cons.INPUT_NAMES[self.no][1] + 50)
            self.smachine.machine.radio_complete.connect(lambda x, y:
                                                         self.get_player(x, y, radio_dict[1]))
            radio_dict[1].show()
            print("DEBUG RButton", self.no, radio_dict[0].id)

    @pyqtSlot(int, int)
    def get_player(self, ability, player, rb):
        """ Load correct computer players
            by checking player no """
        print("DEBUG Get", self.no, player, ability)
        if player == self.no:
            print("DEBUG Load", self.no, player, ability)
            self.scene.removeItem(rb)
            self._load_player(ability)

    def _load_player(self, ability):
        """ Load computer player GADDAG """
        self.smachine.start.show_msg(self.scene.alphabet.QSTATES_MSGS[19])
        self.pc_play = scmoves.Play(self.smachine, ability)


class Radiobuttons(QWidget):
    """ Create grouped radio button widget for language choice """

    def __init__(self, label, instruction, button_list, states):
        super(Radiobuttons, self).__init__()

        self.states = states
        self.default = -1
        self.id = None

        self.frame = QFrame(self)
        self.frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.frame.setStyleSheet("border: 1px solid gray; border-radius: 10px;"
                                 "background-color: rgb(230, 200, 167);")
        # self.frame.setStyleSheet("border: 1px solid gray; border-radius: 10px;
        # background-color: rgba(230, 200, 167);")
        self.setMinimumSize(300, 300)
        self.setAutoFillBackground(True)
        self.title_label = QLabel(label)
        self.title_label.setFont(QFont("Arial", 18))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.instruct_label = QLabel(instruction)
        self.instruct_label.setFont(QFont("Arial", 14))
        self.instruct_label.setAlignment(Qt.AlignCenter)
        self.radio_group_box = QGroupBox()
        self.radio_group_box.setObjectName("ColoredGroupBox")  # Changed here...
        self.radio_group_box.setStyleSheet("""QGroupBox#ColoredGroupBox{
                                                    border: 1px solid gray;
                                                    border-radius: 10px;
                                                    background-color: rgb(230, 200, 167);
                                                    margin-top: 10px;
                                                    margin-bottom: 10px;
                                                    margin-left: 20px;
                                                    margin-right: 20px;}""")
        self.radio_group_box.setFont(QFont("Helvetica MS", 18))
        self.radio_button_group = QButtonGroup()
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.radio_button_list = []
        for b in button_list:
            rb = QRadioButton(b)
            rb.setStyleSheet("""QRadioButton{
                                    font: 14pt Arial;
                                    background-color: rgb(230, 200, 167);
                                    border: 0px;
                                    padding: 4px;} 
                                QRadioButton::indicator{ 
                                    width: 20px; 
                                    height: 30px;}""")
            self.radio_button_list.append(rb)

        self.radio_button_layout = QVBoxLayout()
        counter = 0
        for b in self.radio_button_list:
            self.radio_button_layout.addWidget(b)
            self.radio_button_group.addButton(b)
            self.radio_button_group.setId(b, counter)
            b.clicked.connect(self.radio_button_clicked)
            counter += 1
        self.radio_group_box.setLayout(self.radio_button_layout)

        self.main_layout = QVBoxLayout(self.frame)
        self.main_layout.setSpacing(20)
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.radio_group_box)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.instruct_label)
        self.setLayout(self.main_layout)

    def set_frame(self, on):
        """ Turn frame around radio burtton widget on and off """
        if on:
            self.frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
            self.frame.setStyleSheet("border: 1px solid gray; border-radius: 10px;"
                                     "background-color: rgb(230, 200, 167);")
        else:
            self.frame.setStyleSheet("border: 0px solid gray; border-radius: 10px;"
                                     "background-color: rgb(230, 200, 167);")

    def set_default(self, val):
        """ Set default button """
        self.default = val
        self.radio_button_list[self.default].setChecked(True)

    def set_ID(self, player_id):
        """ Set ID for radiobuutons """
        self.id = player_id

    def resizeEvent(self, event):
        """ Deal with resize event """
        self.frame.resize(self.size())
        QWidget.resizeEvent(self, event)

    def radio_button_clicked(self):
        """ Store ID of checked button when clicked """
        self.states.machine.radio_complete.emit(self.radio_button_group.checkedId(), self.id)
