"""Tier 1 deterministic waste-detection rules.

Each rule is config, not code: a resource type whose only real purpose
is to be referenced by something else in the same file. If nothing in
the reference graph points at it, it's flagged. One evaluation loop
handles every type in TIER_ONE_RULES — no per-rule function needed.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Finding:
    resource_id: str
    rule: str
    reason: str
    estimated_monthly_cost: float | None = None


@dataclass(frozen=True)
class TierOneRule:
    rule_name: str
    resource_type: str
    reason: str
    inline_association_attrs: tuple = field(default_factory=tuple)


TIER_ONE_RULES = [
    TierOneRule(
        "unattached_ebs_volume", "aws_ebs_volume",
        "EBS volume has no aws_volume_attachment referencing it — "
        "billed per GB-month whether attached or not.",
    ),
    TierOneRule(
        "orphaned_nat_gateway", "aws_nat_gateway",
        "NAT gateway has no aws_route sending traffic through it — "
        "billed hourly regardless of use.",
    ),
    TierOneRule(
        "orphaned_eip", "aws_eip",
        "Elastic IP has no aws_eip_association and no inline instance/"
        "network_interface set — AWS only waives the hourly charge "
        "while it's attached to a running resource.",
        inline_association_attrs=("instance", "network_interface"),
    ),
    TierOneRule(
        "orphaned_efs_mount", "aws_efs_file_system",
        "EFS file system has no aws_efs_mount_target — inaccessible "
        "and still billed per GB stored.",
    ),
    TierOneRule(
        "empty_load_balancer", "aws_lb",
        "Load balancer has no aws_lb_listener — billed hourly but "
        "cannot serve any traffic.",
    ),
    TierOneRule(
        "unattached_target_group", "aws_lb_target_group",
        "Target group has no listener action pointing at it — "
        "declared but never wired into traffic routing.",
    ),
]


def evaluate_tier_one(resources: list, graph: dict) -> list:
    findings = []
    for resource in resources:
        for rule in TIER_ONE_RULES:
            if resource["type"] != rule.resource_type:
                continue
            if graph[resource["address"]]:
                continue
            if any(
                resource["attributes"].get(attr) is not None
                for attr in rule.inline_association_attrs
            ):
                continue
            findings.append(Finding(
                resource_id=resource["address"],
                rule=rule.rule_name,
                reason=rule.reason,
            ))
    return findings
