"""Folder-as-contract manifest schema (IC3).

Required fields per A_STAR_v0.md §3:
  scope, exclusions, allowed_artifact_types, owner, lifecycle_status,
  required_metadata, outbound_relations, review_cadence

Plus retention class (IC2, §3) so a single manifest file satisfies both
hard integrity constraints for its folder.
"""

# A folder is considered to have a manifest if any of these files exist at its root.
MANIFEST_FILE_NAMES: tuple[str, ...] = (
    ".manifest.yaml",
    ".manifest.yml",
    ".manifest.json",
    "MANIFEST.yaml",
    "MANIFEST.yml",
    "MANIFEST.json",
)


# JSON Schema (Draft 2020-12) for the folder-as-contract manifest.
MANIFEST_SCHEMA: dict = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://p0p/architecture-as-function/a_star/manifest.schema.json",
    "title": "A* Folder Manifest",
    "description": "Folder-as-contract manifest. Satisfies IC2 (declared retention) + IC3 (manifest consistency).",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "scope",
        "exclusions",
        "allowed_artifact_types",
        "owner",
        "lifecycle_status",
        "required_metadata",
        "outbound_relations",
        "review_cadence",
        "retention",
    ],
    "properties": {
        "scope": {
            "type": "string",
            "minLength": 8,
            "description": "Single sentence: what this folder is for and what bounds it.",
        },
        "exclusions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "What does NOT belong here. Empty array allowed if folder is unbounded.",
        },
        "allowed_artifact_types": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string"},
            "description": "Concrete artifact categories (code, dataset, document, secret, etc.).",
        },
        "owner": {
            "type": "string",
            "minLength": 1,
            "description": "Human or team owner of this folder's contract.",
        },
        "lifecycle_status": {
            "type": "string",
            "enum": ["explore", "bootstrap", "production", "scale", "archive"],
            "description": "Matches A* L parameter (§1).",
        },
        "required_metadata": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Metadata fields required on every artifact in this folder.",
        },
        "outbound_relations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["target", "type"],
                "additionalProperties": False,
                "properties": {
                    "target": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": [
                            "depends_on",
                            "derived_from",
                            "supersedes",
                            "links_to",
                            "owned_by",
                        ],
                    },
                    "note": {"type": "string"},
                },
            },
            "description": "Typed graph edges this folder declares to other folders/systems.",
        },
        "review_cadence": {
            "type": "string",
            "pattern": "^(daily|weekly|monthly|quarterly|annually|on_change|never)$",
            "description": "How often the manifest must be re-verified.",
        },
        "retention": {
            "type": "object",
            "required": ["class", "policy"],
            "additionalProperties": False,
            "properties": {
                "class": {
                    "type": "string",
                    "enum": ["active", "archived", "scheduled_for_destruction", "destroyed"],
                },
                "policy": {
                    "type": "string",
                    "enum": ["none", "soft", "hard", "sanitize"],
                },
                "window": {
                    "type": "string",
                    "description": "Human-readable retention window (e.g. '7y', '30-90d').",
                },
                "legal_basis": {"type": "string"},
                "destruction_deadline": {
                    "type": "string",
                    "format": "date",
                    "description": "Required when class=scheduled_for_destruction.",
                },
            },
        },
        "manifest_version": {
            "type": "string",
            "default": "1",
            "description": "Manifest schema version this file targets.",
        },
        "source_of_truth": {
            "type": "boolean",
            "description": "True if this folder holds the canonical record (IC1).",
        },
        "k_class": {
            "type": "string",
            "description": "Optional: K-class this folder belongs to (e.g. outbound-pipeline).",
        },
    },
    "allOf": [
        {
            "if": {
                "properties": {"retention": {"properties": {"class": {"const": "scheduled_for_destruction"}}}},
                "required": ["retention"],
            },
            "then": {
                "properties": {
                    "retention": {"required": ["destruction_deadline"]},
                },
            },
        },
    ],
}
