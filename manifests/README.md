# corpus_v0

Source: **pubget** Open Access download, 2026-08-29.

| File | What |
|---|---|
| `corpus_v0.csv` | 246 OA PMCIDs: DOI, `oa=true`, `has_body`, SHA256, bytes, title |
| `corpus_v0.pmcids.txt` | 245 PMCIDs with a JATS `<body>` (use this for `build_corpus.py`) |
| `corpus_v0.all_oa.pmcids.txt` | All 246 OA PMCIDs, including the one without `<body>` |

**Dropped from the PMCID list (still in the CSV):** `PMC13342866` (`10.1073/pnas.2517987123`) — OA record, 15,822 bytes, no `<body>`.

XML is **not** in git. Local copy: `data/corpus_v0/xml/` (gitignored). Do not commit it.

The earlier EFetch dump of 307 PMCIDs is a **superset**. It mixed OA and non-OA manuscripts and had ~25 files without `<body>`. **corpus_v0 is only the 246 pubget OA IDs.**
