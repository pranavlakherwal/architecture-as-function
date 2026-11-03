# Category-Aware Deletion Makes A* Integrity Safer

## Executive Summary

- **Reject Universal Reversibility**: GDPR Article 17 requires erasure when personal data is no longer necessary, consent is withdrawn, data is unlawfully processed, or erasure is legally required, while Article 17(3) preserves exceptions for legal obligations, public-interest archiving, research, statistics, and legal claims GDPR, EUR-Lex [31] -> A* should not require every deletion to be reversible.
- **Use A Declared Lifecycle State**: Records standards converge on declared retention and disposition: DoD 5015.02 requires records to be created, maintained, used, disposed, and preserved under records schedules DoD 5015.02 [18], and MoReq2010 requires each record to have a disposal schedule that says how long it is retained and whether it is destroyed or transferred MoReq2010 Executive Summary [112] -> Make retention class and destruction policy first-class hard constraints.
- **Certificate Beats Archive For Some Data**: NIST SP 800-88 Rev. 2 defines **Clear**, **Purge**, and **Destroy**, and includes verification and a Certificate of Sanitization model NIST SP 800-88 Rev. 2 [20] -> For secrets, expired consent, payment account data, and media leaving control, A* should emit a destruction certificate rather than a recoverable archive.
- **Payment Data Must Shrink Over Time**: PCI DSS v4.0.1 Requirement 3.2.1 requires account data storage to be kept to a minimum, retention time limited to legal/regulatory/business need, secure deletion or rendering unrecoverable when no longer needed, and verification at least once every **three months** PCI DSS v4.0.1 [106] -> Payment artifacts should default to minimization, tokenization, and scheduled irreversible deletion.
- **Financial Records Are The Counterexample**: SEC Rule 17 CFR 210.2-06 requires audit and review records to be retained for **seven years** after the audit or review concludes 17 CFR 210.2-06 [41]; the SEC final rule says this retention discourages destruction of relevant records SEC Final Rule 33-8180 [54] -> Audit and financial evidence should default to WORM archive until retention and legal holds expire.
- **Soft Delete Is A Temporary State, Not A Policy**: KurrentDB/EventStore supports soft delete and hard delete, with hard delete implemented by appending a tombstone event Kurrent Event Streams [85]; Google Cloud Storage soft delete defaults to **seven days** and then permanent deletion follows Google Cloud Soft Delete [99] -> A* should treat soft delete as scheduled-for-destruction, not final erasure.
- **Tombstones Preserve Convergence But Create Residue**: Kafka uses tombstone records with null payloads for compacted-topic deletes and removes them after `delete.retention.ms` Kafka Log Compaction [8]; CRDT designs use tombstones to prevent deleted elements from reappearing, but they create metadata overhead CRDT Study [88] -> A* should require tombstone garbage collection windows and lag-aware consumers.
- **Always-Reversible Archives Expand Breach Surface**: GitHub documents that secret scanning scans the entire Git history of all branches for hardcoded credentials GitHub Secret Scanning [80], and Carlini et al. show that training examples can be extracted from large language models Extracting Training Data From Large Language Models [78] -> Secrets, PII-heavy prompts, and training corpora need purge or irreversible de-identification, not indefinite recovery.
- **Recommended Constraint**: Adopt option (d) with option (b) as the transition rule: every artifact must declare a retention class and destruction policy, and every destructive operation must produce either a recoverable archive or a verifiable destruction certificate consistent with artifact category -> This is precise enough for Z3 and avoids both illegal archives and unaudited deletion.

## Decision: Destruction Is Sometimes The Integrity-Preserving Choice

The defensible policy is: **reversibility is the default for artifacts whose integrity value is evidentiary, operational, or historical; irreversible deletion is mandatory or preferred for artifacts whose continued recoverability creates legal, security, or privacy risk after the retention basis expires**. That means the original constraint, "no destructive operation can be performed without a recoverable archive," is too strong and sometimes wrong.

The better constraint is lifecycle-based. A valid A* architecture must declare, for every artifact, a retention class, destruction policy, retention trigger, and proof obligation. Destruction is not an integrity failure when it is authorized, scheduled, policy-consistent, and evidenced.

**Case study: GDPR erasure versus SOX retention.** A SaaS account-deletion request and an audit workpaper deletion request look similar at the UI layer, but they should compile to opposite architectural outcomes. GDPR Article 17 says erasure is required in several cases, including when data is no longer necessary or consent is withdrawn, subject to exceptions GDPR, EUR-Lex [31]. By contrast, 17 CFR 210.2-06 requires audit and review records to be retained for seven years 17 CFR 210.2-06 [41]. A universal archive rule would violate the first case; a universal hard-delete rule would violate the second.

The integrity principle is therefore not "always recover." It is **"never mutate lifecycle state without a declared lawful retention/destruction policy and evidence of the outcome."**

## Legal And Standards Survey: Where Destruction Is Required Or Preferred

| Regime or standard | What it says about archive versus destruction | A* design implication |
| --- | --- | --- |
| GDPR Article 17 and Article 5 | Article 17 creates a right to erasure; Article 5(1)(e) requires storage limitation; Article 17(3) preserves exceptions for legal obligation, public interest, research/statistics, and legal claims GDPR, EUR-Lex [31] | PII cannot default to indefinite reversible archive. It needs a legal basis, retention deadline, and erasure workflow. |
| GDPR anonymization and pseudonymization | Recital 26 excludes truly anonymous information from data-protection principles, but pseudonymized data remains personal data if re-identification is possible GDPR, EUR-Lex [31]; ICO treats anonymisation as outside personal-data scope only when individuals are not identifiable ICO Anonymisation [32] | A* may preserve aggregates if anonymization is irreversible; pseudonymization is a safeguard, not deletion. |
| Schrems II and EDPB supplementary measures | Schrems II is a transfer-risk doctrine, not an erasure rule. EDPB Recommendations 01/2020 require exporters to assess third-country law and adopt supplementary measures such as encryption or pseudonymization where needed EDPB Recommendations 01/2020 [34] | Reversible archives in third countries must be treated as live regulated personal data unless anonymized or otherwise protected. |
| CCPA/CPRA | California consumers can request deletion of personal information collected from them; businesses must direct service providers to delete, subject to exceptions such as transactions, security, legal obligations, and legal claims California AG CCPA [26], Cal. Civ. Code 1798.105 [36] | Consumer data needs request verification, exception handling, downstream deletion propagation, and suppression records. |
| HIPAA | HHS says covered entities must use reasonable safeguards when disposing of PHI and disposal methods should make PHI unreadable or indecipherable, while HIPAA does not mandate one disposal method HHS PHI Disposal FAQ [28] | PHI artifacts need secure disposal and documented safeguards; medical-record retention windows often come from state or sector rules, not a universal HIPAA archive rule. |
| PCI DSS v3.2.1 and v4.x | PCI DSS v4.0.1 Requirement 3.2.1 requires account data storage minimization, retention limits, secure deletion or rendering unrecoverable when no longer needed, and verification at least once every three months PCI DSS v4.0.1 [106] | Cardholder data should be tokenized, minimized, and purged on a schedule. Sensitive authentication data should not be archived after authorization. |
| SOX and SEC audit retention | 17 CFR 210.2-06 requires audit and review records to be retained for seven years; the SEC final rule frames retention as a way to discourage destruction and preserve relevant audit evidence 17 CFR 210.2-06 [41], SEC Final Rule 33-8180 [54] | Financial/audit evidence should default to WORM or immutable archive until retention and holds expire. |
| ISO 15489 and ISO disposition guidance | ISO 15489-1 covers creation, capture, and management of records over time ISO 15489-1:2016 [45]. ISO/TS 7538:2024 addresses retention periods, disposition processes and authorities, and destruction requirements ISO Disposition [16] | Records need authorized disposition, not ad hoc delete. |
| DoD 5015.02 | DoD records must be managed in all media, and DoD records programs include creation, maintenance, use, disposal, and preservation DoD 5015.02 [18] | A* should distinguish records from non-record convenience copies and require schedule-driven disposition. |
| MoReq2010 | MoReq2010 requires each record to have a disposal schedule that states retention duration and whether the record is destroyed or transferred; it also supports disposal holds and residual records MoReq2010 Executive Summary [112] | Deletion can be legitimate if a residual proof record remains. |
| OAIS / ISO 14721 | OAIS defines an archive responsible for preserving information for a Designated Community and requires documented policies; the public CCSDS model warns against ad hoc deletion and permits deletion only under an approved strategy OAIS Reference Model [114] | Preservation systems can dispose of information, but only through approved strategy and preservation metadata. |
| PREMIS | PREMIS preservation-event vocabulary includes appraisal, deaccession, deletion, redaction, and other preservation events PREMIS Events Vocabulary [100] | A* should log deletion as a preservation event, not as silent absence. |
| NIST SP 800-88 Rev. 2 | NIST defines Clear, Purge, and Destroy, with verification and certificate-of-sanitization guidance NIST SP 800-88 Rev. 2 [20] | Destructive operations need method selection and proof, especially for media leaving control. |

The legal pattern is consistent: **archival is required for evidence, rights, continuity, and regulated records; destruction is required or preferred when data has no continuing legal basis, creates special security risk, or exceeds minimization rules**.

**Case study: PCI account data.** A payment system that archives full PANs, CVVs, and authorization traces to preserve reversibility is backwards. PCI DSS pushes the architecture toward less data, shorter retention, and recurring verification that excess account data is securely deleted or unrecoverable PCI DSS v4.0.1 [106]. The integrity-preserving design is tokenization plus signed disposal logs, not full recovery.

## Engineering Patterns: What Reversibility Each Pattern Preserves

| Pattern | Reversibility preserved | Costs imposed | Prevents | Does not prevent | Key citations |
| --- | --- | --- | --- | --- | --- |
| Soft delete flag | Application-level undo while the row remains present but hidden | c_storage increases; c_modify increases because every query needs filters; c_derive risk if deleted rows leak into analytics | Accidental user deletion | Legal erasure failure if data remains recoverable; query bugs | Kurrent Event Streams [85], Google Cloud Soft Delete [99] |
| Hard delete | No object-level recovery unless backups or replicas retain it | c_modify for cascades and referential cleanup; lower c_storage over time | Residual live-data exposure | Backup residue; audit loss if done before retention | Kurrent Event Streams [85] |
| Tombstones | Delete intent remains observable until compaction or GC | c_storage for markers; c_modify for compaction; c_derive if consumers replay tombstones | Resurrection in distributed systems; state reconstruction errors | Tombstone bloat; lagging consumers missing deletes after retention | Kafka Log Compaction [8], CRDT Study [88] |
| CRDT tombstone garbage collection | Convergence is preserved until all replicas have observed delete | c_storage and metadata overhead until causal stability; c_modify for GC coordination | Reappearance of removed elements in eventually consistent replicas | Unsafe GC if replicas are offline; unbounded metadata if GC absent | CRDT Study [88] |
| Kafka log compaction | Latest value per key and recent uncompacted head remain recoverable | c_modify from background cleaning; c_storage lower than full log; c_derive from replay | Unbounded update history; inability to rebuild latest state | Historical audit loss; tombstone expiry before lagging consumers read it | Kafka Log Compaction [8] |
| ClickHouse TTL | Data can be moved, rolled up, or deleted by time policy | c_storage decreases; c_money decreases via cold tiers; c_modify from merges; c_derive if rollups replace raw rows | Runaway observability/analytics storage | Immediate erasure guarantee, because deletion occurs during merges | ClickHouse TTL [83] |
| PostgreSQL VACUUM | MVCC preserves old row versions temporarily for transactions; VACUUM later reclaims dead tuples | c_modify from vacuum work; c_storage if dead tuples accumulate | Table bloat and transaction ID wraparound | Legal erasure by itself; backup residue | PostgreSQL Routine Vacuuming [84] |
| Event sourcing with snapshot-then-discard | Current state remains recoverable from snapshot; old event history may be discarded by retention policy | c_storage lower than full event log; c_derive lower for restore; c_modify for snapshot/version logic | Infinite replay cost; old-event privacy exposure | Full forensic replay after discard; legal audit if event log was required evidence | Kurrent Event Streams [85], Kafka Log Compaction [8] |
| Restic forget and prune | `forget` removes snapshot metadata; data remains until `prune`; `--dry-run` previews removal | c_modify from repository scan/repack; c_storage decreases after prune; c_money decreases with reclaimed storage | Backup sprawl; accidental policy application via dry run | Recovery after prune; stale restore testing | Restic Forget [1] |
| ZFS and Btrfs snapshots | Point-in-time filesystem state; ZFS holds can prevent snapshot destruction | c_storage grows as changed blocks are retained; c_modify for snapshot/hold management | Accidental rollback need; ransomware or operator error | Secret/PII residue; deletion blocked by dependent clones or active root snapshot | Oracle ZFS Snapshots [95], Oracle Btrfs Snapshot Deletion [96] |
| S3 Object Lock and Glacier Vault Lock | WORM archive prevents deletion or overwrite for a fixed period or legal hold | c_storage and c_money persist until lock expires; c_modify intentionally constrained | Ransomware, insider deletion, evidence tampering | Privacy erasure during lock unless exception applies; wrong retention cannot be shortened in compliance mode | S3 Object Lock [5], Glacier Vault Lock [98] |

**Case study: Kafka compacted topics.** Kafka compaction preserves the latest value for each key and uses null-payload tombstones to express deletion Kafka Log Compaction [8]. This is an excellent architecture for restoring current state, but it is not a full historical archive and not a guaranteed privacy erasure mechanism until compaction and tombstone retention complete.

**Case study: Restic backups.** Restic deliberately separates `forget` from `prune`: the first removes snapshot references, the second reclaims unreferenced data Restic Forget [1]. That distinction maps directly into A*: a destructive operation may first enter scheduled-for-destruction, then destroyed only after the proof step finishes.

## Failure Modes Of Always-Reversible Archival

| Failure mode | Security, cost, or legal argument | Evidence | A* implication |
| --- | --- | --- | --- |
| Tombstone bloat | Cost and correctness | Kafka tombstones persist until `delete.retention.ms`; CRDT tombstones preserve delete knowledge but add metadata Kafka Log Compaction [8], CRDT Study [88] | Require tombstone retention windows, lag bounds, and GC proof. |
| Backup residue after erasure | Legal | GDPR erasure and storage limitation conflict with indefinite recoverable backup copies GDPR, EUR-Lex [31]; ICO right-to-erasure guidance treats backup deletion as an operational obligation, not an excuse to keep using erased data ICO Right to Erasure [48] | Backups may be time-limited and quarantined; restores must reapply delete journals. |
| Cold-storage cost explosion | Cost | ClickHouse TTL exists to move, roll up, or delete older data for storage efficiency ClickHouse TTL [83]; restic states backup space is finite and supports retention policies Restic Forget [1] | Treat c_storage and c_money as soft objectives, but not a license to delete regulated evidence early. |
| False recoverability | Security and operations | NIST requires verification and certificate evidence for sanitization outcomes NIST SP 800-88 Rev. 2 [20]; restic requires prune mechanics to actually remove unreferenced data Restic Forget [1] | "Archived" must mean tested, indexed, decryptable, and restorable within an RTO, not merely stored. |
| Secret leakage through history | Security | GitHub secret scanning scans entire Git history on all branches for hardcoded credentials GitHub Secret Scanning [80] | Secrets should be rotated and purged; source history should not be treated as harmless archive. |
| Message-retention surprise | Legal and privacy | Slack says free workspaces can choose deletion after **90 days** or keeping messages and files, including edits, for a year Slack Privacy FAQ [79] | Collaboration archives need explicit retention settings and operator-visible consequences. |
| Training-data memorization | Security and privacy | Carlini et al. demonstrate extraction attacks that recover individual training examples from large language models Extracting Training Data From Large Language Models [78] | Research memory and model training corpora need deletion, de-identification, or exclusion paths, not only archival. |

The security argument is about attack surface: if credentials, PII, or training examples remain recoverable, compromise of the archive becomes compromise of the data. The cost argument is about storage, compaction, replay, and operational complexity. The legal argument is about purpose limitation, storage limitation, retention schedules, erasure rights, and litigation holds.

**Case study: LLM training data.** The Carlini paper shows that model behavior can reveal memorized training examples Extracting Training Data From Large Language Models [78]. For A*, this means deleting a raw dataset after training is not enough if the trained artifact itself can reproduce sensitive examples; the destruction policy must cover derived artifacts such as embeddings, checkpoints, caches, and fine-tuned weights.

## Artifact Typology: Default Policy By Data Class

| Artifact category | Default reversibility policy | A* integrity constraint to emit | K classes where it dominates |
| --- | --- | --- | --- |
| Secrets, credentials, keys, tokens | Must be irreversible after rotation or exposure; preserve only salted hash/fingerprint and rotation evidence | `requires(policy in {hard, sanitize})`, `forbid(recoverable_plaintext_archive)`, `requires(destruction_certificate or rotation_certificate)` | product-saas, outbound-pipeline, intel-pipeline, audit-pipeline |
| PII, PHI, payment account data, consent-bound identifiers | Parameterized by jurisdiction, consent, purpose, and legal hold; irreversible when erasure is valid and no exception applies | `requires(legal_basis)`, `requires(retention_until)`, `if erasure_valid then hard_or_anonymize_plus_certificate`, `pseudonymized != anonymized` | product-saas, product-marketing, outbound-pipeline, research-memory, intel-pipeline |
| Raw event, behavioral, telemetry, and observability logs | Reversible only for short operational window; then roll up, anonymize, or delete | `soft_delete_allowed_until(window_end)`, `requires(ttl or compaction)`, `requires(delete_journal_for_restore)` | product-saas, product-marketing, content-pipeline, intel-pipeline |
| Derived artifacts, caches, embeddings, features, indexes, model checkpoints | Usually irreversible or recomputable; archive only if needed for reproducibility or audit | `if derivation_contains_sensitive_source then inherits_source_retention`, `if recomputable then prefer_destroy`, `if audit_model then archive_manifest` | research-memory, content-pipeline, product-marketing, intel-pipeline |
| Source code, build artifacts, configs, design docs | Must be reversible for integrity and rollback, except embedded secrets must be purged/rotated | `archive_signed_version`, `scan_for_secret_residue`, `separate_secret_material_from_repo_history` | product-saas, content-pipeline, research-memory |
| User-generated content, messages, uploads, collaboration artifacts | Parameterized by user deletion rights, workspace retention settings, contractual retention, and legal hold | `requires(owner_policy and jurisdiction)`, `if deletion_request_valid then remove_live_and_schedule_backup_expiry`, `hold_overrides_delete_until_release` | content-pipeline, product-saas, outbound-pipeline, research-memory |
| Audit, financial, legal, and provenance records | Must be reversible and tamper-evident until retention window and holds expire; destroy only after authorized disposition | `requires(WORM or immutable_archive)`, `forbid_destroy_before(retention_until or hold_release)`, `destroy_requires_residual_record` | audit-pipeline, product-saas, outbound-pipeline, intel-pipeline |

The typology makes reversibility a property of the artifact, not an operation-wide moral rule. A* should emit different constraints for a leaked API key, a SOX audit workpaper, a Kafka tombstone, and a ClickHouse behavioral log shard.

## Revised Integrity Constraint #2: Recommended Wording

| Option | Verdict | Reason |
| --- | --- | --- |
| (a) All destructive operations must be reversible | Reject | Violates GDPR/CCPA erasure, PCI minimization, secret handling, and NIST sanitization use cases. |
| (b) Every destructive operation must produce either a recoverable archive or a verifiable destruction certificate | Keep as transition invariant | Good operation-level rule, but insufficient unless artifact categories decide which outcome is legal. |
| (c) Reversibility default; secret/PII/expired consent require irreversible deletion with certificate | Keep as category rule | Correct direction, but too narrow because audit records, payment data, research data, and legal holds also need explicit handling. |
| (d) Every artifact has declared retention class and destruction policy consistent with category | Recommend | Best matches records standards, preservation metadata, engineering lifecycle states, and Z3 compilation. |

**Recommended statement of integrity constraint #2:**

> **A* Integrity Constraint #2 - Declared Retention And Verifiable Disposition:** An architecture is valid only if every artifact has a declared retention class `{active, archived, scheduled_for_destruction, destroyed}` and a declared destruction policy `{none, soft, hard, sanitize}` consistent with its artifact category, legal basis, retention schedule, and K class. Every destructive transition must produce either (1) a recoverable, integrity-checked archive when retention requires reversibility, or (2) a verifiable destruction certificate/residual record when retention requires irreversible deletion. Soft deletion is never a terminal state; it must resolve to archive or verified destruction by a declared deadline.

This statement absorbs option (b) as the operation-level proof rule and option (c) as a category-specific specialization. It rejects option (a) because the literature shows that irreversible deletion is sometimes the correct integrity-preserving outcome.

## Default Archival Policy For The Seven K Classes

These windows are recommended A* defaults, not legal advice. They should be overridden by jurisdiction, contract, legal hold, regulator, customer policy, and sector rule.

| K class | Must be irreversibly destroyed | Must be archived | Typical default windows | Storage tier |
| --- | --- | --- | --- | --- |
| outbound-pipeline | Expired contact PII, unsubscribed targeting attributes beyond suppression minimum, credentials, old campaign payload caches | Consent receipts, suppression records, delivery proofs, template versions | Raw events **30-90 days**; consent/suppression **3-7 years** where needed for proof | Hot for active sends; warm for suppression; cold/WORM for consent evidence |
| content-pipeline | Prompt logs with PII after review window, temporary renders, caches, embedded secrets | Published assets, rights metadata, approvals, source versions | Temp artifacts **7-30 days**; published record lifecycle of content; rights records **contract term plus dispute window** | Hot for active production; warm/cold for source archives; WORM if regulated publication |
| product-marketing | Raw behavioral events after aggregation, expired leads, third-party enrichment without basis | Consent records, campaign attribution rollups, experiment decisions | Raw events **30-180 days**; aggregate analytics **13-25 months**; consent evidence **3-7 years** | Hot for current experiments; warm analytics; cold for proof records |
| product-saas | Deleted-account PII after grace/backup expiry, secrets, payment account data beyond PCI need, raw debug logs | Account ledgers, invoices, audit trails, security events, versioned configs | Account deletion grace **7-30 days**; backups **30-90 days**; financial records often **7 years** if SOX-like; security logs **1 year or policy-based** | Hot app DB; warm logs; cold backups; WORM for audit/financial evidence |
| research-memory | Raw PII datasets without consent, sensitive prompts, unapproved scraped corpora, derived embeddings that retain sensitive source | Dataset cards, consent/provenance records, reproducibility manifests, approved de-identified corpora | Raw sensitive data **project window plus 30-90 days**; manifests **3-7 years**; approved corpora per IRB/contract/license | Hot research workspace; warm feature store; cold manifest archive; restricted WORM for regulated studies |
| audit-pipeline | Convenience copies after authoritative archive exists and retention expires | Audit logs, financial workpapers, access logs, chain-of-custody records, destruction certificates | Audit/review records **7 years** under SEC rule when applicable; destruction only after hold release | WORM/immutable hot or warm for current audit; cold/glacier WORM for long retention |
| intel-pipeline | Live credentials, malware staging copies outside quarantine, raw scraped PII without basis, obsolete high-risk indicators with no retention need | Source provenance, analytic reports, chain of custody, sanitized indicators | Raw collection **30-180 days**; reports/provenance **1-7 years** depending mission; secrets immediate rotation and purge | Hot secure enclave; warm graph store; cold/WORM for chain-of-custody; quarantine for malware |

**Case study: audit-pipeline versus product-marketing.** In audit-pipeline, WORM storage is the right default because tamper resistance is the value. In product-marketing, indefinite WORM archives of behavioral events can be the wrong default because storage limitation, consent revocation, and breach surface dominate. The same `delete()` verb must compile to different architecture depending on K.

## Z3 Constraint Sketch For A*

A* should model destruction primarily as a **declarative retention schedule attached to each artifact**, with a **side-effect predicate on every mutation operation**. A pure operation-level hard constraint is too late: by the time deletion occurs, the architecture may already have replicated data into backups, indexes, embeddings, logs, or WORM stores that cannot satisfy erasure.

```python
# Sorts
Artifact, Operation, Time = DeclareSorts("Artifact Operation Time")
Category = EnumSort(
    "Category", ["secret", "pii", "phi", "payment", "raw_event", "derived", "source_doc", "ugc", "audit_record"]
)
RetentionClass = EnumSort("RetentionClass", ["active", "archived", "scheduled_for_destruction", "destroyed"])
DestructionPolicy = EnumSort("DestructionPolicy", ["none", "soft", "hard", "sanitize"])
StorageTier = EnumSort("StorageTier", ["hot", "warm", "cold", "glacier", "worm"])
KClass = EnumSort(
    "KClass",
    [
        "outbound_pipeline",
        "content_pipeline",
        "product_marketing",
        "product_saas",
        "research_memory",
        "audit_pipeline",
        "intel_pipeline",
    ],
)

cat = Function("cat", Artifact, Category)
kclass = Function("kclass", Artifact, KClass)
retention_class = Function("retention_class", Artifact, RetentionClass)
policy = Function("policy", Artifact, DestructionPolicy)
retention_until = Function("retention_until", Artifact, Time)
legal_hold = Function("legal_hold", Artifact, BoolSort())
erasure_valid = Function("erasure_valid", Artifact, BoolSort())
anonymized = Function("anonymized", Artifact, BoolSort())
pseudonymized = Function("pseudonymized", Artifact, BoolSort())
archive_exists = Function("archive_exists", Artifact, BoolSort())
archive_recoverable = Function("archive_recoverable", Artifact, BoolSort())
destruction_cert = Function("destruction_cert", Artifact, BoolSort())
residual_record = Function("residual_record", Artifact, BoolSort())
contains_plaintext_secret = Function("contains_plaintext_secret", Artifact, BoolSort())
destructive = Function("destructive", Operation, BoolSort())
target = Function("target", Operation, Artifact)
produces_archive = Function("produces_archive", Operation, BoolSort())
produces_cert = Function("produces_cert", Operation, BoolSort())
restore_reapplies_deletes = Function("restore_reapplies_deletes", Artifact, BoolSort())

# 1. Every artifact has declared lifecycle and policy.
ForAll([a], And(retention_class(a) != None, policy(a) != None, cat(a) != None, kclass(a) != None))

# 2. A destructive operation must prove either recoverability or verified destruction.
ForAll(
    [op],
    Implies(
        destructive(op),
        Or(
            And(produces_archive(op), archive_exists(target(op)), archive_recoverable(target(op))),
            And(produces_cert(op), destruction_cert(target(op)), residual_record(target(op))),
        ),
    ),
)

# 3. Secrets cannot have recoverable plaintext archives.
ForAll(
    [a], Implies(cat(a) == secret, And(policy(a) == sanitize, Not(contains_plaintext_secret(a)), destruction_cert(a)))
)

# 4. Valid erasure requests require hard delete, sanitization, or irreversible anonymization.
ForAll(
    [a],
    Implies(
        erasure_valid(a),
        And(Not(legal_hold(a)), Or(policy(a) == hard, policy(a) == sanitize, anonymized(a)), destruction_cert(a)),
    ),
)

# 5. Pseudonymization is not anonymization.
ForAll([a], Implies(pseudonymized(a), Not(anonymized(a))))

# 6. Audit records cannot be destroyed before retention expiry or hold release.
ForAll(
    [a],
    Implies(
        Or(cat(a) == audit_record, legal_hold(a)),
        And(retention_class(a) != destroyed, archive_exists(a), archive_recoverable(a)),
    ),
)

# 7. Soft delete must resolve by a deadline.
ForAll([a], Implies(policy(a) == soft, retention_class(a) == scheduled_for_destruction))

# 8. Restores must not resurrect erased data.
ForAll([a], Implies(erasure_valid(a), restore_reapplies_deletes(a)))
```

Soft objectives should optimize, after hard constraints are satisfied:

```python
minimize(c_storage + c_money + c_modify + c_derive)
minimize(privacy_risk + secret_residue + unbounded_tombstones)
maximize(recoverability_score for archive_required artifacts)
maximize(auditability_score for destroyed artifacts)
```

This encoding treats legal retention, erasure, holds, and sanitization as hard constraints. It treats storage and operational cost as soft objectives. It treats c_reverse residual as a diagnostic: irreversible deletion is not automatically bad, but unexplained or category-inconsistent irreversibility is invalid.

## Operator Experience: Explain Every Irreversibility Choice

If A* emits an architecture where some artifacts cannot be recovered, the operator needs a short, auditable explanation. NIST provides the model: sanitization should have method, verification, and certificate evidence NIST SP 800-88 Rev. 2 [20]. MoReq2010 provides the records-management model: destruction can leave a residual record proving correct disposal MoReq2010 Executive Summary [112]. PREMIS provides the preservation model: deletion, deaccession, redaction, and appraisal are lifecycle events PREMIS Events Vocabulary [100].

A* should emit this minimal explanation bundle for every irreversible choice:

| Field | Required content |
| --- | --- |
| Artifact identity | Artifact ID, category, K class, owner, system of record, derived copies known. |
| Policy basis | Legal basis, retention schedule, consent state, contract, regulatory rule, or security trigger. |
| Lifecycle transition | Previous state, new state, destruction policy, deadline, and whether soft delete is temporary. |
| Exception check | Legal hold, audit hold, transaction need, public-interest archive, research/statistical exception. |
| Mechanism | Hard delete, cryptographic erase, NIST Clear/Purge/Destroy, anonymization, redaction, TTL, compaction, prune. |
| Evidence | Archive pointer and restore test if reversible; destruction certificate, residual record, hashes, actor, timestamp, verifier if irreversible. |
| Backup and replica handling | Whether backups are purged, expired, quarantined, or protected by delete journal on restore. |
| Consequence notice | Plain-language warning: "After this deadline, A* cannot recover this artifact; only residual proof remains." |
| Human approval | Approver, policy version, ticket/request ID, and appeal/escalation route for high-risk destruction. |

The key UX rule is that the operator should never see irreversibility as an unexplained optimization. It should appear as a traceable policy decision: "This artifact is a rotated credential; reversible archive is forbidden; NIST purge plus rotation evidence is required." Or: "This artifact is a SOX audit record; irreversible deletion is forbidden until seven-year retention and legal holds expire."

## Synthesis

The major tension is not archive versus delete. It is **recoverability versus exposure**. Audit records, financial workpapers, source releases, and provenance logs derive integrity from tamper-resistant recovery. Secrets, expired-consent PII, raw behavioral exhaust, and payment account data often derive integrity from the opposite property: proof that the recoverable copy is gone.

Across the standards, three mechanisms recur. First, records-management systems require declared schedules and authorized disposition, as shown by ISO disposition guidance, DoD 5015.02, and MoReq2010 ISO Disposition [16], DoD 5015.02 [18], MoReq2010 Executive Summary [112]. Second, privacy and payment regimes require minimization, erasure, or secure deletion once purpose expires, as shown by GDPR, CCPA, HIPAA disposal guidance, and PCI DSS GDPR, EUR-Lex [31], California AG CCPA [26], HHS PHI Disposal FAQ [28], PCI DSS v4.0.1 [106]. Third, engineering systems implement deletion as staged state transitions: tombstone, compact, TTL merge, vacuum, forget, prune, lock, and destroy Kafka Log Compaction [8], ClickHouse TTL [83], PostgreSQL Routine Vacuuming [84], Restic Forget [1].

The non-obvious divergence is that WORM storage and right-to-erasure are both integrity tools, but for different artifact categories. S3 Object Lock and Glacier Vault Lock protect integrity by preventing deletion S3 Object Lock [5], Glacier Vault Lock [98]. NIST sanitization protects integrity by making recovery infeasible and proving it NIST SP 800-88 Rev. 2 [20]. A* must be able to emit both outcomes without treating one as a violation.

The final policy is therefore: **make reversibility category-dependent, make lifecycle declaration mandatory, make proof mandatory, and make soft delete temporary.** This preserves the useful spirit of the original hard constraint, which was to prevent silent destructive loss, while removing the false assumption that every integrity-preserving architecture must be able to recover everything forever.

## References

1. *Removing backup snapshots — restic 0.18.1-dev documentation*. https://restic.readthedocs.io/en/latest/060_forget.html
2. *Amazon S3 Object Lock*. https://www.amazon.com/s3/features/object-lock
3. *Object First | Backup Storage Solutions*. http://cdw.com/content/cdw/en/brand/object-first.html
4. *What Are Immutable Backups? Autonomous Ransomware Protection*. https://www.sentinelone.com/cybersecurity-101/cybersecurity/immutable-backups/
5. *Locking objects with Object Lock - Amazon Simple Storage Service*. https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html
6. *Manage data with TTL (Time-to-live) | ClickHouse Docs*. http://clickhouse.com/docs/guides/developer/ttl
7. *Event streams - Kurrent Docs*. http://docs.kurrent.io/server/v26.0/features/streams
8. *Kafka Log Compaction | Confluent Documentation*. https://docs.confluent.io/kafka/design/log_compaction.html
9. *Designing a Soft-Delete and Data Lifecycle System: Tombstones ...*. https://letsbuildsolutions.com/blog/system-design/designing-a-soft-delete-and-data-lifecycle-system/
10. *crdt-foundation-implementation/ (2) 2p-set/README.md ... - GitHub*. https://github.com/giteshsarvaiya/crdt-foundation-implementation/blob/main/(2)%202p-set/README.md
11. *Adopted on 16 January 2025 Guidelines - edpb.europa.eu*. http://edpb.europa.eu/system/files/2025-01/edpb_guidelines_202501_pseudonymisation_en.pdf
12. *Schrems II landmark ruling: A detailed analysis*. http://nortonrosefulbright.com/de-de/wissen/publications/ad5f304c/schrems-ii-landmark-ruling-a-detailed-analysis
13. *Guidelines | European Data Protection Board*. https://www.edpb.europa.eu/our-work-tools/our-documents/publication-type/guidelines_en
14. *GDPR EU-US Data Transfers: Schrems II Compliance Guide 2026 ...*. https://www.aigovhub.io/guides/gdpr-eu-us-data-transfers-post-schrems-ii-guide-2026
15. *Diritto all'oblio*. http://garanteprivacy.it/i-miei-diritti/diritti/oblio
16. *Disposition - committee.iso.org*. https://committee.iso.org/sites/tc46sc11/home/projects/published/disposition.html
17. *Records Maintenance and Release*. http://marquette.edu/mupd/documents/records_maintenance_and_release.pdf
18. *DoDI 5015.02, February 24, 2015, Incorporating Change 1 on ...*. https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/501502p.pdf
19. [[PDF] Regular Meeting of the Board of Directors Tuesday, March 26, 2024 ...](http://avta.com/downloads/meetings/bod/2024/03262024-agenda.pdf)
20. *SP 800-88 Rev. 2, Guidelines for Media Sanitization | CSRC*. https://csrc.nist.gov/pubs/sp/800/88/r2/final
21. *GDPR and Backups: How to Handle Deletion Requests in 2026*. http://probackup.io/blog/gdpr-and-backups-how-to-handle-deletion-requests
22. *CRDTs (Conflict-free Replicated Data Types) - Page 5 of 5*. https://www.onenoughtone.com/learn/crdts/5
23. *Orda*. http://github.com/orda-io
24. *Slack's GDPR Commitment | Legal*. https://slack.com/trust/compliance/gdpr
25. *Secret leakage risks - GitHub Docs*. https://docs.github.com/en/code-security/concepts/secret-security/secret-leakage-risks
26. *California Consumer Privacy Act (CCPA) | State of California ...*. https://www.oag.ca.gov/privacy/ccpa
27. *Optimize PCI Data Retention for Cardholder Security*. https://www.pcicompliance.com/pci-data-retention/
28. *Disposal of Protected Health Information - HHS.gov*. https://www.hhs.gov/hipaa/for-professionals/faq/disposal-of-protected-health-information/index.html
29. *Consumers' "Right to Delete" under US State Privacy Laws*. http://privacyworld.blog/2021/03/consumers-right-to-delete-under-us-state-privacy-laws
30. *Evervault PCI Compliance Documentation*. http://docs.evervault.com/compliance/pci-compliance
31. *Regulation - 2016/679 - EN - gdpr - EUR-Lex*. https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng/
32. *Anonymisation | ICO*. https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/anonymisation/
33. *Everything you need to know about the "Right to be forgotten"*. http://gdpr.eu/right-to-be-forgotten
34. *Recommendations 01/2020 on measures that supplement ... - Europa*. https://www.edpb.europa.eu/our-work-tools/our-documents/recommendations/recommendations-012020-measures-supplement-transfer_en
35. *Art. 17 GDPR Right to erasure (‘right to be forgotten’)*. https://gdpr-info.eu/art-17-gdpr/
36. *California Civil Code section 1798.105 (2025)*. https://california.public.law/codes/civil_code_section_1798.105
37. *Senate Standing Committee on Privacy, Digital Technologies ...*. http://calmatters.digitaldemocracy.org/hearings/278917
38. *http://cppa.ca.gov/announcements/2025/20250909.html*. http://cppa.ca.gov/announcements/2025/20250909.html
39. *California Approves Delete Act Regulations - cppa.ca.gov*. https://cppa.ca.gov/announcements/2025/20251113.html
40. *Versapay: Trust Center*. http://trust.versapay.com/
41. *17 CFR 210.2-06 -- Retention of audit and review records.*. https://www.ecfr.gov/current/title-17/chapter-II/part-210/subject-group-ECFR2f5dcb24c1c571e/section-210.2-06
42. *PCI Security Standards Council – Protect Payment Data with ...*. https://www.pcisecuritystandards.org/document_library/
43. *HIPAA and Privacy Laws | Texas Health and Human Services*. http://hhs.texas.gov/regulations/legal-information/hipaa-privacy-laws
44. *Security White Paper*. http://help.fiery.com/Security/en-us/45266125_Fiery_Security_WhitePaper_FS700_en-us.pdf
45. *ISO 15489-1:2016 - Information and documentation — Records ...*. https://www.iso.org/standard/62542.html
46. [[PDF] ED3 Eisen Duurzaam Digitaal Depot - Provincie Noord-Holland](http://noord-holland.nl/bestanden/pdf/Brochure_Eisen_Digitaal_Depot.pdf)
47. *Home | OAIS Reference Model (ISO 14721)*. http://www.oais.info/
48. *Page not found | ICO*. https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/right-to-erasure/
49. *Records Management Division*. http://princegeorgescountymd.gov/departments-offices/police/bureaus-police-stations/bureau-administration/records-management-division
50. *MoReq2010, Modular Requirements for Records Systems - Joinup*. https://interoperable-europe.ec.europa.eu/sites/default/files/inline-files/OS15(1).pdf
51. *Records Management | Douglas County, GA*. http://douglascountyga.gov/440/Records-Management
52. *Retention of Records Relevant to Audits and Reviews - SEC.gov*. http://sec.gov/rules-regulations/2003/01/retention-records-relevant-audits-reviews
53. *SOX Compliance Data Retention Requirements - pathlock.com*. https://pathlock.com/learn/sox-data-retention-requirements/
54. *Final Rule: Retention of Records Relevant to Audits and Reviews*. https://www.sec.gov/files/rules/final/33-8180.htm
55. *Securities and Exchange Commission (SEC) Rule 17a-4, SEC Rule ...*. http://learn.microsoft.com/en-us/compliance/regulatory/offering-sec-docs
56. *Consumer Disclosures*. http://northwoodtech.edu/about/safety-and-security/consumer-disclosures
57. *PCI DSS Data Destruction For Banks: 2025 Secure Disposal Guide*. https://datadestruction.com/pci-dss-financial-institutions-secure-data-destruction-requirements-in-2025/
58. *PCI-DSS-v4_0_1.pdf*. http://middlebury.edu/sites/default/files/2025-01/PCI-DSS-v4_0_1.pdf?fv=AKHVQBp6
59. *PCI DSS v4.0 | Risk Cognizance GRC*. http://riskcognizance.com/framework/pci-dss-v4.0
60. *What are the PCI DSS Data Retention and Disposal Requirements?*. https://pcidssguide.com/what-are-the-pci-dss-data-retention-and-disposal-requirements/
61. *Securing the Future of Payments: PCI SSC Publishes PCI Data Security Standard v4.0 - PCI Security Standards Council*. http://pcisecuritystandards.org/about_us/press_releases/securing-the-future-of-payments-pci-ssc-publishes-pci-data-security-standard-v4-0
62. *PREMIS: Preservation Metadata Maintenance Activity (Library ...*. https://www.loc.gov/standards/premis/
63. *The Electronic Digital Archive*. http://ibacz.eu/wp-content/uploads/2019/10/produktovy%CC%81-list_iba-eng_eda-1.pdf
64. *Using PREMIS with METS*. http://loc.gov/standards/premis/premis-mets.html
65. *PREMIS Data Dictionary for Preservation Metadata, Version 3.0*. https://www.loc.gov/standards/premis/v3/
66. *Fetched web page*. https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-88r2.pdf
67. *Managing data - ClickHouse Docs*. https://clickhouse.com/docs/observability/managing-data
68. *Privacy Policy | Mendral*. http://mendral.com/privacy
69. *Kafka Log Compaction*. http://docs.confluent.io/kafka/design/log_compaction.html
70. *How to Set Up Automatic Data Retention Policies in ClickHouse*. https://oneuptime.com/blog/post/2026-01-21-clickhouse-retention-policies/view
71. *How to Test Backups and Prove Restores - NinjaOne*. https://www.ninjaone.com/blog/how-to-test-backups-and-prove-restores/
72. *Windows Server Backup Software - MSP360*. http://msp360.com/backup/windows-server-backup-software
73. *Article 17 📖 GDPR. Right to erasure ('right to be forgotten')*. http://gdpr-text.com/read/article-17
74. *Right to erasure | ICO*. https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/right-to-erasure/?id=15
75. *Tempus | Secure IT Asset Disposition & Electronics Recycling*. http://4tempus.com/
76. *Strengthen Governance, Risk, and Compliance in Your ...*. http://azion.com/en/documentation/architectures/compliance/governance-risk-compliance
77. *Document Retention and Destruction Policy and Procedure*. http://nuvancehealth.org/sites/default/files/PDF%20Files/Compliance%20Pages/Policies%20and%20Procedures/Compliance%20Policies/Document%20Retention%20and%20Destruction%20Policy%20and%20Procedure.pdf
78. *Extracting Training Data from Large Language Models*. https://arxiv.org/abs/2012.07805
79. *Privacy FAQs | Legal | Slack*. https://slack.com/trust/privacy/privacy-faq
80. *About secret scanning - GitHub Docs*. https://docs.github.com/en/code-security/concepts/secret-security/about-secret-scanning
81. *Resources for compliance | Slack*. http://slack.com/trust/compliance
82. *API | GitGuardian documentation*. http://docs.gitguardian.com/platform/gitguardian-suite/api
83. *Overview of TTL​*. https://clickhouse.com/docs/guides/developer/ttl
84. *PostgreSQL: Documentation: 18: 24.1. Routine Vacuuming*. https://www.postgresql.org/docs/current/routine-vacuuming.html
85. *Event streams | Kurrent Docs*. https://docs.kurrent.io/server/v26.0/features/streams
86. *GitHub - ChinmayLokare/crdt-distributed-systems-project*. https://github.com/ChinmayLokare/crdt-distributed-systems-project
87. *v3.7.0 — Phase 5 Part 4: CRDT Vector-Clock ... - GitHub*. https://github.com/Jovancoding/Network-AI/discussions/44
88. *A comprehensive study of Convergent and Commutative ...*. http://db.cs.berkeley.edu/cs286/papers/crdt-tr2011.pdf
89. *Supersynergy/synapse: One file. Your AI's entire memory. ...*. http://github.com/Supersynergy/synapse
90. *Soft Delete, Hard Delete, and Tombstones: - LinkedIn*. https://www.linkedin.com/pulse/soft-delete-hard-tombstones-akash-gautam-mb1ic
91. *Efficient Soft-Delete Models Without Query Degradation in SQL ...*. https://www.c-sharpcorner.com/article/efficient-soft-delete-models-without-query-degradation-in-sql-server-a-practic/
92. *Cloud Storage | Google Cloud*. http://cloud.google.com/storage
93. *Backup and Restore*. http://pve.proxmox.com/pve-docs/chapter-vzdump.html
94. *Locking objects with Object Lock - Amazon Simple Storage Service*. https://www.amazon.com/AmazonS3/latest/userguide/object-lock.html
95. *Creating and Destroying ZFS Snapshots - Oracle*. https://docs.oracle.com/cd/E19253-01/819-5461/gbcya/index.html
96. *Deleting Snapshots of the root File System - docs.oracle.com*. https://docs.oracle.com/en/operating-systems/oracle-linux/9/btrfs/btrfs-DeletingSnapshotsoftherootFileSystem.html
97. *MSP360 Object Lock Feature Types*. http://help.msp360.com/cloudberry-backup/backup/about-backups/object-lock/feature-types
98. *Amazon Glacier Vault Lock*. https://docs.aws.amazon.com/amazonglacier/latest/dev/vault-lock.html
99. *Soft delete  |  Cloud Storage  |  Google Cloud Documentation*. https://cloud.google.com/storage/docs/soft-delete
100. *Preservation Events Controlled Vocabulary - Library of Congress*. https://www.loc.gov/standards/premis/v3/preservation-events.pdf
101. *Data Dictionary Only: PREMIS Data Dictionary for Preservation ...*. https://wiki.lib.sun.ac.za/images/c/c5/Premis-3-0-datadictionary-only.pdf
102. *PREMIS RECOMMENDATIONS - HathiTrust*. https://www.hathitrust.org/documents/hathitrust-premis-recommendations.pdf
103. *CIDOC Guidelines: Deaccession and Disposal Information Group*. http://cidoc.ics.forth.gr/docs/guidelines/guidedis.htm
104. *Configuration — PREMIS Event Service 1.0 documentation*. https://premis-event-service.readthedocs.io/en/latest/configuration.html
105. *Input & Output Logging*. http://openrouter.ai/docs/guides/features/input-output-logging
106. *Payment Card Industry Data Security Standard - Middlebury*. https://www.middlebury.edu/sites/default/files/2025-01/PCI-DSS-v4_0_1.pdf?fv=AKHVQBp6
107. *Partner Validation Report*. http://marketplace.oracle.com/media/86486017/other/Partner_Validation_Report_Aurus_STSGen2.pdf
108. *3.2.1—Account data storage is kept to a minimum through ...*. https://www.myctrl.tools/frameworks/pci-dss-v4/3-2-1
109. *PCI Security Standards Council – Protect Payment Data with ...*. https://www.pcisecuritystandards.org/standards/pci-dss/
110. *ISO 14721:2025 - Space Data System Practices — Reference ...*. https://www.iso.org/standard/87471.html
111. [[PDF] lgs-1-2022.pdf - New York State Archives |](http://archives.nysed.gov/sites/archives/files/lgs-1-2022.pdf)
112. *MoReq2010 - Executive Summary ENGLISH*. https://moreq.info/files/MoReq2010%20-%20Executive%20Summary%20EN.pdf
113. *RRSDAs - Archives and Records Management*. http://sfu.ca/archives/records-management/directory-of-university-records/RRSDA.html
114. *Fetched web page*. https://public.ccsds.org/Pubs/650x0m2.pdf
