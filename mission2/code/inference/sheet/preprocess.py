import numpy as np


def to_one_hot(labels: list[int], num_classes: int = 10) -> np.ndarray:
    """
    Default position = 0
    A3 = 1,
    B3 = 2,
    C4 = 3,
    D4 = 4,
    E4 = 5,
    F4 = 6,
    G4 = 7,
    A4 = 8,
    B4 = 9,
    C5 = 10
    """
    one_hot = np.zeros((len(labels), num_classes), dtype=np.uint8)
    for idx, label in enumerate(labels):
        if label > 0:
            one_hot[idx, label - 1] = 1
    return one_hot
