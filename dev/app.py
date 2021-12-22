from tree import Rule
from ga import GeneticAlgorithmParameters
from parameters import LSystemParameters
from constant import *

from typing import List, Callable

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import (QCheckBox, QInputDialog, QMainWindow, QApplication, QGridLayout, QMessageBox, QSizePolicy, QWidget, QPushButton, QLabel,
                               QLineEdit, QSlider, QComboBox, QGroupBox, QHBoxLayout, QAbstractSlider,
                               QFrame, QFormLayout, QVBoxLayout, QDockWidget)
from PySide6.QtCore import Qt, Slot, Signal, QSize
from PySide6.QtGui import (QPixmap, QImage, QColor, QRegularExpressionValidator, QValidator, QIcon)

from __feature__ import snake_case, true_property


class LSystemApp(QMainWindow):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.window_title = "Lindenmayer 3000"
        self.window_icon = QIcon("./images/lsystem.jpg")
        self.simulation_panel: SimulationPanel = None
        self._set_up_vue(controller)
        self.maximum_size = QSize(1300, 600)

    def _set_up_vue(self, controller):
        lsystem_panel = LSystemPanel(controller, "Panneau systeme L")
        self.simulation_panel = SimulationPanel("Panneau simulation")
        ga_panel = GAPanel(controller, "Panneau algorithme genetique")

        lsystem_panel.maximum_size = QSize(400, 600)
        ga_panel.maximum_size = QSize(400, 600)
        self.simulation_panel.maximum_size = QSize(500, 600)

        lsystem_panel.minimum_size = QSize(400, 500)
        ga_panel.minimum_size = QSize(400, 500)
        self.simulation_panel.minimum_size = QSize(400, 500)

        central_widget = QWidget(self)

        layout = QHBoxLayout()

        layout.add_widget(lsystem_panel)
        layout.add_widget(self.simulation_panel)
        layout.add_widget(ga_panel)

        central_widget.set_layout(layout)

        self.set_central_widget(central_widget)


class LSystemPanel(QGroupBox):
    def __init__(self, controller, title: str, parent: QWidget = None):
        super().__init__(title, parent)
        self._lsystem_controls = LSystemControls("Controles")
        self._first_prob_sliderbox = SliderBox(0.1, 1, .1)
        self._second_prob_sliderbox = SliderBox(0.1, 1, .1)
        self._iterations_sliderbox = SliderBox(1, Constant.MAX_ITERATIONS, 1)
        self._angle_sliderbox = SliderBox(15, 90 , .1)
        self._first_rule_edit = QLineEdit()
        self._second_rule_edit = QLineEdit()
        self._axiom_edit = QLineEdit()
        self._shape_rgbabox = RGBABox()
        self._bg_rgbabox = RGBABox()
        self._parameters = LSystemParameters()
        self._saved_lsystems = QComboBox()
        self.controller = controller
        self._default_lsystems = controller.default_lsystems
        self._set_up()

    @property
    def lsystem_controls(self):
        return self._lsystem_controls

    @property
    def parameters(self) -> LSystemParameters:
        return self._parameters

    def _set_up(self) -> None:
        layout = QFormLayout()

        self._lsystem_controls.connect_buttons(self._start_button_command, self._save_button_command)

        self._saved_lsystems.add_items([lsystem.name for lsystem in self._default_lsystems])

        self._saved_lsystems.currentIndexChanged.connect(self._update_fields)

        layout.add_row(QLabel("Axiome"), self._axiom_edit)
        layout.add_row(QLabel("Règle de transformation 1"), self._first_rule_edit)
        layout.add_row(QLabel("Règle de transformation 2"), self._second_rule_edit)
        layout.add_row(QLabel("Itérations"), self._iterations_sliderbox)
        layout.add_row(QLabel("Angle"), self._angle_sliderbox)
        layout.add_row(QLabel("Probabilité 1"), self._first_prob_sliderbox)
        layout.add_row(QLabel("Probabilité 2"), self._second_prob_sliderbox)
        layout.add_row(QLabel("Formes enregistrées"), self._saved_lsystems)
        layout.add_row(QLabel("Couleur fond"), self._bg_rgbabox)
        layout.add_row(QLabel("Couleur forme"), self._shape_rgbabox)
        layout.add_row(self._lsystem_controls)

        self.set_layout(layout)

        self._axiom_edit.textChanged.connect(self._update_parameters)
        self._first_rule_edit.textChanged.connect(self._update_parameters)
        self._second_rule_edit.textChanged.connect(self._update_parameters)
        self._iterations_sliderbox.get_slider.valueChanged.connect(self._update_parameters)
        self._angle_sliderbox.get_slider.valueChanged.connect(self._update_parameters)
        self._first_prob_sliderbox.get_slider.valueChanged.connect(self._update_parameters)
        self._second_prob_sliderbox.get_slider.valueChanged.connect(self._update_parameters)
        self._shape_rgbabox.color_changed.connect(self._update_parameters)
        self._bg_rgbabox.color_changed.connect(self._update_parameters)

        self._shape_rgbabox.set_color_components(QColor(0, 0, 0))
        self._first_prob_sliderbox.current_value = 1
        self._second_prob_sliderbox.current_value = 1

    @Slot(int)
    def _update_fields(self, current_index: int):
        current_lsystem = self._default_lsystems[current_index]

        self._axiom_edit.text = current_lsystem.axiom
        self._first_rule_edit.text = current_lsystem.rule_one
        self._second_rule_edit.text = current_lsystem.rule_two if current_lsystem.rule_two else ""
        self._iterations_sliderbox.get_slider.value = current_lsystem.iterations
        self._first_prob_sliderbox.current_value = current_lsystem.probability_one
        self._second_prob_sliderbox.current_value = 1
        if current_lsystem.probability_two:
            self._second_prob_sliderbox.current_value = current_lsystem.probability_two
        self._angle_sliderbox.current_value = current_lsystem.angle
        self._shape_rgbabox.set_color_components(QColor(current_lsystem.bg_red,
                                                        current_lsystem.bg_green,
                                                        current_lsystem.bg_blue,
                                                        255))
        self._bg_rgbabox.set_color_components(QColor(current_lsystem.shape_red,
                                                     current_lsystem.shape_green,
                                                     current_lsystem.shape_blue,
                                                     255))

        self._lsystem_controls.draw_lsystem_button.clicked.emit()

    @Slot()
    def _update_parameters(self):
        """
        Pass parameters to turtle
        """
        self._parameters.axiom = self._axiom_edit.text
        self._parameters.first_transformation_rule = self._first_rule_edit.text.strip()
        self._parameters.second_transformation_rule = self._second_rule_edit.text.strip()
        self._parameters.num_of_iterations = int(self._iterations_sliderbox.current_value)
        self._parameters.angle = float(self._angle_sliderbox.current_value)
        self._parameters.probability_one = float(self._first_prob_sliderbox.current_value)
        self._parameters.probability_two = float(self._second_prob_sliderbox.current_value)
        self._parameters.polygon_shape = None
        r, g, b, a = self._bg_rgbabox.color_components
        self._parameters.bg_color = QColor(int(r), int(g), int(b), int(a))
        r, g, b, a = self._shape_rgbabox.color_components
        self._parameters.shape_color = QColor(int(r), int(g), int(b), int(a))

        self.controller.lsystem_parameters = self._parameters

    @Slot()
    def _save_button_command(self):
        user_input, response = QInputDialog.get_text(self, "Sauvegarder", "Nommez la forme à sauvegarder")
        if response and user_input.strip() != "":
            try:
                if self._parameters.axiom not in Constant.TERMINAL_SET:
                    raise ValueError("Caractère inconnu")
                if self._parameters.first_transformation_rule == "":
                    raise ValueError("Première règle de transformation ne peut être vide")
                Rule.is_well_formed(self._parameters.first_transformation_rule)
                if self._parameters.second_transformation_rule != "":
                    Rule.is_well_formed(self._parameters.second_transformation_rule)
                self._update_parameters()
                self.controller.add_custom_shape(user_input)
            except ValueError as e:
                QMessageBox.warning(self, "Erreur", f"{e}")
            finally:
                self._axiom_edit.clear()
                self._first_rule_edit.clear()
                self._second_rule_edit.clear()

    @Slot()
    def _start_button_command(self):
        try:
            self.controller.render_image()
        except ValueError as e:
            QMessageBox.warning(self, "Erreur", f"{e}")


class LSystemControls(QGroupBox):
    def __init__(self, title: str):
        super().__init__(title)
        self.draw_lsystem_button = QPushButton("Commencer")
        self.save_lsystem_button = QPushButton("Sauvegarder")
        self._layout = QHBoxLayout(self)
        self._set_up_vue()

    def add_button(self, button_to_add: QPushButton) -> None:
        self._layout.add_widget(button_to_add)

    def _set_up_vue(self) -> None:
        self._layout.add_widget(self.draw_lsystem_button)
        self._layout.add_widget(self.save_lsystem_button)

    def connect_buttons(self, start_button_command: Callable, save_button_command: Callable):
        self.draw_lsystem_button.clicked.connect(start_button_command)
        self.save_lsystem_button.clicked.connect(save_button_command)


class SimulationPanel(QGroupBox):
    def __init__(self, title: str, parent: QWidget = None):
        super().__init__(title, parent)
        self._pixmap = QPixmap(Constant.IMAGE_WIDTH, Constant.IMAGE_HEIGHT)
        color = QColor(255, 255, 255, 255)
        self._pixmap.fill(color)
        self._color_label = QLabel()
        self.update(self._pixmap)

        layout = QFormLayout(self)

        layout.add_row(self._color_label)

    def update(self, image: QPixmap) -> None:
        self._pixmap = image
        self._color_label.pixmap = self._pixmap

    @property
    def simulation_image(self) -> QPixmap:
        return self._pixmap


class FitnessSelector(QGroupBox):
    def __init__(self, title: str):
        super().__init__(title)
        self._fitness_checkboxes: List[QCheckBox] = []
        self._set_up()

    @property
    def fitness_checkboxes(self):
        return self._fitness_checkboxes

    def _set_up(self):
        checkbox_layout = QVBoxLayout(self)
        for strategy in GeneticAlgorithmParameters.default_fitness_strategies:
            strategy_checkbox = QCheckBox(strategy.__repr__())
            checkbox_layout.add_widget(strategy_checkbox)
            self._fitness_checkboxes.append(strategy_checkbox)

    def connect_checkboxes(self, status_changed: Callable):
        for checkbox in self._fitness_checkboxes:
            checkbox.stateChanged.connect(status_changed)

    def are_checked(self) -> bool:
        check_sum = 0
        for checkbox in self._fitness_checkboxes:
            check_sum |= checkbox.checked
        return bool(check_sum)


class GAPanel(QGroupBox):
    def __init__(self, controller, title: str, parent: QWidget = None):
        super().__init__(title, parent)
        self._ga_controls = LSystemControls("Contrôles algorithme")
        self._parameters = GeneticAlgorithmParameters()
        self._pop_slider = SliderBox(Constant.INITIAL_POP_MIN_SIZE, Constant.INITIAL_POP_MAX_SIZE, 1)
        self._elitism_slider = SliderBox(Constant.MIN_ELITISM_RATE, Constant.MAX_ELITISM_RATE, .1)
        self._generation_slider= SliderBox(1, Constant.MAX_GENERATIONS, 1)
        self._fitness_selector = FitnessSelector("Stratégie de fitness")
        self.controller = controller
        self._set_up()

    def _set_up(self):
        layout = QFormLayout(self)

        layout.add_row(QLabel("Taille de la population"), self._pop_slider)
        layout.add_row(QLabel("Pourcentage d'élitisme"), self._elitism_slider)
        layout.add_row(QLabel("Nombre de génération"), self._generation_slider)
        layout.add_row(QFormLayout())
        layout.add_row(QFormLayout())
        layout.add_row(self._fitness_selector)
        layout.add_row(QFormLayout())
        layout.add_row(QFormLayout())
      
        layout.add_row(self._ga_controls)

        self.set_layout(layout)
        
        stop_simulation_button = QPushButton("Arrêter")

        self._pop_slider.get_slider.valueChanged.connect(self._update_parameters)
        self._elitism_slider.get_slider.valueChanged.connect(self._update_parameters)
        self._generation_slider.get_slider.valueChanged.connect(self._update_parameters)

        stop_simulation_button.clicked.connect(self.controller.stop_simulation)

        self._ga_controls.connect_buttons(self._start_button_command, self._save_button_command)
        self._fitness_selector.connect_checkboxes(self._update_parameters)

        self._ga_controls.add_button(stop_simulation_button)

        self._pop_slider.current_value = Constant.INITIAL_POP_MIN_SIZE

    @Slot()
    def _save_button_command(self):
        if not self.controller.save_ga_image():
            QMessageBox.warning(self, "Erreur", "Image n'a pu être sauvée")

    @Slot()
    def _start_button_command(self):
        self._parameters.fitness_strategies = []
        if self._fitness_selector.are_checked(): 
            for i, checkbox in enumerate(self._fitness_selector.fitness_checkboxes):
                if checkbox.checked:
                    self._parameters.fitness_strategies.append(GeneticAlgorithmParameters.default_fitness_strategies[i])
            self._parameters.update()
            self.controller.start_simulation()
        else:
            QMessageBox.warning(self, "Erreur", "Sélectionner au moins une stratégie de sélection!")

    @Slot()
    def _update_parameters(self):
        self._parameters.population_size = int(self._pop_slider.current_value)
        self._parameters.elitism_rate = float(self._elitism_slider.current_value)
        self._parameters.max_generations = int(self._generation_slider.current_value)

        self.controller.ga_parameters = self._parameters


class RGBABox(QFormLayout):

    color_changed = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._entries: List[QLineEdit] = []
        self._color_label = QLabel()
        self._pixmap = QPixmap(300, 25)
        self._entries = [QLineEdit("255") for _ in range(4)]
        self._set_up()

    @property
    def color_label(self) -> QLabel:
        return self._color_label

    def _set_up(self) -> None:
        r_component_label = QLabel("R")
        g_component_label = QLabel("G")
        b_component_label = QLabel("B")
        a_component_label = QLabel("A")

        label_layout = QHBoxLayout()
        entry_layout = QHBoxLayout()

        label_layout.add_widget(r_component_label)
        label_layout.add_widget(g_component_label)
        label_layout.add_widget(b_component_label)
        label_layout.add_widget(a_component_label)

        validator = QRegularExpressionValidator("^([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$")

        for entry in self._entries:
            entry_layout.add_widget(entry)
            entry.set_validator(validator)
            entry.textChanged.connect(self._set_color)

        self._set_color()

        self.add_row(label_layout)
        self.add_row(entry_layout)
        self.add_row(self._color_label)

    @Slot()
    def _set_color(self) -> None:
        r, g, b, a = [int(entry.text) for entry in self._entries]

        color = QColor(r, g, b, a)

        self._pixmap.fill(color)
        self._color_label.pixmap = self._pixmap
        self.color_changed.emit()

    @property 
    def color_components(self) -> List[str]:
        return [entry.text for entry in self._entries]

    def set_color_components(self, color: QColor) -> None:
        self._entries[0].text = str(color.red())
        self._entries[1].text = str(color.green())
        self._entries[2].text = str(color.blue())
        self._entries[3].text = str(color.alpha())    


class SliderBox(QHBoxLayout):
    def __init__(self, minimum: int, maximum: int, steps: float, parent: QWidget = None):
        super().__init__(parent)
        self._current_value_label: QLabel = None
        self._slider: QSlider = None
        self._steps = steps
        self._set_up(minimum, maximum)
        self._slider.value = maximum

    def _set_up(self, minimum, maximum) -> None:
        self._current_value_label = QLabel(str(minimum))

        self._slider = QSlider(Qt.Orientation.Horizontal)

        self._slider.minimum = minimum / self._steps
        self._slider.maximum = maximum / self._steps

        self._slider.valueChanged.connect(lambda value: self._current_value_label.set_num(float(value) * self._steps))

        self.add_widget(self._slider)
        self.add_widget(self._current_value_label)

    @property
    def current_value(self) -> int:
        return self._current_value_label.text

    @property
    def get_slider(self) -> QSlider:
        return self._slider

    @current_value.setter
    def current_value(self, new_value: int) -> None: 
        self._slider.value = new_value / self._steps