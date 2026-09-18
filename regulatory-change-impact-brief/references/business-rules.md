# Business Rules (from the stakeholder interview + confirmed sources)

Filled from the real Project B stakeholder interview transcript and the
disclosed source documents the interview named, cross-checked live where
each source allows it. Every rule below cites the interview language,
the internal policy text (`references/internal-policy.md`), or the
fetched regulatory text that supports it. Anything not directly
supported is in the Decisions log at the bottom, with rationale and
tradeoffs, per the schema's `decisionRecord` shape.

## Stage 1 -- scope

- **Trigger / cadence**: reviews are driven by formal review cycles and
  scheduled calendar actions coordinated across Operations, Legal, and
  system owners -- not ad hoc or left to the Compliance Manager's
  discretion ("not merely left to my personal discretion, nor is it an
  ad-hoc task"). The interview did not disclose a closed list of
  distinct trigger *types* beyond "organization-wide reviews set for
  specific as-of dates" -- treated as a single review type (see
  Decisions log).
- `review_type`: single fixed value used for this run --
  `"Article 50 transparency obligation impact review"`. No second
  review type was evidenced in the interview.
- `as_of`: `2026-08-26T00:00:00Z` -- the interview's explicit
  "as of 26 August 2026" date, confirmed independently by the internal
  policy doc's own "Business observation date: 26 August 2026" and by
  the SYSTEMS/EVIDENCE/CALENDAR sheets' shared `record_version` /
  `source_version` tag `*-2026-08-26`.
- `systems_in_scope`: all eight registered systems (`AI-001`..`AI-008`).
  The interview named AI-007/AI-008 only as examples, but the internal
  policy's operating-facts section states the EU programme team
  "administers all eight registered uses for its professional work,"
  and the live SYSTEMS sheet lists exactly eight rows.
- `audiences`: `["Legal", "Operations"]` -- the package's two named
  recipients ("I send the completed review package to Legal and
  Operations"). System owners are contributors of facts, not
  recipients of the package, so they are not listed as an audience.
- `approval_gates`: `["Legal interpretation and exception approval",
  "Operations activation and closure approval"]` -- matches both the
  interview ("Legal retains final interpretive authority and
  Operations retains activation and closure authority") and the
  internal policy's "Approval boundary" section verbatim ("Legal owns
  final interpretation... Operations owns policy activation and
  operational deadlines").

## Stage 2 -- source-capture

Ten sources total (interview said "8," but its own follow-up answer
folded in system/evidence/calendar registers -- see Decisions log).

| id | source_role | authority | locator | retrieval |
|---|---|---|---|---|
| SRC-LAW | official-guidance | advisory | ai-act-service-desk.ec.europa.eu/en/ai-act/article-50 | live GET; plain-language Art. 50 restatement, dated "Official version of 13 June 2024" |
| SRC-OJ | binding-regulation | binding | eur-lex.europa.eu/eli/reg/2024/1689/oj/eng | live GET; original OJ publication of Reg. (EU) 2024/1689, 12.7.2024 |
| SRC-AMEND | binding-regulation | binding | eur-lex.europa.eu (OJ L 2026/1744, "Digital Omnibus on AI") | live GET; in force 27 July 2026, amends Art. 50 |
| SRC-CONSOLIDATED | binding-regulation | binding | eur-lex.europa.eu CELEX:02024R1689-20260727 | live GET; consolidated text as of 27 July 2026 |
| SRC-POLICY | internal-policy | internal-control | Notion (private-pecorino-70e...) | **manual export** -- see decision below; local copy at `references/internal-policy.md` |
| SRC-FAQ | official-guidance | advisory | digital-strategy.ec.europa.eu FAQ | live GET; "Last Updated: 24 July 2026" |
| SRC-TIME | official-guidance | advisory | ai-act-service-desk.ec.europa.eu implementation timeline | live GET; no last-updated marker on page (noted, not treated as stale by itself) |
| SRC-SYSTEMS | operational-record | operational-evidence | Google Sheet (system register) | live CSV export fetch |
| SRC-EVIDENCE | operational-record | operational-evidence | Google Sheet (incident/evidence register) | live CSV export fetch |
| SRC-CALENDAR | operational-record | operational-evidence | Google Sheet (compliance calendar) | live CSV export fetch |

- **Retrieval mechanism**: Google Sheets are fetched via their public
  `export?format=csv&gid=0` URL and parsed with stdlib `csv` --
  confirmed working with a plain `curl`/`urllib` GET, no auth needed.
  EU-site pages are fetched as raw HTML via stdlib `urllib`; the script
  does not do full HTML parsing -- it hashes the retrieved bytes for
  the audit trail and checks for an expected marker string (e.g.
  `"Article 50"`, `"2026/1744"`, the sheet's own version date) to set
  `retrieval_status`. POLICY is read from the local manual-export file;
  its `locator` field still records the original Notion URL for audit
  identity, `local_reference` points at the file.
- **Stale / unavailable, per source**: for the sheets, staleness is
  keyed to the `*_version` column disagreeing with the run's `as_of`
  source-version tag (`2026-08-26`); "unavailable" is HTTP failure or
  empty body. For the EU pages, "stale" isn't independently checkable
  without a second historical fetch to diff against, so the script
  only distinguishes retrieved (marker found) vs. invalid/unavailable
  (HTTP failure or marker missing) -- documented as a scope limit, not
  silently treated as "stale never happens."

## Stage 3 -- authority-and-timing

- **Binding vs. advisory vs. guidance, in practice**: OJ / AMEND /
  CONSOLIDATED are `binding` (they are the enacted regulation and its
  amendment). LAW and FAQ and TIME are `advisory` / `guidance_context`
  -- they restate or interpret the binding text but are not themselves
  the enacted law. POLICY is `internal-control` -- it binds Quillhaven
  internally but is not itself a source of EU statutory obligation.
- **Timing**: Article 50 applies from **2 August 2026** (TIME, FAQ).
  A **4-month transitional period to 2 December 2026** applies
  specifically to the Article 50(2) machine-readable-marking
  obligation, for providers whose systems were already placed on the
  EU market before 2 August 2026 (AMEND recital 38 + Art. 1(41); FAQ's
  "grace period... 2 December 2026" answer; TIME's Dec-2026 milestone).
  This grace is scoped to 50(2) marking only -- it does not extend to
  Art. 50(1) direct-interaction notice, 50(3) biometric/emotion
  disclosure, or 50(4) deepfake disclosure, none of which carry a
  stated transitional date.
- **Authority blocker (real, found in the fetched sources, not
  invented)**: `BLOCKER-LAW-ART50-7` -- LAW's Article 50 text (dated
  "Official version of 13 June 2024") still describes the Commission's
  power to adopt implementing acts approving codes of practice under
  Art. 50(7). AMEND (in force 27 July 2026) and CONSOLIDATED (as of
  27 July 2026) both confirm that empowerment was **removed**. LAW is
  therefore stale relative to the currently governing text. This
  doesn't change any of the eight systems' analysis below (none turn
  on Art. 50(7)), but it means LAW cannot be relied on as the
  authoritative current text without cross-checking CONSOLIDATED/AMEND,
  and is flagged for Legal's attention on that basis alone.

## Stage 4 -- evidence-reconciliation

Policy controls, drawn directly from `references/internal-policy.md`:

| id | control |
|---|---|
| CTRL-NOTICE | Clear notice before/at first interaction unless AI nature is obvious from context |
| CTRL-MARKING | Public synthetic image/audio/video must retain machine-readable provenance where the tool supports it, plus a visible label from Communications, unless Legal approves a documented exception |
| CTRL-ATTRIBUTES | Every registered system must record owner, use, exposed group, disclosure status, human-review path, evidence reference |
| CTRL-EXCEPTION | An exception requires named owner, rationale, expiry date, and Legal approval; the automation may draft but not approve one |

Incident/evidence records are the ten `REC-###` rows fetched live from
SRC-EVIDENCE, used as-is (see the CSV in the source-capture stage --
`evidence_state` values found: `complete`, `missing`, `conflicting`,
`stale`, `partial`).

- **What a `conflict` looks like (real examples, not hypothetical)**:
  REC-003 (AI-003) -- "Visible label exists but exported platform copy
  may have lost metadata," `evidence_state: conflicting`. REC-008
  (AI-007) -- "Owner says a banner exists but the current capture
  shows none," `evidence_state: conflicting`. Both are direct
  contradictions between two accounts of the *same* fact, which is
  the distinguishing feature vs. an evidence gap.
- **What an `evidence_gap` looks like**: REC-002 (AI-002, `missing`) --
  no evidence recipients are told generated text was used. REC-005
  (AI-005, `stale`) -- the provider-role questionnaire predates the
  current release. REC-009 (AI-008, `partial`) -- visible label
  verified but machine-readable provenance not checked. REC-010
  (AI-008, `missing`) -- exception request has no Legal approval or
  expiry date. These are missing/stale/incomplete proof, not two
  sources actively disagreeing.
- **Who resolves a conflict**: not one fixed role -- it depends on the
  kind of gap. Named system owners correct the underlying facts (e.g.
  Marketing for REC-008, Communications for REC-009/REC-010);
  interpretive or exception-approval questions escalate to Legal (e.g.
  REC-010's missing Legal approval); Operations owns scheduling the
  correction and eventual activation/closure. This is the interview's
  own description of the approval boundary, applied per-record rather
  than assumed to be a single owner for every gap.

## Stage 5 -- impact-analysis

This is the one stage where the four enum values are **not**
symmetrical, per the SKILL.md warning -- each system landed on its
state for a different underlying reason. Mapping rule used
(documented, not hardcoded per-system guesswork): if Article 50
applies to a system given its actual technical/use-case facts (from
the internal policy's operating-facts section + the SYSTEMS row), the
linked EVIDENCE record's `evidence_state` decides the impact state --
`complete` maps to `supported-impact` (if the evidenced fact IS a gap)
or `supported-no-impact` (if the evidenced fact shows compliance);
`conflicting` maps to `conflicting`; `missing`/`stale`/`partial` maps
to `unresolved` -- *unless* Article 50 doesn't apply to that system's
actual use at all, in which case the system is `supported-no-impact`
regardless of any open internal-hygiene evidence gap, because the
underlying statutory trigger isn't present.

| system | applicable Art. 50 provisions | state | why |
|---|---|---|---|
| AI-001 | 50(1) notice, 50(5) timing | **supported-no-impact** | REC-001 `complete`: notice screenshot and release record agree |
| AI-002 | *none* -- narrowed out | **supported-no-impact** | Advisor reviews/edits and personally sends; applicant never converses with the AI, and an individual admin reply isn't material published to inform the public. 50(1)/(4) don't trigger on these facts. REC-002's `missing` evidence gap is a policy-hygiene item, not an Art. 50 gap -- tracked as ACT-003 pending Legal confirmation of this reading, not treated as a legal violation |
| AI-003 | 50(2) marking (public synthetic image; not an assistive-editing/minor-correction exemption) | **conflicting** | REC-003 `conflicting`: label present, but whether machine-readable provenance survived export is actively disputed. (Also within the Art.50(2) transitional window to 2 Dec 2026, since the product entered the EU market 1 June 2026 -- not yet a missed deadline, but unresolved) |
| AI-004 | 50(1) notice, 50(5) timing | **supported-impact** | REC-004 `complete` evidence that is itself the gap: "First interaction contains no AI notice" |
| AI-005 | undetermined | **unresolved** | provider_role is `unknown`; REC-005 questionnaire is `stale` and predates the current release; whether the flagging even uses biometric/emotion inference is unestablished -- can't determine which Art. 50 paragraph governs, let alone compliance |
| AI-006 | *none* -- out of scope | **supported-no-impact** | Internal-only staff tool, not published, no synthetic media, restricted to staff workspace; REC-007 `complete`/closed |
| AI-007 | 50(1) notice (public exposed group) | **conflicting** | REC-008 `conflicting`: owner asserts a banner notice exists, current capture shows none |
| AI-008 | 50(2) marking + 50(4) deepfake-style disclosure (real presenters, altered speech, public programme communication, no artistic/editorial exemption) | **supported-impact** | REC-009 `partial` (provenance untested) *and* REC-010 `missing` (the exception meant to excuse the marking gap is itself incomplete -- no Legal approval, no expiry). Net evidenced conclusion: neither the marking requirement nor a valid exception is currently satisfied. The 50(4) deepfake-disclosure duty (distinct from 50(2) marking) carries no transitional grace and has applied since 2 Aug 2026, so this is a present gap, not merely a future deadline |

- **Who has authority to assign the classification**: the Compliance
  Manager documents the *supported* classification from the evidence
  and rules as a draft; Legal confirms or overrides the interpretation
  (this is explicit in the interview and in the internal policy's
  approval boundary). None of the above states are final until Legal
  signs off -- that is why every `approval_requirements` record in
  stage 6 for an affected system starts `pending`, even where the
  evidence strongly supports one reading.

## Stage 6 -- actions-and-approvals

`proposed_actions` are the eight rows fetched live from SRC-CALENDAR
(`ACT-001`..`ACT-008`), used as-is -- shape is `{system_id, action,
owner, due_date, status, approval_required}`.

- **`approval_requirements`**: one per action, `status` is `pending`
  for all eight as of 2026-08-26 -- none have been approved or
  rejected yet in any source. `approval_required` (`legal` /
  `operations`) from the sheet decides who the gate belongs to.
- **What triggers an `escalation`**, vs. a normal approval step: resolved
  by stakeholder follow-up. Quoted: an ordinary approval step is a
  completed draft package going to Legal/Operations "for their routine
  review, sign-off, or feedback"; an escalation is "blocked progress,
  conflicting evidence that system owners cannot resolve on their own,
  unapproved exceptions, or missing required legal and operational
  inputs that prevent us from forming a valid compliance position" --
  in those cases "the unresolved gap must be explicitly highlighted for
  formal intervention rather than processed as a routine sign-off."
  Mapped onto structured fields (see `DEC-ESCALATION-RULE` below), this
  run escalates: `ACT-002` (AI-007, conflicting evidence), `ACT-004`
  (AI-003, conflicting evidence), `ACT-005` (AI-005, unresolved --
  missing inputs prevent a position), and `ACT-007` (AI-008, blocked
  *and* an unapproved exception on a Legal-gated action). `ACT-006`
  (AI-008's other action, completing a provenance test) stays a normal
  step -- Communications can execute it without formal intervention,
  which is exactly the routine/escalation line the stakeholder drew.
  `ACT-001`, `ACT-003`, `ACT-008` stay normal for the same reason: each
  has a clear, owner-executable position already.

## Stage 7 -- publication-validation

- `artifacts`: `impact-register.csv`, `compliance-brief.md`,
  `action-calendar.ics` -- confirmed by the README's "Final artifacts"
  section, consistent with the interview's three-part package
  description.
- `validation_checks`: every snapshot passes `snapshot.schema.json`;
  the predecessor hash chain is intact end-to-end; the register,
  brief, and calendar agree with stages 06-07 (same action/impact IDs,
  same states); all four binding-regulation sources (OJ, AMEND,
  CONSOLIDATED -- and LAW as advisory) were successfully retrieved.
- **`publication_status` when items still ship unresolved (the open
  question this file used to flag)** -- resolved as an explicit
  decision below: `validated` describes the package's own
  well-formedness (schema-valid, hash-chain intact, artifacts
  internally consistent), not that every question has been answered.
  Unresolved/conflicting *items* stay visible inside a `validated`
  package. `blocked` is reserved for when a *binding* source
  (OJ/AMEND/CONSOLIDATED) is itself unavailable/invalid, per the
  README's explicit rule that unavailable binding evidence blocks
  formal impact conclusions -- that did not happen on this run.
  `failed` is reserved for a hard schema/lineage break.

## Decisions log

### Decision: treat all 10 named items as the source set, not "8"
Rationale: the interview said "8 documents" but its own next answer
described the set as covering "legal texts, guidance, internal policy,
system inventories, evidence records, and action calendars" -- which
only adds up if SYSTEMS/EVIDENCE/CALENDAR are included, i.e. 10 total.
The stakeholder confirmed this reading directly when asked.
Tradeoffs:
- If a genuine 8th legal/guidance document exists that wasn't named,
  this run would miss it silently. No such document surfaced in any
  of the fetched content, so this is treated as the interview's
  wording being loose, not a missing source.

### Decision: POLICY is a manual-export local reference, not a live fetch
Rationale: direct `curl` of the Notion URL returns a client-rendered
shell (`<title>Notion</title>`, generic description, no page body) --
confirmed by inspecting the raw HTML, not just an AI-summarized fetch.
A stdlib-only script cannot execute the JS that renders real content,
so a "live fetch" of this URL would produce the same empty result
every run, which is indistinguishable from a permanent outage and
would incorrectly block the whole package if treated as a required
live binding-adjacent source. Confirmed with the stakeholder.
Tradeoffs:
- The script cannot detect if the Notion page's *content* changes
  between runs the way it can for the CSV/HTML sources. Re-exporting
  this file is a manual step the operator must remember to do when
  the policy version changes -- mitigated by the version string
  (`AI-POL-2026-08-15`) being checked against what's on file.

### Decision: `DEC-ESCALATION-RULE` -- operationalizing the stakeholder's escalation definition
Rationale: the stakeholder's confirmed follow-up answer defines
escalation as "blocked progress, conflicting evidence that system
owners cannot resolve on their own, unapproved exceptions, or missing
required legal and operational inputs that prevent us from forming a
valid compliance position," as against an ordinary approval step being
a "routine review, sign-off, or feedback." Each clause is mapped to a
structured field already computed this run, not to matching the
action's free-text description (which would be fragile and guessy):
`status == "blocked"` (blocked progress); the action's system has an
`evidence_state == "conflicting"` record (conflicting evidence a
system owner alone hasn't resolved); the system has a
`record_type == "exception_request"` record that isn't `complete`
**and** the action itself is `approval_required == "legal"` (unapproved
exception -- scoped to the Legal-gated action specifically, since an
exception literally requires Legal approval per `CTRL-EXCEPTION`, not
every action that happens to touch the same system); the system's
stage-5 impact `state == "unresolved"` (missing inputs -- we could not
even form a position, let alone act on it routinely).
Tradeoffs:
- Scoping the exception trigger to `approval_required == "legal"`
  correctly separates AI-008's two actions (`ACT-007` reviewing the
  exception vs. `ACT-006` completing a routine provenance test
  Communications can do on its own), but relies on `approval_required`
  being coded correctly per action -- a miscoded action could hide a
  real escalation or falsely raise one.
- A conflicting-evidence system escalates every action tied to it, not
  just the one addressing that specific record. On this run every
  conflicting system (AI-003, AI-007) has exactly one action, so this
  hasn't been tested against a system with multiple actions where only
  one actually addresses the conflict.

### Decision: `publication_status` = `validated` with unresolved items inside
Rationale: the README explicitly frames "insufficient or conflicting
applicability evidence stays unresolved... " as a normal non-happy-path
outcome distinct from "unavailable binding evidence blocks formal
impact conclusions" -- only the latter is described as blocking. The
interview itself treats shipping a package with open items as routine
("cases with unresolved evidence... do not automatically resolve just
because I file my findings").
Tradeoffs:
- This means `validated` does not mean "fully resolved" -- a reader of
  just the top-level `publication_status` field, without opening the
  register, could mistake it for a clean bill of health. Mitigated by
  requiring the register/brief to surface every unresolved/conflicting
  item explicitly, and by stage 7's own `unresolved` array.

### Decision: AI-002 and AI-006 are `supported-no-impact` despite open
### CALENDAR/EVIDENCE items
Rationale: the internal policy's operating-facts section gives
specific, evidenced reasons Article 50 doesn't trigger on these two
systems' actual use (no direct AI-to-person interaction for AI-002;
no publication/public exposure for AI-006), independent of whether
supporting internal evidence (REC-002, disclosure-practice logging) is
itself complete. Non-applicability and evidence-completeness are
different questions; only the first one determines the impact state
here.
Tradeoffs:
- If Legal disagrees with the non-applicability reading (e.g. decides
  the applicant-facing email *does* count as a form of direct AI
  interaction), AI-002 would flip to a different state entirely. That
  is exactly why ACT-003 exists as a pending Legal-confirmation action
  rather than the register treating this as closed.
