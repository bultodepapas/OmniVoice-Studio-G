# VoiceStudio: product and creator workflow research

## Scope and current state

Research snapshot: **22 November 2026, 17:13:24 UTC / 12:13:24 America/Bogota**. Upstream [main](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/README.md) remains `2bb21302241793977055c44f7c52815bcbf0261e`. The 15 open PRs have the same heads as at the research start. The issue collection read at 17:08 UTC contained 29 open issues plus those 15 PRs; new [#4355](https://github.com/debpalash/VoiceStudio/issues/4355) concerns low-VRAM OmniVoice memory release and belongs to the performance track.

This is read-only product research. The four proposals below are **feature hypotheses**, not maintainer-approved issues. They are ranked by the strength of the inspected gap, likely usefulness, and ability to extend existing workflows. No product changes, GitHub writes, model runs, user interviews or external-editor compatibility tests were performed. Historical PR test claims are evidence of intended coverage, not fresh verification.

Inspected material includes README, current Electron feature docs, the complete 4,990-entry repository tree, and 43 distinct source/document files covering Compare Voices, take metadata, project persistence, project bundles, longform generation/history and dubbing draft/edit/export. Absence findings are bounded to those surfaces and the stated searches; unpublished work can exist.

## Recommendation

**Research durable audition sessions first, then saved project revisions.** Both have clear current implementation boundaries and can start outside the active dubbing work. External-editor interchange is a valuable discovery track if creators confirm a specific target workflow. Human review notes are a smaller product experiment but have weaker demand evidence.

| Priority | Research candidate | Existing-gap confidence | Relative implementation effort | Demand evidence |
| --- | --- | --- | --- | --- |
| 1 | Durable audition sessions and selected takes | High for missing session/group/decision persistence | Medium; trustworthy rerender depends on the provenance work | Existing take-history PR explicitly describes trial-and-error generation; incremental session demand still needs validation |
| 2 | Saved project revisions with diff and restore-as-copy | High for current single-draft project storage | Medium to high; storage/lifecycle rules matter | Prior project-creation request documents fear of losing earlier work; it does not itself request revision history |
| 3 | Editable timeline handoff to a selected external editor | High for absence in the inspected export implementation; compatibility unknown | High until one target format/editor is validated | Product hypothesis; no direct matching issue found |
| 4 | Human review notes and approval tied to the exact segment/audio version | Moderate to high for absence in inspected editor contracts | Medium for one local workflow; high for collaborative/cloud scope | Product hypothesis; no direct matching issue found |

### Capabilities that should not be proposed again

- **Two-voice A/B generation already exists.** [CompareVoices](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/tools/compare-voices.tsx) generates the same phrase sequentially with two selected saved voices/presets. It uses the current clone settings and profile seeds, has readiness/error handling, and previews both results.
- **Take history already preserves useful work.** Merged [#1052](https://github.com/debpalash/VoiceStudio/pull/1052) added replay, starring, restore and bounded retention that protects starred takes. Current [take settings](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/lib/store/takes.ts) retain per-take settings for the latest 200 entries in local storage, and [take details](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/clone/take-details.tsx) display/reuse settings. Merged [#3355](https://github.com/debpalash/VoiceStudio/pull/3355) added a shared player that survives page navigation. The new proposal is not “save takes” or “add A/B.”
- **Targeted work and recovery already exist.** [Longform docs](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/docs/electron-longform.md) describe line/chapter auditions, content-addressed reuse, render metadata, explicit resume and rolling runtime ETA. [Dubbing docs](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/docs/electron-dubbing.md) describe partial regeneration, per-language speech fingerprints, fitting provenance and a 50-state undo/redo stack.
- **Project handoff already exists.** Merged [#3357](https://github.com/debpalash/VoiceStudio/pull/3357) and the current [bundle service](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/project_bundle.py) exchange editable `.vsproject` archives containing scripts, casts, pronunciation data, dub timelines, references and SHA-256-checked assets. Desktop/mobile handoff is not a missing feature.
- **Output delivery already has many formats.** [Dubbing exports](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/dub_export.py) include audio/video, SRT/VTT/ASS/TXT, segment ZIPs and stems; Stories can export character stems, and longform can export chapter cue sheets. The residual external-editor proposal is structured timeline interchange.

## 1. Durable audition sessions and selected takes

### User problem and exact residual

A creator can compare two voices, generate additional takes, star individual results and reopen their settings. The remaining problem is preserving **which candidates belonged to the same creative decision, under which common script, and which one was chosen**.

Current [comparison-state.ts](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/tools/comparison-state.ts) is a module-level TanStack store containing only text, two voice IDs, search strings and object URLs. It has no durable session ID, candidate take IDs, saved decision or persistence adapter. [CompareVoices.run](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/tools/compare-voices.tsx#L62-L108) clears both comparison URLs at the start of a new run and replaces each slot with a fresh blob URL. Results may still exist in normal History; what is missing is their durable relationship and selection.

**Proposed first slice:** save a named audition session for one script, attach two or more existing/generated take IDs, keep their recorded recipe references, mark a selected take, and reopen the session after restart. Reuse the existing player and history. Keep generation on the currently active engine in the first slice; cross-engine benchmark orchestration belongs to the quality/evaluation track.

### First investigation and proof

1. Trace how `generateClone` returns the history ID and how History retention/deletion treats referenced WAVs. Establish whether session membership can safely reference the existing take without copying audio.
2. Create a disposable mocked session using two current History records. Reload the renderer, reopen the session and play the exact same saved audio.
3. Ask creators to compare their current star-and-history workflow with the session prototype. The key observation is whether they can recover a decision and its alternatives later without re-generating or reconstructing settings.

### Acceptance signals

- Reload restores the session's script, candidate identity, exact saved audio and selected take.
- Adding a third candidate does not replace the first two or synthesize them again.
- Normal history pruning cannot silently destroy a retained candidate; the pin/reference policy is explicit, and intentional deletion is handled clearly.
- Switching voice settings or model makes a new candidate; old candidate metadata is not rewritten.
- Unsupported/cancelled generation preserves already completed candidates.
- Selecting a winner can reuse the existing profile/take workflow without changing application preferences such as autoplay.
- Keyboard navigation and all current locale catalogs support the added controls.

### Coordination, dependencies and effort

**Medium**, if scoped to session grouping and decisions. No open PR specifically implements this workflow in the inspected queue. [#4216](https://github.com/debpalash/VoiceStudio/pull/4216) changes shared voice selection behavior, so avoid rebuilding the picker. The immutable generation-receipt proposal in the quality research is the prerequisite for making strong rerender/provenance promises. A seed alone does not guarantee identical audio across model/runtime/hardware changes.

Existing [#1052](https://github.com/debpalash/VoiceStudio/pull/1052) is the relevant foundation: its description explicitly states that generation is an iterative, try-until-it-sounds-right process. It already solved lost individual takes; this proposal addresses decision context.

## 2. Saved project revisions with diff and restore-as-copy

### User problem and exact residual

A creator revises dialogue, casting, pronunciation or settings after a successful render, then needs to recover an earlier editorial choice. Current projects support saving, reopening, renaming and manual copies, but an overwritten project does not expose a revision timeline.

The current [Electron project library](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/longform/project-library.ts) stores one `draft` and `updatedAt` per project ID. Saving constructs a new project record and replaces the previous record with that ID. The [IndexedDB adapter](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/shared/utils/indexedDbLongformStore.ts) has a monotonic writer revision field, but that is concurrency metadata, not a collection of recoverable editorial versions. The current [backend project PUT](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/projects.py#L53-L66) likewise overwrites a single `state_json`.

This must be distinguished from [dubbing's undo stack](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/dub/dub-session.ts#L403-L489), manual Save as copy, output history and interrupted-job checkpoints. Those capabilities already exist.

**Proposed first slice:** explicit named revisions for saved Stories/Audiobook projects, with a small diff of script/cast/production changes and **restore as a new copy**. Begin with explicit checkpoints on save/render rather than saving every keystroke. Defer dubbing and cross-device revision exchange until the lifecycle is proven.

### First investigation and proof

1. Map the durable project write queue, output ownership and bundle import/export path. Define whether a revision promises editable input recovery, retained audio, or both.
2. Using disposable data, save revision A, edit text/cast into B, reload, inspect their differences and restore A as C. Confirm B and its result reference remain intact.
3. Test missing voice profiles, unavailable backend results, failed IndexedDB writes, schema upgrades and interrupted writes. Existing generated media must not be silently deleted or treated as regenerated.

### Acceptance signals

- A restored copy reproduces the saved script, cast, pronunciation and production settings.
- A failed revision write leaves the prior durable project readable.
- Rename-only changes can be distinguished from synthesis-affecting edits.
- Diffs use stable line/character identities; line reordering does not appear as wholesale deletion/recreation.
- Storage limits and pruning are visible, and a chosen checkpoint cannot disappear through an unrelated cleanup.
- Missing referenced media/voices produce a precise state; restoring inputs does not claim that the original waveform can be reproduced.
- Older project records still load, and exporting a normal `.vsproject` continues to work.

### Coordination, dependencies and effort

**Medium to high**. Start in the current Electron `project-library.ts` to avoid turning this into a simultaneous backend/mobile migration. Coordinate public format changes with the maintainers of [#3357](https://github.com/debpalash/VoiceStudio/pull/3357) and current bundle contracts. The active dubbing series [#4217](https://github.com/debpalash/VoiceStudio/pull/4217)–[#4221](https://github.com/debpalash/VoiceStudio/pull/4221) owns adjacent project/editor flows; defer that integration or agree on boundaries.

Merged [#4055](https://github.com/debpalash/VoiceStudio/pull/4055) responded to a user who previously had to copy, rename and clear a book manually, risking the original. That particular problem is already fixed by New project. It is contextual evidence for preservation concerns, not proof that maintainers requested version history.

## 3. Editable timeline handoff to one external editor

### User problem and exact residual

A creator finishes synthesis in VoiceStudio but wants to adjust the final mix or timing in an audio/video editor. Current stems and clip ZIPs provide audio, and `.vsproject` provides VoiceStudio-native editability. An external editor still needs a machine-readable placement/track structure for those clips.

In the inspected [segment ZIP route](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/dub_export.py#L2397-L2426), exports contain discovered WAVs named with segment order, rounded start/end values and speaker. The route does not emit an external timeline interchange document. Current [project bundles](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/project_bundle.py#L26-L27) explicitly use the native `voicestudio.project` format/version. The complete tree and inspected export sources did not reveal OpenTimelineIO, FCPXML, AAF or EDL adapters; relevant PR searches for OpenTimelineIO, FCPXML and EDL returned zero results.

**Proposed residual:** a one-way, editable timeline export for a **single selected target format/editor**, reusing existing segment/stem exports. Include stable clip IDs, selected language, speaker tracks, placement, mute/gain, source-vs-fitted timing and asset references. OpenTimelineIO is an investigation candidate, not a claim of compatibility with every editor. Do not start with round-trip import.

### First investigation and proof

- Ask active creators which editor and operation they actually need. Choose one target before adding a dependency or a format promise.
- Export a small fixture with two speakers, overlapping speech, one silence, one timing-fit adjustment and non-ASCII names.
- Import it in that editor and compare placement, duration, track naming and a rendered mix with VoiceStudio's selected-language output.
- Inspect whether source or fitted placement is authoritative for each timing strategy. Use existing fitted timing functions instead of deriving timing from clip filenames.

### Acceptance signals

- Every exported clip resolves locally after moving the package.
- No missing/duplicated clip, wrong-language audio, lost overlap or unintended timing shift occurs in the fixture.
- The selected frame/sample rate and rounding policy are explicit and tested, including long timelines.
- A background stem retains correct alignment, and unsupported retime behavior is stated before export.
- Existing ZIP snapshot semantics prevent regeneration during export from mixing versions.
- Existing native bundle and simple audio/subtitle exports remain independently available.

### Coordination and effort

**High until interoperability is demonstrated; medium for a narrow adapter after that proof.** Direct overlap with [#4220](https://github.com/debpalash/VoiceStudio/pull/4220) in `dub_export.py` and [#4221](https://github.com/debpalash/VoiceStudio/pull/4221) in export UX requires coordination. Current [export documentation](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/docs/dubbing/export.md) already defines Smart Fit and overlapping cue behavior; preserve it. The current feature evidence is strong, but demand remains a hypothesis.

## 4. Human review notes tied to exact segment/audio versions

### User problem and exact residual

A creator or reviewer may want to mark “pronunciation approved,” “keep this performance,” or “redo the last phrase” while listening, then know which decisions became outdated after an edit. Automatic QC does not capture editorial intent.

Current [DubSegment](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/dub/dub-session.ts#L71-L130) records machine QC drift/recognition flags, translation errors/critique, timing fit and source translation provenance. It does not define human review notes, approval state or the audio revision the reviewer heard. The inspected [draft restoration](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/dub/dub-draft.ts) and timeline controls do not provide that workflow. The similarly named `use-review-mode.ts` is an on/off application preference, not segment review records.

**Proposed first slice:** local notes and reviewed/needs-change status attached to stable segment ID, target language and the relevant audio/text fingerprint. Regeneration or a material text/voice edit makes prior approval stale. Start with one creator on one computer, then optionally export a review sheet. Do not build accounts, live comments or team permissions as part of this experiment.

### First investigation and proof

- Put three notes on a small rendered project, edit one segment, regenerate one and leave one untouched.
- Verify that the unchanged segment retains its decision, changed versions need review again, and the original note remains inspectable.
- Exercise split/merge/delete and language switching. Decide explicitly how notes are carried, superseded or orphaned; never silently transfer approval to different speech.
- Conduct a lightweight workflow trial to see whether this reduces external notes/spreadsheets or merely adds clutter.

### Acceptance signals

- Notes and status survive save/reload and retain exact language/segment association.
- Notes are never injected into synthesis or translation prompts.
- Editing or replacing audio invalidates approval only for affected work; changing UI selection does not.
- QC warnings and human decisions remain distinct; a human approval is not a guarantee of acoustic correctness.
- Filter/navigation reaches unresolved notes without losing playback position.
- Import/export is scoped deliberately; no claim that review state transfers to phones until their contracts are updated.

### Coordination and effort

**Medium for local notes; high for collaboration.** This is the lowest-confidence demand hypothesis in this set. Coordinate with [#4221](https://github.com/debpalash/VoiceStudio/pull/4221) because it owns `dub-session.ts` and the guided editing workflow, and with the [#4347](https://github.com/debpalash/VoiceStudio/issues/4347) provenance investigation before choosing invalidation rules. The companion quality research covers automatic spoken-script verification; these human decisions should consume those findings, not duplicate the checker.

## Search and evidence limits

The complete current open-PR queue was reviewed for ownership and compared with the earlier full changed-file audit. Focused historical GitHub searches returned complete result sets for `is:pr compare in:title` (5), `audition in:title` (0), `revision in:title` (7), `handoff in:title` (1), `undo in:title` (0), `take in:title` (16), `snapshot in:title` (13), `annotation in:title` (2), and `approval in:title` (1). Searches for OpenTimelineIO, FCPXML and EDL in PRs each returned zero. Recent `project in:title updated:>=2026-10-01` returned 8 and `export in:title updated:>=2026-10-01` returned 20. All these searches were scoped to `repo:debpalash/VoiceStudio` and reported `incomplete_results=false`.

A broad “review notes” search returned 334 mixed code-review results and was not fully paginated; it is not used as absence evidence. Broad exact-phrase search can produce unrelated lexical matches, so source/schema inspection carries more weight than a zero or irrelevant search result.

Before claiming any feature: refresh main/open PR heads, check the candidate's issue/timeline and relevant closed work, discuss the smallest slice with a maintainer, and obtain user-workflow evidence for the two lower-confidence hypotheses. No “no matching PR” observation is an ownership reservation.

