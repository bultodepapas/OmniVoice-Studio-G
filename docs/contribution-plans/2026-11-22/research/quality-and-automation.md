# VoiceStudio: new quality, evaluation and automation directions

Research checkpoint: 22 November 2026, 17:12 UTC / 12:12 America/Bogota. Source baseline: [`2bb21302241793977055c44f7c52815bcbf0261e`](https://github.com/debpalash/VoiceStudio/commit/2bb21302241793977055c44f7c52815bcbf0261e), still the reviewed upstream `main`. The open-PR read returned 15 PRs. This is research, not implemented code or a report of audio experiments. No models were installed, no real synthesis or listening tests were run, and no performance or accuracy improvement is claimed.

## Recommendation

The strongest user-facing directions on this track are **a spoken-script completeness check for ordinary generated takes** and **a durable generation receipt that explains how a particular take was made**. Both extend capabilities already in the application, and both have a more precise gap than a generic request for quality scoring, comparisons, or workflows.

A third useful direction is programmable repeatability through MCP. A fourth, an installed-engine quality corpus, should be combined with the performance research’s extension of the existing benchmark tools. A fifth, chapter-level voice consistency review, is an experiment with a high uncertainty threshold before any product work.

## What already exists, and what must not be proposed again

| Existing capability | Source-confirmed behavior | Consequence for a new proposal |
|---|---|---|
| Finished-take signal checks | `GET /audio/{audio_id}/quality` calls `analyze_audio`; it detects empty/invalid audio, clipping, silence and relative volume changes, with a two-hour/100-warning bound. | “Add audio quality checks” is already implemented. Spoken-content verification is a different residual. [1] |
| Dubbing ASR QC | `/dub/qc/{job_id}` re-recognizes the selected generated track, scores it against its own language and fitted timing, and adds advisory per-line drift/timing fields. The source text remains authoritative. Missing local ASR gives a typed 409; the route uses the guarded ASR worker. | Reuse the implementation's policy and scoring seams; do not propose basic dubbing QC or unbounded automatic re-dubbing. [2] |
| Model evaluation | `docs/evaluation.md` describes WER/CER, ECAPA/WavLM speaker similarity and UTMOS; `examples/run_eval.sh` drives OmniVoice inference over public test sets. | New model metrics or another generic evaluation framework are not novel. [3] |
| Probe judges and reports | `tests/probe` has WER/CER, optional speaker embeddings, declarative specs and HTML reports. The ordinary design/clone tests exercise the judges with synthetic audio and a `FakeTranscriber`; the opt-in real ASR test takes an existing WAV from `PROBE_ASR_SAMPLE`. | The residual is driving real installed adapters through a repeatable corpus and retaining comparable evidence. A green judge-unit test is not a real-engine quality run. [4] |
| Quality sweep | `scripts/compare_generation_quality.py` runs installed engines offline for one English text/seed, multiple step counts, clone/TTS modes and raw/broadcast output, then exports three WAV precisions and JSON signal/timing measurements. | Extend its evidence contract or reuse it; do not recreate its export/precision matrix. [5] |
| Take reuse | Electron stores generation controls per take in `voicestudio.take-settings.v1`, capped at the last 200 records, and restores validated controls. Backend history stores text, language, profile ID, seed and a design recipe, among other summary fields. | “Remember settings” is not new. The gap is durable, effective, server-side model/reference/runtime attribution, including takes created through other clients. [6] |
| Engine execution evidence | `engine_evidence.snapshot` already returns sanitized loaded-device/provider/precision/runtime facts; unobserved values remain unknown. Some adapters provide `model_identity()`. | Reuse these facts. Do not add another speculative “GPU used” detector or claim every model identity is an immutable revision. [7] |
| Compare Voices, project bundles and workflows | Compare Voices already auditions two voices with the same phrase. Project bundles carry a manifest/asset hashes. Workflows already run typed graphs serially and persist completed-step checkpoints. | The companion product research covers saved audition decisions and project handoff. Do not propose comparison, project ZIPs, generic workflow graphs or resume as new features. [8] |

### Relevant history and maintainer constraints

- [PR #2406](https://github.com/debpalash/VoiceStudio/pull/2406), merged 29 September 2026, introduced the precision/quality controls and current signal-check/sweep work. Its documentation reports limited real-engine Windows trials, explicitly not a universal perceptual ranking. Preserve that distinction.
- [Issue #4199](https://github.com/debpalash/VoiceStudio/issues/4199) remains open, with no comments at this read. A reporter says CosyVoice3 adds unrelated words for two seeds and omits a sentence for another, including with a direct reference and no saved profile. File properties and routing checks were verified; the actual generated content and model cause remain unverified. It motivates content checking, but is not proof of its root cause or of a working fix.
- [PR #2743](https://github.com/debpalash/VoiceStudio/pull/2743) proposed Hindi normalization, humanization, retries and a Hindi evaluation script. It was **closed without merging** on 26 October. The [maintainer's closing comment](https://github.com/debpalash/VoiceStudio/pull/2743#issuecomment-6425230526) rejects the approximately 10,000-line bundle as too broad and welcomes focused proposals. Its claimed experiments are not current-main behavior.
- [PR #4032](https://github.com/debpalash/VoiceStudio/pull/4032) removed the weekly eval workflow and `tests/evals`. The [owner decision](https://github.com/debpalash/VoiceStudio/issues/2603#issuecomment-6808580795) says it always skipped; the issue explains the missing LLM backend. This is distinct from the still-present speech evaluation and `tests/probe` modules. The [final closure](https://github.com/debpalash/VoiceStudio/issues/2603#issuecomment-6885799421) also declines broad upstream training/eval consolidation. An explicit local corpus experiment should not become a proposal to resurrect that weekly job or reorganize upstream evaluation.

## 1. Check whether a finished take actually says the script

**User value.** A user can hear where a take may have skipped, repeated or added words without listening to every minute first. This would be an optional action on an ordinary Clone/Design take, with long-form support only after the short-take contract is reliable.

**Precise residual.** Current ordinary-take checks are signal checks. The existing dubbing route compares recognized speech with target content, but the ordinary generation endpoint does not do an output ASR comparison. It already reports chunks that produced no audio; that is useful but does not catch a nonempty waveform saying the wrong words. [1], [2], [9]

**Narrow first feature.** “Check spoken text” produces a side-by-side script/recognized-text view with insertion, deletion and substitution candidates. Each flag links to a real recognized audio span when one is available. It records an explicit unavailable/uncertain timing state otherwise. The check never replaces the script, mutates the WAV, changes the selected voice, or rerenders automatically. Intentional pauses and supported inline cues must be lowered consistently with generation before calculating the comparison.

**Implementation hypothesis.** Build a reusable artifact-scoring service around the existing ASR loader, timeout/model-missing/license handling and local audio path validation. Keep the output independent of the dubbing job schema. `dub_qc`'s NFC/script-aware tokenization is a useful starting point; returning edit operations rather than just one aggregate ratio would make the result explainable. JiWER documents word/character alignment operations, but the current repository pins `jiwer==3.1.0` only in its evaluation extra. Do not assume the newest documentation's API is installed, or add an application dependency before comparing a small pure implementation with the current code. [2], [10]

**Why ASR is advisory.** The Whisper model card explicitly documents hallucination, repetition and uneven language/dialect accuracy. A mismatch can be the recognizer's error rather than TTS's. Forced alignment can locate recognized words; aligning the requested text is not independent evidence that those words were spoken. WhisperX also documents missing timing for some numerals/currency strings, overlapping-speech limitations and the need for a language-specific aligner. [11], [12]

**First experiment and go/no-go.** Proposed, not executed: use 12 short scripts across two initial languages, two installed TTS engines and two seeds (48 generated takes), plus hand-labeled omission/insertion/repetition cases created from consented or repository-owned audio. Include names, numerals, acronyms, code switching, intentional pauses and clean negative examples. Two listeners label content errors independently before seeing model flags. Measure error-detection recall, false alerts per minute, localization accuracy, ASR wall time and peak resource use. A useful initial gate could be at least 90% detection of the deliberately obvious omitted/added whole-sentence cases with at most 10% of clean takes falsely flagged; these are proposed pilot targets, not measured guarantees or universal shipping thresholds. If ASR cannot separate those cases, stop at a transcript comparison tool without a quality verdict. Broaden languages only with separate calibration.

**Costs and coordination.** Medium scope: backend scoring/report persistence, finished-take UI and translations, bounded cancellation, and model-free regression tests. Actual ASR consumes time and potentially competes with resident TTS memory; sequence it through existing admission/model lifecycle rules and coordinate with the performance track. No implicit model downloads or cloud recognizer. A local result may contain a private script/transcript, so ordinary retention/deletion must cover it. Hashing or redacting some fields does not automatically make a report anonymous.

## 2. Preserve an immutable receipt for each generated take

**User value.** “Why does this rerender sound different?” becomes answerable. A user can export audio with its production recipe, compare old/new environments, or supply a small reproducible report without disclosing a whole project.

**Precise residual.** Backend `generation_history` and `_finalize_generation` do not retain a complete effective engine/model/reference/runtime recipe. The renderer does preserve quality and other controls locally for up to 200 takes, and design recipes exist; those are useful authoring settings, not a durable record of the actual loaded model, source reference version and processing that produced a file. Live engine evidence already exists but is not attached immutably to each ordinary take. [6], [7], [9]

**Narrow first feature.** Add a versioned, additive generation receipt linked to an audio ID. Capture requested settings separately from effective values: engine/adapter, available model identity and immutable revision when known, app commit/version, sanitized execution evidence, used seed and seed-support state, resolved language, effective inference controls, reference content hash and transcript hash, normalization/markup version, DSP settings and encoded audio format/hash. Mark unobservable model/runtime facts as unknown; do not invent them from a current Settings screen after generation. A legacy take can have a partial receipt with a clear reason.

The first UI can simply expose “Generation details” and a deliberate export. Full rerender UX or storing every historical reference is a later decision. If a reference has changed or vanished, say so instead of silently using the profile's current audio. The receipt complements project-bundle hashes and local take settings; it is not a replacement project format. A reference hash identifies a dependency but cannot reconstruct it.

**First experiment and go/no-go.** Trace ordinary takes through local inline OmniVoice and one installed sidecar, using HTTP and MCP clients; include full-file and streaming paths where supported. The open-source GPU gateway executes accelerator work on the backend's own machine, so this experiment covers local execution reached through those clients. [16] Confirm that the same audio ID receives a stable record across restarts and that changes to model/reference/processing appear in a structured comparison. Preserve current response behavior if history persistence fails. Record only execution facts the backend or sidecar can establish; unknown is acceptable, incorrect attribution is not. Test the schema against a legacy DB fixture and ensure deletion/retention removes orphan receipts. Stop or narrow the schema if a field cannot be captured at the actual execution seam without broad adapter changes.

**Reproduction promise.** A receipt supports recreating conditions; it cannot guarantee identical waveforms on another device or library version. PyTorch explicitly says even identical seeds do not guarantee reproduction across releases/platforms or CPU versus GPU. Use checksums for an existing artifact's identity, not cross-platform golden-WAV acceptance. [13]

**Costs and coordination.** Medium scope, spread over bounded PRs: schema/storage contract first, one producer path next, then other paths and export UI. Reuse `engine_evidence`, `model_identity`, existing reference/fingerprint helpers and project asset conventions. The product research’s saved audition session should link to receipts. The performance/quality corpus should use the same manifest schema. Export defaults must omit filesystem paths, credentials and raw references, with an explicit user choice for including private material. The existing synthetic-audio watermark is a separate mechanism and should retain its semantics.

## 3. Make MCP generation explicitly repeatable and inspectable

**User value.** A script or an external assistant can request a particular installed engine and seed, then find out what actually happened, without changing global application settings or guessing from audio bytes.

**Precise residual.** Current `generate_speech` accepts text, language, profile, instruct, speed, steps, format and pause/trim options. It does not accept `seed`, `engine` or WAV precision, and `_speech_result` returns duration/time/audio identity but drops the backend's seed/routing/dropped-text headers. The application HTTP generation route already has per-request engine/seed/precision controls. MCP exposes transcription, but has no ordinary generated-audio signal/QC result tool or receipt resource. [9], [14]

**Narrow first feature.** Add optional supported per-request controls and additive result metadata, preserving defaults for existing callers. Prefer a small `get_generation_details(audio_id)`/receipt resource and explicit `check_generated_audio` action over attaching a second model run to every generation. A capabilities response should reuse backend-declared settings and differentiate a requested feature from an adapter that actually honors it. Do not change the existing MCP 16-step default as a side effect of this feature; default quality policy deserves its own decision.

**First experiment and go/no-go.** With a fake HTTP backend, prove omitted options produce the current form exactly, optional options are forwarded and validated, returned seed/routing warnings survive, and one tool call causes one generation POST. Then run a bounded real same-engine/same-input trial, treating stable metadata as the contract rather than assuming bit identity. Keep current caller/client binding, authentication, file confinement, timeout and error behavior. Confirm no broader caller access through the new resource. If old-server compatibility cannot be expressed additively, expose an explicit capability/version check first.

**Costs and coordination.** Small-to-medium for control/result parity alone; larger if combined with persisted receipts/QC. This is a separate product feature from the already planned stdio/session repair. Never hide a failed non-idempotent generation behind blind automatic replay, and do not silently switch to another engine after an ASR warning: voice, language, license and quality semantics may change.

## 4. Turn installed-engine trials into comparable quality evidence

**User value.** Maintainers and advanced users can check whether an upgrade or faster setting damages their own voice/language use case, and show the evidence behind a recommendation.

**Precise residual.** The tools already have complementary pieces: an installed-engine precision sweep, OmniVoice benchmark evaluation, probe judges/reports, pipeline timing, runtime evidence and local performance preferences. The inspected standard probe media tests do not automatically synthesize a real multi-engine corpus. The sweep hard-codes English and a single text/seed, and does not run ASR/speaker judges or record a complete model/reference/environment manifest. [3], [4], [5], [7]

**Narrow direction, combined with the performance track.** Extend the existing tools with a small explicit corpus/manifest adapter. Each case records text/language/reference identity, engine/model/options, seeds, and the same performance measurement definitions. Generation artifacts feed the existing judges; known unsupported capabilities, missing models and unknown measurements remain separate from failure/pass. Add a comparison view of baseline versus candidate, not a universal model ranking. Human, matched-volume, blinded listening can record similarity, delivery and naturalness separately; it must remain distinguishable from ASR content accuracy and predicted MOS.

**First experiment and go/no-go.** Use the same small corpus as proposal 1 and one unchanged baseline rerun. Measure its own run-to-run variance before calling a changed score a regression. Then deliberately introduce one truncation and one format/silence defect into local copies to establish that the pipeline detects meaningful failures. Require an identity-matched comparison, explicit coverage/skips and finite resource/cost reporting. Stop if reproducing a scenario depends on hidden cache state or if all reported “quality” results merely exercise fake judges. No automated periodic model downloads; no rewrite/consolidation of the upstream evaluation package.

**Costs and coordination.** Medium tooling work plus hardware time and human listening. Share the manifest and metrics schema with the performance research’s `bench_pipeline.py` extension (TTFA, warm distributions and sidecar process memory), not a second benchmark system. Preserve local-only raw artifacts. A lightweight shareable report should explicitly select text/audio disclosure and should never turn a single English example into a multilingual quality claim.

## 5. Research chapter-level voice consistency review

**User value.** A long narration can be intelligible but sound like a different speaker in a few paragraphs. A review list could prioritize those locations for listening before export.

**Precise residual and uncertainty.** Current evaluation/probe code compares a reference and generated clip using speaker embeddings. The inspected sources do not provide a user-facing sequence of per-chapter/segment consistency candidates with intentional voice/style changes excluded. This is a scoped negative finding, not proof that no related internal code exists anywhere. The existing probe implementation itself warns against universal cosine cutoffs and its default Resemblyzer's English bias. [3], [4], [15]

**Experiment first.** Reuse an approved local embedding backend; do not introduce a new package into the default runtime initially. Build a small consented dataset with the same speaker under normal emotional/style variations and intentionally substituted different-voice paragraphs. Compare per-segment reference similarity and local temporal outliers, grouping only segments meant to use the same voice. Evaluate whether flagged segments agree with blinded listeners and whether normal whispering, pitch changes, short clips, noise or language changes dominate the flags. Use per-engine/language distributions, not an absolute “same person” threshold. This is a production-consistency aid, not identity verification.

**Go/no-go.** Proceed only if the model finds the deliberately substituted paragraphs while normal delivery variation creates a manageable listening queue. If not, retain the evidence as a developer experiment and do not surface a percentage “voice match” score. Human-confirmed delivery differences are the outcome; embedding similarity is an imperfect signal. No accuracy or user benefit is measured yet.

**Costs and coordination.** Large/research scope relative to the other proposals: multilingual calibration, optional model downloads/license acceptance, resource admission, and reference/embedding retention. Embeddings and reference audio should remain local and be deleted with the associated data. Reuse the product research’s later human review/notes model if it lands, rather than inventing a competing review state.

## Suggested sequencing

1. Draft a narrowly scoped content-check experiment and the receipt schema independently. Neither requires shipping a broad UI redesign or new engine.
2. Validate content flags with labeled audio and receipt completeness with real producer seams. These resolve different risks and can run in parallel.
3. Ship a bounded short-take feature only after the relevant go/no-go checks. MCP control/result parity is a small parallel contribution if kept additive.
4. Integrate shared manifests and real corpus execution into the existing performance/quality tools. This supports future optimizations without becoming its own competing framework.
5. Keep sequence-level speaker consistency as research until listener evidence supports it.

## Evidence links

All application source links below are pinned to the reviewed commit. Public primary upstream documentation was opened and read on the research date; it is feasibility/limitation evidence, not a statement that VoiceStudio installs the newest upstream version.

[1]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/audio_quality.py
[2]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/dub_export.py#L1736-L1865
[3]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/docs/evaluation.md
[4]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/probe/test_probe_spec.py
[5]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/scripts/compare_generation_quality.py
[6]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/lib/store/takes.ts
[7]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/engine_evidence.py
[8]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/docs/electron-workflows.md
[9]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/generation.py
[10]: https://jitsi.github.io/jiwer/usage/
[11]: https://github.com/openai/whisper/blob/main/model-card.md
[12]: https://github.com/m-bain/whisperX#limitations
[13]: https://docs.pytorch.org/docs/2.15/notes/randomness.html
[14]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/mcp_server.py#L924-L1021
[15]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/probe/judges/speaker.py
[16]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/gpu_gateway.py

Additional exact source seams:

- [Backend history schema](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/core/db.py#L75-L90)
- [Shared generation finalizer and current history insertion](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/generation.py#L1718-L1840)
- [MCP result shape](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/mcp_server.py#L563-L589)
- [Live engine metadata types](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/lib/api/types.ts)
- [Probe's real ASR opt-in test](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/probe/test_probe_asr_e2e.py)
- [Synthetic design test](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/probe/test_probe_design.py)
- [Probe's current WER/CER and transcriber implementations](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/probe/judges/transcription.py)
- [Probe HTML reporting](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/probe/report.py)
- [Script-aware dubbing text scorer](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/dub_qc.py)
- [OmniVoice upstream-style evaluation runner](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/examples/run_eval.sh)
- [Import/availability checks without constructing user models](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/_performance_probe.py)
- [Existing measured-quality documentation and limitations](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/docs/audio-quality.md)

The `tests/probe/README.md` contains historical Tauri references and numerical coverage claims; they were not treated as evidence of the maintained Electron product's current real-engine coverage. Executable source above determines the conclusions.
