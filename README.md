# FlyBrainGPT

Thirst-circuit **retrieval-augmented generation** over **PubMed Central Open Access JATS XML**.

This is **not** a trained GPT. There are **no model weights** in this repository. The current deliverable is a **reproducible OA corpus** plus a script that turns PMCIDs into a parquet table (`pmcid`, `title`, `abstract`, `body`).

## What this project is

*Drosophila melanogaster* papers on thirst, NPF/NPFR, Allatostatin A, PAM/mushroom-body memory, pC1, and oviDN/oviIN — mined from **native PMC XML** so we skip PDF-to-text conversion.

These counts are **different sets**. Do not collapse them.

| Set | n (as of 2026-08-29, re-count on disk) | Where |
|---|---|---|
| Mixed EFetch dump (unique PMCIDs) | **307** | local Temp only — **not in git** |
| Mixed EFetch files with `<body>` | **283 / 308** files (the extra file is a Landayan duplicate) | same dump |
| Mixed EFetch body-less / &lt; 20 KB | **25** | `manifests/dropped_nobody_efetch.csv` |
| pubget **Open Access** subset | **246 / 307** | `manifests/corpus_v0.csv` |
| OA with `<body>` | **245** | `manifests/corpus_v0.pmcids.txt` (build list) |
| OA without `<body>` | **1** — `PMC13342866` | listed in the OA CSV, **not** in the build list |

XML lives only on disk under `data/` (gitignored). Git tracks the **manifest**, not the articles.

## Reproduce

You need Python **3.11+**, [`uv`](https://github.com/astral-sh/uv), and network access to NCBI E-utilities (no campus VPN required for OA XML). `uv` builds a **project-local** `.venv`. Do not install these packages into a Hermes environment.

```bash
cd FlyBrainGPT
uv sync --python 3.11   # project + dev tools, exact versions from uv.lock

# Optional: rebuild XML from the OA PMCID list (writes data/corpus_v0/, gitignored)
uv run python scripts/build_corpus.py \
  --pmcids manifests/corpus_v0.pmcids.txt \
  --out data/corpus_v0/corpus.parquet \
  --xml-dir data/corpus_v0/xml

uv run pytest
```

### Pre-commit hooks

| When | Hook | What it does |
|---|---|---|
| `git commit` | pre-commit-hooks | Trims whitespace, fixes file endings, validates YAML/TOML, blocks merge markers and files > 1 MB, blocks private keys |
| `git commit` | **gitleaks** | Blocks API keys and tokens in staged changes |
| `git commit` | **ruff** | Lints (`--fix`) and formats Python |
| `git commit` | **mypy** | Type-checks `flybraingpt/`, `scripts/`, `tests/` |
| `git push` | **pytest** | Runs the test suite before code leaves your machine |

Committed data (`manifests/`, `tests/fixtures/`) is never rewritten, but it is still checked for large files and secrets. Config lives in `.pre-commit-config.yaml`; ruff and mypy settings live in `pyproject.toml`.

```bash
uv run pre-commit install          # once per clone: installs commit + push hooks
uv run pre-commit run --all-files  # check everything by hand
```

CI runs `uv sync --locked`, the same hooks, a full-history gitleaks scan, and pytest, so skipping hooks locally with `--no-verify` still fails the PR. After `uv run pre-commit autoupdate`, set the matching `ruff==` pin in `pyproject.toml` and run `uv lock`.

NCBI asks for ≤ 3 EFetch requests/second without an API key. Set `NCBI_API_KEY` if you have one.

Landayan et al. 2021 (*eLife*) is the CI fixture: DOI `10.7554/eLife.66286`, **PMC8139827**, PMID **34018925**.

## What is excluded

- **Paywalled** publisher PDFs (including many *Nature* papers), even if a university VPN can open them in a browser.
- **Non-OA PMC** author manuscripts. EFetch can still return JATS for some of those; **corpus_v0 does not include them**. pubget kept **246 / 307** PMCIDs as Open Access (~61 author manuscripts stayed out).
- Papers **without a PMCID** (no NCBI full-text XML).
- The **25** mixed-EFetch files without a `<body>` / under 20 KB (`manifests/dropped_nobody_efetch.csv`). That **25** is not the OA-subset **1**.
- **Four grey-list misclassifications** (not *D. melanogaster* primary research) in `manifests/dropped_grey.csv`:
  - mosquito AstA receptors `10.1016/j.peptides.2017.10.016`
  - mammalian heterochromatin `10.1016/s1097-2765(01)00218-0`
  - mouse landscape diffusion `10.1038/s41586-023-06715-z` (Richman et al., *Nature*)
  - hypothalamic autophagy/NPY `10.1101/2025.06.20.660653`
- **PDF-derived** text from paper-search-mcp.
- Sci-Hub or any non-OA bulk download.
- pubget `articleset_*.xml` and any Temp JATS dump — never commit those.

## Data vs code licenses

- **Code** in this repository: **MIT** (see `LICENSE`).
- **Article XML**: remains under each paper’s **PMC / publisher license** (often CC BY). Do not relicense the papers as MIT. Do not commit the XML.

## Layout

```
manifests/          # committed: PMCID list, SHA256, DOI, OA, has_body, drop lists
scripts/            # committed: build_corpus.py
tests/fixtures/     # committed: one OA JATS fixture (Landayan 2021)
data/               # gitignored: local XML + parquet
```

## Status

| Piece | State |
|---|---|
| Repo skeleton | `main`, MIT on **code** |
| corpus_v0 manifest | 246 OA PMCIDs; 245 in the build list |
| Grey-list + body-less drops | committed CSVs; builder skips them |
| Retrieval eval (Janu-AstA, L1-l, oviIN, NPF sign) | not started |
| Model weights | none |

## Topics

`drosophila` · `neuroscience` · `rag` · `pubmed-central` · `flybrain` · `open-access`
