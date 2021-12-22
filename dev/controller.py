from __future__ import annotations

from PySide6.QtWidgets import QMessageBox
from ga import *
from lib import *
from parameters import LSystemParameters
from turtle import Turtle, Renderer
from app import LSystemApp
from tree import Tree, Rule, Rules
from db import Database, LsystemDAO

from queue import Queue
import threading
import time
from enum import Enum


class Status(Enum):
    STOPPED = 0
    RUNNING = 1


class Controller:
    class UpdateThread(threading.Thread):
        def __init__(self, controller: Controller):
            super().__init__(daemon=True)
            self._controller = controller
            self._update_time: float = 0.3
            self._last_entry_time: float = 0.0
            self._status: Status = Status.RUNNING

        @property
        def status(self) -> Status:
            return self._status

        @status.setter
        def status(self, status: Status) -> None:
            self._status = status

        def run(self):
            super().run()
            while self._status == Status.RUNNING \
                  and self._controller._ga.generation < self._controller.ga_parameters.max_generations:
                entry_time = time.time()
                if entry_time - self._last_entry_time >= self._update_time:
                    self._last_entry_time = entry_time
                    self._controller.render_ga_image()
            self._status = Status.STOPPED

    def __init__(self):
        self._lsystem_parameters: LSystemParameters = None
        self._ga_parameters: GeneticAlgorithmParameters = None
        self._ga = GeneticAlgorithm()
        self._turtle: Turtle = None
        self.default_lsystems = self.get_default_lsystems()
        self._vue = LSystemApp(self)
        self._update_queue = Queue()
        self._update_thread: Controller.UpdateThread = None
        self._vue.show()

    @property
    def update_queue(self) -> Queue:
        return self._update_queue

    @property
    def ga_parameters(self) -> GeneticAlgorithmParameters:
        return self._ga_parameters

    @ga_parameters.setter
    def ga_parameters(self, ga_parameters: GeneticAlgorithmParameters) -> None:
        self._ga_parameters = ga_parameters
        self._ga.parameters = ga_parameters

    @property 
    def lsystem_parameters(self) -> LSystemParameters:
        return self._lsystem_parameters

    @lsystem_parameters.setter
    def lsystem_parameters(self, parameters: LSystemParameters) -> None:
        self._lsystem_parameters = parameters

    def get_default_lsystems(self) -> LsystemDAO:
        db = Database()
        return db.get_lsystems()

    def generate_line_vector_from_params(self):
        first_transformation_rule = Rule(self._lsystem_parameters.first_transformation_rule,
                                         self._lsystem_parameters.probability_one)
        second_transformation_rule = None
        if self.lsystem_parameters.second_transformation_rule.strip() != "":
            second_transformation_rule = Rule(self._lsystem_parameters.second_transformation_rule,
                                              self._lsystem_parameters.probability_two)
        rules = Rules()
        iterations = self.lsystem_parameters.num_of_iterations
        axiom = self.lsystem_parameters.axiom
        angle = self.lsystem_parameters.angle
        
        rules.append(first_transformation_rule)
        if second_transformation_rule:
            rules.append(second_transformation_rule)
        
        transformed_value = Tree.transform(rules, iterations, axiom)
        
        tree = Tree(transformed_value)
        
        self._turtle = Turtle(tree, angle)
        self._turtle.parse()

    @Slot()
    def render_image(self):
        self.generate_line_vector_from_params()
        
        bg_color = self.lsystem_parameters.bg_color
        shape_color = self.lsystem_parameters.shape_color
        renderer = Renderer(self._turtle.bounds, self._turtle.line_vector, bg_color=bg_color, shape_color=shape_color)
        
        self._vue.simulation_panel.update(renderer.pixmap)

    @Slot()
    def render_ga_image(self):
        self._ga.run()
        best = self._ga.best
        worst = self._ga.worst

        best_turtle = Turtle(best.tree, best.angle)
        best_turtle.parse()

        worst_turtle = Turtle(worst.tree, worst.angle)
        worst_turtle.parse()

        renderer = Renderer(best_turtle.bounds, best_turtle.line_vector)
        renderer.line_vector = worst_turtle.line_vector
        renderer.shape_color = QColor(0, 0, 255)
        renderer.bounds = worst_turtle.bounds
        renderer._render()

        renderer.line_vector = best_turtle.line_vector
        renderer.shape_color = QColor(0, 0, 0)
        renderer.bounds = best_turtle.bounds
        self._vue.simulation_panel.update(renderer.pixmap)

    @Slot()
    def save_ga_image(self) -> bool:
        if not self._update_thread:
            return self._vue.simulation_panel.simulation_image.save(Constant.IMAGE_SAVE_PATH, "PNG", 100)

    @Slot()
    def start_simulation(self) -> None:
        if not self._update_thread or self._update_thread.status == Status.STOPPED:
            self._update_thread = Controller.UpdateThread(self)
            self._update_thread.start()
        else:
            QMessageBox.warning(self._vue.simulation_panel, "Erreur", "Simulation déjà en cours!")

    @Slot()
    def stop_simulation(self) -> None:
        if self._update_thread.status == Status.RUNNING:
            self._update_thread.status = Status.STOPPED
            self._update_thread = None
            self._ga.reset()

    def add_custom_shape(self, shape_name: str) -> None:
        db = Database()

        params = ["custom_color"]
        params.extend(self.lsystem_parameters.bg_color.get_rgb())
        bg_color_id = db.add_color(tuple(params))
        params = ["custom_color"]
        params.extend(self.lsystem_parameters.shape_color.get_rgb())
        shape_color_id = db.add_color(tuple(params))

        params = [shape_name]
        params.extend([
                    self.lsystem_parameters.axiom,
                    self.lsystem_parameters.first_transformation_rule,
                    self.lsystem_parameters.second_transformation_rule,
                    self.lsystem_parameters.num_of_iterations,
                    self.lsystem_parameters.probability_one,
                    self.lsystem_parameters.probability_two,
                    *bg_color_id, *shape_color_id,
                    self.lsystem_parameters.angle
                    ])

        db.add_custom(tuple(params))
