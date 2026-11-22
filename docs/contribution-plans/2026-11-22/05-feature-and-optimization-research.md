# New features and optimization research

## Recommendation

For a new product contribution, investigate **durable audition sessions** first. For a quality feature, investigate **spoken-script completeness review on ordinary generated takes**. For a runtime optimization, investigate **releasing the GPU worker before long-form CPU finalization**.

These are three independent investigations, not a proposal to combine their implementation into one PR. A smaller first technical contribution is to correct the existing inference benchmark's cold-load timing; that improves the evidence used to judge subsequent optimizations.

The strongest supporting foundation is an immutable generation receipt: it connects a saved take with the effective model, reference and settings that produced it. Saved project revisions are the next substantial creator-workflow feature. The new low-VRAM report deserves an early reproduction, but the first comparison must use the already implemented isolated engine.

This addendum extends the [original contribution plan](README.md) beyond its MLX and MCP fixes and markup-streaming proposal. All feature value rankings, effort assessments and experiment targets are recommendations. No new feature here is claimed, assigned or approved by this document.

## Snapshot, method and confidence

- **Final repository refresh:** 22 November 2026, **17:18:54 UTC / 12:18:54 America/Bogota**.
- **Upstream baseline:** [2bb21302241793977055c44f7c52815bcbf0261e](https://github.com/debpalash/VoiceStudio/commit/2bb21302241793977055c44f7c52815bcbf0261e).
- **Current open inventory:** 29 issues and 15 PRs. The PR heads are unchanged from the [earlier complete file audit](backlog-audit.md), so its 175 changed-file entries remain applicable.
- **New evidence:** [#4355](https://github.com/debpalash/VoiceStudio/issues/4355) was opened after the earlier 28-issue snapshot and reports retained GPU memory after OmniVoice unload.
- Three research tracks covered creator workflows, quality/evaluation/automation, and performance/architecture. Additional synthesis checked current roadmap guidance, existing prediction controls and the real-time voice-conversion proposal.
- Source/schema inspection and targeted historical searches establish bounded implementation gaps. They do not establish customer demand, a measured speedup, model accuracy or the absence of unpublished work.
- No models were installed, no synthesis/ASR/benchmark/listening experiment was run, and no product code was changed.

The older backlog document deliberately retains its own timestamp. The additional issue and research conclusions belong to this later snapshot.

## Shortlist

The order reflects investigation value and scope, not a measured numerical score. Effort is relative and excludes hardware access and upstream review.

| Option | Type | Existing foundation | Precise addition to investigate | Effort | Main decision gate |
|---|---|---|---|---|---|
| 1. Saved audition sessions | Creator feature | Compare Voices, History, starred takes, settings reuse | Persist comparison groups, alternatives and the selected take | Medium | Reopen the exact decision and audio after restart without regeneration |
| 2. Check spoken text | Quality feature | Signal checks and dubbing ASR QC | Explain possible missing/added/repeated speech in ordinary takes | Medium | Useful error detection with tolerable ASR false alerts |
| 3. Free the GPU worker during finalization | Runtime optimization | Guarded GPU pool and separate watermark executor | Move long-form CPU marking and durable save outside synthesis occupancy | Medium | Better short-request wait time without memory or publication regressions |
| 4. Generation receipts | Shared foundation | Take settings, backend history, live engine evidence | Durable effective model/reference/runtime/processing record per audio artifact | Medium | Accurate attribution, unknown fields explicit, restart-safe persistence |
| 5. Named project revisions | Creator feature | Saved projects, copies, undo, render recovery | Revision history, focused diff and restore as a new copy | Medium–large | Recover editorial inputs without overwriting newer work |
| 6. Explicit GPU release policy | Resource feature/investigation | Existing OmniVoice subprocess backend and unload APIs | Make useful device release understandable and reliable across sessions | Investigation first | Reproduce #4355 and compare correct native/sidecar lifecycle paths |
| 7. Correct and extend benchmark evidence | Measurement tooling | Pipeline/startup benchmarks, quality sweeps, probe judges | Correct cold timing, shared manifests and comparable real adapter runs | Small first PR; medium follow-up | Comparable definitions, actual engine evidence and bounded cleanup |
| 8. Disk-backed long-form assembly | Structural optimization | Segment caches, durable chapter files, disk-backed dubbing | Bound retained chapter waveform memory | Large | Reduced memory growth with unchanged audio and failure semantics |
| 9. MCP controls and generation details | Automation feature | Existing MCP generation and HTTP controls | Optional engine/seed/precision plus additive result metadata | Small–medium | Old defaults unchanged; one request produces one generation |
| 10. Real-time voice changer | Ambitious feature | Existing offline Convert and approved research direction | Live conversion and selected output device | Large; hardware gated | End-to-end latency and uninterrupted audio meet the owner's test |

The detailed evidence and acceptance matrices are in [product workflows](research/product-workflows.md), [quality and automation](research/quality-and-automation.md), and [performance](research/performance.md).

## 1. Durable audition sessions: strongest new creator feature

### What changes for the user

A creator can keep a decision such as “Narrator for chapter one,” reopen its script and candidate takes later, hear the same saved recordings, add another alternative and record the chosen take. This makes an iterative creative decision durable.

The current app already compares two voices and saves individual generations in History. The inspected [comparison store](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/tools/comparison-state.ts) contains text, two voice IDs, search strings and temporary object URLs. The [comparison run](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/tools/compare-voices.tsx) clears its two preview slots when generating another comparison. It does not persist a named session, candidate membership or a winner. Existing takes may survive in History; their relationship is the missing part.

### Small first scope

Save one script and a list of existing/generated take IDs, with a selected candidate and optional concise decision note. Reuse the existing player, History and voice picker. Start on the active engine. Cross-engine sweeps, automatic quality ranking and new voice-picker behavior would expand the first PR unnecessarily.

Before persisting membership, establish the retention contract. A session reference must not silently disappear when normal History pruning runs. Use existing pin/reference mechanisms where possible and make intentional deletion precise. A session should reference audio instead of duplicating every waveform.

### First proof and stop condition

Create a disposable session from two existing takes, reload the renderer, reopen both recordings and add a third candidate. Verify that settings changes create a new candidate rather than rewriting old metadata. Cancel a new generation and confirm earlier candidates remain usable.

Then compare this workflow with ordinary starring/history during a small creator trial. Continue if it makes recovering and extending past decisions easier. If users can already accomplish the task just as reliably with current History, narrow or reject the extra session UI.

Reliable recipe comparison can build on option 4. Reopening the same saved audio is a stronger initial contract than promising identical future synthesis. Avoid collisions with [#4216](https://github.com/debpalash/VoiceStudio/pull/4216)'s shared picker work.

## 2. Spoken-script completeness review: strongest quality feature

### What changes for the user

After generating an ordinary Clone/Design take, the user can choose “Check spoken text.” The result presents the intended spoken text beside recognition results, highlighting possible insertions, omissions, repetitions and substitutions, with playback locations when actual timestamps exist.

This extends existing tools. [Ordinary audio quality checks](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/audio_quality.py) inspect signal properties such as silence, clipping and volume. [Dubbing QC](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/dub_qc.py) already compares recognized content with target text. Ordinary generation also reports empty/dropped chunks, but a nonempty waveform can still say the wrong words. [#4199](https://github.com/debpalash/VoiceStudio/issues/4199) is a relevant user report; its claimed audio errors and root cause have not been independently reproduced here.

### First investigation

Use the existing local ASR admission/loading and script-aware scoring seams. Compare the text actually intended to be spoken after pronunciation/number/markup preparation; raw authoring markup is not a suitable reference. Treat timing as unavailable when the recognizer cannot provide it. Aligning the requested script to audio is not independent proof that every requested word was spoken.

A proposed pilot is 12 short scripts across two initial languages, two installed engines and two seeds, plus deliberately labeled missing/added/repeated-speech cases. Include clean negatives, numbers, names, acronyms and code switching. This is a proposed 48-take study, not an executed result or a sufficient universal shipping validation.

Measure false alerts per minute, detection of obvious content errors, location accuracy, wall time and peak memory. Have listeners label the audio before seeing automated flags.

### Decision boundary

The first release should remain advisory. ASR itself can hallucinate, repeat or misrecognize speech, and accuracy varies by language and dialect; the [Whisper model card](https://github.com/openai/whisper/blob/main/model-card.md) documents these limitations. If the system cannot separate obvious test errors from clean takes, expose a transcript comparison without a “quality passed” verdict.

Keep checking explicit, local and cancellable. Do not automatically rerender, replace the script or download another model. It must respect the same resource-admission policy as other ASR work.

## 3. Release the GPU worker before long-form finalization

### Verified scheduling gap

The inspected [audiobook path](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/audiobook.py#L933-L1051) submits a callable that includes chapter synthesis, synchronous watermarking, durable WAV writing and cache-input recording. [The gateway](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/gpu_gateway.py#L98-L116) executes that whole callable inside the guarded GPU pool. Its slot therefore remains occupied while post-synthesis CPU and filesystem work finishes.

The repository already provides [asynchronous marking on a dedicated executor](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/watermark.py#L464-L515). The opportunity is to apply the existing separation carefully to long-form work.

### Experiment before architecture

Measure the current synthesis, marking and save phases independently. Submit a short speech request while a chapter is in deliberately controlled finalization. A deterministic test should demonstrate the scheduling boundary; real one-worker measurements should establish whether the wait is material.

The desired outcome is shorter wait and earlier audio for another request while the chapter completes. Total book rendering may stay unchanged. Report both, along with peak host memory and CPU pressure.

### Correctness constraints

Separate synthesis from publication, with bounded finalization admission or a byte budget. Merely putting full chapter tensors into another executor can create an unbounded queue and increase memory use. Keep reference/cache leases until actual workers stop, including cancellation. Announce completion only after the existing marking and durable-write boundary, preserving disk-full, shutdown, resume and partial-file handling.

Continue if a meaningful contention improvement survives these checks. Stop if finalization is negligible, CPU contention only relocates the delay, or safe ownership requires a larger rewrite than the measured benefit justifies.

## 4. Durable generation receipts

A generation receipt would explain how an exact saved artifact was produced: requested versus effective engine/model, available model revision, seed and seed support, reference identity, resolved language, processing options, app/runtime versions and output identity.

Current [take settings](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/lib/store/takes.ts) already support reuse for the latest 200 locally stored entries. Current backend history keeps important fields, and [engine evidence](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/engine_evidence.py) already exposes sanitized loaded-runtime information. The residual is attaching effective evidence durably to the particular generation instead of reconstructing it later from current Settings.

Start with an additive receipt linked to an audio ID for local native and sidecar paths, accessed through HTTP/MCP clients. Unknown provider or model facts must remain unknown. A hash can identify a reference but cannot recreate missing audio. Default export should omit paths, credentials and raw reference recordings.

This supports saved auditions, issue reproduction and baseline-versus-candidate evaluation. It does not guarantee identical output on another GPU or library version; [PyTorch's reproducibility guidance](https://docs.pytorch.org/docs/2.15/notes/randomness.html) explicitly limits that promise.

## 5. Named project revisions

Current [project storage](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/longform/project-library.ts) replaces one saved draft for each project ID. Its underlying writer revision is concurrency metadata. Existing manual copies, dubbing undo, output history and job recovery solve other preservation needs.

The new feature would save explicit editorial checkpoints, show differences in script/cast/pronunciation/settings, and restore an old revision as a new copy. Begin with Stories/Audiobook and explicit saves; do not attempt every-keystroke history, cloud collaboration and all project types together.

The critical trial is A → edit/save B → restart → compare → restore A as C, preserving B and its media. Test failed storage writes, missing voices, schema upgrades, stable line identity, and retention. Decide whether a checkpoint promises input recovery, retained rendered media, or both. Start with input recovery and describe missing media honestly.

This is a strong product gap but a broader persistence change than audition sessions. Dubbing integration needs coordination with [#4217–#4221](https://github.com/debpalash/VoiceStudio/pull/4221).

## 6. Low-VRAM resource handoff

The new [#4355](https://github.com/debpalash/VoiceStudio/issues/4355) reports about 2.1 GiB still attributed to a process after OmniVoice unload on a 6 GB NVIDIA system. These are reporter measurements; “all remaining bytes are CUDA context” is not a diagnosis established by this review.

An [isolated OmniVoice engine already exists](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/docs/engines/omnivoice-subprocess.md). MPS selects it automatically; CUDA/ROCm/CPU can choose it explicitly. Compare current main's native engine with that existing implementation before building another worker or changing defaults.

Record per-PID device usage, Torch allocated/reserved memory, other loaded engines, correct lifecycle IDs, actual idle state and next-request reload cost. Calling native TTS unload after selecting a sidecar is not a valid sidecar-unload experiment.

If isolation releases enough capacity, the worthwhile feature may be an explicit “release the device between sessions” policy and truthful status. Distinguish keeping a model warm, moving weights to RAM, and terminating an idle model process; each has different latency/resource consequences.

[PyTorch cache clearing](https://docs.pytorch.org/docs/2.15/generated/torch.cuda.memory.empty_cache.html) releases unused allocator cache, not every class of process-held GPU memory. The proposed [NVIDIA checkpoint mechanism](https://docs.nvidia.com/cuda/cuda-driver-api/cuda_driver_api/group__CUDA__CHECKPOINT.html) is Linux-specific and locks CUDA operations during its lifecycle. Treat it as a separate advanced investigation only if ordinary process isolation cannot satisfy the validated need.

## 7. Correct benchmark boundaries and reuse the evaluation tools

A source-confirmed inconsistency makes a small, useful first contribution possible. [bench_pipeline.py](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/scripts/bench_pipeline.py#L158-L214) resolves the backend before starting the timer labeled cold model load plus synthesis. [Native OmniVoice resolution](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/tts_backend.py#L5261-L5317) already awaits model loading, so that work falls outside the timer; lazy sidecars can include it in their first call.

First separate resolution/load, first synthesis and end-to-end first use. Prove the distinction using controlled fake load and synthesis intervals. The correction improves measurement; it does not itself accelerate inference.

Then reuse the existing pipeline/startup harness, installed-engine precision sweep and probe judges for a common fixture/receipt schema. Add bounded warm repetitions, real first-emitted-audio timing, process-tree memory where observable and baseline comparisons. Separate missing models, unsupported capabilities and unknown counters from failures and zero measurements.

Quality evidence should come from actual installed adapters and annotated audio, not synthetic judge tests alone. The current tools already contain many needed pieces; [the quality appendix](research/quality-and-automation.md) identifies which tests use fake audio/transcripts.

The owner deliberately removed the old weekly eval workflow in [#4032](https://github.com/debpalash/VoiceStudio/pull/4032). Keep this an explicit local experiment; do not revive periodic model downloads or a broad upstream training/evaluation reorganization.

## 8. Disk-backed long-form audio assembly

[Chapter synthesis](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/audiobook.py#L389-L549) retains span tensors while assembling a full chapter. [Watermarking](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/watermark.py#L584-L630) bounds per-chunk model activation memory but still collects complete output. Linear-time concatenation already exists; the target is retained waveform storage.

By arithmetic, one hour of mono float32 audio at 24 kHz is 345.6 MB per complete waveform. That is not measured process RSS. Several simultaneously retained copies, model memory and processing buffers raise the actual working set.

Investigate a private disk spool with bounded overlap buffers, reusing durable segment cache files and the existing publication contract. Test increasing-duration fixtures, peak memory, disk use, exact sample count, gaps, crossfades, silence/room tone, loudness, marking and cancellation.

Global processing may need two passes or a supported fallback. A memory map alone does not guarantee flat RSS because mapped pages and the OS cache still matter. Interactive dubbing already has disk-backed mixing; begin with long-form rather than replacing that work.

## 9. MCP controls and inspection

Current [MCP generation](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/mcp_server.py#L924-L1021) lacks optional seed, engine and WAV-precision arguments that the HTTP route already supports. Its result also omits useful seed/routing/dropped-text information.

A small feature can add supported optional controls and additive response metadata while preserving omitted-argument behavior and the existing default step count. Generation receipts can later provide a stable details resource; explicit quality checks can become a separate tool.

Prove exact forwarding against a fake backend, one generation POST per call, unchanged authentication/caller identity, useful errors and compatibility with older servers. This remains separate from the [stdio session repair](02-mcp-stdio-session.md). Recovery must not silently repeat a potentially mutating generation.

## 10. Real-time voice conversion: the ambitious research track

[#3420](https://github.com/debpalash/VoiceStudio/issues/3420) has real workflow demand for Discord/OBS/calls. The maintainer approved an opt-in direction and set a concrete experiment: microphone-to-speaker latency at or below 300 ms with no dropped/late audio over five minutes.

The [latest maintainer result](https://github.com/debpalash/VoiceStudio/issues/3420#issuecomment-6790571974) says MeanVC2 failed that bar on an M2. It directs the next test toward Seed-VC on an RTX 3060-class GPU. Do not repeat the already completed MeanVC2 study as a new contribution.

Two findings raise the uncertainty: [Seed-VC's official repository](https://github.com/Plachtaa/seed-vc) is archived, and its README describes roughly 300 ms algorithm delay plus roughly 100 ms device delay. Those upstream figures are not an end-to-end VoiceStudio measurement and do not establish the required 300 ms result.

The first deliverable should be a pinned, optional hardware experiment measuring capture, conversion, buffering and playback together, with late-block counts and voice quality. Only after it passes should the application UI, device routing and installation path be built. Platform-specific virtual-device setup and the maintainer's optional-engine packaging policy remain part of the existing proposal.

This could become a visible differentiator. Its feasibility and maintenance risk make it a research project, not the easiest next feature PR.

## Additional options considered

| Option | Why it may matter | What must be established first |
|---|---|---|
| Native batch reduction after OOM | Current width can remain unchanged after a failed group, wasting repeated attempts | Reproduce repeated waste; preserve seeds/order/timeouts; coordinate #4220. See performance appendix E. |
| Editable timeline export to one external editor | Segment ZIPs and native project bundles do not carry an editor-specific timeline | Confirm one creator workflow and target editor, then import a small overlap/timing fixture; coordinate #4220/#4221. |
| Human review notes tied to an audio version | Editorial approval and automatic QC express different information | Validate demand and exact invalidation on edit/regenerate/split/language change. Keep first scope local. |
| Chapter-level voice consistency review | Long narration can vary in perceived speaker identity | Compare deliberate substitutions with normal expressive/language variation and human listening. No universal similarity cutoff. |
| Confidence and identity in existing speed estimates | Current predictions can be improved after model/runtime changes | Measure calibration error and freshness; extend existing estimator instead of adding another ETA system. |

The last option has a concrete current boundary. [render-speed.ts](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/lib/audio/render-speed.ts) keys samples by engine/device and models characters and steps from at most 12 observations, without a model revision or language in that key. [Rolling long-form ETA](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/longform_progress.py) and [hardware-aware memory plans](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/performance_budget.py) already exist, and [#3929](https://github.com/debpalash/VoiceStudio/pull/3929) already offers faster settings from local measurements.

A useful forecast experiment would compare the existing point estimate with identity-aware, aged samples and uncertainty ranges on held-out runs. Unknown evidence should produce “not enough data,” and a new model should not inherit a false precision from another model's history. Full pre-run project forecasts should wait until the basic model's calibration is demonstrated.

## Investigation sequence and deliverables

### First creator-feature proof

Prototype saved audition membership using existing History IDs and exact stored audio. Deliver the persistence contract, deletion/retention behavior and a creator workflow comparison. Proceed to a focused feature PR only if the session materially improves the task.

### First quality proof

Define the small labeled spoken-content corpus and receipt schema separately. Deliver false-alert/detection results and a receipt coverage matrix for native/sidecar plus HTTP/MCP entry points. This resolves model limitations and attribution independently.

### First performance proof

Correct benchmark cold timing, then measure long-form finalization occupancy. Deliver paired timing reports and a deterministic scheduling regression. Reproduce #4355 on suitable hardware alongside this work, using existing isolation as the comparison baseline.

### Larger work after evidence

Choose disk-backed chapters if realistic memory growth is substantial; choose named project revisions if creator feedback favors safer editing history; choose real-time conversion only after the five-minute latency gate passes. Native batching and dubbing export/review features need coordination with the active dubbing series.

Every investigation should end with a decision record: observed baseline, experiment identity, actual result, uncertainty, proceed/narrow/stop decision, and the smallest reviewable implementation slice. A negative result is useful when it prevents a broad change without benefit.

## Work already covered and contribution boundaries

Current source already implements two-voice comparison, take history/reuse, project bundles, partial regeneration, resumable jobs, workflow graphs/checkpoints, ordinary signal checks, dubbing ASR QC, hardware-aware presets, long-form ETA, multiple caches and substantial startup/UI optimizations. The appendices cite the relevant implementations and merged PRs.

[Engine acceptance policy](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/docs/engine-acceptance.md) requires a specific unmet job, demand evidence, compatible architecture and a steward for new integrations. Adding a model solely to expand the catalog is therefore a weak initial direction.

Keep behavior local-first and downloads explicit, reuse current Electron controls, translate new UI strings, preserve provenance marking and retain input/audio ownership until workers finish. Each runtime change needs a meaningful failing-before/passing-after regression and focused documentation. Review current main and public ownership again before implementation. The new proposals are not reservations or maintainer commitments.

## Detailed research appendices

- [Product and creator workflows](research/product-workflows.md): saved auditions, revisions, editable timeline handoff, version-linked review notes.
- [Quality, evaluation and automation](research/quality-and-automation.md): spoken-content review, generation receipts, MCP controls, real-adapter corpus evidence, voice consistency.
- [Performance and architecture](research/performance.md): benchmark timing, CPU finalization, disk-backed chapters, low-VRAM release, native-batch backoff.

All implementation and experiment details in these documents remain proposals unless explicitly identified as source observations or historical/reporter evidence.

