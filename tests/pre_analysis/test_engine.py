import json

from pre_analysis.engine import run_pre_analysis


def _load(fixture_path):
    with open(fixture_path) as f:
        return json.load(f)


def test_end_to_end_flags_nothing_when_everything_is_referenced():
    resources = _load("tests/fixtures/mixed_resources.json")
    assert run_pre_analysis(resources) == []


def test_end_to_end_flags_the_orphaned_volume():
    resources = _load("tests/fixtures/unattached_volume.json")
    findings = run_pre_analysis(resources)
    assert len(findings) == 1
    assert findings[0].rule == "unattached_ebs_volume"
