#!/usr/bin/env python3
"""Host-local cryptographic primitive microbenchmark; not an app/Fabric benchmark."""
from __future__ import annotations
import csv, hashlib, json, math, os, platform, random, statistics, sys, time
from datetime import datetime, timezone
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence"
SIZES = [1024, 65536, 1048576, 10485760]
REPETITIONS = 30
WARMUPS = 3
SEED = 20261030

def percentile(values, p):
    xs = sorted(values)
    return xs[max(0, min(len(xs)-1, math.ceil(p*len(xs))-1))]

def ms(fn):
    t0 = time.perf_counter_ns(); result = fn(); return result, (time.perf_counter_ns()-t0)/1e6

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows=[]
    key=hashlib.sha256(f"test-key-{SEED}".encode()).digest(); aes=AESGCM(key)
    nonce_counter=0
    for size in SIZES:
        payload=hashlib.shake_256(f"synthetic-payload-{SEED}-{size}".encode()).digest(size)
        hash_ms=[]; enc_ms=[]; dec_ms=[]; rt_ms=[]
        for rep in range(WARMUPS+REPETITIONS):
            _, h=ms(lambda: hashlib.sha256(payload).digest())
            nonce_counter += 1
            nonce=nonce_counter.to_bytes(12,'big')
            cipher, e=ms(lambda: aes.encrypt(nonce,payload,None))
            plain, d=ms(lambda: aes.decrypt(nonce,cipher,None))
            if plain != payload: raise RuntimeError(f"roundtrip mismatch at {size} bytes")
            tampered=bytearray(cipher); tampered[-1] ^= 1
            try: aes.decrypt(nonce,bytes(tampered),None)
            except Exception: pass
            else: raise RuntimeError("tampered ciphertext was accepted")
            if rep >= WARMUPS:
                hash_ms.append(h); enc_ms.append(e); dec_ms.append(d); rt_ms.append(e+d)
        med_rt=statistics.median(rt_ms)
        rows.append({
            "payload_bytes":size,"repetitions":REPETITIONS,
            "sha256_median_ms":f"{statistics.median(hash_ms):.6f}","sha256_p95_ms":f"{percentile(hash_ms,.95):.6f}",
            "aesgcm_encrypt_median_ms":f"{statistics.median(enc_ms):.6f}","aesgcm_encrypt_p95_ms":f"{percentile(enc_ms,.95):.6f}",
            "aesgcm_decrypt_median_ms":f"{statistics.median(dec_ms):.6f}","aesgcm_decrypt_p95_ms":f"{percentile(dec_ms,.95):.6f}",
            "aesgcm_roundtrip_median_ms":f"{med_rt:.6f}","aesgcm_roundtrip_p95_ms":f"{percentile(rt_ms,.95):.6f}",
            "roundtrip_mib_per_s_median":f"{(size*2)/(med_rt/1000)/(1024*1024):.3f}",
            "tamper_rejected_trials":REPETITIONS
        })
    csvpath=OUT/"crypto_primitive_microbenchmark.csv"
    with csvpath.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    metadata={"run_utc":datetime.now(timezone.utc).isoformat(),"scope":"local SHA-256/AES-256-GCM primitive check only; excludes FastAPI, MinIO, Fabric, database, network and baseline comparisons","python":sys.version,"cryptography":__import__('cryptography').__version__,"os":platform.platform(),"processor":platform.processor(),"logical_cpu_count":os.cpu_count(),"seed":SEED,"warmups_per_size":WARMUPS,"measured_repetitions_per_size":REPETITIONS,"sizes_bytes":SIZES,"validation":"all decryptions matched input and all ciphertext-tamper trials were rejected"}
    (OUT/"crypto_primitive_microbenchmark_metadata.json").write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print(csvpath)
    for r in rows: print(r)
if __name__=='__main__': main()
