"""Hard-drop lists for FlyBrainGPT corpus ingest.

Grey-list papers are not *Drosophila melanogaster* primary research.
Body-less EFetch files are incomplete JATS (no <body>), counted on the
mixed dump (n=25 as of 2026-08-29), which is a different set than the
pubget OA subset.
"""

from __future__ import annotations

import csv
from pathlib import Path


def _norm_doi(doi: str) -> str:
    return (doi or "").strip().lower()


def _norm_pmcid(pmcid: str) -> str:
    val = (pmcid or "").strip().upper()
    if not val:
        return ""
    if val.startswith("PMC"):
        return val
    if val.isdigit():
        return f"PMC{val}"
    return val


def load_doi_set(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".csv":
        rows = csv.DictReader(text.splitlines())
        out = set()
        for row in rows:
            doi = _norm_doi(row.get("doi") or "")
            if doi:
                out.add(doi)
        return out
    return {
        _norm_doi(line) for line in text.splitlines() if line.strip() and not line.startswith("#")
    }


def load_pmcid_set(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".csv":
        rows = csv.DictReader(text.splitlines())
        out = set()
        for row in rows:
            pmcid = _norm_pmcid(row.get("pmcid") or "")
            if pmcid:
                out.add(pmcid)
        return out
    return {
        _norm_pmcid(line) for line in text.splitlines() if line.strip() and not line.startswith("#")
    }


def corpus_dois(path: Path) -> set[str]:
    """Lowercased DOIs from a corpus CSV; strips publisher version suffixes after the core DOI."""
    out = set()
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            doi = _norm_doi(row.get("doi") or "")
            if not doi:
                continue
            out.add(doi)
            # also keep the stem before .saN version tags so grey matches cannot hide
            if ".sa" in doi:
                out.add(doi.split(".sa", 1)[0])
    return out


def filter_pmcids(pmcids: list[str], dropped_pmcids: set[str]) -> list[str]:
    dropped = {_norm_pmcid(x) for x in dropped_pmcids}
    kept = []
    for pmcid in pmcids:
        n = _norm_pmcid(pmcid)
        if n and n not in dropped:
            kept.append(n)
    return kept
