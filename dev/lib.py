from typing import List, Callable, Dict, Tuple
from abc import ABC, abstractmethod
import sys

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import (QMainWindow, QApplication, QGridLayout, QWidget, QPushButton, QLabel,
                               QLineEdit, QSlider, QComboBox, QGroupBox, QHBoxLayout, QAbstractSlider,
                               QFrame, QFormLayout, QVBoxLayout, QDockWidget, QSizePolicy, QCheckBox)
from PySide6.QtCore import Qt, Slot, Signal, QSize, QPointF, QSize, QLineF
from PySide6.QtGui import (QPixmap, QImage, QColor, QRegularExpressionValidator, QValidator, QIcon,
                           QPen, QPainter)

from __feature__ import snake_case, true_property
