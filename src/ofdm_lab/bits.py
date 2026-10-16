"""Séquences binaires reproductibles, sans état aléatoire global."""

import numpy as np
from numpy.typing import ArrayLike, NDArray


def validate_bits(bits: ArrayLike) -> NDArray[np.uint8]:
    """Vérifier une séquence 1D binaire avant conversion (pas de troncature)."""
    values = np.asarray(bits)
    if values.ndim != 1 or values.dtype.kind not in "biuf":
        raise ValueError("Les bits doivent être un vecteur numérique réel à une dimension.")
    if not np.all((values == 0) | (values == 1)):
        raise ValueError("Chaque bit doit valoir exactement 0 ou 1.")
    return values.astype(np.uint8)


def generate_bits(count: int, seed: int | None = None) -> NDArray[np.uint8]:
    """Générer count bits équiprobables avec le générateur local NumPy PCG64."""
    if isinstance(count, bool) or not isinstance(count, (int, np.integer)) or count < 0:
        raise ValueError("Le nombre de bits doit être un entier positif ou nul.")
    return np.random.default_rng(seed).integers(0, 2, size=count, dtype=np.uint8)
