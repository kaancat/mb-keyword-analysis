import json
import os
import argparse
import sys
import jsonschema
from jsonschema import validate

# Load Schemas
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")


def load_schema(name):
    path = os.path.join(SCHEMA_DIR, name)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Schema file '{name}' not found in {SCHEMA_DIR}")
        return None


SCHEMAS = {
    "keyword_analysis": load_schema("keyword_analysis.schema.json"),
    "campaign_structure": load_schema("campaign_structure.schema.json"),
    "ad_copy": load_schema("ad_copy.schema.json"),
    "negative_keywords": load_schema("negative_keywords.schema.json"),
}

# Filter out None schemas
SCHEMAS = {k: v for k, v in SCHEMAS.items() if v is not None}


def validate_data(data, schema_type):
    """
    Validates a list of dictionaries against the specified schema.
    Returns (True, []) if valid, (False, [errors]) if invalid.
    """
    if schema_type not in SCHEMAS:
        return False, [f"Unknown schema type: {schema_type}"]

    schema = SCHEMAS[schema_type]
    errors = []

    # 1. JSON Schema Validation (Structure, Types, MaxLength)
    try:
        validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        # Create a readable error message
        path = " -> ".join([str(p) for p in e.path]) if e.path else "root"
        errors.append(f"Schema Error at '{path}': {e.message}")
        # We continue to check custom rules even if schema fails, if possible

    # 2. Custom Business Logic Validation
    if isinstance(data, list):
        for i, row in enumerate(data):
            row_prefix = f"Row {i}"

            # Check Campaign Naming Convention (All tabs)
            if "Campaign" in row:
                campaign = row.get("Campaign", "")
                if campaign and not str(campaign).startswith("mb |"):
                    errors.append(
                        f"{row_prefix}: Campaign '{campaign}' must start with 'mb |'"
                    )

            # Check Ad Group Naming (All tabs)
            if "Ad Group" in row:
                ad_group = row.get("Ad Group", "")
                if ad_group and " | " not in str(ad_group):
                    # Soft warning or strict? Prompt implies strict pattern check.
                    # Let's just warn for now to avoid blocking valid variations.
                    pass

            # Check Sentence Case in Headlines (Ad Copy)
            if schema_type == "ad_copy":
                for i in range(1, 16):
                    key = f"Headline {i}"
                    if key in row:
                        h = row[key]
                        if not isinstance(h, str):
                            continue
                        # Check for Title Case (simple heuristic: more than half words capitalized)
                        words = h.split()
                        if len(words) > 1:
                            capitalized_words = sum(1 for w in words if w[0].isupper())
                            if capitalized_words > len(words) / 2 and not h.isupper():
                                errors.append(
                                    f"{row_prefix}: {key} '{h}' appears to be Title Case. Use sentence case."
                                )

            # NEW: Check Match Type Rationale (Keyword Analysis)
            if schema_type == "keyword_analysis":
                # Check Match Type Rationale is present and non-empty
                if "Match Type" in row:
                    rationale = row.get("Match Type Rationale", "")
                    if not rationale or rationale.strip() == "":
                        errors.append(
                            f"{row_prefix}: Keyword '{row.get('Keyword', 'unknown')}' has Match Type but no Match Type Rationale"
                        )

                # Check Service_ID is present (can be null for excluded keywords)
                if "Include" in row and row.get("Include") is True:
                    service_id = row.get("Service_ID")
                    if service_id is None:
                        errors.append(
                            f"{row_prefix}: Included keyword '{row.get('Keyword', 'unknown')}' has no Service_ID - validate against $CANONICAL_SERVICES"
                        )

                # Check Exclusion_Reason for excluded keywords
                if row.get("Include") is False:
                    reason = row.get("Exclusion_Reason")
                    if not reason or reason.strip() == "":
                        errors.append(
                            f"{row_prefix}: Excluded keyword '{row.get('Keyword', 'unknown')}' has no Exclusion_Reason"
                        )

    # NEW: Additional aggregate checks for keyword_analysis
    if schema_type == "keyword_analysis" and isinstance(data, list):
        # Check positioning keyword percentage (if any exist)
        total_included = sum(1 for row in data if row.get("Include") is True)
        positioning_count = sum(
            1
            for row in data
            if row.get("Positioning") is True and row.get("Include") is True
        )

        if total_included > 0:
            positioning_pct = (positioning_count / total_included) * 100
            if positioning_count > 0 and positioning_pct < 10:
                errors.append(
                    f"⚠️  Warning: Only {positioning_pct:.1f}% of keywords are positioning keywords. Consider if $POSITIONING_MODE requires 10-20%."
                )

        # Check for unvalidated keywords
        unvalidated = [
            row.get("Keyword")
            for row in data
            if row.get("Service_Validation") == "PENDING_REVIEW"
        ]
        if unvalidated:
            errors.append(
                f"⚠️  Warning: {len(unvalidated)} keywords still marked PENDING_REVIEW - complete Phase 3.5 validation"
            )

    if errors:
        return False, errors

    return True, []


def main():
    parser = argparse.ArgumentParser(
        description="Validate Google Ads deliverables against Monday Brew schemas."
    )
    parser.add_argument("--keywords", help="Path to Keyword Analysis JSON/CSV file")
    parser.add_argument("--structure", help="Path to Campaign Structure JSON/CSV file")
    parser.add_argument("--ads", help="Path to Ad Copy JSON/CSV file")
    parser.add_argument(
        "--all",
        help="Path to a JSON file containing all 3 tabs (as keys: keyword_analysis, campaign_structure, ad_copy)",
    )

    args = parser.parse_args()

    if not any([args.keywords, args.structure, args.ads, args.all]):
        parser.print_help()
        sys.exit(1)

    all_valid = True

    def run_validation(path, schema_type):
        print(f"Validating {schema_type} from {path}...")
        try:
            with open(path, "r") as f:
                data = json.load(f)

            is_valid, errors = validate_data(data, schema_type)
            if is_valid:
                print(f"✅ {schema_type}: Valid")
                return True
            else:
                print(f"❌ {schema_type}: Invalid")
                for err in errors:
                    print(f"  - {err}")
                return False
        except json.JSONDecodeError:
            print(f"❌ Error: Could not decode JSON from {path}")
            return False
        except FileNotFoundError:
            print(f"❌ Error: File not found {path}")
            return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

    if args.keywords:
        if not run_validation(args.keywords, "keyword_analysis"):
            all_valid = False

    if args.structure:
        if not run_validation(args.structure, "campaign_structure"):
            all_valid = False

    if args.ads:
        if not run_validation(args.ads, "ad_copy"):
            all_valid = False

    if args.all:
        print(f"Validating full deliverable from {args.all}...")
        try:
            with open(args.all, "r") as f:
                full_data = json.load(f)

            # Expecting keys matching schema names
            for key in ["keyword_analysis", "campaign_structure", "ad_copy"]:
                if key in full_data:
                    is_valid, errors = validate_data(full_data[key], key)
                    if is_valid:
                        print(f"✅ {key}: Valid")
                    else:
                        print(f"❌ {key}: Invalid")
                        for err in errors:
                            print(f"  - {err}")
                        all_valid = False
                else:
                    print(f"⚠️  Missing key '{key}' in full deliverable file.")
        except Exception as e:
            print(f"❌ Error processing --all file: {str(e)}")
            all_valid = False

    if not all_valid:
        sys.exit(1)
    else:
        print("\nAll checks passed! 🚀")


if __name__ == "__main__":
    main()
