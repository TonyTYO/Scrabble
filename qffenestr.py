""" Startup script for game
    sets window, scene, view """

from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QTransform
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QGraphicsScene, QGraphicsView, QGraphicsRectItem)

import Constants as Cons
import qbwtwm
import qcloc


class GraphicsScene(QGraphicsScene):
    """ Main graphics screen for the game """

    move_complete = pyqtSignal(object, int, int)  # Signal for end of cursor move
    active_scene = False

    def __init__(self, parent=None):
        super(GraphicsScene, self).__init__(parent)

        self.parent = self.parent()
        self.state = None  # Holds current state of FSM
        self.active = []  # List of active tiles
        # cleared in ActiveTiles class
        self.item = None  # Item under mouse press
        self.move = False  # Flag set to True if mouse is moved
        self.players = {}  # Dictionary of playerno:player
        self.alphabet = None
        # self.alphabet = qalphabet.Alphabet("cymraeg")    # Default playing language
        self.buttons = qbwtwm.Setbuttons(self)  # Setup all on-screen buttons
        self.machine = qbwtwm.SetupMachine(self)  # Setup and start FSM
        self.states = self.machine.st_code

        # Used for code simulation for pc player
        self.path = []  # Holds path of cursor as list of points
        self.move_complete.connect(self.m_c_default)  # Connect signal to default slot
        # (does nothing)
        self.interval = qcloc.DigitalClock(self, 1, 1)  # Millisecond interval timer
        # time_out signal emitted after 1 ms
        # used in pc player mouse/tile moves
        GraphicsScene.active_scene = True

    def mousePressEvent(self, event):
        """ Handle mouse pressed event """
        # modifiers = event.modifiers()
        self.item = self.itemAt(event.scenePos(), QTransform())
        self.state = self.machine.property("state")
        self.move = False

        if event.button() == Qt.LeftButton:
            if hasattr(self.item, 'letter'):
                self.item.setCursor(Qt.PointingHandCursor)
                if self.state == "tile":
                    self.item.setZValue(3000)
        super(GraphicsScene, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """ Handle mouse released event """

        self.item = self.itemAt(event.scenePos(), QTransform())

        if event.button() == Qt.LeftButton:
            if hasattr(self.item, 'letter'):
                if self.item.tile not in self.active:
                    self.active.append(self.item.tile)
                    if self.state == "exchange":
                        if self.move:
                            self.item.tile.lift_tile()
                            self.item.clearFocus()
                else:
                    if self.state == "exchange":
                        self.active.remove(self.item.tile)
                        self.item.tile.drop_tile()
                        self.item.clearFocus()
                self.clearSelection()
                self.item.setCursor(Qt.ArrowCursor)
                if self.state == "play":
                    collisions = self.item.collidingItems()
                    if collisions:
                        self.process_collisions(collisions)
        super(GraphicsScene, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """ Handle mouse move event """
        if event.buttons() == Qt.LeftButton:
            self.move = True  # required for exchange
        super(GraphicsScene, self).mouseMoveEvent(event)

    def process_collisions(self, collisions):
        """ Jump tile to nearest board cell """

        rects = [r.rect() for r in collisions if isinstance(r, QGraphicsRectItem)]
        rects = [[r.x(), r.y(), r.width(), r.height()] for r in rects
                 if r.width() == Cons.WIDTH and r.height() == Cons.HEIGHT]
        tilerect = [self.item.x(), self.item.y(), Cons.WIDTH, Cons.HEIGHT]
        overlaps = [self.overlap(tilerect, r) for r in rects]
        if overlaps:
            index = max(range(len(overlaps)), key=overlaps.__getitem__)
            self.item.setPos(rects[index][0], rects[index][1])

    def get_players(self):
        """ Return player details as dict """

        return self.players

    @staticmethod
    def overlap(rect1, rect2):
        """ Calculate overlap between two rectangles - return size of overlap """

        rect1 = [rect1[0], rect1[1], rect1[0] + rect1[2], rect1[1] + rect1[3]]
        rect2 = [rect2[0], rect2[1], rect2[0] + rect2[2], rect2[1] + rect2[3]]
        if rect2[0] > rect1[2] or rect1[0] > rect2[2] or rect2[1] > rect1[3] or rect1[1] > rect2[3]:
            return 0
        x_overlap = max(0, min(rect1[2], rect2[2]) - max(rect1[0], rect2[0]))
        y_overlap = max(0, min(rect1[3], rect2[3]) - max(rect1[1], rect2[1]))
        return x_overlap * y_overlap

    # -------------------------------------------------------------------------
    # Move mouse and tiles for computer player
    # Uses self.interval msec timer

    def tile_move(self, tile, x, y):
        """ Move tile with cursor
            simulating drag and drop
            (x, y) end point """

        tile.hand_cursor()
        end = self.parent.mapToGlobal(QPoint(x, y))
        cursor = self.parent.cursor()
        pos = cursor.pos()
        path = self.line(pos.x(), pos.y(), end.x(), end.y())
        path.append((x, y))  # store (x, y) in local coordinates at end of path
        self.state = self.machine.property("state")
        if self.state == "tile":
            tile.setZValue(3000)
        self.interval.reconnect_params(self.moving_tile)
        self.moving_tile([cursor, tile, path])

    def moving_tile(self, cur_tile_path):
        """ Advance mouse cursor to next point """
        cursor, tile, path = cur_tile_path
        newx, newy = path[0]
        x, y = path[-1]  # retrieve local end point (x, y)
        newt = self.parent.mapFromGlobal(QPoint(newx, newy))
        path = path[3:]
        if not path:
            tile.reset_cursor()
            self.mouse_move(newt.x() + 10, newt.y() + 10)
            self.move_complete.emit(self, x, y)
        else:
            cursor.setPos(newx, newy)
            tile.set_pos(newt.x(), newt.y())
            self.interval.hidden(5, [cursor, tile, path])

    def mouse_move(self, x, y):
        """ Move cursor smoothly to x,y
            Cursor uses global coordinates """
        end = self.parent.mapToGlobal(QPoint(x, y))
        cursor = self.parent.cursor()
        pos = cursor.pos()
        path = self.line(pos.x(), pos.y(), end.x(), end.y())
        path.append((x, y))  # store (x, y) in local coordinates at end of path
        self.interval.reconnect_params(self.moving)
        self.moving([cursor, path])

    def moving(self, cur_path):
        """ Advance mouse cursor to next point """
        cursor, path = cur_path
        newx, newy = path[0]
        x, y = path[-1]  # retrieve local end point (x, y)
        path = path[3:]  # Use every 4th point to increase speed
        if not path:
            self.move_complete.emit(self, x, y)
        else:
            cursor.setPos(newx, newy)
            self.interval.hidden(5, [cursor, path])

    def move_reconnect(self, newhandler=None):
        """ Connect move_complete to new slot """

        self.move_complete.disconnect()
        if newhandler is None:
            self.move_complete.connect(self.m_c_default)
        else:
            self.move_complete.connect(newhandler)

    @staticmethod
    def m_c_default(s, x, y):
        """ Default slot for move_complete - does nothing
            Required to prevent error on disconnect """

        pass

    @staticmethod
    def line(x0, y0, x1, y1):
        """ Bresenham's line algorithm
            Create list of points
            between (x0, y0) and (x1, y1) """
        points_in_line = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                points_in_line.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                points_in_line.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        points_in_line.append((x, y))
        return points_in_line


class MainWindow(QMainWindow):
    """ Main window for the game """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.resize(Cons.WINDOW_SIZE[0], Cons.WINDOW_SIZE[1])
        self.center()

        self.setWindowTitle("Scrabble")
        self.view = MainView()
        self.setCentralWidget(self.view)

    def center(self):
        """ Centre window on screen """

        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def reset_window(self, size=None, title=None):
        """ Resize and/or retitle window
            size as tuple (l, w) """

        if size is not None:
            self.resize(size[0], size[1])
        if title is not None:
            self.setWindowTitle(title)


# pylint: disable=too-few-public-methods
class MainView(QGraphicsView):
    """ Main graphics view for the game """

    def __init__(self, parent=None):
        super(MainView, self).__init__(parent)

        self.scene = GraphicsScene(self)
        self.scene.setSceneRect(0, 0, Cons.WINDOW_SIZE[0], Cons.WINDOW_SIZE[1])

        self.setScene(self.scene)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setBackgroundBrush(QColor(230, 200, 167))
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setFrameStyle(0)
