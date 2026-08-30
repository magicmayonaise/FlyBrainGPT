# FlyBrainGPT

Thirst-circuit **retrieval-augmented generation** over **PubMed Central Open Access JATS XML**.

This is **not** a trained GPT. There are **no model weights** in this repository. The current deliverable is a **reproducible OA corpus** plus a script that turns PMCIDs into a parquet table (`pmcid`, `title`, `abstract`, `body`).

## What this project is

*Drosophila melanogaster* papers on thirst, NPF/NPFR, Allatostatin A, PAM/mushroom-body memory, pC1, and oviDN/oviIN — mined from **native PMC XML** so we skip PDF-to-text conversion.

Corpus **v0** is the **246** articles **pubget** reported as PMC Open Access (2026-08-29). **245** have a JATS `<body>`; **PMC13342866** is OA but body-less and is listed in the CSV, not in `corpus_v0.pmcids.txt`. XML lives only on disk under `data/` (gitignored). Git tracks the **manifest**, not the articles.

## Reproduce

You need Python **3.11+**, `uv` or `pip`, and network access to NCBI E-utilities (no campus VPN required for OA XML).

```bash
cd FlyBrainGPT
uv venv --python 3.11
uv pip install -e ".[dev]"

# Optional: rebuild XML from the OA PMCID list (writes data/corpus_v0/, gitignored)
uv run python scripts/build_corpus.py \
  --pmcids manifests/corpus_v0.pmcids.txt \
  --out data/corpus_v0/corpus.parquet \
  --xml-dir data/corpus_v0/xml

uv run pytest
```

NCBI asks for ≤ 3 EFetch requests/second without an API key. Set `NCBI_API_KEY` if you have one.

Landayan et al. 2021 (*eLife*) is the CI fixture: DOI `10.7554/eLife.66286`, **PMC8139827**, PMID **34018925**.

## What is excluded

- **Paywalled** publisher PDFs (including many *Nature* papers), even if a university VPN can open them in a browser.
- **Non-OA PMC** author manuscripts. EFetch can still return JATS for some of those; **corpus_v0 does not include them**. pubget kept **246 / 307** PMCIDs as Open Access.
- Papers **without a PMCID** (no NCBI full-text XML).
- XML files **without a `<body>`** element (front-matter / incomplete records).
- **PDF-derived** text from paper-search-mcp.
- Sci-Hub or any non-OA bulk download.

## Data vs code licenses

- **Code** in this repository: **MIT** (see `LICENSE`).
- **Article XML**: remains under each paper’s **PMC / publisher license** (often CC BY). Do not relicense the papers as MIT. Do not commit the XML.

## Layout

```
manifests/          # committed: PMCID list, SHA256, DOI, OA, has_body
scripts/            # committed: build_corpus.py
tests/fixtures/     # committed: one OA JATS fixture (Landayan 2021)
data/               # gitignored: local XML + parquet
```

## Status

| Piece | State |
|---|---|
| Repo skeleton | this commit |
| corpus_v0 manifest | 246 OA PMCIDs |
| Retrieval eval (Janu-AstA, L1-l, oviIN, NPF sign) | not started |
| Model weights | none |

## Topics

`drosophila` · `neuroscience` · `rag` · `pubmed-central`
