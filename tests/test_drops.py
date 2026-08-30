"""Hard-drops: four grey-list non-fly papers and the 25 body-less EFetch files.

No network. Manifests are the source of truth.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREY_CSV = ROOT / "manifests" / "dropped_grey.csv"
NOBODY_CSV = ROOT / "manifests" / "dropped_nobody_efetch.csv"
OA_CSV = ROOT / "manifests" / "corpus_v0.csv"
BUILD_LIST = ROOT / "manifests" / "corpus_v0.pmcids.txt"

GREY_DOIS = {
    "10.1016/j.peptides.2017.10.016",  # mosquito AstA receptors
    "10.1016/s1097-2765(01)00218-0",  # mammalian heterochromatin
    "10.1038/s41586-023-06715-z",  # mouse landscape diffusion (Richman)
    "10.1101/2025.06.20.660653",  # hypothalamic autophagy/NPY
}


def test_grey_module_loads_four_named_dois():
    from flybraingpt.drops import load_doi_set

    got = load_doi_set(GREY_CSV)
    missing = GREY_DOIS - got
    assert not missing, f"grey manifest missing {missing}"
    assert len(got) == 4


def test_grey_dois_are_not_in_corpus_v0():
    from flybraingpt.drops import corpus_dois, load_doi_set

    grey = load_doi_set(GREY_CSV)
    oa = corpus_dois(OA_CSV)
    overlap = grey & oa
    assert not overlap, f"grey DOIs leaked into corpus_v0: {overlap}"


def test_nobody_efetch_has_exactly_25_and_is_dropped_from_build_list():
    from flybraingpt.drops import load_pmcid_set

    nobody = load_pmcid_set(NOBODY_CSV)
    build = load_pmcid_set(BUILD_LIST)
    assert len(nobody) == 25
    leak = nobody & build
    assert not leak, f"body-less EFetch IDs still in build list: {leak}"


def test_filter_pmcids_removes_drops():
    from flybraingpt.drops import filter_pmcids

    kept = filter_pmcids(
        ["PMC8139827", "PMC13342866", "PMC1460924"],
        dropped_pmcids={"PMC13342866", "PMC1460924"},
    )
    assert kept == ["PMC8139827"]
