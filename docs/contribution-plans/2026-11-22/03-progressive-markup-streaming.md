# Plan 3: Start preview playback before a marked-up narration finishes

## Decision and status

Add progressive preview delivery for eligible `POST /generate` requests containing pause markers, paragraph gaps, SSML-lite changes, or engine-silence trimming. Reuse the existing speech plan and preserve the canonical final take.

This follows the explicitly unfinished streaming item in [merged PR #4254](https://github.com/debpalash/VoiceStudio/pull/4254). It is a new implementation proposal, not an existing assigned issue or a completed change. Source was inspected on 2026-11-22 at upstream commit [2bb21302241793977055c44f7c52815bcbf0261e](https://github.com/debpalash/VoiceStudio/commit/2bb21302241793977055c44f7c52815bcbf0261e). No runtime synthesis, test command, or benchmark was executed for this plan; all validation below is proposed.

At the final review checkpoint on 2026-11-22 at 16:37:12 UTC, #4254 was merged and still listed “Stream span by span” as unfinished. The [audited backlog](backlog-audit.md) records all 15 open PRs, including the five new Dependabot PRs #4350–#4354, whose inspected changes are confined to pinned actions in GitHub Actions workflows. None implemented this Generate streaming change. Related searches returned historical span/seed work and #4254, not a current replacement. Recheck before starting and before pushing.

**Suggested implementation PR:** `feat(generate): stream completed markup spans during synthesis`.

**Planning estimate:** three to five focused development days for the bounded first slice and regression coverage, plus hardware/review time. Stateful audio and cancellation findings can change this estimate.

## What is known

| Finding | Evidence | Confidence |
|---|---|---|
| #4254 ships paragraph gaps, trimming and SSML-lite while leaving span streaming unfinished | [PR #4254](https://github.com/debpalash/VoiceStudio/pull/4254), merged 2026-11-22 02:44 UTC | Verified PR record |
| Markup requests currently use the whole-take inference path even when streaming was requested | [stream branch][stream-branch]: `_has_pause` empties `_text_chunks`; `_stream_events()` awaits the whole render before yielding its first audio | Verified source |
| The branch covers more than explicit pauses | [needs_span_render()][planner]: paragraph structure, speed/spelling transformations and trim-only requests can require span rendering | Verified source |
| Current per-span rendering already preserves chunking, trimming, seed and silence semantics | [_render_with_pauses()][span-renderer], [_run_inference()][native-inference], [_run_backend_inference()][backend-inference] | Verified source |
| Room tone is not independently decidable for an early span | [fill_gaps()][gap-fill] derives a noise profile from all speech spans and modifies neighboring edges | Verified source; architectural constraint |
| The renderer applies a single advertised crossfade to successive preview chunks | [createStreamingPreview()][preview-player] | Verified source; explicit gaps must not be crossfaded away |
| Per-sentence generation had a substantial CPU cost in the preceding work | #4254 reports 113 s versus 214 s and says the owner removed sentence-gap support | Reported measurement in the PR; not rerun here |

### Why the delay exists

The ordinary streaming path divides plain text into chunks and emits each rendered preview immediately. The markup path must preserve intentional silence and per-span speed, so it currently delegates to the existing whole-take renderer. That renderer returns only after all spans and gaps have been assembled. The streaming wrapper then sends one audio chunk.

The opportunity is a delivery change: expose completed audio from the existing plan as it becomes available. A new sentence splitter, different seeds, extra inference calls, or a second synthesis pass would change the workload and defeat the purpose.

## Scope of the first implementation

### Objectives

1. For an eligible multi-span request, deliver the first playable speech before later spans finish.
2. Preserve the same transformed text, paragraph/pause plan, inner chunk boundaries, engine parameters and seed policy as classic generation.
3. Preserve final output construction through the existing whole-take DSP, watermarking, save and history pipeline.
4. Keep deliberate silence lengths intact in preview and final audio.
5. Preserve GPU-pool budgets, temporary-reference ownership, keepalives, failure reporting and cancellation.
6. Support both the native model path and the `TTSBackend` path using one model-independent scheduling/assembly design.
7. Select a tested compatible fallback before rendering when the preview cannot preserve the requested semantics.

### Explicit first-slice boundary: room tone

The first PR should retain whole-take preview for `pause_fill=room_tone`. Current `fill_gaps()` uses the quietest frames of the entire take and blends generated tone into the ends of adjacent speech. Emitting an earlier span permanently commits samples that the final whole-take operation may later change.

A silent switch from room tone to digital silence, or a profile based only on the first span, would change the requested output. Neither belongs in this PR. Choose the existing whole-take path before synthesis and record a fixed, content-free fallback reason. Keep the final room-tone artifact unchanged. A future incremental room-tone design would require an explicit audio contract and separate review.

Digital-silence joins are the primary progressive path. Normal preview DSP can follow the existing per-chunk preview policy, while final DSP remains whole-take. Any effect whose preview semantics cannot pass the required tests/listening checks also stays on the existing whole-take path until its behavior is understood; do not turn off a requested effect.

### Non-goals

- Reintroduce sentence-gap controls or split every sentence into a new engine call.
- Add native token streaming, concurrent model inference, speculative rendering, or a new audio transport.
- Promise that an MCP tool streams audio simply because its underlying Generate route has this capability. The target is `POST /generate` with `stream=true`; existing nonstream consumers retain their behavior.
- Change the final WAV's format, final history publication, text normalization, pronunciation rules or model selection.
- Replace whole-take room-tone analysis or redesign mastering.
- Resolve the separately suspected preset-voice forwarding defect without declaring it as distinct work.
- Add dependencies, a version bump, required network access or telemetry.

## Current code and test seams

| File | Relevant existing functions or role |
|---|---|
| [backend/services/generate_markup.py][planner] | `Span`, `JoinOptions`, `plan_spans()`, `needs_span_render()`: pure planning, limits and markup grammar |
| [backend/api/routers/generation.py][span-renderer] | `_render_with_pauses()`, `_plan_generate()`, `_span_speed()`: render plan and assemble intentional gaps |
| [backend/api/routers/generation.py][native-inference] | `_run_inference()`: native model calls, cached reference and seed behavior |
| [backend/api/routers/generation.py][backend-inference] | `_run_backend_inference()`: adapter parameters, optional duration, emotion and native-proxy controls |
| [backend/api/routers/generation.py][stream-branch] | `_render_stream_chunk()`, `_assemble_stream_chunks()`, `_stream_events()`: current streaming behavior and error mapping |
| [backend/api/routers/generation.py][reference-lease] | `_run_with_reference_lease()` and the temporary-reference lease: worker/request lifetime coordination |
| [backend/api/routers/generation.py][finalize] | `_finalize_generation()`: one whole-take mark, file save, history and cleanup |
| [backend/services/chunked_tts.py][chunking] | `split_text_into_chunks()`, `concatenate_audio_chunks()`, dropped-chunk reporting |
| [backend/services/audio_dsp.py][gap-fill] | `pause_fill_mode()`, `fill_gaps()`, whole-take room-tone dependency |
| [backend/core/stream_keepalive.py][keepalive] | `with_keepalive()`, blank NDJSON keepalives and cancellation-safe source cleanup |
| [electron/src/renderer/src/lib/api/generate.ts][stream-client] | `generateCloneStreaming()`, optional `total_chunks`, preview/error/fallback consumption |
| [electron/src/renderer/src/lib/audio/streaming-preview.ts][preview-player] | `createStreamingPreview()`: playback scheduling, crossfades, underruns and stop/finalize |
| [tests/test_generate_streaming.py][test-streaming] | Deterministic fake engine, hermetic output/history fixture and `_asgi_stream_post()` send-time observation |

No nested AGENTS.md or CLAUDE.md exists below the root at this source snapshot. Applicable [AGENTS.md][agents], [CLAUDE.md][claude], [CONTRIBUTING.md][contributing] and [AGENT_PR_GUIDE.md][pr-guide] require a focused, tested change; fallback to the working behavior; offline verification; unchanged saved-data compatibility; normal review/CI; and documentation/changelog updates in the same implementation PR.

## Proposed architecture

### A. Plan once, after all existing text preparation

Keep the current validation order. Pronunciation replacements and other existing preparation may change the text, so use the final prepared text and repeat the existing bounded planner validation at the same point. Preserve the silence/tag limits and reject invalid requests before model work.

Produce a stable list of render units from the existing `Span(text, pause_ms, speed_factor)` values. Within each speech span, call the existing chunk splitter with the existing maximum. Preserve the exact engine-call sequence and per-call options. A plain request with default options must retain its current path.

Start with delivery of completed spans, including their internal chunk joins. A very long first span may still delay first audio; that limitation is preferable to changing chunking or introducing a new crossfade protocol in this PR.

### B. Separate raw assembly from preview delivery

Retain the raw rendered speech needed for final assembly. Do not put preview-marked or preview-mastered audio into the final take.

For eligible digital-silence plans:

1. Render a span through the selected native/adapter path.
2. Apply the same per-chunk and per-span trimming used by the classic span renderer.
3. Assemble that span's internal chunks using the existing crossfade helper.
4. Attach its requested digital silence, or emit a carefully defined gap unit with the same duration; choose one convention and test the entire consumer path.
5. Produce a preview copy using the existing preview DSP policy and `mark_synthetic_async(..., context="generate.stream_preview")`.
6. Yield the preview without waiting for later spans.
7. When every unit is complete, assemble the retained raw material and run the existing final whole-take effect chain and `_finalize_generation()` once.

Preserve the current sample-rate contract. Some adapters discover their actual rate only after a first render; do not emit a guessed `start` rate. A mid-take rate change requires explicit compatible handling or a classified error, not silent reinterpretation of PCM.

### C. Preserve intentional gaps at the client boundary

The current player crossfades every adjacent preview chunk by the stream-wide `crossfade_ms`. Using that value for already-assembled spans would shorten deliberate pauses and apply an extra fade across span boundaries.

For span delivery, advertise `crossfade_ms=0` after internal chunk crossfades have already been applied. Deliver exact pause samples as part of the chosen unit convention. Preserve existing non-markup chunk delivery unchanged.

Check leading silence, trailing explicit pauses, adjacent pauses, SSML-only boundaries, and zero-gap adjacent speech. Preview sample counts must match the planned timeline after trimming; a blank NDJSON keepalive is transport liveness, not audio silence.

The current TypeScript stream type makes `total_chunks` optional and treats absence as unknown progress. Define counts as delivery units, not engine calls. If failed/empty spans make an exact count unknowable, use supported unknown progress rather than fabricating a percentage. Preserve existing plain-text count semantics and verify both maintained renderer and shared consumers before changing metadata.

### D. Preserve failure and cancellation ownership

Schedule model work through the existing guarded GPU-pool mechanism. Each dispatch that can still read a temporary reference must hold the existing lease until the worker actually exits. Cancellation of an awaiting task does not prove the native operation stopped.

Keep blank-line keepalives and no-buffer headers. Preserve progress/deadline updates for long spans; do not replace the existing text/hardware-aware execution budget with a fixed timeout.

Mid-stream cancellation/error must not emit `done`, create a successful history entry, publish a partial final file, or leave an unowned reference/worker. If final saving has started, retain `_finalize_generation()`'s shielded-writer cleanup. Keep classified public errors and scrubbed diagnostics.

Fallback is a pre-render compatibility decision for known unsupported modes. Once inference or preview emission has started, do not add a hidden second render as “fallback.” Preserve existing client retry/terminal policy and test that this change does not accidentally trigger duplicate synthesis.

## Implementation phases

### Phase 0 — Revalidate and choose the bounded contract

- Fetch current upstream main and compare #4254 plus the source seams above.
- Read current PRs for Generate/markup/streaming work and recent seed, cancellation or audio changes.
- Record the supported preview modes and explicit whole-take fallback modes. Room tone is a fallback in this plan.
- Agree the emission-unit convention, crossfade metadata and unknown-progress behavior before changing rendering.
- Prepare isolated synthetic speech/reference fixtures. Keep all automated tests offline with empty caches; real-model performance runs use separately provisioned local models.

### Phase 1 — Prove the missing incrementality

Extend [test_generate_streaming.py][test-streaming] with pause, paragraph-gap, speed-tag and trim-only cases. Reuse its direct ASGI send boundary: TestClient/httpx's in-process transport buffers the entire body and cannot prove incremental delivery.

Prefer explicit worker-entry/release synchronization for new tests. Block a later span and prove a playable earlier chunk was sent before releasing it. Always release and join worker fixtures in cleanup. An arbitrary short sleep is not a reliable proof on a busy runner.

Add classic-versus-streaming final-output fixtures and engine-call recording before changing the implementation. At baseline, the incrementality cases should fail for the observed reason; existing output-parity cases should pass.

### Phase 2 — Extract only the shared span mechanics required

Factor the smallest model-free iteration/assembly seam from `_render_with_pauses()` so classic and streaming paths share plan ordering, trim behavior, inner chunk joins and explicit silence lengths. Avoid a broad renderer rewrite.

Keep model calls injected. Centralize per-call parameters enough to prevent native/adapter/streaming drift, but do not change unrelated engine behavior. Preserve duration only in the same one-unsplit-span cases as the current implementation.

If a new service module is justified, update the applicable structure documentation and deterministic count guard in the same PR. Prefer an existing module when it keeps ownership clearer.

### Phase 3 — Connect progressive delivery and safe fallbacks

Wire eligible plans into `_stream_events()`, mark every outgoing preview copy, retain raw material for finalization and use `crossfade_ms=0` for preassembled spans.

Choose room-tone/unsupported-mode fallback before model execution, using the existing whole-take pipeline. Test both selection and output, and use a fixed reason in logs rather than text, model paths or exception content. Preserve no-markup and short-request behavior.

### Phase 4 — Exercise boundaries, then measure

Run the acceptance matrix and targeted regressions below. Use real playback to inspect pauses, underrun recovery, transitions and stopping, while deterministic fixtures establish exact final-output parity.

Measure time to first playable speech, whole render time, engine calls and memory under the same workload. Publish actual results with limits; do not infer an inference speedup from reduced waiting time.

### Phase 5 — Package the contribution

Update the expressive-speech and streaming documentation with supported modes and fallback behavior. Keep MCP documentation accurate about its own delivery contract. If an API/NDJSON schema changes, update the maintained consumers and generated contracts as applicable; do not claim contract compatibility without checking.

Add a numbered user-facing changelog fragment once the implementation PR exists. Use the repository's normal review and CI process. A planning-document branch is not evidence that any implementation gate passed.

## Acceptance matrix

| Case | Required outcome | Proposed proof |
|---|---|---|
| Three speech spans with digital pauses | First audio sent before final span completes; correct gaps | Synchronized ASGI send test |
| Paragraph gaps | Same spans, same calls, same configured gap lengths as classic | Planner/call-recording + waveform comparison |
| Explicit pause next to a blank line | Pause replaces paragraph gap exactly as today | Existing planner tests plus streamed waveform |
| Nested SSML across pause/paragraph boundaries | Tags not spoken; speed scope preserved | Planner and native/adapter spies |
| `trim_engine_silence` alone | Original chunk trimming and duration semantics retained | Trim/one-span fixtures |
| Long span with internal chunks | Same chunk boundaries, same crossfades, same seed per call | Call sequence + decoded samples |
| Leading/trailing/consecutive pauses | Intended silence retained; no extra client crossfade | PCM sample count + playback test |
| Pause-only or empty-speech output | Existing valid silence/error behavior retained; no invented speech | Edge-case unit/API tests |
| Room tone | Automatic whole-take fallback; identical final audio behavior | Fallback assertion + existing room-tone tests |
| Native and adapter engines | Equivalent delivery guarantees and correct parameters | Existing native fixture plus deterministic adapter |
| Effects/mastering | Final whole-take DSP unchanged; preview timing/quality acceptable | Exact final fixture + listening comparison |
| 16/24/32-bit final export | PCM bytes identical where applicable; FLOAT decoded samples/format identical | Existing bit-depth parity test extended to markup |
| Marking enabled/disabled/unavailable | Every preview goes through the chokepoint; final raw take marked once | Marking spies + existing detection fixtures |
| Disconnect during queued/running work | Lease held until worker exit; no successful publication | Controlled worker/cancellation fixture |
| Error in a later span | Classified error after earlier chunks; no done/history/output | Midstream failure fixture |
| Save cancellation | Writer drains safely; unpublished file removed | Finalizer cancellation coverage |
| Slow span | Keepalives continue; deadline/progress semantics remain correct | Existing keepalive/budget tests |
| Unsupported preview mode | Working fallback selected before synthesis; no duplicate call sequence | Mode selection/call-count test |

## Concrete test plan

Use and extend existing tests rather than adding assertions that merely mirror implementation:

- [tests/test_generate_streaming.py][test-streaming]: incrementality, native path, classic parity, errors, short-text path, keepalives and subtype/sample checks.
- [tests/test_generate_markup.py][test-markup]: default plan preservation, gap budgets, tag limits, scope across boundaries, trim-only behavior and unchanged default requests.
- [tests/test_generate_chunk_seed_3730.py][test-seeds]: every engine call keeps the take seed; unsupported engines are not sent a seed.
- [tests/test_pause_markers.py][test-pauses] and [tests/test_pause_fill.py][test-fill]: intentional gaps, room-tone determinism and fallback.
- [tests/test_synthetic_audio_watermark_1169.py][test-marking]: streamed previews and final output pass through the established provenance path. Keep real-model detection fixtures separate from lightweight spies.
- [tests/test_chunk_progress_extends_generate_budget_1391.py][test-budget], [tests/test_stream_keepalive.py][test-keepalive] and [tests/test_stream_failure_terminal.py][test-terminal]: liveness, deadline and error policy.
- [electron/src/renderer/src/lib/audio/streaming-preview.test.ts][test-preview] and [electron/src/renderer/src/lib/api/generate.test.ts][test-client]: zero crossfade for assembled spans, exact pause scheduling, unknown progress, finalize/abort and retry policy.

Proposed targeted commands, after normal dependency setup and isolated environment configuration:

~~~bash
uv run pytest tests/test_generate_streaming.py tests/test_generate_markup.py tests/test_generate_chunk_seed_3730.py tests/test_pause_markers.py tests/test_pause_fill.py -q
uv run pytest tests/test_chunk_progress_extends_generate_budget_1391.py tests/test_stream_keepalive.py tests/test_stream_failure_terminal.py -q
~~~

Select the current Electron runner from electron/package.json for the two renderer test files. Run marking detection tests only with their documented local fixture prerequisites; do not fetch models during offline CI. Run the broader relevant implementation gates before landing. **No command above has been run for this plan.**

## Measurement protocol

### Workloads

Use reproducible synthetic text that may be committed publicly:

1. A plain-text control without markup.
2. The same content with three paragraph gaps.
3. Explicit leading, middle and trailing pause markers.
4. A long first span plus later spans, to expose the first-slice latency limit.
5. Nested speed/spelling tags across a paragraph boundary.
6. Room-tone fallback control.

Use a declared engine/model revision, voice fixture, seed, quality settings, sample rate and output format. Separate warm-model and cold-model trials. Model loading is not the claimed optimization.

### Procedure and metrics

- Compare the pinned baseline and implementation on the same machine/environment.
- Run an unmeasured warm-up, then at least five measured runs per selected case; alternate baseline/change where feasible to reduce thermal/order bias.
- Measure request start, first playable **speech** received, first speech scheduled for playback, final completion, engine-call count, generated sample count, and peak process-tree RSS. Record VRAM where the existing instrumentation supports it.
- Do not count an early `start` event, a keepalive, or intentional leading silence as successful time to first speech.
- Report median and p90, sample count and observed spread. Use the same harness for both branches.
- Verify final sample/format parity and call sequence alongside timing. A faster preview with different speech is not a valid win.
- Start with a CPU-only deterministic fixture, then one real CPU model and one GPU or Apple Silicon engine if available. List missing platform/hardware coverage explicitly.

### Proposed release criteria

The synchronized fixture must prove first speech precedes final-span completion. A real eligible multi-span workload must show earlier playback without extra model calls. Total synthesis time should remain within ordinary measurement noise; investigate a sustained median regression greater than roughly 5% rather than declaring it acceptable automatically. The 5% value is a proposed review threshold, not a repository policy or a measured result.

Peak memory must not gain an unnecessary full-take duplicate beyond the existing final assembly and bounded preview copy. Do not claim constant memory: the present final-output pipeline still retains full audio. A larger memory redesign is outside scope.

## Risks and stop/revalidation criteria

- **Whole-take dependencies:** room tone, peak normalization and stateful effects cannot all be made sample-identical by independently processing spans. Keep final processing whole-take and use the explicit compatibility fallback where needed.
- **Double crossfade:** preserving the original stream-wide fade for assembled spans shortens pauses. Assert the wire metadata and actual scheduling.
- **Seed/call drift:** new task boundaries must not change random-state ownership or engine-call parameters. Compare full call sequences, not only final duration.
- **Temporary-reference lifetime:** cancelling the consumer can leave native work running. Preserve the lease/worker completion contract.
- **Duplicate inference:** do not recover a partially streamed request with an unannounced second generation pass.
- **Overclaiming:** final artifact equality does not mean every preview PCM sample equals whole-take-mastered audio. Document the distinction and validate audible boundaries.
- **Upstream overlap:** stop and compare if another PR changes #4254's follow-up, stream protocol, generation pool, markup planner or finalizer.
- **Scope growth:** if correct progress requires a new audio protocol, a new concurrency architecture or a whole-take DSP rewrite, split the work and retain the working fallback.
- **No reliable reproduction:** if the new baseline already streams the same marked-up request, retire or narrow this proposal.

## Separate candidate: missing preset forwarding

The current multi-chunk `_render_stream_chunk()` does not visibly pass `voice=preset_voice` to the adapter, while `_run_backend_inference()` does. This source observation suggests a distinct preset-selection defect but has not been runtime-confirmed.

Keep it separate from this feature. A dedicated regression should record `voice` on every short-stream, long-stream and classic engine call. If it fails, file or implement a focused correction with an explicit relationship to this PR. The new markup path must preserve the parameters of the existing classic markup path; it must not quietly repair or broaden unrelated plain-text behavior. The [cloning-capability plan](01-mlx-cloning-capabilities.md) records the same separate candidate.

## Immutable source references

[planner]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/generate_markup.py
[span-renderer]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/generation.py#L625
[native-inference]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/generation.py#L1349
[backend-inference]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/generation.py#L1451
[stream-branch]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/generation.py#L2439
[reference-lease]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/generation.py#L275
[finalize]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/generation.py#L1718
[chunking]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/chunked_tts.py
[gap-fill]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/audio_dsp.py#L658
[keepalive]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/core/stream_keepalive.py
[stream-client]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/lib/api/generate.ts
[preview-player]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/lib/audio/streaming-preview.ts
[test-streaming]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_generate_streaming.py
[test-markup]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_generate_markup.py
[test-seeds]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_generate_chunk_seed_3730.py
[test-pauses]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_pause_markers.py
[test-fill]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_pause_fill.py
[test-marking]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_synthetic_audio_watermark_1169.py
[test-budget]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_chunk_progress_extends_generate_budget_1391.py
[test-keepalive]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_stream_keepalive.py
[test-terminal]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_stream_failure_terminal.py
[test-preview]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/lib/audio/streaming-preview.test.ts
[test-client]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/lib/api/generate.test.ts
[agents]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/AGENTS.md
[claude]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/CLAUDE.md
[contributing]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/.github/CONTRIBUTING.md
[pr-guide]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/.github/AGENT_PR_GUIDE.md
