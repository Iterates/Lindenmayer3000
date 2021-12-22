from __future__ import annotations
from lib import *
from constant import Constant
from tree import *
from util import Bounds, clamp

from math import sin, cos, radians, pi

from __feature__ import snake_case, true_property


class Turtle:
    def __init__(self, tree: Tree, rotation_angle: float, segment_length: float = 5.):
        if not isinstance(tree, Tree):
            raise TypeError("Arbre doit être de type Tree")
        self._segment_length = segment_length
        self._tree = tree
        self._centroid: QPointF = QPointF(0, 0)
        self._turtle_start = QPointF(0, 0)
        self._current_position: QPointF = self._turtle_start
        self._heading: float = -90.
        self._rotation_angle: float = rotation_angle
        self._stack_positions: List[QPointF] = []
        self._stack_angles: List[float] = []
        self._point_vector: List[QPointF] = [self._turtle_start]
        self._line_vector: List[QLineF] = []
        self._current_node: Tree._Node = self._tree.root
        self._at = 0
        self._bounds = Bounds()

    @property
    def point_vector(self) -> List[QPointF]:
        return self._point_vector

    @property
    def centroid(self) -> QPointF:
        return self._centroid / len(self._point_vector)

    @property
    def line_vector(self) -> List[QLineF]:
        return self._line_vector

    @property
    def bounds(self) -> Bounds:
        return self._bounds

    def parse(self) -> None:
        self.parser(self._current_node)

    def parser(self, node: Tree._Node) -> None:
        """
        TODO Remplacer par un switch case (disponible en Python 3.10)
        """
        at = 0
        for char in node.value:
            if char == "+":
                self._rotate_left()
            if char == "-":
                self._rotate_right()
            if char == "F":
                self._draw_straight_line()
            if char == "$":
                self._stack_positions.append(self._current_position)
                self._stack_angles.append(self._heading)
                self.parser(node.child[at])
                at += 1
                self._current_position = self._stack_positions.pop()
                self._heading = self._stack_angles.pop()

    def _stack_turtle(self):
        self._current_node = self._current_node.child[self._at] if self._current_node.child else self._current_node
        self._stack_positions.append(self._current_position)
        self._stack_angles.append(self._heading)
        self.parser(self._current_node)
        self._at += 1
        self._heading = self._stack_angles.pop()

    def _draw_straight_line(self):
        x_coord = cos(radians(self._heading)) * self._segment_length + self._current_position.x()
        y_coord = sin(radians(self._heading)) * self._segment_length + self._current_position.y()

        self.bounds.update(x_coord, y_coord)

        next_position = QPointF(x_coord, y_coord)

        self._point_vector.append(next_position)

        self._centroid = self._centroid + next_position         

        self._line_vector.append(QLineF(self._current_position, next_position))
        self._current_position = next_position

    def _rotate_right(self):
        self._heading -= self._rotation_angle

    def _rotate_left(self):
        self._heading += self._rotation_angle


class Renderer:
    def __init__(self, bounds: Bounds, line_vector: List[QLineF], image_width: int = 400, image_height: int = 500,
                 bg_color: QColor = QColor(255, 255, 255), shape_color: QColor = QColor(0, 0, 0)):
        if not isinstance(bounds, Bounds):
            raise TypeError("Limites doivent être de type Bounds")
        if not isinstance(bg_color, QColor):
            raise TypeError("Couleur doit être de type QColor")
        if not isinstance(shape_color, QColor):
            raise TypeError("Couleur doit être de type QColor")
        self._bounds = bounds
        self._image_width = image_width
        self._image_height = image_height
        self._bg_color = bg_color
        self._shape_color = shape_color
        self._line_vector = line_vector
        self._pixmap = QPixmap(image_width, image_height)
        self._pixmap.fill(self._bg_color)

    @property
    def bounds(self) -> Bounds:
        return self._bounds

    @bounds.setter
    def bounds(self, bounds: Bounds) -> None:
        self._bounds = bounds

    @property
    def line_vector(self) -> List[QLineF]:
        return self._line_vector

    @line_vector.setter
    def line_vector(self, line_vector: List[QLineF]) -> None:
        self._line_vector = line_vector

    @property
    def shape_color(self) -> QColor:
        return self._shape_color

    @shape_color.setter
    def shape_color(self, shape_color: QColor) -> None:
        self._shape_color = shape_color
        
    def _bound_image(self, painter: QPainter) -> None:
        scale = self._bounds.scale(self._image_width, self._image_height)
        painter.scale(scale, scale)
        painter.translate(-self._bounds.min_x + (self._image_width / scale - self._bounds.width) / 2., 
                          -self._bounds.min_y + (self._image_height / scale - self._bounds.height) / 2.)

    def _render(self) -> None:
        pen = QPen(self._shape_color)
        painter = QPainter(self._pixmap)
        self._bound_image(painter)
        painter.set_pen(pen)
        painter.draw_lines(self._line_vector)
        painter.end()

    @property
    def pixmap(self) -> QPixmap:
        self._render()
        return self._pixmap
