#!/usr/bin/env python3
"""
Upload data-year folders to s3://cid-mbs/cow-data-v2/
Storage class : GLACIER_IR (S3 Glacier Instant Retrieval)
                → optimised for ~quarterly access, instant download
Optimisations : - .pkl files gzip-compressed before upload (saves ~40-70%)
                - .jpg / .mp4 / .csv uploaded as-is (already compressed)
                - Multipart upload (16 MB chunks, 10 parallel threads)
                - Excludes ._*, .DS_Store, *.log, *.tmp

Usage:
    python3 upload_to_cow_data_v2.py                    # upload all years
    python3 upload_to_cow_data_v2.py --years 2024 2025  # specific years
    python3 upload_to_cow_data_v2.py --dry-run          # preview only
"""

import argparse
import gzip
import os
import shutil
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import boto3
from boto3.s3.transfer import TransferConfig

# ── Config ────────────────────────────────────────────────────────────────────
BUCKET        = "cid-mbs"
S3_PREFIX     = "cow-data-v2"
AWS_PROFILE   = "cli-algorec"
STORAGE_CLASS = "GLACIER_IR"
BASE_DIR      = Path(__file__).parent          # folder containing this script
ALL_YEARS     = ["2021", "2022", "2023", "2024", "2025"]

EXCLUDE_PREFIXES = ("._",)
EXCLUDE_FILES    = {".DS_Store"}
EXCLUDE_SUFFIXES = (".log", ".tmp")

TRANSFER_CONFIG = TransferConfig(
    multipart_threshold = 64  * 1024 * 1024,   # 64 MB
    multipart_chunksize = 16  * 1024 * 1024,   # 16 MB chunks
    max_concurrency     = 10,
    use_threads         = True,
)
# ─────────────────────────────────────────────────────────────────────────────


def should_skip(fname: str) -> bool:
    if any(fname.startswith(p) for p in EXCLUDE_PREFIXES):
        return True
    if fname in EXCLUDE_FILES:
        return True
    if any(fname.endswith(s) for s in EXCLUDE_SUFFIXES):
        return True
    return False


def collect_files(year: str):
    """Return list of (local_path, s3_key, is_pkl) tuples for a data-year folder."""
    folder = BASE_DIR / f"data-{year}"
    if not folder.exists():
        print(f"  [WARN] {folder} does not exist, skipping.")
        return []

    items = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for fname in sorted(files):
            if should_skip(fname):
                continue
            local_path = Path(root) / fname
            rel        = local_path.relative_to(BASE_DIR)
            is_pkl     = fname.endswith(".pkl")
            s3_key     = f"{S3_PREFIX}/{rel}.gz" if is_pkl else f"{S3_PREFIX}/{rel}"
            items.append((local_path, s3_key, is_pkl))
    return items


def upload_one(args):
    """Upload a single file. Returns (s3_key, 'ok'|error_str)."""
    local_path, s3_key, is_pkl, s3_client, dry_run = args
    if dry_run:
        return s3_key, "dry-run"
    try:
        if is_pkl:
            with tempfile.NamedTemporaryFile(suffix=".pkl.gz", delete=False) as tmp:
                tmp_path = tmp.name
            with open(local_path, "rb") as f_in, gzip.open(tmp_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            s3_client.upload_file(
                tmp_path, BUCKET, s3_key,
                ExtraArgs={
                    "StorageClass": STORAGE_CLASS,
                    "Metadata": {"original-name": local_path.name},
                },
                Config=TRANSFER_CONFIG,
            )
            os.remove(tmp_path)
        else:
            s3_client.upload_file(
                str(local_path), BUCKET, s3_key,
                ExtraArgs={"StorageClass": STORAGE_CLASS},
                Config=TRANSFER_CONFIG,
            )
        return s3_key, "ok"
    except Exception as exc:
        return s3_key, f"ERROR: {exc}"


def upload_year(year: str, s3_client, dry_run: bool, workers: int = 8):
    print(f"\n{'[DRY RUN] ' if dry_run else ''}▶  data-{year}", flush=True)
    items = collect_files(year)
    if not items:
        return 0, 0, 0

    total   = len(items)
    done    = 0
    errors  = 0
    t_start = time.time()

    task_args = [(lp, sk, ip, s3_client, dry_run) for lp, sk, ip in items]

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(upload_one, a): a[1] for a in task_args}
        for fut in as_completed(futures):
            s3_key, result = fut.result()
            done += 1
            if result not in ("ok", "dry-run"):
                errors += 1
                print(f"  ✗ {result}", flush=True)
            if done % 1000 == 0 or done == total:
                elapsed = time.time() - t_start
                rate    = done / elapsed if elapsed > 0 else 0
                eta     = (total - done) / rate if rate > 0 else 0
                print(
                    f"  {done:>6,}/{total:,}  "
                    f"errors={errors}  "
                    f"elapsed={elapsed:.0f}s  "
                    f"rate={rate:.0f} files/s  "
                    f"ETA≈{eta:.0f}s",
                    flush=True,
                )

    elapsed = time.time() - t_start
    skipped = 0  # already excluded in collect_files
    print(
        f"  ✅  data-{year} done — "
        f"uploaded={done - errors:,}  errors={errors}  time={elapsed:.0f}s",
        flush=True,
    )
    return done - errors, errors, skipped


def verify_year(year: str, s3_client):
    """Compare local file count vs S3 object count for a year."""
    items     = collect_files(year)
    local_cnt = len(items)

    prefix    = f"{S3_PREFIX}/data-{year}/"
    paginator = s3_client.get_paginator("list_objects_v2")
    s3_cnt    = sum(
        p.get("KeyCount", 0)
        for p in paginator.paginate(Bucket=BUCKET, Prefix=prefix)
    )

    match = "✅" if local_cnt == s3_cnt else "❌"
    print(f"  {match}  data-{year}: local={local_cnt:,}  s3={s3_cnt:,}  diff={s3_cnt - local_cnt:+,}")
    return local_cnt == s3_cnt


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--years",   nargs="+", default=ALL_YEARS,
                        help="Which years to upload (default: all)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what would be uploaded without transferring")
    parser.add_argument("--workers", type=int, default=8,
                        help="Parallel upload threads (default: 8)")
    parser.add_argument("--skip-verify", action="store_true",
                        help="Skip post-upload verification")
    args = parser.parse_args()

    session  = boto3.Session(profile_name=AWS_PROFILE, region_name="us-east-1")
    s3       = session.client("s3")

    print("=" * 60)
    print(f"  Destination  : s3://{BUCKET}/{S3_PREFIX}/")
    print(f"  Storage class: {STORAGE_CLASS}")
    print(f"  Years        : {', '.join(args.years)}")
    print(f"  Workers      : {args.workers}")
    print(f"  Dry run      : {args.dry_run}")
    print("=" * 60)

    grand_uploaded = grand_errors = 0
    t0 = time.time()

    for year in args.years:
        up, err, _ = upload_year(year, s3, args.dry_run, args.workers)
        grand_uploaded += up
        grand_errors   += err

    total_time = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"  Grand total uploaded : {grand_uploaded:,}")
    print(f"  Total errors         : {grand_errors}")
    print(f"  Total time           : {total_time:.0f}s  (~{total_time/60:.1f} min)")
    print(f"  S3 location          : s3://{BUCKET}/{S3_PREFIX}/")
    print(f"{'=' * 60}")

    if not args.dry_run and not args.skip_verify:
        print("\n🔍  Verifying upload counts against S3...\n")
        all_ok = all(verify_year(y, s3) for y in args.years)
        if all_ok:
            print("\n✅  All year folders verified — upload complete!")
        else:
            print("\n⚠️   Some folders have count mismatches — re-run for those years.")


if __name__ == "__main__":
    main()
