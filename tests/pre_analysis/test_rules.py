import json

from pre_analysis.graph import build_reference_graph
from pre_analysis.rules import evaluate_tier_one


def _findings_for(fixture_path):
    with open(fixture_path) as f:
        resources = json.load(f)
    graph = build_reference_graph(resources)
    return evaluate_tier_one(resources, graph)


def test_attached_volume_is_not_flagged():
    flagged = {f.resource_id for f in _findings_for("tests/fixtures/mixed_resources.json")}
    assert "aws_ebs_volume.data_1" not in flagged


def test_unattached_volume_is_flagged():
    findings = _findings_for("tests/fixtures/unattached_volume.json")
    assert len(findings) == 1
    assert findings[0].resource_id == "aws_ebs_volume.orphan"
    assert findings[0].rule == "unattached_ebs_volume"


def test_eip_with_inline_instance_is_not_flagged():
    findings = _findings_for("tests/fixtures/eip_inline_association.json")
    assert findings == []


def test_eip_with_no_association_at_all_is_flagged():
    findings = _findings_for("tests/fixtures/eip_orphaned.json")
    assert len(findings) == 1
    assert findings[0].rule == "orphaned_eip"
