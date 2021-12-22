from random import uniform, choice
from statistics import mean
from math import floor
from copy import deepcopy
import numpy as np
import re

from util import cosine_law, Bounds, sigmoid, to_upper
from turtle import Turtle, Renderer
from lsystem import LSystemFactory, LSystem
from geneticsetup import *
from lib import *
from constant import Constant


class FitnessStrategy(ABC):
    def __repr__(self):
        """
        Méthode retournant une chaîne correspondant au nom de la stratégie. Utilisé dans la vue
        afin de créer des labels. Le pattern de l'expression régulière a été trouvé à
        https://stackoverflow.com/questions/510972/getting-the-class-name-of-an-instance
        """
        strategy_name = re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', type(self).__name__)[0]
        fr_strategy_name = Constant.FR_ENG_DICT.get(strategy_name.lower())
        return to_upper(fr_strategy_name)


    @abstractmethod
    def evaluate(self):
        raise NotImplementedError()


class SymmetryFitness(FitnessStrategy):
    def evaluate(self, turtle: Turtle, lsystem: LSystem) -> float:
        return 1.0 - (abs(turtle.centroid.x() - turtle.bounds.x_center) / (turtle.bounds.width + 1e-10))


class CumulativeSymmetryFitness(FitnessStrategy):
    """
    Seconde classe permettant d'évaluer la symétrie d'une image. La valeur absolue de la somme
    des coordonnées en x négatives et des coordonnées en y positive est normalisée dans la fonction
    sigmoïde : plus l'arbre est débalancé, plus le résultat tendra vers 1.
    """
    def evaluate(self, turtle: Turtle, lsystem: LSystem) -> float:
        x_coordinates_sum = abs(sum(point.x() for point in turtle.point_vector))
        try:
            result = 1 - sigmoid(x_coordinates_sum)
        except OverflowError:
            result = 0
        finally:
            return result


class BranchFitness(FitnessStrategy):
    def __init__(self):
        self._max_branch_count: int = 0

    @property
    def max_branch(self) -> int:
        return self._max_branch_count
    
    def evaluate(self, turtle: Turtle, lsystem: LSystem):
        branch_count = lsystem.value.count("]")
        self._max_branch_count = max(branch_count, self._max_branch_count)
        return branch_count


class CanopyFitness(FitnessStrategy):
    def evaluate(self, turtle: Turtle, lsystem: LSystem) -> float:
        a = ((turtle.bounds.min_x - turtle.bounds.max_x) ** 2) ** 0.5
        b = (turtle.bounds.min_x ** 2 + (turtle.bounds.min_y - turtle.centroid.y()) ** 2) ** 0.5
        c = ((turtle.bounds.min_x - turtle.bounds.max_x) ** 2 + (turtle.centroid.y() - turtle.bounds.min_y) ** 2) ** 0.5

        if a * b * c:
            alpha, beta, gamma = cosine_law(a, b, c) 
            mean_angle = mean([beta, gamma])
        else:
            mean_angle = 90

        return 1.0 - mean_angle / 90.0


class HeightFitness(FitnessStrategy):
    def __init__(self):
        self._max_tree_height: float = 0.

    @property
    def max_height(self) -> float:
        return self._max_tree_height

    def evaluate(self, turtle: Turtle, lsystem: LSystem) -> float:
        self._max_tree_height = min(self._max_tree_height, turtle.bounds.min_y)
        return turtle.bounds.min_y


class SelectionStrategy(ABC):
    def __init__(self):
        self._population_fitness_weights: List[float] = None

    @abstractmethod
    def calculate_weights(self, population_fitness: np.array, generation_count: int):
        raise NotImplementedError()

    def select(self, population: List[Any], number_of_parents: int) -> List[Any]:
        population = deepcopy(population)
        parents = []
        for i in range(number_of_parents):
            parent_to_add = choices(population, self._population_fitness_weights, k=1)[0]
            for parent in parents:
                if parent_to_add is parent:
                    parent_to_add = deepcopy(parent_to_add)
            parents.append(parent_to_add)
        return parents


class RouletteWheelStrategy(SelectionStrategy):
    """
    Selection de geniteurs. Utilisation d'une boucle afin d'éviter que le même objet
    ne se retrouve deux fois dans la liste retournée.
    """
    def calculate_weights(self, population_fitness: np.array, generation_count: int = None) -> None:
        mean_fitness = np.mean(population_fitness)
        self._population_fitness_weights = list(population_fitness / mean_fitness)


class RankStrategy(SelectionStrategy):
    def select(self):
        pass


class BoltzmannStrategy(SelectionStrategy):
    """
    A continuously varying "temperature" controls the rate of selection according to a preset schedule. The
    temperature starts out high, which means that selection pressure is low (i.e., every individual has some
    reasonable probability of reproducing). The temperature is gradually lowered, which gradually increases the
    selection pressure, thereby allowing the GA to narrow in ever more closely to the best part of the search space
    while maintaining the "appropriate" degree of diversity.

    Tiré de An Introduction to Genetical Algorithms par Melanie Mitchell
    """
    def calculate_weights(self, population_fitness: np.array, generation_count: int):
        temperature_weights = np.exp(population_fitness / generation_count)
        self._population_fitness_weights = temperature_weights / np.mean(temperature_weights)


class SigmaStrategy(SelectionStrategy):
    """
     "Sigma scaling" (Forrest 1985; it was called "sigma truncation" in Goldberg
    1989a), which keeps the selection pressure (i.e., the degree to which highly fit individuals are allowed many
    offspring) relatively constant over the course of the run rather than depending on the fitness variances in the
    population. Under sigma scaling, an individual's expected value is a function of its fitness, the population
    mean, and the population standard deviation. 

    Tiré de An Introduction to Genetical Algorithms par Melanie Mitchell
    """
    def select(self):
        pass
    

class CrossoverStrategy(ABC):
    @abstractmethod
    def crossover(self):
        raise NotImplementedError()


class AngleCrossover(CrossoverStrategy):
    """
    Stratégie permettant d'effectuer un croisement des angles de deux géniteurs.
    Un angle moyen est calculé, auquel est rajouté ou enlevé une valeur déterminée. 
    """
    def __init__(self):
        self._angle_mutation: int = 5

    def crossover(self, first_parent: LSystem, second_parent: LSystem) -> None:
        crossover_angle = mean([first_parent.angle, second_parent.angle])
        first_parent.angle = uniform(crossover_angle - self._angle_mutation, crossover_angle + self._angle_mutation)
        second_parent.angle = uniform(crossover_angle - self._angle_mutation, crossover_angle + self._angle_mutation)


class NodeCrossoverStrategy(CrossoverStrategy):
    """
    Les enfants de deux nodes sont échangés, générant deux enfants de la prochaine génération. 
    La méthode pourrait être éventuellement modifiée afin de ne générer qu'un seul descendant au lieu
    de deux.
    """
    def crossover(self, first_parent: LSystem, second_parent: LSystem, angle_crossover: bool = True) -> Tuple[LSystem]:
        first_subtree = choice([node for node in Traversal.node_generator(first_parent.tree.root)]) 
        second_subtree = choice([node for node in Traversal.node_generator(second_parent.tree.root)])

        first_cut_off_index = randint(0, len(first_subtree.child) - 1)
        second_cut_off_index = randint(0, len(second_subtree.child) - 1)

        first_cut_off = first_subtree.child.pop(first_cut_off_index)
        second_cut_off = second_subtree.child.pop(second_cut_off_index)

        first_subtree.child.insert(first_cut_off_index, second_cut_off)
        second_subtree.child.insert(second_cut_off_index, first_cut_off)

        if angle_crossover:
            angle_crossover = AngleCrossover()
            angle_crossover.crossover(first_parent, second_parent)
        
        return first_parent, second_parent


class CumulativeFitness:
    """
    Classe permettant de ne retourner que la fitness cumulative d'une population donnée 
    en vue de son utilisation par l'algorithme génétique.
    """
    def __init__(self, population: List[Any], fitness_strategies: List[FitnessStrategy], fitness_weights: List[float]):
        self._fitness_strategies = fitness_strategies
        self._population = population
        self._fitness_weights = np.array(fitness_weights).reshape((len(fitness_weights), 1))
        self._cumulative_fitness: np.array = None

    @property
    def cumulative_fitness(self) -> np.array:
        return self._cumulative_fitness

    @property
    def fitness_weights(self) -> List[float]:
        return self._fitness_weights

    @fitness_weights.setter
    def fitness_weights(self, fitness_weights: List[float]) -> None:
        self._fitness_weights = fitness_weights

    @abstractmethod
    def compute_fitness(self) -> float:
        raise NotImplementedError()


class LSystemCumulativeFitness(CumulativeFitness):
    """
    Classe permettant de calculer la fitness cumulative des Systemes de Lindenmayer.
    Une troisieme boucle est necessaire afin de normaliser les fitness de hauteur 
    et de branches en les divisant par les plus grandes mesures.
    """
    def compute_fitness(self) -> np.array:
        fitness_array = np.zeros((len(self._fitness_strategies), len(self._population)))
        
        for i, lsystem in enumerate(self._population):
            turtle = Turtle(lsystem.tree, lsystem.angle)
            turtle.parse()
            for j, fitness_strategy in enumerate(self._fitness_strategies):
                fitness_array[j][i] = fitness_strategy.evaluate(turtle, lsystem)
        
        for i, fitness_strategy in enumerate(self._fitness_strategies):
            if isinstance(fitness_strategy, HeightFitness):
                fitness_array[i] /= fitness_strategy.max_height
            elif isinstance(fitness_strategy, BranchFitness):
                fitness_array[i]  /= fitness_strategy.max_branch

        self._cumulative_fitness = np.sum(fitness_array * self._fitness_weights, axis=0)
        
        return self._cumulative_fitness


class GeneticAlgorithmParameters:
    default_fitness_strategies: List[FitnessStrategy] = [
                                                        CumulativeSymmetryFitness(),
                                                        HeightFitness(),
                                                        BranchFitness(),
                                                        CanopyFitness(),
                                                        SymmetryFitness()
                                                        ]

    def __init__(self):
        self.population_size: int = 2
        self.elitism_rate: float = 0.1
        self.max_generations: int = 50
        self.selection_strategy: SelectionStrategy = RouletteWheelStrategy()
        self.mutation_strategies: MutationStrategy = SymbolMutationStrategy()
        self.crossover_strategy: CrossoverStrategy = NodeCrossoverStrategy()
        self.fitness_strategies: List[FitnessStrategy] = []
        self.population_size = clamp(Constant.INITIAL_POP_MIN_SIZE, Constant.INITIAL_POP_MAX_SIZE, self.population_size)
        self.elitism_rate = clamp(Constant.MIN_ELITISM_RATE, Constant.MAX_ELITISM_RATE, self.elitism_rate)
        self.population = LSystemFactory.get_random_population(self.population_size)
        self.cumulative_population_fitness = LSystemCumulativeFitness(self.population, [
                                                                            CumulativeSymmetryFitness(),
                                                                            HeightFitness(),
                                                                            BranchFitness(),
                                                                            CanopyFitness(),
                                                                            SymmetryFitness()
                                                                            ], [0.2, 0., 0.5, 0.3, 0.0])

    def update(self) -> None:
        self.population = LSystemFactory.get_random_population(self.population_size)
        self.cumulative_population_fitness = LSystemCumulativeFitness(self.population, self.fitness_strategies,
                                                                      [1 / len(self.fitness_strategies) for _ in range(len(self.fitness_strategies))])


class GeneticAlgorithm:
    def __init__(self, parameters: GeneticAlgorithmParameters = GeneticAlgorithmParameters()):
        self._parameters: GeneticAlgorithmParameters = parameters
        self._population: List[Any] = None
        self._population_fitness: np.array = None
        self._cumulative_population_fitness: CumulativeFitness = None
        self._best: Any = None
        self._worst: Any = None
        self._elites_count: int = None
        self._generation_count: int = 0

    @property
    def generation(self) -> int:
        return self._generation_count

    @property
    def best(self) -> Any:
        return self._best

    @property
    def worst(self) -> Any:
        return self._worst

    @property
    def parameters(self) -> GeneticAlgorithmParameters:
        return self._parameters

    @parameters.setter
    def parameters(self, parameters: GeneticAlgorithmParameters) -> None:
        self._parameters = parameters
        self._elites_count = floor(self._parameters.population_size * self._parameters.elitism_rate)
        self._cumulative_population_fitness = self._parameters.cumulative_population_fitness
        self._population = self._parameters.population

    @property
    def population_fitness(self) -> np.array:
        return self._cumulative_population_fitness.cumulative_fitness

    def reset(self) -> None:
        self._generation_count = 0
        self._best = None
        self._worst = None

    def run(self):
        self._generation_count += 1

        # Calcul de la fitness cumulative
        self._population_fitness = self._cumulative_population_fitness.compute_fitness()

        # Nouvelle population
        new_population = []
        while len(new_population) <= self._parameters.population_size:
            self._parameters.selection_strategy.calculate_weights(self._population_fitness)
            parents = self._parameters.selection_strategy.select(self._population, 2)
            children = self._parameters.crossover_strategy.crossover(*parents)
            new_population.extend(children)

        # Ajustement de la taille de la nouvelle population si nécessaire
        new_population = new_population[:self._parameters.population_size]

        # Ajout des élites
        self._population.sort(key=lambda x: next(fit for fit in self._population_fitness), reverse=True)
        elites = self._population[:self._elites_count]
        new_population = new_population[:(len(new_population) - self._elites_count)]
        new_population.extend(elites)

        self._population = new_population

        # Mutation
        for lsystem in self._population:
            self._parameters.mutation_strategies.mutate(lsystem.tree.root)

        self._best = self._population[max(np.argsort(self.population_fitness))]
        self._worst = self._population[min(np.argsort(self.population_fitness))]
