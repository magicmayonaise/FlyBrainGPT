"""Parse PMC JATS XML into title / abstract / body."""

from __future__ import annotations

from pathlib import Path

from lxml import etree

JATS_NS = {"jats": "http://jats.nlm.nih.gov"}


def _local(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def _text(el) -> str:
    if el is None:
        return ""
    return " ".join("".join(el.itertext()).split())


def parse_jats(path: Path | str) -> dict:
    """Return pmcid, title, abstract, body, has_body from a JATS or pmc-articleset file."""
    path = Path(path)
    root = etree.parse(str(path)).getroot()
    article = root
    if _local(root.tag) == "pmc-articleset":
        article = root.find(".//{*}article")
        if article is None:
            raise ValueError(f"no <article> in {path}")

    pmcid = ""
    doi = ""
    for aid in article.findall(".//{*}article-id"):
        kind = (aid.get("pub-id-type") or "").lower()
        val = (aid.text or "").strip()
        if kind in {"pmc", "pmcid"} and val:
            pmcid = val.upper() if val.upper().startswith("PMC") else f"PMC{val}"
        if kind == "doi" and val:
            doi = val.lower()

    title_el = article.find(".//{*}article-title")
    title = _text(title_el)

    abstract_bits = []
    for abs_el in article.findall(".//{*}abstract"):
        if abs_el.get("abstract-type") == "graphical":
            continue
        t = _text(abs_el)
        if t:
            abstract_bits.append(t)
    abstract = " ".join(abstract_bits)

    body_el = article.find(".//{*}body")
    body = _text(body_el)
    return {
        "pmcid": pmcid,
        "doi": doi,
        "title": title,
        "abstract": abstract,
        "body": body,
        "has_body": bool(body_el is not None and body),
        "source_path": str(path),
    }


def looks_like_jats(raw: bytes) -> bool:
    head = raw[:2000]
    return b"<article" in head or b"<pmc-articleset" in head
