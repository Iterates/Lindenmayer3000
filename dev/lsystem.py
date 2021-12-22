from random import choice, randint
from tree import Tree, Node, Rules, Rule
from constant import Constant
from typing import List, Union

from lib import *
from util import clamp, Bounds
from geneticsetup import MutationStrategy, Randomizer, SymbolMutationStrategy


class LSystem:
    def __init__(self, transformation_rules: Rules, tree_structure: Tree, iterations: int, axiom: str, angle: float):
        if not isinstance(transformation_rules, Rules):
            raise TypeError("Règles doivent etre de type Rules")
        if not isinstance(tree_structure, Tree):
            raise TypeError("Arbre doit être de type Tree")
        if not isinstance(iterations, int):
            raise TypeError("Iterations doivent être une valeur entière")
        if not isinstance(angle, float):
            raise TypeError("Angle doit être un réel")
        if axiom not in Constant.TERMINAL_SET:
            raise ValueError("Caractère inconnu, doit faire partie de l'alphabet existant")
        
        self._transformation_rules = transformation_rules.get_rules
        self._tree = tree_structure
        self._value = tree_structure.solution()
        self._iterations = iterations
        self._axiom = axiom
        self._angle = angle
        self._line_vector = None
        self._bounds = None

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
    def angle(self) -> float:
        return self._angle

    @angle.setter
    def angle(self, angle: float) -> None:
        self._angle = angle

    @property
    def value(self) -> str:
        return self._value

    @property
    def tree(self) -> Tree:
        return self._tree

    @property
    def axiom(self) -> str:
        return self._axiom

    @property
    def iterations(self) -> int:
        return self._iterations

    @property
    def rules(self) -> List[Rule]:
        return self._transformation_rules

    @iterations.setter
    def iterations(self, iterations: int) -> None:
        if not isinstance(iterations, int):
            raise ValueError("Itérations doivent être un entier")
        self._iterations = clamp(0, Constant.MAX_ITERATIONS, iterations)

    def transform(self) -> None:
        transformed_value = self._value
        for i in range(self._iterations):
            for rule in self._transformation_rules:
                transformed_value = rule + transformed_value
        self._value = transformed_value
        

class DefaultLSystem(LSystem):
    """
    Arbre par défaut utilisé dans la génération de la population de départ
    Constructeur initialisé avec des valeurs fixes.
    """
    def __init__(self):
        rules = Rules()
        rule = Rule("F=F[+F]F[-F]F")
        rules.append(rule)
        self._transformation_rules = rules
        self._value = "F"
        self._iterations = 4
        self._angle = 25.7
        self.transform()
        self._tree = Tree(self._value)
        self._mutation_strategy: MutationStrategy = SymbolMutationStrategy()
        self._mutation_strategy.mutate(self._tree.root)


class RandomLSystem(LSystem):
    """
    Arbre aléatoire utilisé dans la génération de la population de départ.
    Constructeur initialisé avec des valeurs aléatoires.
    """
    def __init__(self):
        rules = Rules()
        string_pool = Randomizer.generate_random_string_pool(50)
        self._iterations = 4
        self._angle = randint(Constant.MIN_ANGLE, Constant.MAX_ANGLE)
        rules_from = []
        for i in range(Constant.MAX_RULES):
            rule_from = choice(string_pool)
            rules_from.append(rule_from) 
            rule_to = Randomizer.generate_random_tree(1)
            rule = Rule(f"{rule_from}={rule_to.solution()}")
            rules.append(rule)
        self._transformation_rules = rules
        self._value = choice(rules_from)
        self.transform()
        self._tree = Tree(self._value)


class LSystemFactory(ABC):
    """
    Classe permettant de générer des populations de tailles déterminées, soit
    composées d'individus par défaut, soit aléatoire, soit mixte en spécifiant
    le ratio de mixte à défaut
    """
    @staticmethod
    def get_default_population(population_size: int) -> List[DefaultLSystem]:
        return [DefaultLSystem() for _ in range(population_size)]

    @staticmethod
    def get_random_population(population_size: int) -> List[RandomLSystem]:
        return [RandomLSystem() for _ in range(population_size)]

    @staticmethod
    def get_mixed_population(population_size: int,
                             default_to_random_ratio: float) -> List[Union[RandomLSystem, DefaultLSystem]]:
        default_population_size = int(population_size * default_to_random_ratio)
        random_population_size = int(population_size - default_population_size)
        return LSystemFactory.get_default_population(default_population_size) + \
               LSystemFactory.get_random_population(random_population_size)
