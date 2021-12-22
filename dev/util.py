from typing import Generator, Union, Tuple
from math import acos, degrees, exp


def int_generator(steps: int, lower_bound: int = 0, upper_bound=15) -> Generator:
    return (i//steps for i in range(lower_bound, upper_bound))

def to_upper(word: str) -> str:
    return chr(ord(word[0]) - 32) + word[1:]

def clamp(minimum: Union[int, float], maximum: Union[int, float], value: Union[int, float]) -> Union[int, float]:
    return max(minimum, min(value, maximum))

def sigmoid(x) -> float:
    return 1 / (1 + exp(-x))


class Bounds:
    def __init__(self):
        self._min_x: float = 0.
        self._max_x: float = 0.
        self._min_y: float = 0.
        self._max_y: float = 0.

    def update(self, x: float, y: float):
        self._min_x = min(x, self._min_x)
        self._max_x = max(x, self._max_x) 
        self._min_y = min(y, self._min_y)
        self._max_y = max(y, self._max_y)

    @property
    def x_center(self) -> float:
        return self.width / 2

    @property
    def y_center(self) -> float:
        return self.height / 2

    @property
    def width(self) -> float:
        return self._max_x - self._min_x

    @property
    def height(self) -> float:
        return self._max_y - self._min_y

    @property
    def min_x(self) -> float:
        return self._min_x

    @property
    def min_y(self) -> float:
        return self._min_y

    @property
    def max_x(self) -> float:
        return self._max_x

    @property
    def max_y(self) -> float:
        return self._max_y

    def scale(self, image_width: float, image_height: float) -> float:
        x_scale = image_width / self.width
        y_scale = image_height / self.height
        return min(x_scale, y_scale)


def cosine_law(a: float, b: float, c: float) -> Tuple:
    if not a or not b or not c:
        raise ZeroDivisionError("Dénominateur ne peut être égal à zéro")
    alpha = acos((b ** 2 + c ** 2 - a ** 2)/(2 * b * c))
    beta = acos((a ** 2 + c ** 2 - b ** 2)/(2 * a * c))
    gamma = acos((b ** 2 + a ** 2 - c ** 2)/(2 * a * b))
    return degrees(alpha), degrees(beta), degrees(gamma)


class Point:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            self._x += other
            self._y += other
            return self
        elif isinstance(other, Point):
            self._x += other._x
            self._y += other._y
            return self
        else:
            raise ValueError()

    def __radd__(self, other):
        return self.__add__(other)
