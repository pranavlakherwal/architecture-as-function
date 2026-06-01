"""Smoke tests for K-class profiles."""

import pytest

from a_star.profiles import (
    CORE_AXES,
    H_K,
    K_CLASSES,
    PROFILES,
    W_K,
    get_profile,
)


def test_all_seven_classes_present():
    assert set(PROFILES) == set(K_CLASSES)
    assert len(PROFILES) == 7


def test_weights_sum_to_one():
    for k, weights in W_K.items():
        total = sum(weights.values())
        assert 0.99 <= total <= 1.01, f"{k}: weights sum to {total}"


def test_all_axes_present_per_profile():
    for k, weights in W_K.items():
        assert set(weights) == set(CORE_AXES), f"{k}: missing or extra axes"


def test_hard_constraints_nonempty():
    for k, constraints in H_K.items():
        assert len(constraints) >= 3, f"{k}: too few hard constraints"


def test_archival_policy_present():
    for k, profile in PROFILES.items():
        assert profile.archival.storage_tier, f"{k}: missing storage tier"
        assert profile.archival.typical_windows, f"{k}: missing windows"


def test_seed_mapping():
    expected = {
        "outbound-pipeline": "AgencyA",
        "content-pipeline": "LSD",
        "product-marketing": "BrandB",
        "product-saas": "UniversityC",
        "research-memory": "Personal Twin",
        "audit-pipeline": "DeskD Engine",
        "intel-pipeline": "deskd-intel",
    }
    for k, seed in expected.items():
        assert get_profile(k).seed == seed


def test_outbound_top_axes_match_spec():
    """Spec §5: outbound-pipeline c_money > c_drift > c_modify."""
    w = W_K["outbound-pipeline"]
    assert w["c_money"] > w["c_drift"] > w["c_modify"]


def test_audit_top_axes_match_spec():
    """Spec §5: audit-pipeline c_loss > c_find > c_derive."""
    w = W_K["audit-pipeline"]
    assert w["c_loss"] > w["c_find"] > w["c_derive"]


def test_research_memory_top_axes_match_spec():
    """Spec §5: research-memory c_find > c_storage > c_derive."""
    w = W_K["research-memory"]
    assert w["c_find"] > w["c_storage"] > w["c_derive"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
