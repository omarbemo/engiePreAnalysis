"""Builds a reference graph from parsed Terraform resources with no
knowledge of what any resource type means. A reference is always the
same syntactic shape — '${type.name.attr}' — so one recursive walk over
every attribute value, on every resource, finds every reference.
"""


def _iter_string_values(value):
    """Recursively yield every string in a nested attribute structure
    (dicts, lists, or a bare scalar)."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _iter_string_values(v)
    elif isinstance(value, list):
        for v in value:
            yield from _iter_string_values(v)


def _extract_reference(value: str):
    """'${aws_ebs_volume.data_1.id}' -> 'aws_ebs_volume.data_1'.
    Returns None if value isn't a ${...} reference expression at all."""
    if not (value.startswith("${") and value.endswith("}")):
        return None
    parts = value[2:-1].split(".")
    if len(parts) < 2:
        return None
    return f"{parts[0]}.{parts[1]}"


def build_reference_graph(resources: list) -> dict:
    known_addresses = {r["address"] for r in resources}
    incoming = {addr: set() for addr in known_addresses}

    for resource in resources:
        for raw in _iter_string_values(resource["attributes"]):
            target = _extract_reference(raw)
            if (
                target is not None
                and target in known_addresses
                and target != resource["address"]
            ):
                incoming[target].add(resource["address"])

    return incoming
