# PrivCloud-Chain research package

This repository contains the current paper, a generated synthetic evidence corpus, the project-provided Verification Center run summary, and reproducible protocols for the comparative experiments requested in the mentor guidance.

## Contents

- `PrivCloud-Chain_IEEE_Research_Paper.docx` — the single current paper copy.
- `data/synthetic_evidence/` — 60 deterministic, fictional event records and a manifest. These are test fixtures, not real forensic evidence or observations from the deployed application.
- `evidence/verification_report.csv` — the 15 outcomes transcribed from the supplied Verification Center report. It is not an independent rerun.
- `experiments/README.md` — three baseline definitions, four ablations, and a preregistered measurement protocol. No baseline or ablation results are claimed yet.
- `scripts/generate_synthetic_dataset.py` — recreates the data and manifest using only the Python standard library.
- `evidence/crypto_primitive_microbenchmark.csv` — measured local SHA-256/AES-GCM primitive timings; it excludes the application, storage, blockchain, and network.
- `scripts/run_crypto_microbenchmark.py` — recreates the local primitive benchmark (requires Python and the `cryptography` package).

## Recreate the synthetic corpus

Run `python scripts/generate_synthetic_dataset.py`. The generator uses a fixed seed and writes 60 JSONL records plus `data/synthetic_evidence/manifest.csv` and `dataset_card.md`. Files are grouped into normal, access-denied, and tamper-alert scenarios. A stratified 70/15/15 split is included for bookkeeping; this is a system-test corpus, not an ML training dataset.

## Evidence and limits

The project report supplied to the authors records 15/15 checks passed in one configured run (38.658 s). The CSV preserves those reported outcomes and their provenance. No raw logs, host specifications, source-code revision, or per-test latency measurements were supplied. Do not interpret the aggregate run as proof of security or comparative performance.

The separate primitive benchmark uses 30 measured repetitions per payload size after three warmups. At 10 MiB, median SHA-256 time was 5.532 ms, median AES-GCM encrypt/decrypt round trip was 10.992 ms, and all 30 modified-ciphertext trials were rejected. These are local library-level observations on the recorded host; they are not end-to-end project timings and do not compare baselines.

The PrivCloud-Chain application source was not present in the available workspace when this package was prepared. The baselines and ablations are therefore protocols only. Do not fill their results with simulated or invented values. After the source is provided, implement the protocol against the actual application and record commit IDs, configuration, and raw outputs.

## GitHub

Public repository: https://github.com/gotr0oted/privcloud-chain-research

`scripts/watch_paper.ps1` watches the paper for saved changes, waits for an eight-second quiet period, commits only the document, and pushes to `origin`. It retries local commits that could not be pushed during a network interruption. A scheduled task starts the watcher at Windows sign-in. GitHub login must remain available through Git Credential Manager for pushes to succeed.

## Authorship and disclosures

The author-contribution split in the paper package is a proposed draft and must be confirmed by all three authors. Funding, competing interests, ethics/privacy and dataset statements must be verified by the authors before submission.
