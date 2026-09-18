"""Build and validate the 7-stage regulatory-compliance snapshot chain.

Implements the contract in ../../snapshot.schema.json without a third-party
JSON Schema library (stdlib only, matching the Project A precedent). Each
function here is purely mechanical -- it enforces the SHAPE of a snapshot.
None of it knows anything about your actual interview content. Fill that in
via the `state=` dict you pass to build_snapshot() for each stage.
"""

import hashlib
import json
import pathlib
from datetime import datetime, timezone

SCHEMA_VERSION = "regulatory-compliance-stage-snapshot/2"

# stage name -> (sequence number, required keys inside state{})
STAGE_REQUIREMENTS = {
    "scope": (1, ["as_of", "review_type", "systems_in_scope", "audiences", "approval_gates"]),
    "source-capture": (2, ["sources"]),
    "authority-and-timing": (3, ["binding_rules", "timing_rules", "guidance_context", "authority_blockers"]),
    "evidence-reconciliation": (4, ["system_facts", "policy_controls", "incident_evidence", "conflicts", "evidence_gaps"]),
    "impact-analysis": (5, ["impacts", "unaffected_items", "conflicts", "unresolved_items"]),
    "actions-and-approvals": (6, ["proposed_actions", "approval_requirements", "escalations"]),
    "publication-validation": (7, ["artifacts", "validation_checks", "publication_status"]),
}

VALID_STATUS = {"complete", "partial", "blocked", "failed"}


def _canonical_bytes(obj):
    # sort_keys makes the hash reproducible regardless of dict insertion order
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_of(obj):
    return "sha256:" + hashlib.sha256(_canonical_bytes(obj)).hexdigest()


def build_snapshot(
    stage,
    run_id,
    state,
    *,
    prior_snapshot=None,
    prior_path=None,
    consumed_record_ids=None,
    produced_record_ids=None,
    unresolved=None,
    decisions=None,
    status="complete",
):
    """Construct one stage's snapshot dict. Does NOT write it to disk.

    prior_snapshot / prior_path: pass the dict and path of the previous
    stage's snapshot (as returned by save_snapshot) to link the chain.
    Omit both only for stage == "scope" (sequence 1).
    """
    if stage not in STAGE_REQUIREMENTS:
        raise ValueError(f"unknown stage {stage!r}; must be one of {list(STAGE_REQUIREMENTS)}")
    sequence, required_keys = STAGE_REQUIREMENTS[stage]

    missing = [k for k in required_keys if k not in state]
    if missing:
        raise ValueError(f"stage {stage!r} state is missing required keys: {missing}")

    if sequence == 1:
        if prior_snapshot is not None:
            raise ValueError("stage 'scope' (sequence 1) must not have a predecessor")
        predecessor = None
        consumed_record_ids = []
    else:
        if prior_snapshot is None or prior_path is None:
            raise ValueError(f"stage {stage!r} (sequence {sequence}) requires prior_snapshot and prior_path")
        predecessor = {
            "snapshot_id": prior_snapshot["snapshot_id"],
            "path": str(prior_path),
            "sha256": sha256_of(prior_snapshot),
        }
        consumed_record_ids = consumed_record_ids or []
        if not consumed_record_ids:
            raise ValueError(f"stage {stage!r} requires at least one consumed_record_id")

    if status not in VALID_STATUS:
        raise ValueError(f"status must be one of {VALID_STATUS}, got {status!r}")

    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "snapshot_id": f"{run_id}-{stage}",
        "run_id": run_id,
        "stage": stage,
        "sequence": sequence,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "predecessor": predecessor,
        "consumed_record_ids": consumed_record_ids,
        "produced_record_ids": produced_record_ids or [],
        "state": state,
        "unresolved": unresolved or [],
        "decisions": decisions or [],
    }
    validate_snapshot(snapshot)
    return snapshot


def validate_snapshot(snapshot):
    """Raise ValueError with a specific message on the first violation found."""
    top_required = [
        "schema_version", "snapshot_id", "run_id", "stage", "sequence", "created_at",
        "status", "predecessor", "consumed_record_ids", "produced_record_ids",
        "state", "unresolved", "decisions",
    ]
    for key in top_required:
        if key not in snapshot:
            raise ValueError(f"snapshot missing required top-level key: {key}")

    if snapshot["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION!r}")

    stage = snapshot["stage"]
    if stage not in STAGE_REQUIREMENTS:
        raise ValueError(f"unknown stage {stage!r}")
    expected_sequence, required_state_keys = STAGE_REQUIREMENTS[stage]
    if snapshot["sequence"] != expected_sequence:
        raise ValueError(f"stage {stage!r} must have sequence {expected_sequence}, got {snapshot['sequence']}")

    if snapshot["status"] not in VALID_STATUS:
        raise ValueError(f"status must be one of {VALID_STATUS}")

    if expected_sequence == 1:
        if snapshot["predecessor"] is not None:
            raise ValueError("sequence 1 snapshot must have predecessor: null")
        if snapshot["consumed_record_ids"]:
            raise ValueError("sequence 1 snapshot must have empty consumed_record_ids")
    else:
        pred = snapshot["predecessor"]
        if not isinstance(pred, dict):
            raise ValueError("sequence > 1 snapshot must have a predecessor object")
        for key in ("snapshot_id", "path", "sha256"):
            if key not in pred:
                raise ValueError(f"predecessor missing required key: {key}")
        if not pred["sha256"].startswith("sha256:") or len(pred["sha256"]) != 71:
            raise ValueError(f"predecessor.sha256 malformed: {pred['sha256']!r}")
        if not snapshot["consumed_record_ids"]:
            raise ValueError(f"stage {stage!r} must have at least one consumed_record_id")

    state = snapshot["state"]
    if not isinstance(state, dict):
        raise ValueError("state must be an object")
    missing_state = [k for k in required_state_keys if k not in state]
    if missing_state:
        raise ValueError(f"stage {stage!r} state missing required keys: {missing_state}")

    for i, record in enumerate(snapshot["unresolved"]):
        for key in ("id", "summary", "evidence_ids"):
            if key not in record:
                raise ValueError(f"unresolved[{i}] missing required key: {key}")

    for i, decision in enumerate(snapshot["decisions"]):
        for key in ("id", "summary", "evidence_ids", "rationale", "tradeoffs"):
            if key not in decision:
                raise ValueError(f"decisions[{i}] missing required key: {key}")
        if not decision["tradeoffs"]:
            raise ValueError(f"decisions[{i}].tradeoffs must be non-empty")

    return True


def save_snapshot(snapshot, out_dir):
    """Write snapshot as pretty JSON to out_dir/{sequence:02d}-{stage}.json.
    Returns the path, for use as prior_path in the next stage's build_snapshot call.
    """
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{snapshot['sequence']:02d}-{snapshot['stage']}.json"
    path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    # Smoke test with placeholder content -- proves the chain mechanics work.
    # This is NOT real interview content. Replace with your actual findings
    # in build_review.py before this counts as your submission.
    import tempfile

    run_id = "smoke-test-run"
    out_dir = pathlib.Path(tempfile.mkdtemp())

    s1 = build_snapshot(
        "scope", run_id,
        state={
            "as_of": "2026-08-26T00:00:00Z",
            "review_type": "PLACEHOLDER - fill from interview",
            "systems_in_scope": ["PLACEHOLDER-SYSTEM-1"],
            "audiences": ["PLACEHOLDER-AUDIENCE"],
            "approval_gates": ["PLACEHOLDER-GATE"],
        },
    )
    p1 = save_snapshot(s1, out_dir)
    print(f"stage 1 OK -> {p1}")

    s2 = build_snapshot(
        "source-capture", run_id,
        prior_snapshot=s1, prior_path=p1,
        consumed_record_ids=[s1["snapshot_id"]],
        state={"sources": []},  # PLACEHOLDER
    )
    p2 = save_snapshot(s2, out_dir)
    print(f"stage 2 OK -> {p2}")
    print(f"stage 2 predecessor hash matches stage 1: {s2['predecessor']['sha256'] == sha256_of(s1)}")

    print("\nSmoke test passed. Chain mechanics work. Now replace placeholders with real content.")
