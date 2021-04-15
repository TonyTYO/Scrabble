""" Utility procedures for adding languages to SCrabble """

import sys
import os
import shutil
import unicodedata
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFrame, QListWidget,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
                             QLabel, QWidget, QDesktopWidget,
                             QLineEdit, QFileDialog, QTextEdit,
                             QComboBox, QTabWidget, QCheckBox)
import pygaddag
import qalphabet


class TestListView(QListWidget):
    """ Uses listview to drag and drop files """

    dropped = pyqtSignal(list)
    enter = pyqtSignal()
    leave = pyqtSignal()

    def __init__(self, parent=None):
        super(TestListView, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setIconSize(QSize(72, 72))

    def dragEnterEvent(self, event):
        """ Enter drag """
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()
        self.enter.emit()

    def dragMoveEvent(self, event):
        """ Move drag """
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """ Leave drop area """
        _ = event
        self.leave.emit()

    def dropEvent(self, event):
        """ Drop in box """
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.dropped.emit(links)
        else:
            event.ignore()


class MainForm(QMainWindow):
    """ Main window class for program """

    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        self.setWindowTitle('Language Utilities')
        self.setWindowIcon(QIcon(r'.\tiles\python.png'))
        self.resize(400, 400)
        self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowStaysOnTopHint
        )
        self.win = None
        self.dirs = None
        self.gaddag = None
        self.newlang = None
        self.log = None
        self.view = None
        self.inp = None
        self.chars = None
        self.logOutput = None
        self.lett2_check = None
        self.lett2 = None
        self.c_lett2 = False
        self.drop = None
        self.lang_combo = None

        self.txt_file = None
        self.p_file = None
        self.language = None
        self.multi_char_letts = None
        self.max_char_len = None
        self.multi_char = None
        self.gaddag = None
        self.instr = None
        self.set_UI()

    def set_UI(self):
        """ Set up main window """

        self.win = QTabWidget()
        self.setCentralWidget(self.win)

        self.instr = QWidget()
        self.dirs = QWidget()
        self.gaddag = QWidget()
        self.win.addTab(self.instr, "Instructions")
        self.win.addTab(self.dirs, "Files")
        self.win.addTab(self.gaddag, "GADDAG")
        self.instrUI()
        self.dirsUI()
        self.gaddagUI()

    def instrUI(self):
        """ Set up Instructions tab """

        inst = QTextEdit(self)
        inst.setReadOnly(True)
        inst.setMinimumHeight(100)
        with open("HTMLcreate.html") as myfile:  # read html from file
            text = "".join(line.strip() for line in myfile)
        text = text[text.index("<"):]
        inst.setHtml(text)

        frame0 = QFrame(self)
        frame0.setFrameShape(QFrame.Panel)
        frame0.setFrameShadow(QFrame.Raised)

        hbox1 = QHBoxLayout()
        frame0.setLayout(hbox1)
        hbox1.addWidget(inst)

        vbox = QVBoxLayout()
        vbox.addWidget(frame0)

        self.instr.setLayout(vbox)
        self.centre()

    def dirsUI(self):
        """ Setup directory tab in main window """

        instr = QTextEdit(self)
        instr.setReadOnly(True)
        instr.setMinimumHeight(200)
        instr.insertPlainText("This section helps you to set up a new language.\n\n")
        instr.insertPlainText("Insert the name of the language in the box below and "
                              "a sub-directory of that name will be created with all "
                              "required files which you will then need to amend and "
                              "translate.\n\n")
        self.newlang = QLineEdit(self)
        createdir_btn = QPushButton('Create', self)
        createdir_btn.clicked.connect(self.create_dir)
        self.log = QTextEdit(self)
        self.log.setObjectName("Log")
        quit_btn = QPushButton('Quit', self)
        quit_btn.clicked.connect(self.quit_app)

        frame0 = QFrame(self)
        frame0.setMinimumHeight(240)
        frame0.setFrameShape(QFrame.Panel)
        frame0.setFrameShadow(QFrame.Raised)

        hbox1 = QHBoxLayout()
        frame0.setLayout(hbox1)
        hbox1.addWidget(instr)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel("Enter name of new language"))

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.newlang)
        hbox3.addWidget(createdir_btn)

        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.log)

        hbox5 = QHBoxLayout()
        hbox5.addStretch(1)
        hbox5.addWidget(quit_btn)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(frame0)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox5)

        self.dirs.setLayout(vbox)
        self.centre()
        self.write_log(self.log, "Enter language name and press Create")

    def gaddagUI(self):
        """ Setup GADDAG tab in main window """

        self.inp = QLineEdit(self)
        self.drop = QLabel("Drop file here")
        self.drop.setAlignment(Qt.AlignCenter)

        self.drop.setMinimumWidth(self.inp.frameGeometry().width())
        self.view = TestListView(self.drop)
        self.view.setMaximumHeight(50)
        self.view.resize(self.drop.size())
        self.view.setAttribute(Qt.WA_TranslucentBackground)
        self.view.dropped.connect(self.pictureDropped)
        self.view.enter.connect(lambda: self.set_background(1))
        self.view.leave.connect(lambda: self.set_background(0))

        self.chars = QLineEdit(self)
        browse = QPushButton("Browse", self)
        browse.clicked.connect(self.browse_file)
        self.lang_combo = QComboBox(self)
        self.lang_combo.addItems(self._get_langs("__init__.py"))
        self.lang_combo.setEditable(True)
        self.lang_combo.activated.connect(self.lang_choice)
        self.lett2_check = QCheckBox(self)
        self.lett2_check.stateChanged.connect(self.create_lett2)
        self.logOutput = QTextEdit(self)
        self.logOutput.setObjectName("Log")
        self.logOutput.setReadOnly(True)
        self.logOutput.setLineWrapMode(QTextEdit.WidgetWidth)
        self.logOutput.setMinimumHeight(200)

        create_btn = QPushButton('Create', self)
        create_btn.clicked.connect(self.create_file)
        save_btn = QPushButton('Save', self)
        save_btn.clicked.connect(self.save_file)
        quit_btn = QPushButton('Quit', self)
        quit_btn.clicked.connect(self.quit_app)
        self._set_layout(browse, create_btn, save_btn, quit_btn)

    def _set_layout(self, browse, create_btn, save_btn, quit_btn):
        """ Layout for tab """
        vbox = QVBoxLayout()
        vbox.addStretch(1)

        frame1 = QFrame(self)
        frame1.setFrameShape(QFrame.Panel)
        frame1.setFrameShadow(QFrame.Raised)

        grid1 = QGridLayout()
        frame1.setLayout(grid1)
        grid1.setSpacing(10)
        grid1.setColumnMinimumWidth(3, 30)
        grid1.addWidget(QLabel("Enter filename or drag and drop in box below"), 0, 0, 1, 3)
        grid1.addWidget(self.inp, 1, 0, 1, 3)
        grid1.addWidget(browse, 1, 3, 1, 1)
        grid1.addWidget(self.drop, 2, 0, 1, 3)

        frame2 = QFrame(self)
        frame2.setFrameShape(QFrame.Panel)
        frame2.setFrameShadow(QFrame.Raised)

        grid2 = QGridLayout()
        frame2.setLayout(grid2)
        grid2.addWidget(QLabel("Choose language"), 3, 0, 1, 1)
        grid2.addWidget(self.lang_combo, 3, 1, 1, 3)
        grid2.addWidget(QLabel("or"), 4, 0)
        grid2.addWidget(QLabel("List multi-character letters"), 5, 0, 1, 1)
        grid2.addWidget(self.chars, 5, 1, 1, 3)

        frame3 = QFrame(self)
        frame3.setFrameShape(QFrame.Panel)
        frame3.setFrameShadow(QFrame.Raised)

        hbox = QHBoxLayout()
        frame3.setLayout(hbox)
        hbox.addWidget(QLabel("Create and save two letter words file (lett2)"))
        hbox.addWidget(self.lett2_check, 0, Qt.AlignRight)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.logOutput)

        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(create_btn)
        hbox2.addWidget(save_btn)
        hbox2.addWidget(quit_btn)

        vbox.addWidget(frame1)
        vbox.addWidget(frame2)
        vbox.addWidget(frame3)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.gaddag.setLayout(vbox)
        self.centre()
        self.write_log(self.logOutput, "Choose Text file")

    def centre(self):
        """ Centre window """

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def create_dir(self):
        """ Create language directory
            and copy necessary files into it """

        path = os.getcwd()
        subdir = path + '\\' + self.newlang.text()
        if os.path.isdir(subdir):
            self.write_log(self.log, "\nAlready a langauge of that name")
        else:
            try:
                os.mkdir(subdir)
            except OSError:
                print("Creation of the directory %s failed" % subdir)
                self.write_log(self.log, "\nCreation of the directory %s failed" % subdir)
            else:
                print("Successfully created the directory %s " % subdir)
                self.write_log(self.log, "\nSuccessfully created the directory %s " % subdir)
                self.copy_files(path, subdir)

    def copy_files(self, path, dest):
        """ Copy files into language directory """

        files = ["__init__.py", "alphabet.py", "Final_score.html",
                 "Instructions.html", "scrabble_letters.png"]
        self.write_log(self.log, "\nCopying files")
        for file in files:
            shutil.copy2(path + '\\' + "english" + '\\' + file, dest)
            if file == "alphabet.py":
                try:
                    f = open(dest + '\\alphabet.py', 'r')
                    lines = f.readlines()
                    lines[0] = '""" Language develop """\n'
                    f.close()
                    f = open(dest + '\\alphabet.py', 'w')
                    f.writelines(lines)
                    f.close()
                except IOError:
                    self.write_log(self.log, "\nProblem with alphabet.py")
            self.write_log(self.log, "\nCopying file: " + file)
        self.write_log(self.log, "\nAll files copied")

    @staticmethod
    def _get_langs(file):
        """ Return list of languages installed """
        langs = [None]
        for root, _, files in os.walk(r'.'):  # root, dirs, files
            if file in files and 'alphabet.py' in files:
                drc = os.path.basename(root)
                langs.append(drc)
        return langs

    def browse_file(self):
        """ Browse for text file to convert """
        filename, _ = QFileDialog.getOpenFileName(self, 'Open file', '.', '*.txt')
        self.inp.setText(filename)
        if os.path.isfile(filename):
            self.write_log(self.logOutput, "\nText file: " + filename)
            self.txt_file = filename
        else:
            self.write_log(self.logOutput, "\nError: Text file is not a valid file.")

    def lang_choice(self, index):
        """ Get language from combo box """
        self.language = self.lang_combo.itemText(index)
        self.write_log(self.logOutput, "\nLanguage: " + self.language)

    def create_lett2(self, state):
        """ Set create lett2 flag depending on state of check box """
        if state == Qt.Checked:
            self.c_lett2 = True
            self.write_log(self.logOutput, "\nTwo letter words file will be created (lett2)")
        else:
            self.c_lett2 = False
            self.write_log(self.logOutput, "\nTwo letter words file will not be created")

    def create_file(self):
        """ Create GADDAG in memory """
        if self.txt_file is None:
            self.write_log(self.logOutput, "\nError: No text file.")
            return
        if self.language is not None:
            self.write_log(self.logOutput, "\nCreating GADDAG.")
            self.create_from_file(self.txt_file, qalphabet.Alphabet(self.language))
            self.write_log(self.logOutput, "\nGADDAG created in memory.")
        elif self.multi_char_letts is not None:
            self.multi_char_letts = self.chars.text().split()
            self.max_char_len = len(max(self.multi_char_letts, key=len))
            self.multi_char = [s[0] for s in self.multi_char_letts]
            self.write_log(self.logOutput, "\nCreating GADDAG.")
            self.create_from_file(self.txt_file, self)
            self.write_log(self.logOutput, "\nGADDAG created in memory.")
        else:
            self.write_log(self.logOutput, "\nNo details of language given. "
                                           "Letters assumed to be single characters\n")
            self.create_from_file(self.txt_file, self)
            self.write_log(self.logOutput, "\nGADDAG created in memory.")

    def save_file(self):
        """ Save GADDAG """
        filename, _ = QFileDialog.getSaveFileName(self, 'Save file', '.', '*.p')
        _, f_extension = os.path.splitext(filename)
        f_path, _ = os.path.split(filename)
        lett2_file = f_path + '\\lett2.txt'
        if not f_extension:
            filename = filename + '.p'
        try:
            self.gaddag.save(filename)
        except IOError as inst:
            self.write_log(self.logOutput, "\nError: " + str(inst) + " saving GADDAG")
        else:
            self.write_log(self.logOutput, "\nGADDAG saved: " + filename)
        if self.c_lett2:
            try:
                with open(lett2_file, 'w') as f:
                    for item in self.lett2:
                        f.write("%s\n" % item)
            except IOError as inst:
                self.write_log(self.logOutput, "\nError: " + str(inst) + " saving lett2")
            else:
                self.write_log(self.logOutput, "\nTwo letter words file saved: " + lett2_file)

    def pictureDropped(self, lst):
        """ Drag and drop files into listview """
        for url in lst:
            if os.path.exists(url):
                self.inp.setText(url)
                self.txt_file = url
                self.write_log(self.logOutput, "\nText file: " + url)

    def set_background(self, state):
        """ Change background if drag on label """
        if state == 0:
            self.drop.setStyleSheet("background-color: qradialgradient(cx:0, cy:0,"
                                    "radius: 1, fx:0.5, fy:0.5, stop:0 lightgray,"
                                    "stop:1 #b17d7d);")
        if state == 1:
            self.drop.setStyleSheet("background-color: qradialgradient(cx:1, cy:1,"
                                    "radius: 1, fx:0.5, fy:0.5, stop:0 lightgray,"
                                    "stop:1 #b17d7d);")

    @staticmethod
    def write_log(log, msg):
        """ Write to log """
        log.moveCursor(QTextCursor.End)
        log.insertPlainText(msg)
        log.verticalScrollBar().setValue(log.verticalScrollBar().maximum())

    @staticmethod
    def quit_app():
        """ Quit application """
        QApplication.instance().quit()

    def to_list(self, string):
        """ Convert string in alphabet to list of letters """
        letters = []
        if self.multi_char_letts is None or self.max_char_len == 1:
            letters = list(string)
        else:
            i = 0
            while i < len(string):
                char = string[i]
                if char in self.multi_char:
                    k = 1
                    while k < self.max_char_len:
                        if string[i:i + k + 1] not in self.multi_char_letts:
                            break
                        char = string[i:i + k + 1]
                        k += 1
                letters.append(char)
                i += len(char)
        return letters

    @staticmethod
    def remove_diacritic(text):
        """
        Accept a unicode string, and return a normal string (bytes in Python 3)
        without any diacritical marks.
        """
        return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore')

    def create_from_file(self, filename, iaith):
        """
        Create a GADDAG from a text file of a lexicon. If no filename is supplied
        then it will default to the WORDLIST_PATH setting. The text file should
        only have the words in the lexicon, one per line, with a blank line
        at the very end.

        Args:
            filename: An existing file-like object to read from.
            iaith: Instance of language class Alphabet
        """

        self.gaddag = pygaddag.GADDAG()
        wordcount = 0
        self.lett2 = []
        self.write_log(self.logOutput, "\n")
        with open(filename, 'r', encoding="utf-8") as f:
            for word in f.readlines():
                wordcount += 1
                word = word.strip().lower()
                noaccent = self.remove_diacritic(word).decode()
                output = iaith.to_list(noaccent)
                if not noaccent.isalpha() or len(word) <= 1:
                    self.write_log(self.logOutput, "{0}: {1}\r".format(wordcount, word))
                else:
                    if len(noaccent) == 2:
                        self.lett2.append(noaccent)
                    self.gaddag.add(output)
                if (wordcount % 100) == 0:
                    self.write_log(self.logOutput, "{0}\r".format(wordcount))


def main():
    """ Main function """
    app = QApplication(sys.argv)
    sshFile = "utility.stylesheet"
    with open(sshFile, "r") as fh:
        app.setStyleSheet(fh.read())
    form = MainForm()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
