# Synthetic evidence test corpus

- Source: generated locally by `scripts/generate_synthetic_dataset.py`; no external or case data.
- Purpose: repeatable workflow and access-control test fixtures for the prototype.
- Records: 60 one-event JSONL files.
- Classes: normal=20, access_denied=20, tamper_alert=20.
- Split: stratified by class at 70/15/15 (train/validation/test); included for reproducibility only, not for model training.
- Generator seed: 20261030.
- Fields: synthetic case/object/actor identifiers, reserved documentation-range IP addresses, fixed-range timestamps, action, decision, and scenario outcome.
- Privacy: no real people, cases, or production logs are represented.
- License: CC0-1.0 applies only to the generated records and manifest; see https://creativecommons.org/publicdomain/zero/1.0/.
- Limits: this corpus is artificial and does not establish performance or generalization to operational evidence.
