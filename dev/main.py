from controller import Controller

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QStyleFactory

import sys

from __feature__ import snake_case, true_property

if __name__ == "__main__":
    app = QApplication(sys.argv)

    c = Controller()
    
    sys.exit(app.exec_())
