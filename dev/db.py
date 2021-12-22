import sqlite3
from typing import Tuple, List
from dataclasses import dataclass

PATH = "./db/lsystem.db"

CREATE_LSYSTEM_TABLE = ''' 
CREATE TABLE IF NOT EXISTS lsystem
(
    id INTEGER PRIMARY KEY,
    name CHAR(50) NOT NULL,
    axiom CHAR(50) NOT NULL,
    rule1 CHAR(50) NOT NULL,
    rule2 CHAR(50),
    iterations INT NOT NULL DEFAULT 1 CHECK(iterations > 0 AND iterations < 8),
    probability1 REAL NOT NULL DEFAULT 1 CHECK(probability1 > 0 AND probability1 <= 1),
    probability2 REAL DEFAULT 1 CHECK(probability2 > 0 AND probability2 <= 1),
    bg_color INT DEFAULT 1,
    shape_color INT DEFAULT 2,
    angle REAL CHECK(angle > 0 AND angle <= 90),
    FOREIGN KEY (bg_color) REFERENCES color(id),
    FOREIGN KEY (shape_color) REFERENCES color(id) 
)
'''

CREATE_COLOR_TABLE = '''
CREATE TABLE IF NOT EXISTS color
(
    id INTEGER PRIMARY KEY,
    name CHAR(25),
    red INT NOT NULL CHECK(red >= 0 AND red < 256),
    green INT NOT NULL CHECK(green >= 0 AND green < 256),
    blue INT NOT NULL CHECK(blue >= 0 AND blue < 256),
    alpha INT NOT NULL CHECK(alpha >= 0 AND alpha < 256)
)
'''

ADD_COLOR = "INSERT INTO color(name, red, green, blue, alpha) VALUES(?, ?, ?, ?, ?)"
ADD_CUSTOM_LSYSTEM = """INSERT INTO lsystem(name, axiom, rule1, rule2, iterations, probability1, probability2, bg_color, shape_color, angle)
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
ADD_LSYSTEMS = """INSERT INTO lsystem VALUES(:name, :axiom, :rule1, :rule2, :iterations, :probability1, :probability2, bg_color, shape_color, :angle)
                    WHERE bg_color = (SELECT id FROM color WHERE name = :bg_color) AND
                        WHERE shape_color = (SELECT id FROM color WHERE name = :shape_color)"""
ADD_DEFAULT = "INSERT INTO lsystem(name, axiom, rule1, iterations, probability1, bg_color, shape_color, angle) VALUES(?, ?, ?, ?, ?, 1, 2, ?)"

"""
Ces formes sont directement tirées du livre The Algorithmic Beauty of Plants de Aristid Lindenmayer et de Przemyslaw Prusinkiewicz
"""
DETERMINISTIC_LSYSTEMS = [("Koch Island", "F-F-F-F", "F=F-F+F+FF-F-F+F", 3, 1, 90),
                          ("Quadratic Snowflake Curve", "-F", "F=F+F-F-F+F", 4, 1, 90),
                          ("Koch Curve 1", "F-F-F-F", "F=FF-F-F-F-FF", 4, 1, 90),
                          ("Koch Curve 2", "F-F-F-F", "F=FF-F--F-F", 4, 1, 90),
                          ("Koch Curve 3", "F-F-F-F", "F=F-FF--F-F", 5, 1, 90),
                          ("Tree 1", "F", "F=F[+F]F[-F]F", 5, 1, 25.7),
                          ("Tree 2", "F", "F=F[+F]F[-F][F]", 5, 1, 20),
                          ("Tree 3", "F", "F=FF-[-F+F+F]+[+F-F-F]", 4, 1, 22.5)]


DROP_COLOR_TABLE = 'DROP TABLE IF EXISTS color'
DROP_LSYSTEM_TABLE = 'DROP TABLE IF EXISTS lsystem'
GET_COLOR = 'SELECT DISTINCT id FROM COLOR WHERE name = ? AND red = ? AND green = ? AND blue = ? AND alpha = ? LIMIT 1'
GET_LSYSTEMS = """SELECT lsystem.name, lsystem.axiom, lsystem.rule1, lsystem.rule2, lsystem.iterations, lsystem.probability1, lsystem.probability2, angle,
                  bg.name AS background, bg.red, bg.green, bg.blue, bg.alpha, 
                  shape.name AS shape, shape.red, shape.green, shape.blue, shape.alpha
                    FROM lsystem, color AS bg, color AS shape
                        WHERE lsystem.bg_color = bg.id 
                            AND lsystem.shape_color = shape.id"""


@dataclass
class LsystemDAO:
    name: str
    axiom: str
    rule_one: str
    rule_two: str
    iterations: int
    probability_one: float
    probability_two: float
    angle: float
    bg_name: str
    bg_red: int
    bg_green: int
    bg_blue: int
    bg_alpha: int
    shape_name: str
    shape_red: int
    shape_green: int
    shape_blue: int
    shape_alpha: int


class Database:
    def __init__(self):
        with sqlite3.connect(PATH) as cursor:
            self.cursor = cursor
            cursor.execute("PRAGMA foreign_keys = 1")

    def clear_db(self):
        self.cursor.execute("PRAGMA foreign_keys = 0")
        self.cursor.execute(DROP_COLOR_TABLE)
        self.cursor.execute(DROP_LSYSTEM_TABLE)

        self.cursor.execute(CREATE_COLOR_TABLE)
        self.cursor.execute(CREATE_LSYSTEM_TABLE)

    def add_color(self, params: Tuple):
        self.cursor.execute(ADD_COLOR, params)
        self.cursor.commit()

        color_id = self.cursor.execute(GET_COLOR, params)
        return [color[0] for color in color_id.fetchall()]

    def add_default(self):
        self.cursor.executemany(ADD_DEFAULT, DETERMINISTIC_LSYSTEMS)
        self.cursor.commit()

    def add_custom(self, params: Tuple):
        self.cursor.execute(ADD_CUSTOM_LSYSTEM, params)
        self.cursor.commit()

    def get_lsystems(self) -> List[LsystemDAO]:
        lsystems = self.cursor.execute(GET_LSYSTEMS)
        return [LsystemDAO(*lsystem) for lsystem in lsystems.fetchall()]
