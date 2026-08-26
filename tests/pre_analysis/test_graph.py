import json

from pre_analysis.graph import build_reference_graph


def _load(fixture_path):
    with open(fixture_path) as f:
        return json.load(f)


def test_volume_attachment_creates_incoming_edges_on_both_targets():
    resources = _load("tests/fixtures/mixed_resources.json")
    graph = build_reference_graph(resources)
    assert graph["aws_ebs_volume.data_1"] == {"aws_volume_attachment.a"}
    assert graph["aws_instance.web"] == {"aws_volume_attachment.a"}


def test_resource_with_no_references_has_empty_incoming_set():
    resources = _load("tests/fixtures/mixed_resources.json")
    graph = build_reference_graph(resources)
    assert graph["aws_volume_attachment.a"] == set()


def test_similar_prefixed_addresses_dont_false_match():
    resources = _load("tests/fixtures/prefix_collision.json")
    graph = build_reference_graph(resources)
    assert graph["aws_instance.web"] == set()
    assert graph["aws_instance.web2"] == {"aws_eip.ip"}
