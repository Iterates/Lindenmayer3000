from PySide6.QtGui import QColor


class LSystemParameters:
    def __init__(self):
        self.axiom: str = None
        self.first_transformation_rule: str = None
        self.second_transformation_rule: str = None
        self.num_of_iterations: int = None
        self.angle: float = None
        self.probability_one: float = None
        self.probability_two: float = None
        self.polygon_shape: str = None
        self.shape_color: QColor = None
        self.bg_color: QColor = None



