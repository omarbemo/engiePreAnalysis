"""Run the pre-analysis engine against a JSON file and print every
resource's status — not just the flagged ones — so you can see the full
before/after picture in one glance. No pytest involved.

Usage: uv run python see_findings.py demo_test_case.json
"""
import json
import sys

from pre_analysis_engine.engine import run_pre_analysis


def main(json_path: str):
    with open(json_path) as f:
        resources = json.load(f)

    findings = run_pre_analysis(resources)
    flagged_by_address = {f.resource_id: f for f in findings}

    print(f"Parsed {len(resources)} resource(s) from {json_path}\n")

    for resource in resources:
        address = resource["address"]
        if address in flagged_by_address:
            finding = flagged_by_address[address]
            print(f"[UNUSED]  {address}")
            print(f"          rule:   {finding.rule}")
            print(f"          reason: {finding.reason}\n")
        else:
            print(f"[in use]  {address}")

    print(f"\n{len(findings)} of {len(resources)} resources flagged as waste.")


if __name__ == "__main__":
    main(sys.argv[1])
