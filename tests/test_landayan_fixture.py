"""Parse the Landayan 2021 OA JATS fixture — no network."""

from pathlib import Path

import pytest

from flybraingpt.jats import parse_jats

FIXTURE = Path(__file__).parent / "fixtures" / "PMC8139827.xml"


@pytest.mark.skipif(not FIXTURE.exists(), reason="fixture XML missing")
def test_landayan_2021_jats_fixture():
    rec = parse_jats(FIXTURE)
    assert rec["pmcid"] == "PMC8139827"
    assert rec["has_body"] is True
    assert "thirst" in rec["title"].lower()
    assert "drosophila" in rec["title"].lower() or "drosophila" in rec["abstract"].lower()
    assert len(rec["body"]) > 500
    assert rec["doi"].startswith("10.7554/elife.66286") or rec["doi"] == ""
