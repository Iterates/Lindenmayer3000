from tree import Tree, Rule, Rules, Node
from typing import List, Any
from util import clamp
from random import randint, random, sample, choices
from functools import wraps
from fractions import Fraction
from abc import ABC, abstractmethod
from constant import Constant


class MutationStrategy(ABC):
    @abstractmethod
    def mutate(self, root: Node, at_depth: int = 0):
        raise NotImplementedError()


class SymbolMutationStrategy(MutationStrategy):
    def __init__(self, symbol_mutation_chance: float = 5e-2):
        self._symbol_mutation_chance = symbol_mutation_chance
        self._symbols_weights = [0.8, 0.1, 0.1]

    def mutate(self, root: Node, at_depth: int = 0) -> None:
        root_value_copy = (list(root.value)).copy()
        for i, gene in enumerate(root.value):
            if gene != Constant.PLACEHOLDER:
                if random() < self._symbol_mutation_chance:
                    root_value_copy[i] = "".join(choices(Constant.TERMINAL_SET, weights=self._symbols_weights, k=1))
        root.value = "".join(root_value_copy)
        at_depth += 1
        for child in root.child:
            self.mutate(child, at_depth)
        at_depth -= 1


class NodeMutationStrategy(MutationStrategy):
    def __init__(self, random_pivot: int = 1):
        self._random_pivot = random_pivot

    def mutate(self, root: Node, at_depth: int = 0) -> None:
        for child in root.child:
            at_depth += 1
            if at_depth == self._random_pivot:
                cut_off = root.child[randint(0, len(root.child) - 1)]
                root.child.remove(cut_off)
                root.child.append(Randomizer.generate_random_tree(1))
                root.value = Randomizer.shuffle_genotype(root.value)
                break
            self.mutate(child, at_depth)
            at_depth -= 1


class BlockMutationStrategy(MutationStrategy):
    def __init__(self, block_mutation_chance: float = 5e-2, random_pivot=0):
        self._block_mutation_chance = block_mutation_chance
        self._random_pivot = random_pivot

    def mutate(self, root: Node, at_depth: int = 0) -> None:
        for child in root.child:
            at_depth += 1
            if at_depth >= self._random_pivot:
                if random() < self._block_mutation_chance:
                    number_of_placeholders = child.value.count(Constant.PLACEHOLDER)
                    mutated_block = Randomizer.generate_random_string()
                    mutated_block += number_of_placeholders * Constant.PLACEHOLDER
                    child.value = mutated_block
            self.mutate(child, at_depth)
            at_depth -= 1


class Randomizer:
    """
    Ensemble de méthode statiques aléatoires générant différents types d'objets 
    encapsulées dans une classe
    """
    _max_depth: int = 1
    _max_breadth: int = 4

    def sprinkle(function):
        """
        Afin de s'assurer qu'un caractère particulier sera toujours présent dans la génération alétaoire
        d'une chaîne de caractère. Implémentée comme décorateur par souci de cohésion.
        """
        sprinkles = "F"
        @wraps(function)
        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)
            if sprinkles not in result:
                result += sprinkles
            return "".join(sample(result, len(result)))
        return wrapper

    @staticmethod
    @sprinkle
    def generate_random_string(maximum_count: int = 5) -> str:
        random_string = "".join(choices(Constant.TERMINAL_SET, k=randint(1, maximum_count)))
        return random_string

    @staticmethod
    def generate_random_string_pool(pool_size: int) -> List[str]:
        return [Randomizer.generate_random_string(3) for i in range(pool_size)]

    @staticmethod
    def shuffle_genotype(genotype: str) -> str:
        """
        Substituts ($) seront ajoutés à la fin de chaque valeur de chaque Node suivant 
        leur nombre d'enfants. Il convient donc de distribuer aléatoirement ces caractères
        de substitution dans la chaîne.
        """
        return "".join(sample(genotype, k=len(genotype)))

    @staticmethod
    def generate_random_tree(at_depth: int, children: List[Node] = None):
        #Base case
        if at_depth == 0:
            root = Node(Randomizer.generate_random_string())
            root.child = children
            placeholders = "$" * len(children) if children else ""
            root.value += placeholders
            root.value = Randomizer.shuffle_genotype(root.value)
            return root
        elif at_depth == Randomizer._max_depth:
        #Generate terminal leaves with max breadth, no children
            at_depth -= 1
            number_of_terminal_leaves = randint(1, Randomizer._max_breadth)
            terminal_leaves = [Node(Randomizer.generate_random_string()) for _ in range(number_of_terminal_leaves)]
            return Randomizer.generate_random_tree(at_depth, terminal_leaves)
        else:
        #Generate intermediate leaves and append previous layer, children are randomly split amongst parents
            at_depth -= 1
            number_of_intermediate_leaves = randint(1, len(children))
            parents = [Node(Randomizer.generate_random_string()) for _ in range(number_of_intermediate_leaves)]
        #Split children using split list utility function
            split_list = Randomizer.split_list(children, len(parents))
            for parent in parents:
                child_to_append = next(split_list)
                placeholders = "$" * len(child_to_append)
                parent.child = child_to_append
                parent.value += placeholders
                parent.value = Randomizer.shuffle_genotype(parent.value)
            return Randomizer.generate_random_tree(at_depth, parents)


class Traversal:
    """
    Classe encapsulant diverses méthodes de parcours d'arbre, ainsi que des méthodes permettant
    d'évaluer la profondeur d'un arbre et la profondeur de chacune de ses feuilles
    """
    @staticmethod
    def breadth_first(tree):
        """
        Breadth first traversal trouvée à https://code.activestate.com/recipes/231503-breadth-first-traversal-of-tree/
        Modification apportée à l'itérateur qui doit s'appliquer sur les enfants de la node et non la node elle même.
        Pourrait être remedié en redéfinissant la méthode __iter__ de Node pour que celle-ci retourne un itérateur
        sur ses enfants.
        """
        yield tree
        last = tree
        for node in Traversal.breadth_first(tree):
            for child in node.child:
                yield child
                last = child
            if last == node:
                return

    @staticmethod
    def postorder_traversal(root: Node, at_depth: int = 0) -> None:
        if root:
            for child in root.child:
                at_depth += 1
                Traversal.postorder_traversal(child, at_depth)
                at_depth -= 1
            print(root.value, at_depth)

    @staticmethod
    def node_generator(node: Node, at_depth: int = 0):
        """
        Méthode retournant tous les enfant possédant eux-mêmes des enfants à
        des fins de croisement
        """
        if node.child:
            yield node
            for child in node.child:
                at_depth += 1
                for i in Traversal.node_generator(child, at_depth):
                    yield i
                at_depth -= 1

    @staticmethod
    def max_depth(node: Node) -> int:
        if not node.child:
            return 0
        return 1 + max(Traversal.max_depth(child) for child in node.child)

    @staticmethod
    def max_depth_generator(node: Node, at_depth: int = 0):
        """
        Afin de déterminer la profondeur de toutes les nodes de l'arbre
        et de pouvoir les utiliser aisément dans une liste
        """
        yield at_depth
        for child in node.child:
            at_depth += 1
            for i in Traversal.max_depth_generator(child, at_depth):
                yield i
            at_depth -= 1
