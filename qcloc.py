""" Clock and countdown procedures """

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimer
from PyQt5.QtWidgets import QLCDNumber, QFrame
from PyQt5.QtGui import QColor


class DigitalClock(QLCDNumber):
    """ Class provides count up and countdown digital clock
        Countdown if start parameter positive """

    time_out = pyqtSignal([], [object])  # signal emitted when counter reaches zero

    def __init__(self, scene, start=0, interval=1000, parent=None):
        super(DigitalClock, self).__init__(parent)

        self.scene = scene

        self.setSegmentStyle(QLCDNumber.Filled)
        self.setSegmentStyle(QLCDNumber.Flat)
        self.setFrameStyle(QFrame.NoFrame)
        palette = self.palette()  # get the palette
        palette.setColor(palette.WindowText, QColor(0, 0, 0))  # foreground color
        palette.setColor(palette.Background, QColor(230, 200, 167))  # background color
        palette.setColor(palette.Light, QColor(96, 96, 96))  # "light" border
        palette.setColor(palette.Dark, QColor(0, 0, 0))  # "dark" border
        self.setPalette(palette)  # set the palette
        self.resize(75, 30)
        self.time_out.connect(self.time_slot)  # default connections
        self.time_out[object].connect(self.time_slot_p)  # for overloaded signal
        self.signal_params = None  # parameters for overloaded
        # signal held in list
        self.timer = QTimer()
        self.timer.setInterval(interval)
        self.timer.timeout.connect(self.tick)
        self.start = start
        self.time = start
        self.clock = scene.addWidget(self)
        self.clock.persistent = True  # attribute used when removing items from scene
        self.clock.setVisible(False)

    def showInterval(self):
        """ Format display as min:sec """
        self.display("{0:02.0f}:{1:02.0f}".format(self.time // 60, self.time % 60))

    @pyqtSlot()
    def tick(self):
        """ Increase or decrease time each second """
        if self.start > 0:
            self.time -= 1
        else:
            self.time += 1
        if self.time < 0:
            self.timer.stop()
            if self.signal_params is None:
                self.time_out.emit()
            else:
                self.time_out[object].emit(self.signal_params)
        else:
            self.showInterval()

    def reset(self, start=None):
        """ Reset and restart on screen timer """
        if start is None:
            self.time = self.start
        else:
            self.time = start
        self.clock.setVisible(True)
        self.timer.start()
        self.showInterval()

    def hidden(self, start=None, sig=None):
        """ Reset and restart hidden timer """
        self.signal_params = sig  # set list of params
        if start is None:
            self.time = self.start
        else:
            self.time = start
        self.clock.setVisible(False)
        self.timer.start()

    def stop(self):
        """ Stop timer """
        self.timer.stop()

    def setPos(self, x, y):
        """ Set timer position """
        self.clock.setPos(x, y)

    def reconnect(self, newhandler=None):
        """ Connect time_out to new slot """
        self.time_out.disconnect()
        if newhandler is None:
            self.time_out.connect(self.time_slot)
        else:
            self.time_out.connect(newhandler)

    def reconnect_params(self, newhandler=None):
        """ Connect overloaded time_out to new slot """
        self.time_out[object].disconnect()
        self.signal_params = []  # has to be reset from None
        if newhandler is None:
            self.time_out[object].connect(self.time_slot_p)
        else:
            self.time_out[object].connect(newhandler)

    def reset_time_out(self):
        """ Reset time_out to default slot """
        self.reconnect()
        self.reconnect_params()

    @pyqtSlot()
    def time_slot(self):
        """ Default slot for time_out - does nothing
            Required for disconnect() not to throw error"""
        pass

    @pyqtSlot(object)
    def time_slot_p(self, c, p):
        """ Default slot for time_out - does nothing
            Required for disconnect() not to throw error"""
        pass
