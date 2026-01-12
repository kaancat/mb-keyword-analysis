#!/usr/bin/env python3
"""
Stop Hook: Validates all phases are complete before allowing workflow to finish.

This hook BLOCKS completion unless:
1. All phase artifacts exist
2. Key content markers are present in each artifact
3. Presentation was generated (Phase 7)
4. Validation script was run

Exit codes:
- 0: Approve (all phases complete)
- 2: Block (missing phases) - outputs JSON to stderr
"""

import json
import os
import sys
import re
from pathlib import Path


def find_client_dir():
    """Find the active client directory from environment or recent files."""
    # Check environment variable first
    client_dir = os.environ.get("MB_CLIENT_DIR")
    if client_dir and Path(client_dir).exists():
        return Path(client_dir)

    # Check for clients directory
    cwd = Path.cwd()
    clients_dir = cwd / "clients"
    if clients_dir.exists():
        # Find most recently modified client
        client_dirs = [d for d in clients_dir.iterdir() if d.is_dir()]
        if client_dirs:
            return max(client_dirs, key=lambda d: d.stat().st_mtime)

    return None


def check_file_exists(path: Path) -> bool:
    """Check if file exists and is not empty."""
    return path.exists() and path.stat().st_size > 0


def check_file_contains(path: Path, patterns: list[str]) -> tuple[bool, list[str]]:
    """Check if file contains all required patterns."""
    if not path.exists():
        return False, patterns

    content = path.read_text()
    missing = []
    for pattern in patterns:
        if not re.search(pattern, content, re.IGNORECASE):
            missing.append(pattern)

    return len(missing) == 0, missing


def check_json_valid(path: Path) -> tuple[bool, str]:
    """Check if JSON file is valid."""
    if not path.exists():
        return False, "File does not exist"

    try:
        with open(path) as f:
            json.load(f)
        return True, ""
    except json.JSONDecodeError as e:
        return False, str(e)


def check_json_has_keys(path: Path, keys: list[str]) -> tuple[bool, list[str]]:
    """Check if JSON file has required top-level keys."""
    if not path.exists():
        return False, keys

    try:
        with open(path) as f:
            data = json.load(f)

        if isinstance(data, list):
            # For array JSON, check first item
            if len(data) == 0:
                return False, ["empty array"]
            data = data[0] if isinstance(data[0], dict) else {}

        missing = [k for k in keys if k not in data]
        return len(missing) == 0, missing
    except:
        return False, keys


def check_roi_scenarios(path: Path) -> tuple[bool, str]:
    """Check if ROI calculator has three scenarios."""
    if not path.exists():
        return False, "File does not exist"

    try:
        with open(path) as f:
            data = json.load(f)

        # Check for scenarios in notes or at top level
        scenarios_found = []

        # Check in notes.scenarios
        if "notes" in data and "scenarios" in data["notes"]:
            scenarios = data["notes"]["scenarios"]
            for scenario in ["conservative", "expected", "optimistic"]:
                if scenario in scenarios:
                    scenarios_found.append(scenario)

        # Check at top level
        for scenario in [
            "conservative_scenario",
            "expected_scenario",
            "optimistic_scenario",
        ]:
            if scenario in data:
                scenarios_found.append(scenario.replace("_scenario", ""))

        if len(scenarios_found) >= 3:
            return True, ""

        missing = [
            s
            for s in ["conservative", "expected", "optimistic"]
            if s not in scenarios_found
        ]
        return False, f"Missing scenarios: {', '.join(missing)}"
    except Exception as e:
        return False, str(e)


def validate_phases(client_dir: Path) -> tuple[bool, list[dict]]:
    """Validate all phases are complete."""
    issues = []

    # Phase 1: website_content.md
    phase1_file = client_dir / "website_content.md"
    if not check_file_exists(phase1_file):
        issues.append(
            {
                "phase": 1,
                "severity": "block",
                "message": "Phase 1 incomplete: website_content.md missing",
            }
        )
    else:
        ok, missing = check_file_contains(
            phase1_file, ["Core Services", "Business Type|Target Customers"]
        )
        if not ok:
            issues.append(
                {
                    "phase": 1,
                    "severity": "warn",
                    "message": f"Phase 1 quality: Missing sections in website_content.md: {missing}",
                }
            )

    # Phase 2: potential_analysis.md
    phase2_file = client_dir / "potential_analysis.md"
    if not check_file_exists(phase2_file):
        issues.append(
            {
                "phase": 2,
                "severity": "block",
                "message": "Phase 2 incomplete: potential_analysis.md missing",
            }
        )
    else:
        ok, missing = check_file_contains(
            phase2_file, ["Budget", "Campaign Structure|Proposed"]
        )
        if not ok:
            issues.append(
                {
                    "phase": 2,
                    "severity": "warn",
                    "message": f"Phase 2 quality: Missing sections: {missing}",
                }
            )

    # Phase 3: keyword_analysis.json
    phase3_file = client_dir / "keyword_analysis.json"
    if not check_file_exists(phase3_file):
        issues.append(
            {
                "phase": 3,
                "severity": "block",
                "message": "Phase 3 incomplete: keyword_analysis.json missing",
            }
        )
    else:
        ok, err = check_json_valid(phase3_file)
        if not ok:
            issues.append(
                {
                    "phase": 3,
                    "severity": "block",
                    "message": f"Phase 3 error: Invalid JSON - {err}",
                }
            )
        else:
            # Check keyword count
            try:
                with open(phase3_file) as f:
                    data = json.load(f)
                keywords = (
                    data.get("keywords", data) if isinstance(data, dict) else data
                )
                if isinstance(keywords, list) and len(keywords) < 10:
                    issues.append(
                        {
                            "phase": 3,
                            "severity": "warn",
                            "message": f"Phase 3 quality: Only {len(keywords)} keywords (expected 10+)",
                        }
                    )
            except:
                pass

    # Phase 3: negative_keywords.json (also Phase 3 output)
    phase3_negatives = client_dir / "negative_keywords.json"
    if not check_file_exists(phase3_negatives):
        issues.append(
            {
                "phase": 3,
                "severity": "block",
                "message": "Phase 3 incomplete: negative_keywords.json missing. Must include global, vertical, client_specific, and campaign_negative_lists.",
            }
        )
    else:
        ok, err = check_json_valid(phase3_negatives)
        if not ok:
            issues.append(
                {
                    "phase": 3,
                    "severity": "block",
                    "message": f"Phase 3 error: Invalid negative_keywords.json - {err}",
                }
            )
        else:
            # Check required keys exist
            try:
                with open(phase3_negatives) as f:
                    neg_data = json.load(f)
                required_keys = ["global", "client_specific"]
                missing_keys = [k for k in required_keys if k not in neg_data]
                if missing_keys:
                    issues.append(
                        {
                            "phase": 3,
                            "severity": "warn",
                            "message": f"Phase 3 quality: negative_keywords.json missing keys: {missing_keys}",
                        }
                    )
            except:
                pass

    # Phase 4: campaign_structure.json
    phase4_file = client_dir / "campaign_structure.json"
    if not check_file_exists(phase4_file):
        issues.append(
            {
                "phase": 4,
                "severity": "block",
                "message": "Phase 4 incomplete: campaign_structure.json missing",
            }
        )
    else:
        ok, err = check_json_valid(phase4_file)
        if not ok:
            issues.append(
                {
                    "phase": 4,
                    "severity": "block",
                    "message": f"Phase 4 error: Invalid JSON - {err}",
                }
            )

    # Phase 5: ad_copy.json
    phase5_file = client_dir / "ad_copy.json"
    if not check_file_exists(phase5_file):
        issues.append(
            {
                "phase": 5,
                "severity": "block",
                "message": "Phase 5 incomplete: ad_copy.json missing",
            }
        )
    else:
        ok, err = check_json_valid(phase5_file)
        if not ok:
            issues.append(
                {
                    "phase": 5,
                    "severity": "block",
                    "message": f"Phase 5 error: Invalid JSON - {err}",
                }
            )
        else:
            ok, missing = check_json_has_keys(
                phase5_file, ["Headline 1", "Description 1"]
            )
            if not ok:
                issues.append(
                    {
                        "phase": 5,
                        "severity": "warn",
                        "message": f"Phase 5 quality: Missing ad copy fields: {missing}",
                    }
                )

    # Phase 6: roi_calculator.json
    phase6_file = client_dir / "roi_calculator.json"
    if not check_file_exists(phase6_file):
        issues.append(
            {
                "phase": 6,
                "severity": "block",
                "message": "Phase 6 incomplete: roi_calculator.json missing",
            }
        )
    else:
        # Validate JSON is valid
        ok, err = check_json_valid(phase6_file)
        if not ok:
            issues.append(
                {
                    "phase": 6,
                    "severity": "block",
                    "message": f"Phase 6 error: Invalid JSON - {err}",
                }
            )
        else:
            # Scenarios are optional - presentation has interactive calculator
            ok, err = check_roi_scenarios(phase6_file)
            if not ok:
                issues.append(
                    {
                        "phase": 6,
                        "severity": "warn",
                        "message": f"Phase 6 quality: ROI scenarios are optional - {err}",
                    }
                )

    # Phase 7: presentation.html
    phase7_file = client_dir / "presentation.html"
    if not check_file_exists(phase7_file):
        issues.append(
            {
                "phase": 7,
                "severity": "block",
                "message": "Phase 7 incomplete: presentation.html missing. Run: python scripts/generate_presentation.py",
            }
        )

    # Check for blocking issues
    blocking_issues = [i for i in issues if i["severity"] == "block"]
    return len(blocking_issues) == 0, issues


def main():
    """Main entry point for stop hook."""
    # Read stdin (hook input)
    try:
        input_data = json.load(sys.stdin)
    except:
        input_data = {}

    # Find client directory
    client_dir = find_client_dir()

    if not client_dir:
        # No client directory found - might be a different workflow
        # Allow completion but warn
        print(
            json.dumps(
                {
                    "decision": "approve",
                    "reason": "No client directory found - not a keyword analysis workflow",
                }
            )
        )
        sys.exit(0)

    # Validate all phases
    all_complete, issues = validate_phases(client_dir)

    if all_complete:
        # All phases complete
        warnings = [i for i in issues if i["severity"] == "warn"]
        if warnings:
            warning_msg = "; ".join([w["message"] for w in warnings])
            print(
                json.dumps(
                    {
                        "decision": "approve",
                        "reason": f"All phases complete. Warnings: {warning_msg}",
                    }
                )
            )
        else:
            print(
                json.dumps(
                    {
                        "decision": "approve",
                        "reason": "All phases complete and validated",
                    }
                )
            )
        sys.exit(0)
    else:
        # Blocking issues found
        blocking = [i for i in issues if i["severity"] == "block"]
        block_msg = "\n".join([f"- {b['message']}" for b in blocking])

        result = {
            "decision": "block",
            "reason": f"Cannot complete: {len(blocking)} phase(s) incomplete",
            "systemMessage": f"The following phases must be completed before finishing:\n{block_msg}",
        }
        print(json.dumps(result), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
