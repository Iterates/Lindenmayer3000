from __future__ import annotations

from constant import Constant
from typing import Dict
from copy import deepcopy
from typing import List
from random import choices, seed, randint


class Rules(list):
    """
    Classe contenant des objets de type Rule. La méthode iter a été redéfinie de manière
    à retourner soit un itérateur sur l'instance si la somme des probabilités est supérieur à 1,
    soit une règle choisie aléatoirement selon sa probabilité si la somme des probabilités n'est
    pas égale à 1. La méthode append a également été redéfinie de manière à s'assurer que si p < 1
    pour une règle à ajouter, la somme totale des probabilités ne dépasse pas 1.
    """
    def __init__(self, *args):
        list.__init__(self, *args)
        self._probability: float = 0.

    @property
    def get_rules(self) -> List[Rule]:
        return [rule for rule in super().__iter__()]

    def append(self, to_append: Rule):
        if not to_append:
            return
        if not isinstance(to_append, Rule):
            raise TypeError("Objet doit être type Rule")
        if to_append.is_weighted and to_append.probability + self._probability > 1.:
            raise ValueError("Probabilite totale ne peut etre superieure a 1")
        super().append(to_append)
        self._probability += to_append.probability

    def __iter__(self):
        if sum(rule.probability for rule in super().__iter__()) > 1:
            return super().__iter__()
        return iter(choices(self, weights=[rule.probability for rule in super().__iter__()], k=1))


class Rule:
    def __init__(self, transformation_rule: str, probability: float = 1):
        if "=" not in transformation_rule:
            raise ValueError("Chaîne doit comporter un opérateur d'égalité")
        if not Rule.is_well_formed(transformation_rule):
            raise ValueError("Caractère inconnu. Le caractère doit faire partie de l'alphabet")
        self._transform_from, self._transform_to = transformation_rule.split("=") 
        self._probability = probability

    @property
    def probability(self) -> float:
        return self._probability

    @property
    def transform_to(self) -> str:
        return self._transform_to

    @property
    def transform_from(self) -> str:
        return self._transform_from

    @property
    def is_weighted(self) -> bool:
        return not self.probability == 1

    @staticmethod
    def is_well_formed(transformation_rule: str) -> bool:
        for char in transformation_rule:
            if char not in Constant.ALPHABET + ["="]:
                return False
        return True

    def __add__(self, string_value: str) -> str:
        if not isinstance(string_value, str):
            raise TypeError("Objet a transformer doit etre une chaine de caracteres")
        return string_value.replace(self._transform_from, self._transform_to)

    def __radd__(self, string_value: str):
        return self.__add__(string_value)


class Tree:
    def __init__(self, value: str):
        self.validate_entry(value)
        self.root = Node(value)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index >= len(self.root.value):
            raise StopIteration
        index = self.index
        self.index += 1
        next_char_index = min(index + 1, len(self.root.value) - 1)
        if self.root.value[index] != "$" and self.root.value[next_char_index] != "$":
            if index == len(self.root.value) - 1:
                return self.root.value[index]
            return self.root.value[index] + self.__next__()
        return self.root.value[index]

    def solution(self) -> str:
        sol = [""]
        self.root.rebuild(sol)
        return sol[0]

    def validate_entry(self, value: str) -> None:
        brace_count = 0
        for char in value:
            if char == "[":
                brace_count += 1
            if char == "]":
                brace_count -= 1
            if brace_count < 0:
                raise ValueError("Chaine invalide")
        if brace_count:
            raise ValueError("Chaine invalide")

    @staticmethod
    def transform(rules: Rules, iterations: int, value: str) -> str:
        transformed_value = value
        num_iterations = min(iterations, Constant.MAX_ITERATIONS)
        for i in range(num_iterations):
            for rule in rules:
                transformed_value = rule + transformed_value
        return transformed_value


class Node:
    def __init__(self, value: str):
        self.value = ""
        self.child: List[Node] = []
        brace_count = 0
        start = -1
        for curr, char in enumerate(value):
            if char == "[":
                if start == -1:
                    start = curr
                else:
                    brace_count += 1
            if char == "]":
                if not brace_count:
                    self.child.append(Node(value[start + 1:curr]))
                    self.value = self.value + "$"
                    start = -1
                else:
                    brace_count -= 1
            if start == -1 and char != "]":
                self.value = self.value + char

    def rebuild(self, sol: List[str]):
        i = 0
        for char in self.value:
            if char != "$":
                sol[0] = sol[0] + char
            else:
                sol[0] = sol[0] + "["
                self.child[i].rebuild(sol)
                i += 1
                sol[0] = sol[0] + "]"

    def solution(self) -> str:
        sol = [""]
        self.rebuild(sol)
        return sol[0]
