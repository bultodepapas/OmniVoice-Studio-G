# Conditional investigation: dubbing translation readiness (#4347)

## Decision

Investigate promptly because the report describes expensive incorrect output. Before implementing, compare the active dubbing PR heads and agree on the remaining scope. The reviewed queue already changes the relevant frontend and backend files through [#4220](https://github.com/debpalash/VoiceStudio/pull/4220) and [#4221](https://github.com/debpalash/VoiceStudio/pull/4221).

If a minimal reproduction confirms a remaining gap and the active contributors are not handling it, promote this task ahead of the broader progressive-streaming work. Otherwise, attach the reproduction and acceptance cases to the existing work through a separately authorized contribution. See the [duplication audit](backlog-audit.md).

## Reported evidence

[#4347](https://github.com/debpalash/VoiceStudio/issues/4347) initially reports a translation error card with an ineffective Retry button while source-language detection remains unresolved. The reporter used a recent main build on Fedora/ROCm and supplied job-state fields: missing source language, `source_lang_detection_missing=true`, and a Portuguese target.

The [follow-up](https://github.com/debpalash/VoiceStudio/issues/4347#issuecomment-7081838333) reports 653 segments with no stored Portuguese translation, yet a target-language map containing the original text and approximately 10.4 hours of rendering. These are reporter measurements; they were not reproduced during this planning review. The volume and runtime demonstrate the potential impact if confirmed, not a benchmark for other machines.

## Source-confirmed relationships at the reviewed commit

All code references below are pinned to `2bb21302241793977055c44f7c52815bcbf0261e`.

| Surface | Observation | Implication to investigate |
|---|---|---|
| [dub-session.ts](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/dub/dub-session.ts) | Target switching chooses `translations[code]` or falls back to original/current text | Display fallback can look like a ready target-language segment unless readiness is tracked separately |
| [dub_translate.py](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/dub_translate.py) | `_resolve_source_lang` returns no language for an explicitly missing-detection state without an override; translation returns `source_language_required` | Repeating an unchanged request cannot resolve a missing language selection |
| [dub_generate.py](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/dub_generate.py) | `_sync_job_segments` stores generated request text in `segments_i18n` under the requested language code | The generate boundary must preserve the distinction between deliberate target text and source fallback |
| [dub-session.ts](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/dub/dub-session.ts) | `keepDubSourceText` explicitly records skipped translation, and editing/import helpers maintain several text/provenance states | Existing intentional source-language and manual-edit paths must remain supported |

These relationships are consistent with the report. They do not prove the complete end-to-end failure on current main or either draft PR head.

## Scope and sequencing

### Phase A — Ownership and head comparison

1. Reread #4347 and its comments, plus the latest #4220/#4221 discussion and changed-file lists.
2. Record the exact main and PR head SHAs used in each reproduction.
3. Run the same minimal fixture against main and each relevant PR head. Include the combined intended series state if the draft PRs depend on each other; do not assume isolated branches represent the intended product.
4. Determine whether one PR already adds translation readiness, actionable missing-language guidance, or generate guards.
5. Keep any separate proposal to the demonstrated residual behavior.

### Phase B — Reproduce with a minimal local fixture

Use a two- or three-segment synthetic job rather than a 66-minute video. Set the source language to unknown, preserve the missing-detection flag, choose a different target, and leave target translations absent. Exercise the renderer through target selection, Retry, and Generate. Record method/status/error-code/state transitions without retaining personal audio, logs, or credentials.

Separately call the API with a fixture representing the same state to determine whether the backend can independently prevent a misleading render. Preserve the route's existing authentication and job ownership behavior.

### Phase C — Choose the smallest correct behavior

Candidate behavior, to be confirmed with maintainers and the active series:

- A missing-language error directs the user to the source-language control and names the actual missing state.
- Retry becomes useful only after its prerequisite changes, or explicitly takes the user to that prerequisite.
- Target text readiness is separate from a display fallback. Selecting a target language alone does not certify original text as translated.
- Generation validates the requested operation before queuing expensive model work or marking target-language text as complete.
- Explicit source-language narration, imported/manual target text, and same-language workflows remain possible through intentional state.

**Do not use source-text equality alone as proof that translation is missing.** Proper names, numbers, code, and valid translations can remain identical. The correct evidence is the presence/provenance and intent of the target text, with compatibility for existing jobs and manual edits.

Avoid guessing a missing source language from the selected target or rewriting old saved jobs without an explicit migration/compatibility design. The upstream report contains suggestions, not an approved implementation contract.

## Acceptance matrix

| Case | Required observable behavior |
|---|---|
| Unknown source, no target translation | Clear actionable state; no accidental render labeled as completed target translation |
| Source selected explicitly after failure | Retry uses the new source, clears stale failure state, and stores an actual target result |
| Known source, successful translation | Existing translation and generation remain functional |
| Some segments translated, some missing | The unresolved subset is visible; generation policy is explicit and consistent on client and server |
| A valid translation equals the source text | Accepted when provenance/intent establishes it as valid |
| Manual target text or imported translated captions | Preserved and accepted through the supported editing/import workflow |
| Explicit keep-source / same-language narration | Supported without pretending a different-language translation happened |
| Switch between multiple targets | Readiness and text belong to the selected target; no stale cross-language state |
| Restore/resume an older project | Existing data remains readable; ambiguity becomes actionable rather than silently certified |
| Direct API request bypassing the renderer | Server preserves the same operation semantics and avoids inappropriate target-state mutation |
| Rejected generation | No queued expensive work and no false completed-target history or translation state |

## Existing tests to inspect and extend

- [dub-session.test.ts](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/dub/dub-session.test.ts)
- [dub-source-language.test.ts](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/dub/dub-source-language.test.ts)
- [dub-translation-errors.test.ts](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/dub/dub-translation-errors.test.ts)
- [test_dub_source_lang_1960.py](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_dub_source_lang_1960.py)
- [test_dub_source_language_hint.py](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_dub_source_language_hint.py)
- [test_dub_translate.py](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_dub_translate.py)
- [test_dub_qc_track_language.py](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_dub_qc_track_language.py)

The inspected tree confirms these paths exist; this planning review has not executed them. Check their actual fixtures before adding a test, and follow the current series' evolving contract if it lands.

## Completion / stop criteria

An independent implementation is justified only after the reproduction and overlap review establish remaining work. If an existing PR handles the failure, the useful output is its reproduction evidence and missing acceptance cases. If a separate fix is needed, keep UI retry guidance and generation-readiness enforcement separately reviewable unless the same contract change requires both together.

The final evidence should show the original failure on the applicable baseline, the corrected workflow, preserved intentional source/manual-translation paths, and absence of expensive generation or incorrect state mutation on rejected requests. A short fixture is sufficient; repeating the reporter's multi-hour render is unnecessary.

