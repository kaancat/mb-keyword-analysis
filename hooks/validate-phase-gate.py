#!/usr/bin/env python3
"""
PreToolUse Hook: Validates phase gates before allowing writes to phase artifacts.

This hook BLOCKS writes to later phase files if earlier phases are incomplete.
For example, you cannot write campaign_structure.json (Phase 4) if
keyword_analysis.json (Phase 3) doesn't exist.

Exit codes:
- 0: Approve (phase gate passed or not a phase artifact)
- 2: Block (phase gate failed) - outputs JSON to stderr
"""

import json
import os
import sys
from pathlib import Path


# Phase artifact files in order
PHASE_ARTIFACTS = {
    1: ["website_content.md"],
    2: ["potential_analysis.md"],
    3: ["keyword_analysis.json"],
    4: ["campaign_structure.json"],
    5: ["ad_copy.json"],
    6: ["roi_calculator.json"],
    7: ["presentation.html"],
}

# Reverse mapping: filename -> phase number
FILE_TO_PHASE = {}
for phase, files in PHASE_ARTIFACTS.items():
    for f in files:
        FILE_TO_PHASE[f] = phase


def find_client_dir_from_path(file_path: str) -> Path | None:
    """Extract client directory from file path."""
    path = Path(file_path)

    # Check if path contains 'clients' directory
    parts = path.parts
    if "clients" in parts:
        clients_idx = parts.index("clients")
        if clients_idx + 1 < len(parts):
            return Path(*parts[: clients_idx + 2])

    return None


def get_phase_for_file(file_path: str) -> int | None:
    """Get the phase number for a given file path."""
    filename = Path(file_path).name
    return FILE_TO_PHASE.get(filename)


def check_earlier_phases_complete(
    client_dir: Path, target_phase: int
) -> tuple[bool, list[str]]:
    """Check if all phases before target_phase are complete."""
    missing = []

    for phase in range(1, target_phase):
        phase_files = PHASE_ARTIFACTS.get(phase, [])
        for filename in phase_files:
            file_path = client_dir / filename
            if not file_path.exists() or file_path.stat().st_size == 0:
                missing.append(f"Phase {phase}: {filename}")

    return len(missing) == 0, missing


def main():
    """Main entry point for PreToolUse hook."""
    # Read stdin (hook input)
    try:
        input_data = json.load(sys.stdin)
    except:
        # Can't read input, approve by default
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only check Write and Edit operations
    if tool_name not in ["Write", "Edit"]:
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Check if this is a phase artifact
    target_phase = get_phase_for_file(file_path)
    if target_phase is None:
        # Not a phase artifact, allow
        sys.exit(0)

    # Phase 1 always allowed
    if target_phase == 1:
        sys.exit(0)

    # Find client directory
    client_dir = find_client_dir_from_path(file_path)
    if not client_dir:
        # Can't determine client dir, allow
        sys.exit(0)

    # Check if earlier phases are complete
    ok, missing = check_earlier_phases_complete(client_dir, target_phase)

    if ok:
        # All earlier phases complete, allow
        sys.exit(0)
    else:
        # Earlier phases missing, block
        missing_str = ", ".join(missing)
        result = {
            "decision": "block",
            "reason": f"Cannot write Phase {target_phase} artifact: earlier phases incomplete",
            "systemMessage": f"Phase gate violation. Complete these first: {missing_str}",
        }
        print(json.dumps(result), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
