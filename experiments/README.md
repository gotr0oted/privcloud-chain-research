# Baseline and ablation protocol (pre-results)

This file defines work to run against the actual PrivCloud-Chain source after it is available. No comparative baseline or ablation measurements have been generated. The supplied Verification Center run is a separate, single-run functional result.

## Shared controls

Use the same host, OS, container limits, API build, synthetic corpus, MinIO configuration, authentication policy, key-management setup, file-size distribution, network, and concurrency for each variant. Pin software versions and source commit. Warm each variant with 10 unmeasured requests; collect at least 30 independent repetitions per configuration. Randomize variant order. Report median and p95 latency with 95% bootstrap confidence intervals, operations/second, CPU/memory, bytes stored, and ledger/audit bytes per event. Preserve raw per-operation CSV files and the exact command/configuration.

## Three baselines

| ID | Variant | Controlled difference | What it tests |
|---|---|---|---|
| B1 | Centralized audit | Existing encryption, SHA-256, MinIO and application authorization; custody/access records in one SQL audit table; no Fabric | Conventional centralized audit overhead and administrator trust assumptions |
| B2 | Central append-only hash chain | Same as B1, with each audit row linked to the prior row by a SHA-256 chain; no Fabric | Detectability of modification in a single-admin log |
| B3 | Fabric registration-only | Same crypto, MinIO and API authorization; Fabric records registration/hash; access decisions remain only in the application database | Incremental effect of a permissioned ledger without on-chain access-decision records |
| P | Proposed full workflow | The documented PrivCloud-Chain implementation, including Fabric registration and grant/denial events | Full integrated workflow; treated as the proposed system, not a baseline |

Before running, confirm that each variant can be implemented without changing unrelated components. If the current source does not support a variant, document the adapter and keep the comparison qualified.

## Ablations

| ID | Disabled component | Primary outcomes |
|---|---|---|
| A1 | AES-GCM encryption (test data only) | Plaintext exposure check; upload/retrieval time difference |
| A2 | Fabric integration | Audit availability, verifiability, storage and latency differences |
| A3 | On-chain grant/denial events | Whether custody history still reconstructs each access decision |
| A4 | Role/policy enforcement (isolated test instance only) | Unauthorized retrieval rejection; expected failure is a security regression, not an acceptable configuration |

Ablations must run only in an isolated test deployment with synthetic evidence. Do not disable protections in a live or production environment.

## Dataset and run protocol

Use the 60 generated records in `../data/synthetic_evidence/`, then add independently generated payload-size bands (e.g., 1 KiB, 64 KiB, 1 MiB, and 10 MiB) with fixed seeds and disclose them. Separate functional security assertions from throughput tests. For integrity tests, mutate ciphertext bytes and record whether retrieval is rejected. For access tests, include authorized Investigator and denied Guest cases. Do not treat synthetic split labels as machine-learning train/test evidence.

## Results table template

Populate only from raw captured runs. `NA` means not measured; do not replace it with zero.

| Variant | Median end-to-end ms | p95 ms | Throughput ops/s | CPU / memory | Audit bytes/event | Unauthorized retrievals | Integrity tamper detections |
|---|---:|---:|---:|---|---:|---:|---:|
| B1 | NA | NA | NA | NA | NA | NA | NA |
| B2 | NA | NA | NA | NA | NA | NA | NA |
| B3 | NA | NA | NA | NA | NA | NA | NA |
| P | NA | NA | NA | NA | NA | NA | NA |

A completed paper requires the actual project source, successful runs, raw CSV output, environment details, and author review before claiming comparative results.
