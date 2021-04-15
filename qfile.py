""" File loading classes """

# pylint: disable=function-redefined

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QThread
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar

import Constants as Cons


class FileProgressWidget(QWidget):
    """ Class to show progress bar while loading GADDAG """
    file_finished = pyqtSignal(int)
    no = 0

    def __init__(self, load_to, gaddag, scene, parent=None):
        super(FileProgressWidget, self).__init__(parent)

        FileProgressWidget.no += 1
        self.no = FileProgressWidget.no

        layout = QVBoxLayout(self)
        self.proxy = None

        self.scene = scene

        # style.append("QProgressBar::chunk {background:url
        # ("/UrlImage Background/chunkimage.png");}");
        self.progressBar = QProgressBar(self)

        self.progressBar.setStyleSheet("""QWidget
                                          {
                                            color: #b1b1b1;
                                            background-color: #323232;
                                          }
                                          QProgressBar
                                          {
                                            border: 2px solid grey;
                                            border-radius: 5px;
                                            text-align: center;
                                          }
                                          QProgressBar::chunk
                                          {
                                            background-color: #d7801a;
                                            width: 2.15px;
                                            margin: 0.5px;
                                           }""")

        self.progressBar.setRange(0, 0)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.txt = QLabel(self.scene.alphabet.QLOAD_MSGS[0])
        self.txt.setAlignment(Qt.AlignCenter)
        self.set_colour("yellow")
        layout.addWidget(self.progressBar)
        layout.addWidget(self.txt)

        self.file_finished.connect(self.finished_slot)
        self.proxy = self.scene.addWidget(self)
        self.proxy.setPos(Cons.WINDOW_SIZE[0] / 2 - self.width() / 2,
                          Cons.WINDOW_SIZE[1] - self.height() - 30)
        self.proxy.show()

        self.myLongTask = TaskThread(load_to, gaddag, scene)
        self.myLongTask.taskFinished.connect(self.onFinished)

    @classmethod
    def reset_count(cls):
        """ Reset number count to 0 """
        cls.no = 0

    def set_colour(self, col):
        """ Set text colour """
        style = 'color: ' + col + '; text-align: center; font-size: 20px;'
        self.txt.setStyleSheet(style)

    def Start(self):
        """ Start progress bar and task """
        self.progressBar.setRange(0, 0)
        self.myLongTask.start()

    def onFinished(self):
        """ Stop the pulsation """
        self.progressBar.setRange(0, 1)
        self.scene.removeItem(self.proxy)
        self.file_finished.emit(self.no)

    def reconnect(self, newhandler=None):
        """ Connect file_finished to new slot """
        self.file_finished.disconnect()
        if newhandler is None:
            self.file_finished.connect(self.finished_slot)
        else:
            self.file_finished.connect(newhandler)

    def reconnect_params(self, newhandler=None):
        """ Connect file_finished with parameter to new slot """
        self.file_finished[int].disconnect()
        if newhandler is None:
            self.file_finished[int].connect(self.finished_slot_p)
        else:
            self.file_finished[int].connect(newhandler)

    @pyqtSlot()
    def finished_slot(self):
        """ Default slot for file_finished signal """
        pass

    @pyqtSlot(int)
    def finished_slot_p(self, no):
        """ Default slot for file_finished signal """
        pass


class TaskThread(QThread):
    """ Thread for loading GADDAG """
    taskFinished = pyqtSignal()

    def __init__(self, load_to, gaddag, parent=None):
        super(TaskThread, self).__init__(parent)
        self.load_to = load_to
        self.gaddag = gaddag

    def run(self):
        """ Load the player GADDAG """

        self.load_to.safeload(self.gaddag)
        self.taskFinished.emit()
