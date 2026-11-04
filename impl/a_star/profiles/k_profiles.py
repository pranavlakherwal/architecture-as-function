"""Static K-class profiles for A* v0.1.

Source of truth: /architecture-as-function/A_STAR_v0.md §5 + §10.
Spec frozen 2026-05-21. Any change here must trace to a spec revision.

A K profile is a 5-tuple:
    K_profile = (H_K, W_K, T_K, F_K, E_K)

  H_K = hard constraints (must hold, union under hybrids, never averaged)
  W_K = soft weights over the 7-axis C_core vector
  T_K = typical team composition
  F_K = failure-mode priors (what breaks first in this class)
  E_K = observability requirements (what must be measurable to govern this class)

Plus archival policy excerpted from §10.
"""

from dataclasses import dataclass
from typing import Literal

# ---- Type aliases -----------------------------------------------------------

CoreAxis = Literal[
    "c_find",
    "c_modify",
    "c_storage",
    "c_money",
    "c_drift",
    "c_loss",
    "c_derive",
]

CORE_AXES: tuple[CoreAxis, ...] = (
    "c_find",
    "c_modify",
    "c_storage",
    "c_money",
    "c_drift",
    "c_loss",
    "c_derive",
)

KClass = Literal[
    "outbound-pipeline",
    "content-pipeline",
    "product-marketing",
    "product-saas",
    "research-memory",
    "audit-pipeline",
    "intel-pipeline",
]

K_CLASSES: tuple[KClass, ...] = (
    "outbound-pipeline",
    "content-pipeline",
    "product-marketing",
    "product-saas",
    "research-memory",
    "audit-pipeline",
    "intel-pipeline",
)


@dataclass(frozen=True)
class ArchivalPolicy:
    """Per-K archival policy from §10. Defaults; overridable by jurisdiction/contract/legal-hold."""

    must_irreversibly_destroy: tuple[str, ...]
    must_archive: tuple[str, ...]
    typical_windows: dict[str, str]
    storage_tier: str


@dataclass(frozen=True)
class KProfile:
    """Frozen K-class profile. Constructed at module load; never mutated at runtime."""

    name: KClass
    seed: str  # Neural ecosystem seed project
    hard_constraints: tuple[str, ...]
    soft_weights: dict[CoreAxis, float]  # sums to 1.0 within rounding
    team_composition: dict[str, str]
    failure_priors: tuple[str, ...]
    observability: tuple[str, ...]
    archival: ArchivalPolicy

    def __post_init__(self) -> None:
        total = sum(self.soft_weights.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"{self.name}: soft_weights must sum to 1.0, got {total:.4f}")
        missing = set(CORE_AXES) - set(self.soft_weights)
        if missing:
            raise ValueError(f"{self.name}: missing axes {missing}")


# ---- The 7 v0 profiles ------------------------------------------------------
# Weights derived from the §5 ranking "Top C axes" column. Convention:
#   primary axis  = 0.30
#   secondary     = 0.22
#   tertiary      = 0.16
#   remaining 4   = 0.08 each  (0.30 + 0.22 + 0.16 + 4*0.08 = 1.00)
# v0.1 weights are bootstrap. v0.2 calibrates from observed-cost deltas.


def _weights(primary: CoreAxis, secondary: CoreAxis, tertiary: CoreAxis) -> dict[CoreAxis, float]:
    base = {axis: 0.08 for axis in CORE_AXES}
    base[primary] = 0.30
    base[secondary] = 0.22
    base[tertiary] = 0.16
    return base


OUTBOUND_PIPELINE = KProfile(
    name="outbound-pipeline",
    seed="AgencyA",
    hard_constraints=(
        "fresh_leads_by_cutoff",
        "deliverability_safe_send",
        "idempotent_sequence_state",
        "smtp_verify_before_send",
        "suppression_honored",
    ),
    soft_weights=_weights("c_money", "c_drift", "c_modify"),
    team_composition={
        "T_human": "low",
        "T_agent_internal": "high",
        "T_agent_external": "high",
    },
    failure_priors=(
        "burned_addresses_from_stale_leads",
        "sender_reputation_collapse",
        "double_send_from_non_idempotent_state",
        "deliverability_drift_from_warm_up_skip",
    ),
    observability=(
        "per_send_outcome_log",
        "bounce_rate_by_sender",
        "open_rate_by_cohort",
        "reply_classification",
        "suppression_list_freshness",
    ),
    archival=ArchivalPolicy(
        must_irreversibly_destroy=(
            "expired_contact_PII_beyond_suppression",
            "credentials",
        ),
        must_archive=(
            "consent_receipts",
            "suppression_records",
            "delivery_proofs",
        ),
        typical_windows={"raw_leads": "30-90d", "consent": "3-7y"},
        storage_tier="hot+warm+cold/WORM",
    ),
)

CONTENT_PIPELINE = KProfile(
    name="content-pipeline",
    seed="LSD",
    hard_constraints=(
        "source_provenance",
        "audit_before_publish",
        "publish_cutoff",
        "voice_gate",
        "antihallucination_verified",
    ),
    soft_weights=_weights("c_derive", "c_find", "c_drift"),
    team_composition={
        "T_human": "med",
        "T_agent_internal": "high",
        "T_agent_external": "low",
    },
    failure_priors=(
        "hallucinated_citations",
        "voice_drift_across_runs",
        "stale_source_pool_starvation",
        "publish_pipeline_drift_post_refactor",
    ),
    observability=(
        "per_article_audit_score",
        "voice_gate_pass_rate",
        "source_freshness_distribution",
        "cost_per_published_unit",
    ),
    archival=ArchivalPolicy(
        must_irreversibly_destroy=(
            "prompt_logs_with_PII_post_review",
            "temp_renders",
            "embedded_secrets",
        ),
        must_archive=(
            "published_assets",
            "rights",
            "approvals",
            "source_versions",
        ),
        typical_windows={"temp": "7-30d", "rights": "contract+dispute_window"},
        storage_tier="hot+warm/cold; WORM if regulated",
    ),
)

PRODUCT_MARKETING = KProfile(
    name="product-marketing",
    seed="BrandB",
    hard_constraints=(
        "catalog_truth",
        "spend_ROAS_guardrails",
        "attribution_window_declared",
        "consent_tracked",
    ),
    soft_weights=_weights("c_money", "c_drift", "c_modify"),
    team_composition={
        "T_human": "med",
        "T_agent_internal": "high",
        "T_agent_external": "high",
    },
    failure_priors=(
        "catalog_drift_from_source_of_truth",
        "spend_overshoot_without_kill_switch",
        "attribution_window_silent_change",
        "creative_inventory_starvation",
    ),
    observability=(
        "daily_spend_vs_cap",
        "ROAS_by_adset",
        "catalog_diff_alerts",
        "creative_freshness_index",
    ),
    archival=ArchivalPolicy(
        must_irreversibly_destroy=(
            "raw_events_after_aggregation",
            "expired_leads",
        ),
        must_archive=(
            "consent",
            "campaign_attribution",
            "experiment_decisions",
        ),
        typical_windows={
            "raw": "30-180d",
            "aggregates": "13-25mo",
            "consent": "3-7y",
        },
        storage_tier="hot+warm+cold",
    ),
)

PRODUCT_SAAS = KProfile(
    name="product-saas",
    seed="UniversityC",
    hard_constraints=(
        "RBAC_PII_isolation",
        "schema_migration_safety",
        "output_correctness",
        "session_recovery_safe",
    ),
    soft_weights=_weights("c_modify", "c_loss", "c_find"),
    team_composition={
        "T_human": "high",
        "T_agent_internal": "med",
        "T_agent_external": "med",
    },
    failure_priors=(
        "RLS_leak_via_role_misconfig",
        "irreversible_migration_in_prod",
        "auth_session_regression",
        "silent_KPI_math_drift",
    ),
    observability=(
        "RBAC_audit_per_role",
        "migration_dry_run_diff",
        "session_health",
        "KPI_metamorphic_oracle",
    ),
    archival=ArchivalPolicy(
        must_irreversibly_destroy=(
            "deleted_account_PII_post_grace",
            "secrets",
            "PCI_excess",
            "raw_debug_logs",
        ),
        must_archive=(
            "ledgers",
            "invoices",
            "audit_trails",
            "versioned_configs",
        ),
        typical_windows={
            "account_grace": "7-30d",
            "backups": "30-90d",
            "financial": "7y",
        },
        storage_tier="hot DB+warm logs+cold backups+WORM audit",
    ),
)

RESEARCH_MEMORY = KProfile(
    name="research-memory",
    seed="Personal Twin",
    hard_constraints=(
        "provenance_and_link_integrity",
        "memory_isolation_and_consent",
        "reversible_or_append_only_updates",
        "no_cross_project_leak",
    ),
    soft_weights=_weights("c_find", "c_storage", "c_derive"),
    team_composition={
        "T_human": "high",
        "T_agent_internal": "high",
        "T_agent_external": "low",
    },
    failure_priors=(
        "memory_pollution_across_contexts",
        "dead_links_after_source_move",
        "embedding_drift_after_model_swap",
        "consent_scope_creep",
    ),
    observability=(
        "link_integrity_scan",
        "consent_scope_audit",
        "embedding_version_pinning",
        "retrieval_quality_eval",
    ),
    archival=ArchivalPolicy(
        must_irreversibly_destroy=(
            "raw_PII_without_consent",
            "sensitive_prompts",
            "embeddings_retaining_sensitive_source",
        ),
        must_archive=(
            "dataset_cards",
            "consent_and_provenance",
            "reproducibility_manifests",
        ),
        typical_windows={
            "sensitive": "project+30-90d",
            "manifests": "3-7y",
        },
        storage_tier="hot+warm feature store+restricted WORM",
    ),
)

AUDIT_PIPELINE = KProfile(
    name="audit-pipeline",
    seed="DeskD Engine",
    hard_constraints=(
        "immutable_source_retention",
        "append_only_audit_log",
        "reviewer_signoff",
        "chain_of_custody_preserved",
    ),
    soft_weights=_weights("c_loss", "c_find", "c_derive"),
    team_composition={
        "T_human": "high",
        "T_agent_internal": "high",
        "T_agent_external": "low",
    },
    failure_priors=(
        "mutation_of_source_after_intake",
        "audit_log_gap",
        "reviewer_bypass",
        "stale_authoritative_archive",
    ),
    observability=(
        "WORM_verification",
        "audit_log_continuity",
        "signoff_coverage",
        "fingerprint_drift_alerts",
    ),
    archival=ArchivalPolicy(
        must_irreversibly_destroy=("convenience_copies_after_authoritative_archive_plus_retention_expiry",),
        must_archive=(
            "audit_logs",
            "workpapers",
            "access_logs",
            "chain_of_custody",
        ),
        typical_windows={
            "primary": "7y_under_SEC_style",
            "destruction": "only_post_hold_release",
        },
        storage_tier="WORM-first",
    ),
)

INTEL_PIPELINE = KProfile(
    name="intel-pipeline",
    seed="tenant-a-intel",
    hard_constraints=(
        "fresh_data_by_cutoff",
        "source_timestamp_dedupe",
        "distribution_SLA",
        "lawful_basis_for_collection",
    ),
    soft_weights=_weights("c_drift", "c_find", "c_derive"),
    team_composition={
        "T_human": "low-to-med",
        "T_agent_internal": "high",
        "T_agent_external": "high",
    },
    failure_priors=(
        "stale_indicator_in_live_distribution",
        "credential_leak_via_scraped_pages",
        "dedupe_collision_from_normalized_keys",
        "SLA_breach_under_source_outage",
    ),
    observability=(
        "source_freshness_per_feed",
        "dedupe_collision_rate",
        "distribution_lag_p95",
        "credential_scan_alerts",
    ),
    archival=ArchivalPolicy(
        must_irreversibly_destroy=(
            "live_credentials",
            "raw_scraped_PII_without_basis",
            "obsolete_high_risk_indicators",
        ),
        must_archive=(
            "source_provenance",
            "analytic_reports",
            "chain_of_custody",
            "sanitized_indicators",
        ),
        typical_windows={
            "raw": "30-180d",
            "reports": "1-7y",
            "secrets": "immediate_rotation",
        },
        storage_tier="hot secure enclave + warm graph + cold/WORM chain-of-custody",
    ),
)


# ---- Registry ---------------------------------------------------------------

PROFILES: dict[KClass, KProfile] = {
    p.name: p
    for p in (
        OUTBOUND_PIPELINE,
        CONTENT_PIPELINE,
        PRODUCT_MARKETING,
        PRODUCT_SAAS,
        RESEARCH_MEMORY,
        AUDIT_PIPELINE,
        INTEL_PIPELINE,
    )
}

H_K: dict[KClass, tuple[str, ...]] = {k: p.hard_constraints for k, p in PROFILES.items()}
W_K: dict[KClass, dict[CoreAxis, float]] = {k: p.soft_weights for k, p in PROFILES.items()}
T_K: dict[KClass, dict[str, str]] = {k: p.team_composition for k, p in PROFILES.items()}
F_K: dict[KClass, tuple[str, ...]] = {k: p.failure_priors for k, p in PROFILES.items()}
E_K: dict[KClass, tuple[str, ...]] = {k: p.observability for k, p in PROFILES.items()}


def get_profile(name: KClass) -> KProfile:
    return PROFILES[name]
