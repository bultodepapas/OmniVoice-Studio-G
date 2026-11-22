# VoiceStudio: residual performance and architecture opportunities

## Review basis

Source review on **22 November 2026**. Upstream `main` remained **`2bb21302241793977055c44f7c52815bcbf0261e`**. The open-PR refresh returned the same **15 PRs and heads** as the [previous audited inventory](../backlog-audit.md). The new [low-VRAM report #4355](https://github.com/debpalash/VoiceStudio/issues/4355) was read; it had no comments at 17:13:39 UTC.

This is research, not an implementation or benchmark report. Source behavior below is verified by inspection. Proposed improvements, experiments, thresholds and effort estimates have not been run or validated on hardware. Reporter and historical PR measurements are not measurements made during this review.

The strongest immediate pair is:

1. **Correct and extend the existing inference benchmark**, starting with an actual cold-timing inconsistency.
2. **Release the GPU worker before long-form CPU finalization**, if a controlled queue-latency experiment shows that the remaining occupancy matters.

**Disk-backed chapter rendering** is the largest structural memory opportunity. **Strict GPU release** is the most urgent new user-reported investigation, but the underlying subprocess implementation already exists. **Adaptive native-batch backoff** is promising but overlaps active dubbing work.

| Candidate | Verified residual | Main benefit to test | Relative effort | Confidence / duplication |
| --- | --- | --- | --- | --- |
| A. Honest cold/warm inference benchmark and portable reports | Native OmniVoice loads during resolution before the timer labelled cold load+synthesis; limited per-engine observations, sidecar VRAM unavailable | Reliable performance comparisons and hardware evidence | Small for timing correction; medium for report/fixture extension | High source confidence; extend existing harness and judges |
| B. Long-form CPU finalization outside the GPU worker | One GPU-pool job includes synthesis, CPU marking, durable WAV write and input-record persistence | Lower wait for another speech request during finalization | Medium | High source confidence; runtime payoff unmeasured |
| C. Disk-backed long-form chapter assembly | Span tensors remain live through whole-chapter joining; watermark output is collected into a full tensor | Lower peak host memory for very long chapters | Large | High source confidence; preserve existing joins, marks and cache durability |
| D. Explicit low-VRAM release using existing isolation | Canonical OmniVoice remains in-process on CUDA/ROCm/CPU; optional sidecar already exists | Return enough device capacity for another local application | Investigation small; policy change medium/large | New #4355, attribution unverified; do not recreate the sidecar |
| E. Native batches that shrink after OOM | Width derives from total device capacity and stays fixed after failed groups | Avoid repeated expensive batch failures and improve useful throughput | Medium plus GPU validation | Verified fixed-width control flow; overlap with open #4220 |

Effort ranges below are planning estimates for focused work by a contributor familiar with these paths. They exclude hardware availability, model setup, upstream review and unforeseen compatibility work.

## What is already present

The [performance tracker #3924](https://github.com/debpalash/VoiceStudio/issues/3924) is a useful goal list, but its unchecked boxes are not a current implementation inventory.

- [#4320](https://github.com/debpalash/VoiceStudio/pull/4320), [#4321](https://github.com/debpalash/VoiceStudio/pull/4321), [#4322](https://github.com/debpalash/VoiceStudio/pull/4322) and [#4323](https://github.com/debpalash/VoiceStudio/pull/4323) are merged. Startup/import/database work, renderer timer isolation, lazy waveforms, lighter polling, installer pruning, test sharding, combined media extraction, optional ASR batching and NLLB fp16 are already covered.
- The existing [one-engine residency policy][engine-memory] evicts other idle TTS engines. [#4043](https://github.com/debpalash/VoiceStudio/pull/4043) avoids redundant reloads on unchanged local-folder saves. [#4117](https://github.com/debpalash/VoiceStudio/pull/4117) already adds low dedicated-VRAM cleanup before generation.
- Long-form has [chapter and segment content-addressed caches][longform-cache], resumability, durable cache writes and cache leases. Adding basic sentence reuse or crash recovery would duplicate shipped behavior.
- Interactive dubbing already [mixes into a memmap][dub-mix-call], uses [bounded PCM conversion][dub-mix-helper], and [#3986](https://github.com/debpalash/VoiceStudio/pull/3986) streams temporary ZIP archives. A generic “stream dubbing to disk” proposal is too broad.
- Native TTS batching, accurate streaming TTFA and operation-count regression guards already landed in [#1620](https://github.com/debpalash/VoiceStudio/pull/1620) and [#1622](https://github.com/debpalash/VoiceStudio/pull/1622).
- Current [chunk concatenation][linear-join] is a single-pass allocation. The residual memory issue is retaining and materializing full audio, not an uncorrected quadratic concatenation algorithm.
- [#1129](https://github.com/debpalash/VoiceStudio/pull/1129) documented that extra concurrent MPS synthesis workers did not improve its tested workload, and per-segment reference encoding was a small part of that dub. Do not turn those old intuitions into new recommendations without a different measured workload.
- The previously planned progressive markup streaming contribution concerns earlier audible output from `/generate`; candidate C concerns final audio working memory in long-form. They are distinct, but both must preserve gap, watermark and cancellation semantics.

## A. Correct cold timing, then extend the existing inference benchmark

### Evidence and current behavior

[`scripts/bench_pipeline.py`][pipeline-bench] already provides TTS, cloning and ASR stages, a RAM floor, model cleanup attempts, a cold-labelled call, two warm calls and CUDA allocator peak reporting. It should be extended rather than replaced.

A concrete timing-boundary inconsistency exists:

1. `bench_tts()` resolves the backend at line 171.
2. [`resolve_generation_backend()`][resolve-native] explicitly awaits `get_model()` for the native OmniVoice class.
3. Only later, line 200 times `gen(SHORT)` and labels it “model load + first synth (cold)”.

Thus native OmniVoice model load is outside that timer; a lazy sidecar can load within its first `generate()` call. The label does not describe a comparable cold path across these implementations. No hardware timing is required to verify this ordering, although the size of the discrepancy is unmeasured.

The profiler also selects local macOS dub-reference paths for clone/ASR samples, takes one warm short and one warm long observation, and has no explicit seed in the TTS call. Its sidecar VRAM result is correctly reported as unavailable because parent Torch counters cannot see child allocations. [`docs/benchmarks.md`][benchmark-doc] still has no verified result rows. The [startup harness][startup-bench] already supplies isolated profiles, process-tree RSS and repeat summaries; reuse those conventions. [`performance_probe.py`][runtime-probe] checks runtime readiness in a child, not inference latency. [`render_trace.py`][render-trace] already supplies bounded local stage timing.

### Proposed contribution

Start with a small correctness PR: report backend resolution/load separately, define end-to-end first-use explicitly, and prove that preloading cannot escape the cold total. Retain separately useful first-synthesis and steady-state measurements.

A follow-up can accept an explicit fixture manifest with model revision, device/runtime versions, engine settings, reference hash and seed; export machine-readable reports; and aggregate a bounded number of comparable warm runs. Add actual first-emitted-audio timing through existing streaming surfaces instead of calling full render time TTFA. Reuse `/ws/tts`'s existing metric semantics, which distinguish synthesis time from client delivery time.

Collect process-tree RSS and, where supported, process-specific device memory. Keep unknown fields null rather than claiming zero. Parent allocator “allocated” and “reserved”, process VRAM and total device usage are different metrics.

Quality evaluation belongs to the existing `tests/probe` judges and the complementary quality-corpus investigation. Share the manifest/identity and result schema; do not build another evaluation framework or auto-select a “best” voice from timing.

### Experiment and decision

- Proposed deterministic regression: a fake resolver incurs a known controlled load interval and returns a backend with separate synthesis work. The reported cold total must include both, while warm measurements exclude resolution. Also cover a lazy sidecar-shaped backend.
- On an installed CPU engine and one installed native/sidecar accelerator pair, collect isolated cold runs and at least five paired warm observations. Keep them separate; never download models as a side effect.
- Confirm identical fixture identity and output duration across compared runs; present unsupported settings or unavailable memory counters explicitly.
- Go when timing definitions are correct, results are reproducible and cleanup leaves no harness-owned child running. The small correction does not need to promise a product speedup.
- Stop expansion if it duplicates an existing judge, requires live user recordings by default, or cannot distinguish load time from inference.

**Effort estimate:** 1–2 focused days for timing boundaries/tests/docs; 3–5 more for portable fixtures, JSON comparisons and cross-process memory, plus hardware access. CPU fakes prove semantics, not CUDA/MPS performance. No current open PR in the audited list changes `bench_pipeline.py`.

## B. Move long-form CPU finalization out of the GPU worker

### Evidence and current behavior

The exact call chain is:

- [`audiobook._run_chapter()`][run-chapter], lines 1039–1048, submits `_render_chapter_cached()` as one `gpu_gateway.LocalCall`.
- [`gpu_gateway._run_local()`][gpu-gateway] dispatches that call through `run_on_gpu_pool_guarded`.
- [`_render_chapter_cached()`][chapter-finalize], lines 983–1001, synthesizes the chapter, calls `mark_synthetic()`, writes the marked WAV with `durable=True`, and records cache inputs before returning.

Consequently that GPU-pool slot remains occupied through the chapter's CPU provenance work and filesystem persistence. This is an inspected scheduling fact, not proof of an observed latency regression.

The repository already has [`mark_synthetic_async()`][async-mark] backed by a dedicated watermark executor. Generate, Batch, voice conversion and other paths use it. The current [Batch finalizer comments][batch-mark] explicitly explain why CPU marking should not occupy a GPU worker. Long-form is a residual user of the synchronous arrangement.

### Proposed contribution

Separate the result of synthesis from publication. Return an owned chapter audio/result descriptor from the guarded synthesis call, perform marking on the existing watermark executor, and perform durable persistence on a bounded I/O worker. Publish chapter completion only after the same successful persistence boundary.

Begin with one chapter awaiting finalization; do not introduce unbounded chapter prefetch or multiple concurrent GPU models. The existing watermark executor uses an unbounded internal queue, so moving work there alone does not establish memory backpressure. Add a bounded long-form finalization admission count or byte budget, acquired before producing another full chapter and outside the GPU worker. Release it only when the actual finalizer has stopped, including after caller cancellation. Avoid changing synthesis seeding, segment cache writes or audio processing order. A cache hit should remain cheap and need not enter the heavy GPU stage if preparation can safely prove it.

### Experiment and decision

- Use the existing render trace to measure synthesis, marking and save separately for a representative chapter. Measure GPU-pool occupancy independently of end-to-end chapter time.
- Submit a short unrelated synthesis request when the first chapter enters deliberately controlled marking/save work. A deterministic test must show the second request starts while finalization remains pending, while the first chapter is not announced complete early.
- With installed models, alternate before/after runs on a one-worker host. Compare short-request queue wait, first audio, chapter total time, peak RSS and CPU saturation. A shorter finalization occupancy is useful even if total book time is unchanged.
- Proposed study gate: continue if queue delay is repeatably material and falls without a meaningful whole-job/memory regression. A 10% improvement in the chosen contention workload and investigation of a sustained >5% total-time regression are possible review thresholds, not repository rules or claimed measurements.
- Preserve reference/cache leases until real workers stop, marking exactly once, cancellation during queued/running finalization, disk-full errors, atomic replacement, resume after failure and shutdown behavior. A saturation test must show a bounded number of retained chapter waveforms and fair progress without admitting unlimited finalization tasks.
- Stop if finalization is negligible on realistic workloads, CPU contention simply moves the delay elsewhere, or safe ownership requires a broader rewrite than justified.

**Effort estimate:** 3–5 focused days plus hardware checks. Existing long-form cancellation/cache/provenance tests provide the regression base. No audited open PR edits the principal audiobook or watermark files. This is distinct from [#4198](https://github.com/debpalash/VoiceStudio/pull/4198), which moved interactive dub marking off the event loop, but should reuse that established executor contract.

## C. Bound long-form audio working memory with disk-backed assembly

### Evidence and current behavior

[`synthesize_chapter()`][chapter-assembly] accumulates rendered chunks and span tensors, records them in `items`, materializes gaps and allocates the joined chapter. [`concatenate_audio_chunks()`][linear-join] is already linear-time, but the original pieces remain live while the output is allocated.

[`embed_watermark()`][watermark-assembly] bounds the model's per-chunk activation memory, then collects all marked chunks and concatenates the full output. Bounding the model's activations is not the same as bounding total waveform storage.

The Batch route also allocates [`full_audio = torch.zeros(1, total_samples)`][batch-full-track]. Interactive dubbing is already disk-backed and provides useful publication/PCM-conversion patterns, but its marked-segment flow is not a drop-in replacement for whole-chapter marking.

For scale only, one hour of mono float32 at 24 kHz requires **345.6 MB per full waveform** by arithmetic (`24,000 × 3,600 × 4` bytes). That is not measured process RSS; retained inputs, output, marking intermediates, allocators and model memory add other costs.

### Proposed contribution

Start only with long-form chapter final assembly. Keep completed segments in existing durable cache files, stream their audio into a private chapter spool with bounded overlap buffers, and publish through the existing marked-cache contract. Preserve final M4B/MP3 assembly through ffmpeg's chapter-file inputs.

Digital silence is the simplest initial path. Room tone uses whole-take information; normalization/mark headroom can require global statistics and repeated passes. Use bounded two-pass processing or preserve an explicit fallback until equivalence is established. Do not silently substitute digital silence, drop watermarking, change loudness, add fades, or quantize intermediates earlier.

Treat Batch's full-track allocation as a later sibling contribution after the primitive is proven. Do not simultaneously redesign `/generate` progressive streaming.

### Experiment and decision

- Synthetic deterministic spans of increasing total duration in a separate process, with inference replaced by fixed waveform generation. Record peak RSS/private working memory, allocations, temporary disk size and I/O.
- Compare decoded audio, exact sample count, gaps, crossfades, trim, channel/dtype behavior, chapter metadata and marking detection before/after. Preserve unmarked segment caches and marked chapter caches.
- Real hardware: one long chapter on a 16 GB unified-memory or constrained-RAM machine, with the same installed model/settings/seed. Distinguish model residency from assembly memory.
- Go when increasing chapter duration no longer forces corresponding heap-sized audio copies, with acceptable disk overhead and no output changes. A memmap alone does not guarantee flat RSS because mapped pages and OS page cache still count; measure rather than infer.
- Stop if global room-tone/headroom behavior cannot be preserved, the spool can be published partially, or spill cleanup threatens valid cached segments.

**Effort estimate:** 1–2 weeks for a bounded initial path and robust failure handling; full room-tone/global-DSP parity can extend it. Low direct open-PR overlap on long-form. Larger architectural risk than A/B. Coordinate if extracting shared machinery from `dub_generate.py`, which open [#4220](https://github.com/debpalash/VoiceStudio/pull/4220) changes.

## D. Investigate strict low-VRAM release using the existing sidecar

### Evidence and current behavior

[#4355](https://github.com/debpalash/VoiceStudio/issues/4355) reports roughly 2.1 GiB remaining for a Linux CUDA process after unloading OmniVoice on a 6 GB card, and proposes driver checkpointing or subprocess isolation. Those are reporter observations and proposed causes; this review did not reproduce them.

Source already includes:

- [`OmniVoiceSubprocessBackend`][omnivoice-sidecar], using the same interpreter/model and the shared sidecar primitive.
- [Canonical OmniVoice host routing][effective-backend], which automatically selects isolation on MPS but retains native execution on other hosts.
- [Busy-guarded sidecar shutdown][sidecar-unload].
- [TTS unload][lifecycle-unload], which drops the native shared model; separate `sidecar:<id>` lifecycle IDs release child processes.
- [`free_vram()` and `unload_shared_model()`][native-unload], which already clear references, side caches, allocator caches and optional cuBLAS workspace state. Another generic GC call is not a root-cause explanation.
- [Documentation][sidecar-doc] explaining the existing opt-in and reload/round-trip tradeoffs.

Also, `omnivoice_checkpoint.py` resolves model checkpoint identity; it is not CUDA process checkpoint/restore infrastructure.

### Proposed contribution and experiment

First compare **current main** native OmniVoice and the existing explicit sidecar with the exact same installed model and request. Ensure per-request engine overrides really select the intended backend. Inspect the resident-model inventory and unload the correct native/sidecar ID; changing a backend ID while calling the native-only `tts` unload would be an invalid comparison.

Record, before load / after load / after synthesis / after unload / after idle:

- Parent and every child PID.
- Torch allocated/reserved values where meaningful.
- Process-specific device usage and total free device memory.
- Active ASR/translation/watermark models, live requests and loaded model identities.
- Next-request reload latency and successful output.

If existing isolation solves the practical issue, the new work may be a clear “release device between sessions” policy, a truthful UI/lifecycle status and documentation rather than new inference architecture. Preserve canonical saved project identity and make any reload-cost tradeoff explicit. Do not promise zero process VRAM while another model or the parent still owns a device context.

**Go:** reproduce on current main, attribute the retained memory, and prove that the proposed policy releases a useful amount without killing an active request. **No-go:** existing documented selection is sufficient with no product gap, the remaining memory belongs to another workload, or a new driver-specific checkpoint mechanism cannot satisfy lifecycle/platform requirements.

Do not start with the suggested CUDA driver checkpoint API. It adds restoration, concurrent-work and driver-support questions that are unnecessary if the existing containment path meets the need.

**Effort estimate:** 1–2 days for a proper reproducer on a suitable NVIDIA machine; policy integration 3–7 days plus CUDA/ROCm/MPS/CPU validation. A 6–8 GB NVIDIA card is needed to validate the reported scenario. No relevant open PR was found, but coordinate on #4355 before proposing a solution. It is open work, not an unclaimed new feature.

## E. Native TTS batches that shrink after a proven OOM

### Evidence and current behavior

[`native_batch_width()`][batch-width] derives widths of 1/2/4/8 from host-reported total device capacity minus the engine's declared minimum. It respects a bounded explicit override. This is already hardware-aware; “add device-aware batching” would duplicate it.

The residual is adaptation to a particular workload and a demonstrated failure:

- Interactive dubbing captures the width once and gathers compatible groups.
- [A failed native batch][dub-batch-fallback] clears OOM state as appropriate and returns to per-segment work; the stored width is not reduced.
- [Queued Batch fallback][batch-fallback] similarly retains its chosen width.
- Subsequent group attempts can therefore retry the same oversized width. Whether this causes repeated OOMs in a real workload is a hypothesis to reproduce, not an observed incident.
- Current policy does not use text-length/token-cost budgets for the group, or current free-memory feedback. Do not confuse it with NLLB translation batching, which already has separate live-headroom work.

### Proposed contribution and experiment

Begin with **per-job downward adaptation after classified device OOM**, not a global adaptive scheduler. Reduce the next native group width, preserve ordering/settings and bounded serial fallback, and keep the result local to the current engine/model/device/job. Do not repeatedly increase width during the same failing job. Preserve explicit overrides with a clearly defined safety policy.

A later extension may cap combined text cost before submission using measured engine-specific evidence. Do not reorder speech or lower decoding steps to make a speed graph look better.

- Fake native engine rejects widths above a chosen safe ceiling; prove a bounded number of failures, correct output ordering, no missing/duplicated segments, no retry after a true timeout and correct cancellation.
- Compare mixed short/long subtitle fixtures with fixed model/seed/settings on a constrained and a roomy GPU. Record useful segments/second, failed model calls, peak VRAM and per-segment quality.
- Go when repeated failed batches are reproduced and downward adaptation reduces wasted work without new failure/quality behavior. Stop if existing fallback already dominates negligibly or shape variation makes a stable safe width impossible.
- Seed behavior may vary with batch partitioning. Require reproducibility within a fixed execution strategy and quality checks; do not assume bit-identical samples across different batch shapes.

**Effort estimate:** 3–5 focused days plus two useful accelerator configurations. Extend `tests/test_dub_batch_width_and_budget.py`, `tests/test_perf_operation_budgets.py` and existing interactive/queued engine-selection tests. **High coordination need:** open #4220 changes `dub_generate.py`; choose a shared-helper scope or wait for that work rather than replace it.

## Why the strongest two are A and B

**A** starts with a narrow, provable defect that compromises comparisons: the same cold label has different load boundaries. It then improves the evidence needed to decide C–E. It needs no speculative caching strategy or new model downloads.

**B** has a precise existing-versus-missing contrast inside the repository: the dedicated CPU marking executor already exists, but long-form wraps marking and saving inside an accelerator job. Its benefit can be demonstrated with a deterministic scheduling test before buying hardware time. It should ship only if realistic contention traces justify the additional ownership boundary.

Choose **C** instead of B for a larger memory-focused project if realistic long chapters reproduce substantial memory growth. Investigate **D** promptly because it has a fresh user report, while treating existing sidecar selection as the first baseline. Keep **E** behind the active dubbing coordination boundary.

No claim is made that all five should be implemented. The first milestone is evidence that selects or rejects each proposal.

## Sources

[pipeline-bench]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/scripts/bench_pipeline.py#L158-L214
[resolve-native]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/tts_backend.py#L5261-L5317
[benchmark-doc]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/docs/benchmarks.md
[startup-bench]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/scripts/bench/bench.py
[runtime-probe]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/performance_probe.py
[render-trace]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/core/render_trace.py
[engine-memory]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/engine_memory.py
[longform-cache]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/longform_render.py#L415-L616
[run-chapter]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/audiobook.py#L1006-L1051
[gpu-gateway]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/gpu_gateway.py#L98-L116
[chapter-finalize]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/audiobook.py#L933-L1003
[async-mark]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/watermark.py#L464-L515
[batch-mark]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/batch.py#L745-L768
[chapter-assembly]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/audiobook.py#L389-L549
[linear-join]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/chunked_tts.py#L468-L533
[watermark-assembly]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/watermark.py#L584-L630
[batch-full-track]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/batch.py#L512-L525
[dub-mix-call]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/dub_generate.py#L1927-L1933
[dub-mix-helper]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/dub_mix.py
[omnivoice-sidecar]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/engines/omnivoice_subprocess/__init__.py
[effective-backend]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/tts_backend.py#L4611-L4633
[sidecar-unload]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/subprocess_backend.py#L194-L251
[lifecycle-unload]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/model_lifecycle.py#L306-L329
[native-unload]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/model_manager.py#L3837-L4019
[sidecar-doc]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/docs/engines/omnivoice-subprocess.md
[batch-width]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/dub_batching.py#L14-L41
[dub-batch-fallback]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/dub_generate.py#L1515-L1540
[batch-fallback]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/batch.py#L542-L618

