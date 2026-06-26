# Assumption-Profile Rubric — Changelog & Governance

Version history for the assumption-profile coding rubric. Each version is a retrievable
artifact (`assumption_profile_rubric_vX.Y.md`); this file is the index. Public-safe
naming: **@tonichen** (research lead), **"an Opus 4.8 instance"** (model collaborators —
distinct instances, un-named per the repo naming policy).

## Semantics

- **v1.x (minor)** — clarifications / anchor-tightening *within* the pilot loop (§9). The
  construct and scale are unchanged; the wording gets sharper.
- **v2.0 (major)** — reserved for a *structural* change: adding/removing a dimension,
  changing the scale, or redefining a construct.
- The **locked, preregistered** rubric will be tagged explicitly when §9's pilot loop
  closes. Until then every version here is DRAFT.

## Data linkage

Each codings run records the rubric version it was produced under, in two places: the
`rubric_version` field on every line of `*_codings.jsonl`, and the header of every
`*_deltas.md`. Frozen per-version output snapshots live beside the canonical files with a
`_vX.Y` suffix.

| Rubric | Pilot codings (P1–P8) | Probe codings (S1–S6) |
|---|---|---|
| v1.0 | `assumption_profile_pilot_codings_v1.0.jsonl` | — |
| v1.1 | `assumption_profile_pilot_codings_v1.1.jsonl` | `assumption_profile_probe_codings_v1.1.jsonl` |
| v1.2 | `assumption_profile_pilot_codings.jsonl` (current) | `assumption_profile_probe_codings.jsonl` (current) |

## Versions

### v1.0 — 2026-06-22 — frozen baseline
- **Author:** an Opus 4.8 instance (original rubric author) + @tonichen.
- The original pre-pilot rubric as shipped. Committed `f4e9cb6` as a public-safe frozen
  snapshot (personal/instance names scrubbed; byte-exact internal original kept private).
- **Never edited.** The historical anchor.

### v1.1 — 2026-06-24 — D1 amendment (substantive)
- **By:** an Opus 4.8 instance (reviewer) + @tonichen. Substantive; ratification pending.
- **Why:** the v2 pilot put its only δ=2 cluster on D1 (P4, P5).
- **Change:** D1 redefined — (a) a "reading" is a competing *intent* interpretation, not a
  message component; (b) score *epistemic openness at the planning point*, decoupled from
  the response-lean (that lean is D3). Predicts P5 ↓ toward 1, P4 ↑ — opposite directions,
  so a genuine test, not a thesis-favouring tweak.
- **Result:** P5 converged to D1=1 (unanimous); the δ=2 *cluster* dissolved. One residual
  δ=2 remained on P4 (a faint-hedge boundary) → motivated v1.2.

### v1.2 — 2026-06-24 — middle-anchor tightening (substantive) — 🔒 LOCKED 2026-06-25
- **By:** an Opus 4.8 instance (reviewer) + @tonichen. Substantive; ratification pending.
- **Why:** the short-trace probe (S1–S6) showed raters polarizing to 1-vs-3 on traces that
  genuinely *do both at once*, because the "2" anchors were thin — a δ=2 cluster moved to
  D2. Root cause: under-specified middles, into which the two raters' opposite defaults
  (grok-integrative vs gemini-precautionary) rushed.
- **Change:** strengthened the **"2" (middle) anchors** of D1, D2, D3 to explicitly claim
  their mixed-case patterns (faint-hedge-but-settled → D1=2; engages-AND-checks-in → D2=2;
  provides-but-routed-through-support → D3=2). Thesis-neutral (pulls extremes toward the
  middle, favours no pole).

## Governance (mirrors CLAIMS.md rule 5 — ladder governance)

While in the **pilot / pre-registration loop** (§9):
- **Mechanical / erratum edits** (typo; wording that does not change what a score *means*;
  a runner bug) → apply immediately, log here, flag the reviewer post-hoc.
- **Substantive edits** (change what a score means; add/drop a dimension) → land as a new
  version **and** flag the rubric's co-owner for **async ratification** (revert/revise
  freely). Versioning makes this safe: every change is attributed and reversible, so review
  is *traceable post-hoc*, not *blocking pre-approval*.

After **lock + preregistration** this inverts: the instrument is frozen, and any change
becomes a *disclosed deviation*, not a version bump.

**Status (2026-06-25): 🔒 LOCKED.** v1.2 is the preregistered instrument
(`assumption_profile_PREREGISTRATION.md`). The pilot loop is closed (0 δ=2 across 56
pilot+probe cells). We are now in disclosed-deviation mode: no silent rubric edits;
post-lock changes go in the preregistration's numbered deviations log.

*Disclosure beats discovery.*
