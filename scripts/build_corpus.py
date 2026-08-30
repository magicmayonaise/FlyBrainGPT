"""Build corpus.parquet from a PMCID list via NCBI EFetch (JATS XML, not PDF)."""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

# Allow `python scripts/build_corpus.py` without install
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flybraingpt.drops import filter_pmcids, load_doi_set, load_pmcid_set  # noqa: E402
from flybraingpt.jats import looks_like_jats, parse_jats  # noqa: E402

EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
TOOL = "flybraingpt"
EMAIL = os.environ.get("NCBI_EMAIL", "dlandayan@ucmerced.edu")


def load_pmcids(path: Path) -> list[str]:
    ids = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        num = line.upper().replace("PMC", "")
        if not num.isdigit():
            raise ValueError(f"not a PMCID: {line!r}")
        ids.append(num)
    return ids


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def efetch_jats(pmcid_num: str, dest: Path, session: requests.Session) -> None:
    params = {
        "db": "pmc",
        "id": pmcid_num,
        "retmode": "xml",
        "tool": TOOL,
        "email": EMAIL,
    }
    if os.environ.get("NCBI_API_KEY"):
        params["api_key"] = os.environ["NCBI_API_KEY"]
    r = session.get(EFETCH, params=params, timeout=90)
    r.raise_for_status()
    if not looks_like_jats(r.content):
        raise ValueError(f"PMC{pmcid_num}: response is not JATS")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)


def build(
    pmcids_path: Path,
    xml_dir: Path,
    out_parquet: Path,
    fetch: bool,
    drop_no_body: bool,
    sleep_s: float,
    dropped_pmcids: set[str] | None = None,
    dropped_dois: set[str] | None = None,
) -> pd.DataFrame:
    session = requests.Session()
    session.headers.update({"User-Agent": f"{TOOL}/0.1 (mailto:{EMAIL})"})
    rows = []
    ids = filter_pmcids(load_pmcids(pmcids_path), dropped_pmcids or set())
    ids = [i[3:] if i.startswith("PMC") else i for i in ids]
    dropped_dois = {d.lower() for d in (dropped_dois or set())}
    xml_dir.mkdir(parents=True, exist_ok=True)
    for i, num in enumerate(ids, 1):
        dest = xml_dir / f"PMC{num}.xml"
        if fetch and not dest.exists():
            efetch_jats(num, dest, session)
            time.sleep(sleep_s)
        if not dest.exists():
            rows.append(
                {
                    "pmcid": f"PMC{num}",
                    "doi": "",
                    "title": "",
                    "abstract": "",
                    "body": "",
                    "has_body": False,
                    "sha256": "",
                    "missing_xml": True,
                }
            )
            print(f"[{i}/{len(ids)}] MISSING PMC{num}", flush=True)
            continue
        rec = parse_jats(dest)
        doi = (rec.get("doi") or "").lower()
        if doi and doi in dropped_dois:
            print(f"[{i}/{len(ids)}] GREY-DOI skip {rec['pmcid']} {doi}", flush=True)
            continue
        rec["sha256"] = sha256_file(dest)
        rec["missing_xml"] = False
        rec.pop("source_path", None)
        rows.append(rec)
        print(
            f"[{i}/{len(ids)}] {'BODY' if rec['has_body'] else 'NO-BODY'} "
            f"{rec['pmcid']} {rec.get('title', '')[:50]}",
            flush=True,
        )
    df = pd.DataFrame(rows)
    if drop_no_body:
        df = df[df["has_body"]].copy()
    out_parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_parquet, index=False)
    return df


def main() -> None:
    p = argparse.ArgumentParser(description="PMCID list → JATS → corpus.parquet")
    p.add_argument("--pmcids", type=Path, required=True)
    p.add_argument("--xml-dir", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--fetch", action="store_true", help="EFetch missing XML files")
    p.add_argument("--keep-empty-body", action="store_true")
    p.add_argument("--sleep", type=float, default=0.35)
    p.add_argument(
        "--drop-pmcids",
        type=Path,
        default=ROOT / "manifests" / "dropped_nobody_efetch.csv",
        help="CSV/txt of PMCIDs to hard-drop (default: 25 body-less EFetch files)",
    )
    p.add_argument(
        "--drop-dois",
        type=Path,
        default=ROOT / "manifests" / "dropped_grey.csv",
        help="CSV of grey-list DOIs to hard-drop (mosquito/mammal/mouse/hypothalamic)",
    )
    args = p.parse_args()
    dropped_pmcids = load_pmcid_set(args.drop_pmcids) if args.drop_pmcids.exists() else set()
    dropped_dois = load_doi_set(args.drop_dois) if args.drop_dois.exists() else set()
    df = build(
        args.pmcids,
        args.xml_dir,
        args.out,
        fetch=args.fetch,
        drop_no_body=not args.keep_empty_body,
        sleep_s=args.sleep,
        dropped_pmcids=dropped_pmcids,
        dropped_dois=dropped_dois,
    )
    print(f"wrote {args.out} rows={len(df)} has_body={int(df['has_body'].sum()) if len(df) else 0}")


if __name__ == "__main__":
    main()
