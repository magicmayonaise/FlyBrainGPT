# corpus_v0

Source: **pubget** Open Access download, 2026-08-29.

| File | What |
|---|---|
| `corpus_v0.csv` | 246 OA PMCIDs: DOI, `oa=true`, `has_body`, SHA256, bytes, title |
| `corpus_v0.pmcids.txt` | 245 PMCIDs with a JATS `<body>` (use this for `build_corpus.py`) |
| `corpus_v0.all_oa.pmcids.txt` | All 246 OA PMCIDs, including the one without `<body>` |
| `dropped_nobody_efetch.csv` | **25** mixed-EFetch files with no `<body>` / &lt; 20 KB (SHA256 of the Temp dump). **Not** the OA-subset 1. |
| `dropped_grey.csv` | **4** non-fly misclassifications (mosquito AstA, mammalian heterochromatin, mouse landscape diffusion, hypothalamic autophagy/NPY). None of these four are in `corpus_v0.csv`. |

**OA body-less (still in the OA CSV, not in the build list):** `PMC13342866` (`10.1073/pnas.2517987123`) — also one of the 25 EFetch body-less files. The other 24 of those 25 were never OA.

XML is **not** in git. Local copy: `data/corpus_v0/xml/` (gitignored). Do not commit it. Do not commit Temp JATS or pubget `articleset_00000.xml`.

The earlier EFetch dump of 307 PMCIDs is a **superset**. It mixed OA and non-OA manuscripts. **corpus_v0 is only the 246 pubget OA IDs.**
