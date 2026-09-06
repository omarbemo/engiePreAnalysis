#from tomy
#to see the form run using( uv run python app.py demo_test_case.json --output kept.json)
#open http://127.0.0.1:5000
#will be saved to kept.json if you click submit

import argparse
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify

# Assuming your engine import works the same way
from pre_analysis_engine.engine import run_pre_analysis

app = Flask(__name__)

# Global variables to store path data across the web requests
INPUT_JSON_PATH = ""
OUTPUT_JSON_PATH = None

@app.route("/", methods=["GET", "POST"])
def review_resources_web():
    # 1. Load the original resources
    with open(INPUT_JSON_PATH, encoding="utf-8") as file:
        resources = json.load(file)
        
    findings = run_pre_analysis(resources)
    flagged_by_address = {finding.resource_id: finding for finding in findings}

    if request.method == "POST":
        # 2. Extract selected items from form submission
        # This gets a list of addresses the user checked "Remove" for
        remove_addresses = set(request.form.getlist("remove_resources"))
        
        # Filter resources: Keep them only if their address wasn't marked for removal
        kept_resources = [
            res for res in resources if res["address"] not in remove_addresses
        ]
        
        result_json = json.dumps(kept_resources, indent=2) + "\n"
        
        # Save or return output
        if OUTPUT_JSON_PATH:
            Path(OUTPUT_JSON_PATH).write_text(result_json, encoding="utf-8")
            return f"<h1>Success!</h1><p>Saved {len(kept_resources)} resource(s) to {OUTPUT_JSON_PATH}</p>"
        else:
            return jsonify(kept_resources)

    # 3. Handle GET request: Prepare flagged items for the HTML form
    flagged_resources = []
    for resource in resources:
        address = resource["address"]
        finding = flagged_by_address.get(address)
        if finding:
            flagged_resources.append({
                "address": address,
                "rule": finding.rule,
                "reason": finding.reason
            })
            
    return render_template("form.html", flagged_resources=flagged_resources)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Review unused resources via web interface.")
    parser.add_argument("json_path", help="JSON file containing resources")
    parser.add_argument(
        "--output",
        help="write the kept resources to this JSON file instead of browser window",
    )
    args = parser.parse_args()
    
    INPUT_JSON_PATH = args.json_path
    OUTPUT_JSON_PATH = args.output
    
    # Start the local development web server
    app.run(debug=True, port=5000)
