---
name: regulatory-change-impact-brief
description: "Compares Quillhaven Academy's eight registered AI systems against EU AI Act Article 50 transparency obligations and internal policy AI-POL-2026-08-15, using live-fetched regulatory text and operational registers, and drafts a read-only impact register, compliance brief, and action calendar for Legal and Operations review. Use when a Compliance and Operations Manager needs a fresh Article 50 change-impact package."
---

# Regulatory Change Impact and Compliance Actions

This skill runs a full seven-stage audit trail (`scope` -> `source-capture`
-> `authority-and-timing` -> `evidence-reconciliation` -> `impact-analysis`
-> `actions-and-approvals` -> `publication-validation`) that compares
Quillhaven Academy's eight registered AI systems against EU AI Act Article 50
and the internal AI-use policy, then drafts three artifacts for human
review: an impact register, a compliance brief, and a local draft action
calendar. It never decides anything final -- Legal retains interpretive
authority and Operations retains activation/closure authority throughout;
every produced approval starts `pending`. See `references/business-rules.md`
for the full interview-to-rule mapping and every judgment call's rationale.

## Runtime and dependencies

- Python 3.7+ (standard library only -- no `jsonschema` install required;
  `scripts/snapshot_chain.py` validates against `snapshot.schema.json` by
  hand). Tested against the system's default `python3` (3.7.4).
- Network access required: 9 of the 10 sources are live-fetched over HTTPS
  at runtime (see Inputs below); the internal policy is a manual-export
  local reference (see Gotchas).
- **Cert-store gotcha**: some Python installs (notably python.org builds on
  macOS) ship without a working default TLS trust store, and every fetch
  fails with `CERTIFICATE_VERIFY_FAILED`. `build_review.py` falls back
  through `/etc/ssl/cert.pem`, `/etc/ssl/certs/ca-certificates.pem`,
  `/etc/pki/tls/certs/ca-bundle.crt`, and an installed `certifi` package (if
  present) before giving up on a source -- no new dependency is required,
  but if all of those are also missing/broken, HTTPS fetches will fail.

## Inputs

All ten sources named in the stakeholder interview. Role is identified by
`source_role`/`authority` at capture time, not by list position:

| id | what it is | source_role / authority | retrieval |
|---|---|---|---|
| SRC-LAW | EU AI Act service desk, Article 50 plain-language page | official-guidance / advisory | live HTTPS GET |
| SRC-OJ | Official Journal publication of Reg. (EU) 2024/1689 | binding-regulation / binding | live HTTPS GET |
| SRC-AMEND | Reg. (EU) 2026/1744 "Digital Omnibus on AI" (amends Art. 50) | binding-regulation / binding | live HTTPS GET |
| SRC-CONSOLIDATED | Consolidated text of Reg. 2024/1689 as of 2026-07-27 | binding-regulation / binding | live HTTPS GET |
| SRC-FAQ | EC FAQ on Article 50 transparency obligations | official-guidance / advisory | live HTTPS GET |
| SRC-TIME | EU AI Act implementation timeline | official-guidance / advisory | live HTTPS GET |
| SRC-SYSTEMS | Quillhaven AI system register (Google Sheet) | operational-record / operational-evidence | live CSV export fetch |
| SRC-EVIDENCE | Quillhaven incident/evidence register (Google Sheet) | operational-record / operational-evidence | live CSV export fetch |
| SRC-CALENDAR | Quillhaven compliance action calendar (Google Sheet) | operational-record / operational-evidence | live CSV export fetch |
| SRC-POLICY | Internal policy AI-POL-2026-08-15 + Article 50 operating-facts context | internal-policy / internal-control | **manual export** -- `references/internal-policy.md` (see Gotchas) |

Exact locators are in `scripts/build_review.py`'s `SOURCES` dict and in
`references/business-rules.md`'s Stage 2 table.

## Execution command

```bash
python3 regulatory-change-impact-brief/scripts/build_review.py \
  --run-id rc-article50-2026-08-26 \
  --out-dir deliverables
```

Both flags are optional; they default to the values above.

## Outputs

- `deliverables/snapshots/01-scope.json` through
  `07-publication-validation.json` -- the hash-chained stage snapshots, per
  `snapshot.schema.json`, written during the run (not reconstructed
  afterward).
- `deliverables/snapshots/sources/*.raw` -- the raw bytes captured from each
  live fetch this run, so a reviewer can follow the document-to-decision
  path without re-fetching.
- `deliverables/impact-register.csv` -- one row per system's impact
  determination: `impact_id, system_id, state, evidence_ids, reason, owner,
  proposed_action_id, approval_state`.
- `deliverables/compliance-brief.md` -- scope, source status, supported
  impacts, unresolved/conflicting items, proposed actions, escalations,
  limitations, and pending Legal/Operations decisions.
- `deliverables/action-calendar.ics` -- a valid draft `VCALENDAR`; every
  `SUMMARY` is prefixed `[DRAFT]` and every `DESCRIPTION` states the pending
  approval, per the safety boundary (this is not a production calendar).

## Validation and safe-failure behavior

- A schema-invalid snapshot (a bug, not a data gap) raises inside
  `build_snapshot`/`validate_snapshot`; `main()` catches `ValueError`,
  prints `FAILED: ...` to stderr, and exits `1` **without** writing the
  three final artifacts. Whatever snapshot files were already written up to
  that point are left on disk for debugging, but the package is not
  considered submitted.
- **If a source is unavailable/stale at fetch time**, the script applies
  two different, consistently-applied policies (documented as a decision
  in `references/business-rules.md`, per the assignment's non-happy-path
  requirement):
  - A **binding-regulation** source (OJ, AMEND, or CONSOLIDATED) failing
    retrieval triggers a **whole-run block**: stages 2-7 are all marked
    `status: "blocked"`, every system's impact state collapses to
    `unresolved` (formal impact conclusions are blocked per the README's
    explicit rule), and stage 7's `publication_status` is `blocked`. The
    script still writes every snapshot and artifact -- a blocked run is
    itself a valid, visible result -- but exits `2` rather than `0`.
  - Any other source failing retrieval yields a **safely bounded partial
    result**: that stage's `status` becomes `"partial"`, the failed source
    is listed in that stage's `unresolved` array, and everything else
    proceeds normally. `publication_status` can still reach `validated`.
- `publication_status: "validated"` means the package itself is
  well-formed (schema-valid, hash-chain intact, register/brief/calendar
  agree with stages 06-07) -- **not** that every question has been
  answered. Unresolved and conflicting items (as of this writing: AI-003,
  AI-005, AI-007 unresolved/conflicting; AI-004 and AI-008 supported-impact
  gaps; ACT-002/ACT-004/ACT-005/ACT-007 escalated) ship visibly inside a
  validated package,
  exactly as the interview described normal practice. See the
  `DEC-PUBLICATION-STATUS` decision in `references/business-rules.md`.
- Exit codes: `0` = validated, `2` = ran to completion but blocked (binding
  source unavailable), `1` = hard failure before artifacts were written.

## Gotchas

- The hash chain is order-sensitive and encoding-sensitive: hashing the
  same snapshot dict with different key ordering produces a different hash
  unless you canonicalize (`snapshot_chain.py` does this via
  `sort_keys=True` -- don't bypass it if you change the hashing approach).
- `publication_status` only has three values (`validated`/`blocked`/
  `failed`) -- "shipped with an unresolved item" is deliberately folded
  into `validated` here (see above), not a fourth informal value.
- The internal policy source (SRC-POLICY) is a Notion page that renders
  entirely client-side: a plain HTTP GET returns `<title>Notion</title>`
  and no body, confirmed by inspecting the raw HTML directly (not just an
  AI-summarized fetch). A stdlib-only script cannot execute the JS that
  renders real content, so this source is captured from a manual-export
  local file (`references/internal-policy.md`) instead of a live URL --
  re-export that file by hand if the policy version changes.
- The stakeholder's interview said "8 documents" for the compliance source
  set, but the same answer's own wording implies 10 (it folds in the
  system/evidence/calendar registers). This skill treats the set as all 10
  named sources -- see `DEC-SOURCE-COUNT` in `references/business-rules.md`.
- Google Sheets are fetched via their public `export?format=csv&gid=0` URL
  with plain `urllib` -- no auth needed as long as the sheet stays
  link-shared. If sharing is tightened, retrieval will start failing with
  `retrieval_status: "unavailable"` rather than an exception.

## Quality guidelines

Adhere to the interview and business-rules discipline in
`references/business-rules.md`. Every judgment call not directly supported
by interview evidence appears in that file's Decisions log (and is mirrored
into the relevant stage snapshot's `decisions[]` array by
`build_review.py`), not just in code comments.
