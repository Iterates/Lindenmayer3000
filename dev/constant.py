from typing import List


class Constant:
    """
    Constantes grammaire
    """
    TERMINAL_SET: List[str] = ["F", "-", "+"]
    FUNCTION_SET: List[str] = ["[", "]"]
    ALPHABET = TERMINAL_SET + FUNCTION_SET
    PLACEHOLDER = "$"

    """
    Constantes transformation
    """
    MAX_ITERATIONS: int = 7

    """
    Constantes LSystem
    """
    MAX_RULES = 2
    MIN_ANGLE = 15
    MAX_ANGLE = 90
    """
    Constantes algorithmes génétiques population initiale
    """
    INITIAL_POP_MAX_SIZE = 15
    INITIAL_POP_MIN_SIZE = 2
    MAX_ELITISM_RATE = 0.5
    MIN_ELITISM_RATE = 0.0
    MAX_GENERATIONS = 200
    INITIAL_SEED = None
    """
    Constantes image
    """
    IMAGE_WIDTH = 400
    IMAGE_HEIGHT = 500
    """
    Chemins
    """
    IMAGE_SAVE_PATH = "C:/User/Ari/Desktop/lsystem.png"
    """
    Table d'équivalence
    """
    FR_ENG_DICT = {
                "symmetry": "symétrie", 
                "cumulative": "cumulative", 
                "height": "hauteur", 
                "branch": "branche",
                "canopy": "canopée"
                }