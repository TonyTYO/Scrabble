""" All messaging procedures including scoreboards """

from PyQt5.QtWidgets import QTextEdit, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import Constants as Cons


class Finalscores(QTextEdit):
    """ Display final scores for the game """

    def __init__(self, scene, players, parent=None):
        super(Finalscores, self).__init__(parent)

        self.scene = scene
        self.players = players
        self.setReadOnly(True)
        self.setLineWidth(5)
        self.setMidLineWidth(5)
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.move(Cons.FINAL[0], Cons.FINAL[1])
        self.resize(Cons.FINAL[2], Cons.FINAL[3])
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color:rgb(230, 200, 167);")
        self.proxy = self.scene.addWidget(self)
        self.proxy.setZValue(2000)
        self.proxy.persistent = True
        self.proxy.hide()

    def show_scores(self, hand_score, final_score, winner):
        """ Table html to show final scores
            col1: text, col2: player0, col3: player1
            row1: present scores, row2: left in hand
            row3: final totals """

        win_player = self.players[winner].name + self.scene.alphabet.QTESTUN_MSGS[0]
        self.set_html(hand_score, final_score, win_player)
        self.proxy.show()

    def set_html(self, hand_score, final_score, win_player):
        """ Read html from file and replace markers """

        with open(self.scene.alphabet.lang + r"\Final_score.html") as myfile:
            text = "".join(line.strip() for line in myfile)
        text = text[text.index("<"):]
        text = text.replace('#1#', self.players[0].name)
        text = text.replace('#2#', self.players[1].name)
        text = text.replace('#3#', str(self.players[0].score))
        text = text.replace('#4#', str(self.players[1].score))
        text = text.replace('#5#', str(hand_score[0]))
        text = text.replace('#6#', str(hand_score[1]))
        text = text.replace('#7#', str(final_score[0]))
        text = text.replace('#8#', str(final_score[1]))
        text = text.replace('#9#', win_player)
        self.setHtml(text)


class Scoreboard(QTextEdit):
    """ Class defines the scoreboard to be shown  """

    def __init__(self, scene, player, parent=None):
        super(Scoreboard, self).__init__(parent)

        self.player = player
        self.scene = scene
        self.persistent = True
        self.setReadOnly(True)
        self.setLineWidth(5)
        self.setMidLineWidth(5)
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.move(Cons.SCOREBOARD[self.player.no][0], Cons.SCOREBOARD[self.player.no][1])
        self.resize(Cons.SCOREBOARD[self.player.no][2], Cons.SCOREBOARD[self.player.no][3])
        self.setMinimumHeight(Cons.SCOREBOARD[self.player.no][3])
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color:rgb(230, 200, 167);")
        self.proxy = self.scene.addWidget(self)
        self.proxy.persistent = True

    def show_words(self, words, tick, no_tiles):
        """ Table html to show words and scores
            col1: word, col2: score, col3: cross if wrong
            col3 will be displayesd only on challenge """

        self.get_html(words, tick, no_tiles)
        docheight = self.document().size().height()  # adjust height if necessary
        self.resize(Cons.SCOREBOARD[self.player.no][2], docheight + 20)
        self.show()

    def get_html(self, words, tick, no_tiles):
        """ Table html to show words and scores
            col1: word, col2: score, col3: cross if wrong
            col3 will be displayesd only on challenge """

        row_start = '<tr><td width="65%">'
        row_score = '</td><td width = "20%" align="right">'
        row_end = '</td><td width="5%"></td></tr>'
        row_end_cross = ('</td><td width="5%" align="center" valign="middle">'
                         '<img src="tiles/wrong.png" width="16" alt="16"></td></tr>')

        table_html = ''
        score = 0
        for word in words:
            score += word[1]
            gair = ''.join(word[0])
            if tick and not word[2]:
                table_html = (table_html + row_start + '<s>' + gair + '</s>'
                              + row_score + '<s>' + str(word[1]) + '</s>' + row_end_cross)
            else:
                table_html = table_html + row_start + gair + row_score + str(word[1]) + row_end

        with open("HTML1.html") as myfile:  # read html from file
            text = "".join(line.strip() for line in myfile)
        text = text[text.index("<"):]  # replace marker with
        text = text.replace('#1#', table_html)  # table html fom above
        text = text.replace('#2#', str(score))

        if no_tiles == Cons.NO_HAND:
            text = text.replace('#4#', '')  # Bingo if all tiles used
            text = text.replace('#5#', '')
            text = text.replace('#3#', str(score + 50))
        else:
            text = text.replace('#4#', '<!--')  # comment out Bingo
            text = text.replace('#5#', '-->')

        self.setHtml(text)


class Totals(QLabel):
    """ Class defines the total score area to be shown  """

    def __init__(self, scene, player, parent=None):
        super(Totals, self).__init__(parent)

        self.player = player
        self.scene = scene
        self.setLineWidth(5)
        self.setMidLineWidth(5)
        self.setStyleSheet("""QLabel { border: 2px solid gray;
                                          border-radius: 10px;
                                          padding: 0 8px;
                                          background: yellow;
                                          background-color:rgb(230, 200, 167);
                                          font: 18pt 'Arial';}""")

        self.move(Cons.NAMES_RECT[self.player.no][0], Cons.NAMES_RECT[self.player.no][1])
        self.resize(Cons.NAMES_RECT[self.player.no][2], Cons.NAMES_RECT[self.player.no][3])
        self.setFont(QFont("Arial", 18, QFont.Bold))
        self.html = '<!DOCTYPE html><html>'
        self.proxy = self.scene.addWidget(self)
        self.proxy.persistent = True

    def show_totals(self):
        """ Show the given score in table """

        self.html = ('<!DOCTYPE html><html><body><table border="0" width="100%" cellpadding="5">'
                     '<tr><td width = "80%">' + self.player.name + '</td>'
                     '<td align="right" width="20%">score</td></tr></table></body></html>')
        text = self.html.replace("score", str(self.player.score))
        self.setText(text)

    def clear_totals(self):
        """ Clear totals boxes """

        self.html = ('<!DOCTYPE html><html><body><table border="0" width="100%" cellpadding="5">'
                     '<tr><td width = "80%"></td>'
                     '<td align="right" width="20%">score</td></tr></table></body></html>')
        text = self.html.replace("score", "")
        self.setText(text)


class Msg(QLabel):
    """ Class defines showing of messages """

    def __init__(self, scene, player=None, parent=None):
        super(Msg, self).__init__(parent)

        self.player = player
        self.scene = scene
        self.setLineWidth(5)
        self.setMidLineWidth(5)
        self.setStyleSheet("background-color:rgb(230, 200, 167); color : black;")
        if self.player is not None:
            self.move(Cons.MSGS_RECT[self.player.no][0], Cons.MSGS_RECT[self.player.no][1])
            self.resize(Cons.MSGS_RECT[self.player.no][2], Cons.MSGS_RECT[self.player.no][3])
        else:
            self.move(Cons.INSTR_RECT[0], Cons.INSTR_RECT[1])
            self.resize(Cons.INSTR_RECT[2], Cons.INSTR_RECT[3])
        self.setFont(QFont("Arial", 18))
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setTextFormat(Qt.RichText)
        self.proxy = self.scene.addWidget(self)
        if player is not None:
            self.proxy.persistent = True

    def show_msg(self, text):
        """ Show message for specific player """

        self.setText(self.player.name + " - \n" + text)
        self.adjustSize()
        self.setFixedWidth(Cons.MSGS_RECT[self.player.no][2])
        self.show()

    def general_msg(self, text):
        """ Show message with no player name """

        self.setText(text)
        self.show()
