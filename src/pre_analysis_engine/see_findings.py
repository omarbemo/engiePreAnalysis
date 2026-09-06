"""Review unused resources and print the kept resources as JSON.

Usage: uv run python see_findings.py demo_test_case.json [--output kept.json]
"""
import argparse
import json
from collections.abc import Callable
from pathlib import Path

from pre_analysis_engine.engine import run_pre_analysis


def review_resources(
    resources: list[dict],
    prompt: Callable[[str], str],
) -> list[dict]:
    """Ask whether each flagged resource should be removed."""
    findings = run_pre_analysis(resources)
    flagged_by_address = {finding.resource_id: finding for finding in findings}
    kept_addresses = set()

    for resource in resources:
        address = resource["address"]
        finding = flagged_by_address.get(address)
        if finding is None:
            kept_addresses.add(address)
            continue

        answer = prompt(
            f"{address} is unused ({finding.rule}: {finding.reason}). "
            "Remove it? [y/N] "
        )
        if answer.strip().lower() not in {"y", "yes"}:
            kept_addresses.add(address)

    return [resource for resource in resources if resource["address"] in kept_addresses]


def ask_to_remove(message: str) -> str:
    return input(message)


def main(json_path: str, output_path: str | None = None):
    with open(json_path, encoding="utf-8") as file:
        resources = json.load(file)

    kept_resources = review_resources(resources, ask_to_remove)
    result = json.dumps(kept_resources, indent=2) + "\n"

    if output_path:
        Path(output_path).write_text(result, encoding="utf-8")
        print(f"Saved {len(kept_resources)} resource(s) to {output_path}")
    else:
        print(result, end="")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_path", help="JSON file containing resources")
    parser.add_argument(
        "--output",
        help="write the kept resources to this JSON file instead of stdout",
    )
    args = parser.parse_args()
    main(args.json_path, args.output)
