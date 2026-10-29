#!/usr/bin/env python3
"""Generate a deterministic fictional corpus for PrivCloud-Chain workflow tests.

These records are synthetic test fixtures. They are not acquired evidence, and
must not be cited as real-world forensic observations or representative data.
"""
from __future__ import annotations
import csv, hashlib, json, random
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "synthetic_evidence"
SEED = 20261030
CLASSES = {
    "normal": 20,
    "access_denied": 20,
    "tamper_alert": 20,
}

def make_event(label: str, index: int, rng: random.Random) -> dict:
    base = datetime(2026, 10, 1, tzinfo=timezone.utc) + timedelta(minutes=index * 17 + rng.randrange(0, 12))
    event = {
        "record_id": f"SYN-{index:04d}",
        "case_id": f"CASE-SYN-{1 + (index % 8):03d}",
        "timestamp_utc": base.isoformat().replace("+00:00", "Z"),
        "scenario_label": label,
        "actor_id": f"investigator_{1 + (index % 4):02d}" if label == "normal" else f"guest_{1 + (index % 4):02d}",
        "source_ip": f"192.0.2.{1 + (index % 200)}",  # RFC 5737 documentation range
        "object_id": f"OBJ-SYN-{1 + (index % 25):03d}",
    }
    if label == "normal":
        event.update(action="evidence.retrieve", decision="allow", integrity="verified")
    elif label == "access_denied":
        event.update(action="evidence.retrieve", decision="deny", reason="policy_guest_role", plaintext_returned=False)
    else:
        event.update(action="evidence.verify", decision="deny", reason="authentication_tag_invalid", tamper_detected=True)
    return event

def main() -> None:
    rng = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    index = 0
    for label, total in CLASSES.items():
        ids = list(range(index, index + total))
        rng.shuffle(ids)
        train_end, val_end = int(total * .70), int(total * .85)
        split_by_id = {n: ("train" if i < train_end else "validation" if i < val_end else "test") for i, n in enumerate(ids)}
        for n in range(index, index + total):
            event = make_event(label, n + 1, rng)
            name = f"{event['record_id']}.jsonl"
            raw = (json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
            (OUT / name).write_bytes(raw)
            rows.append({"record_id": event["record_id"], "file": name, "class": label,
                         "split": split_by_id[n], "bytes": len(raw),
                         "sha256": hashlib.sha256(raw).hexdigest(), "synthetic": "true"})
        index += total
    rows.sort(key=lambda r: r["record_id"])
    with (OUT / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    card = f"""# Synthetic evidence test corpus\n\n- Source: generated locally by `scripts/generate_synthetic_dataset.py`; no external or case data.\n- Purpose: repeatable workflow and access-control test fixtures for the prototype.\n- Records: {len(rows)} one-event JSONL files.\n- Classes: normal={CLASSES['normal']}, access_denied={CLASSES['access_denied']}, tamper_alert={CLASSES['tamper_alert']}.\n- Split: stratified by class at 70/15/15 (train/validation/test); included for reproducibility only, not for model training.\n- Generator seed: {SEED}.\n- Fields: synthetic case/object/actor identifiers, reserved documentation-range IP addresses, fixed-range timestamps, action, decision, and scenario outcome.\n- Privacy: no real people, cases, or production logs are represented.\n- License: CC0-1.0 applies only to the generated records and manifest; see https://creativecommons.org/publicdomain/zero/1.0/.\n- Limits: this corpus is artificial and does not establish performance or generalization to operational evidence.\n"""
    (OUT / "dataset_card.md").write_text(card, encoding="utf-8")
    print(f"Wrote {len(rows)} synthetic records to {OUT}")

if __name__ == "__main__":
    main()
