"""Passive C_core measurement from git + filesystem.

Per A_STAR_v0.md §11 closing gap on `C_core` measurement: each axis declares
unit, range, normalization, source, confidence, owner, update cadence.

This module emits a `CoreVector` per repo from cheap, non-instrumented
signals. Where a defensible proxy doesn't exist (c_money, c_loss, c_derive),
the measurement returns `confidence=low` and documents what's missing.
"""

from .core_vector import (
    AXIS_SPECS,
    RUNNER_VERSION,
    AxisSpec,
    CoreVector,
    Measurement,
    measure_repo,
)

__all__ = [
    "AXIS_SPECS",
    "RUNNER_VERSION",
    "AxisSpec",
    "CoreVector",
    "Measurement",
    "measure_repo",
]
