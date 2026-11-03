"""K-class profile registry.

Exports H_K, W_K, T_K, F_K, E_K dictionaries for the 7 v0 classes.
Source of truth: A_STAR_v0.md §5 + §10.
"""

from .k_profiles import (
    CORE_AXES,
    E_K,
    F_K,
    H_K,
    K_CLASSES,
    PROFILES,
    T_K,
    W_K,
    ArchivalPolicy,
    KProfile,
    get_profile,
)

__all__ = [
    "CORE_AXES",
    "K_CLASSES",
    "PROFILES",
    "H_K",
    "W_K",
    "T_K",
    "F_K",
    "E_K",
    "ArchivalPolicy",
    "KProfile",
    "get_profile",
]
