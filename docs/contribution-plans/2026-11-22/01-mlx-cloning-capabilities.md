# Plan 1: Preserve cloning intent when MLX model capabilities change

## Decision and status

Fix [issue #4344](https://github.com/debpalash/VoiceStudio/issues/4344) with a focused capability-and-readiness change. A model that cannot use a selected voice reference must not silently generate an unrelated voice and record it as a Design take.

This is an implementation plan, not an implementation or a test report. Source was inspected on 2026-11-22 at upstream commit [2bb21302241793977055c44f7c52815bcbf0261e](https://github.com/debpalash/VoiceStudio/commit/2bb21302241793977055c44f7c52815bcbf0261e). No application runtime, model synthesis, or test command was executed for this plan. Every test and measurement below is proposed.

At the final review checkpoint on 2026-11-22 at 16:37:12 UTC, #4344 was open and unassigned. The [audited backlog](backlog-audit.md) records all 15 open PRs, including the five new Dependabot PRs #4350–#4354, whose inspected changes are confined to pinned actions in GitHub Actions workflows. No listed PR addressed this issue. #4216 changes shared voice-option click activation, so avoid overlapping that behavior. Recheck the issue and PR queue before implementation and again before pushing; this snapshot is not a reservation.

**Suggested implementation PR:** `fix(clone): resolve MLX presets for the selected model`.

**Planning estimate:** one to two focused development days, followed by review and native Apple Silicon verification. This is an estimate, not a delivery commitment.

## Evidence and confidence

| Finding | Evidence | Status |
|---|---|---|
| MLX VoxCPM2 produces a different voice despite a selected saved clone; Recents shows Design without the profile | Reporter reproduced on VoiceStudio 0.5.8, Apple Silicon, Mandarin input in [#4344](https://github.com/debpalash/VoiceStudio/issues/4344) | Reported; not independently reproduced |
| The adapter currently enables cloning only for CSM and Qwen3 Base | [MLXAudioBackend.cloning_model_keys][mlx-class] and [supports_cloning][mlx-cloning] | Verified source |
| All MLX models inherit the 54 Kokoro preset IDs and Kokoro default voice | [MLXAudioBackend.PRESET_VOICES][mlx-presets]; its comment explicitly says other curated models have no presets | Verified source |
| The active engine payload resolves cloning per model but leaves inherited presets in the payload | [_family_payload][engine-payload] | Verified source |
| Unsupported cloning plus a nonempty preset list is treated as a usable preset engine | [useTtsReadiness and isPresetOnly][tts-readiness] | Verified source |
| The preset branch removes the selected profile and uploaded reference from the request | [profileId/refAudio construction in useGenerateController][request-identity] | Verified source |
| VoxCPM2's current MLX integration reserves cloning/design for the full VoxCPM2 engine | [models.yaml][model-catalog] | Verified source; upstream model capability is a separate question |
| Merely removing leaked presets may leave inaccurate guidance | [CloneReadinessNotice][clone-notice] treats unknown design support as a reason to suggest Voice Design | Verified source; validate resulting UI before choosing the minimal correction |

### Root-cause explanation

One backend ID, `mlx-audio`, represents several different models. Cloning support is resolved for the selected model, while preset voices are still read from the shared class. The renderer receives an internally inconsistent combination: a noncloning model with Kokoro's preset voices.

The renderer intentionally supports genuine preset engines on the Voice Cloning page. Given this inconsistent metadata, it chooses that valid preset workflow, omits the saved profile and reference, and submits ordinary speech. The server cannot reconstruct the user's omitted cloning intent from that request.

The repair therefore belongs at the model-capability boundary and its consumers. A special-case check for the string “VoxCPM2” in one button would leave the same class of bug available to other models and clients.

## Objectives and explicit scope

1. Resolve cloning support, applicable preset IDs and preset default from the same selected-model identity.
2. Advertise Kokoro presets only where the current adapter can use them.
3. Block an unsupported clone request before submission, explain the limitation, and keep the selected saved profile or uploaded reference intact.
4. Preserve correct CSM/Qwen3 Base cloning, genuine preset speech, language-specific Kokoro defaults, saved-profile attribution, and existing offline behavior.
5. Ensure the request-time backend validation and the UI's capability view agree, including when the caller supplies an explicit engine.
6. Keep capability inspection cheap: no model loading, inference, download, or heavyweight engine initialization.

### Non-goals

- Add MLX VoxCPM2 reference conditioning, voice design, a new engine, or new model weights.
- Remove the preset-only workflow used by Kokoro, KittenTTS or Supertonic-3.
- Rewrite the engine registry, generation queue, or profile store.
- Reclassify old generated takes or migrate existing saved data.
- Add a version bump, dependency upgrade, background network request, or telemetry.
- Repair the separate suspected long-stream preset-forwarding issue described below.

## Existing implementation map

| File | Existing seam and intended responsibility |
|---|---|
| [backend/services/tts_backend.py][mlx-class] | `MLXAudioBackend.configured_identity()`, `_curated_key()`, `supports_cloning`, `preset_voices_of()`, `list_backends()`: resolve applicable capabilities without loading weights; retain static engine defaults for fixed-capability backends |
| [backend/api/routers/engines.py][engine-payload] | `_family_payload()`: return one coherent capability snapshot for the selected model |
| [backend/api/routers/generation.py][preset-validation] | `generate_speech()`: validate a requested preset against the model actually used for this request, while preserving the existing saved-reference capability gate |
| [electron/src/renderer/src/hooks/use-tts-readiness.ts][tts-readiness] | `useTtsReadiness()` and `isPresetOnly()`: consume accurate metadata; keep the distinction between unsupported cloning and intentional preset speech |
| [electron/src/renderer/src/hooks/use-clone-readiness.ts][clone-readiness] | `useCloneInputsReadiness()` and `useCloneReadiness()`: preserve the input/readiness gate |
| [electron/src/renderer/src/hooks/use-generate.ts][request-identity] | `useGenerateController()`: submit the selected profile/reference only for a valid clone operation; retain the existing queue snapshot behavior |
| [electron/src/renderer/src/features/clone/clone-readiness-notice.tsx][clone-notice] | `CloneReadinessNotice`: give a valid next action for this model; do not suggest an unsupported design workflow |
| [electron/src/renderer/src/hooks/use-engines.ts][use-engines] | `activeTtsBackend()`, `useEngines()`: verify the existing invalidation/refetch behavior after selecting another model |

The source tree contains no nested AGENTS.md or CLAUDE.md below the root at this commit. The applicable [AGENTS.md][agents], [CLAUDE.md][claude] and [CONTRIBUTING.md][contributing] were read. Their relevant requirements are a focused fix, a regression that fails before and passes after, Electron-only UI work, offline tests, cross-platform behavior, same-PR documentation, and the normal review/CI gates.

## Implementation phases

### Phase 0 — Refresh the evidence and reproduce the failure

1. Start from the freshly fetched upstream main, following the fork workflow in CONTRIBUTING. Record its SHA and compare the files above with this pinned snapshot.
2. Read #4344, its comments, all open PRs, and any recent changes to MLX capabilities or generation readiness.
3. Create a temporary app/profile fixture. Do not use personal saved voices, production data, or the reporter's media without their permission.
4. Reproduce the misleading capability payload with mocked MLX identity and no installed model. Then reproduce the renderer request using a saved clone fixture, `supports_cloning: false`, and the incorrectly advertised presets.
5. On Apple Silicon with already installed models, separately check the reporter's flow. Record which parts were actually exercised; mocked coverage does not establish audio quality.

**Exit condition:** a behavioral regression demonstrates the capability mismatch or incorrect request construction on the baseline. If current main already prevents it, update or retire this plan instead of implementing a redundant fix.

### Phase 1 — Add regressions at the capability boundary

Extend the existing test seams rather than creating a second test framework:

- [test_active_cloning_capability.py][test-active]: expand the selected-model matrix to Kokoro, CSM, Qwen3 Base, Qwen3 VoiceDesign, VoxCPM2, other curated keys, an unknown repository, and supported local-model identity handling.
- [test_mlx_kokoro_preset_voices.py][test-kokoro]: keep all 54 Kokoro voices and language-specific fallback assertions. Make the active-model assumptions explicit; do not simply delete the existing list/default tests.
- [test_preset_voices_2938.py][test-presets]: preserve valid selection, default behavior, invalid-preset rejection, and fixed-capability non-MLX engines.
- [test_cloning_gate_model_dependent_2201.py][test-clone-gate]: retain model-dependent guidance and the no-weight-loading assertion.
- [test_voice_design_profile_and_capability.py][test-design]: retain the explicit server rejection when a saved sample is sent to a model that cannot clone.

Patch `_ensure_loaded()` to fail if invoked by metadata resolution. Arrange environment values and persisted preferences independently; an environment override remains authoritative. Include full repository IDs, not only aliases.

### Phase 2 — Resolve capabilities for the actual model

Choose the smallest compatible helper shape after inspecting current callers of `preset_voices_of()`. It may accept a resolved model/instance or use a model-specific adapter helper, but callers must not accidentally fall back to the class-wide Kokoro list.

Required behavior:

- Active Kokoro: applicable presets and default are preserved.
- Active non-Kokoro MLX model: no Kokoro presets or Kokoro default are advertised or validated as applicable.
- Active CSM/Qwen3 Base: cloning remains supported.
- Active VoxCPM2: current adapter limitation remains explicit; no unsupported capability is invented from an upstream model card.
- Unknown/custom model: no unproven presets are advertised. Preserve existing behavior for capabilities that remain genuinely unknown.
- Local model path: use the adapter's existing identity resolution. A missing local folder must not make the engine inventory disappear or load weights.
- Fixed-capability engine: existing metadata remains unchanged.

Use the same resolved capability logic for the active `/engines` payload and request-time preset validation. Check explicit `engine=` requests as well as the globally active engine. Preserve the existing API behavior for irrelevant optional fields unless a documented correction is necessary; do not introduce unrelated rejection changes.

Do not mutate a global class constant when the user switches models. That would leak one user's or request's selection into other metadata reads.

### Phase 3 — Make the clone UI truthful and reversible

Start by verifying whether the corrected payload makes the existing readiness gate sufficient. Keep UI changes small.

- An unsupported cloning model should show the existing blocked state before a generation is queued.
- Keep the selected profile, its transcript, uploaded reference and text draft while the user changes engines.
- Display a valid action to select a cloning-capable model. For MLX VoxCPM2, the existing unknown `supports_voice_design` value must not lead to an unsupported Voice Design recommendation. Resolve known capabilities or use truthful generic guidance; do not broadly redefine unknown-model support.
- Preserve the valid preset-only UI and its request construction.
- Recheck model switches in Settings, the environment-pinned case, a capability refetch, and a queued take whose execution starts later.

The queue currently snapshots engine selection. Same-backend model switches deserve an explicit regression, but a general queue/model-pinning redesign is outside this PR. If a new race cannot be handled by the existing server capability gate without changing the API, document it and split the work.

Any new user-facing key must be translated in every current locale catalog. This snapshot contains **22 catalogs**, although AGENTS.md still says 21. Enumerate the directory at implementation time; do not hardcode a stale count or copy English into non-English catalogs.

### Phase 4 — Validate the complete flow and document it

Use the acceptance matrix below. Then update the relevant engine/user guide to describe the current MLX limitation and the full-engine alternative accurately. Add the numbered changelog fragment when an implementation PR number exists; do not fabricate a PR number or edit CHANGELOG.md directly.

Run targeted tests while iterating. Before requesting merge, run the applicable repository-wide gates against the updated branch and read existing bot/human findings. Report an unavailable hardware check honestly.

## Acceptance matrix

| Scenario | Required result | Proposed verification |
|---|---|---|
| Saved clone + MLX VoxCPM2 | No Kokoro picker; visible clone blocker; no request or unlinked Design take | Backend metadata test, renderer test, Apple Silicon smoke |
| Uploaded reference + unsupported MLX model | Reference remains selected; no silent omission followed by synthesis | Renderer request test |
| Switch VoxCPM2 → Qwen3 Base | Existing profile can be used; request carries its ID; generated history remains linked | Renderer transition + API fixture + native smoke |
| CSM with valid reference/transcript | Existing clone flow remains valid | Existing clone regressions |
| Kokoro preset selected | Correct ID reaches the non-stream generation path; requested-language defaults remain correct | Kokoro and preset API tests |
| Supertonic-3 or KittenTTS | Intentional preset speech remains available | Fixed-capability control cases |
| Custom MLX repository or missing local folder | No invented Kokoro presets; inventory remains usable; no download/load | Capability tests with failing load sentinel |
| Environment pins another model | Environment value wins consistently in payload and execution | Preference/identity matrix |
| Model changes while a request is waiting | No unsupported clone is silently accepted; failure retains useful context | Queue/server boundary regression |
| Rejected clone | No output file or successful history row is published | API fixture inspection |
| Non-Apple-Silicon host | Existing unavailable-MLX behavior and other engines remain unchanged | Mocked platform matrix and desktop CI |

## Proposed validation commands

Use the repository's configured environment with isolated test data, `HF_HUB_OFFLINE=1`, and a newly empty `HF_HUB_CACHE`. Do not point automated tests at the user's cache. Provisioned real-model smoke tests are separate and use only explicitly prepared local fixtures.

~~~bash
uv run pytest tests/test_active_cloning_capability.py tests/test_mlx_kokoro_preset_voices.py tests/test_cloning_gate_model_dependent_2201.py tests/test_preset_voices_2938.py tests/test_voice_design_profile_and_capability.py -q
bun run --cwd electron locale:check
~~~

For focused renderer runs, use the current Electron test runner against `use-tts-readiness.test.ts`, `use-tts-readiness.test.tsx`, `use-tts-readiness-refresh.test.tsx`, `use-generate.test.tsx`, and `clone-readiness-notice.test.tsx`. Confirm the runner command from electron/package.json before execution. The broader implementation gates remain those in CONTRIBUTING; none was run for this document.

## Performance and resource guard

This is primarily a correctness fix. Do not claim inference acceleration.

Measure capability lookup only if the implementation adds measurable work: same machine, same process/environment, same set of identities, repeated warm metadata requests before and after. Record median/p90 latency and count calls to model loading/import-heavy helpers. The hard acceptance requirement is **zero weight loads, zero downloads and zero inference calls** during capability resolution. Any latency regression should be explained rather than hidden by changing the fixture.

## Risks and stop/revalidation criteria

- **Kokoro regression:** removing presets globally would reintroduce #3802. Keep the language/preset tests green.
- **Misleading repair action:** removing the preset list is insufficient if the UI redirects to unsupported design. Exercise the actual blocked notice.
- **Stale identity:** shared backend IDs, local paths, environment pins and model switches can disagree. Resolve one identity per operation and validate again at execution.
- **Behavioral scope growth:** adding an API field, changing unknown-model semantics, or redesigning queued generation needs separate review. Stop and narrow the PR if it becomes necessary.
- **New upstream work:** if another PR fixes #4344 or changes these seams, rebase and compare outcomes before proceeding.
- **Insufficient proof:** do not mark the issue fixed solely because a metadata unit test passes. At minimum verify the user-visible request flow; report remaining Apple Silicon checks.
- **Resource side effects:** stop if a capability read imports/loads a model, downloads data, or mutates stored model choice.

## Separate candidate: preset voice forwarding in long streaming requests

Source inspection also found that [the non-stream adapter path][backend-inference] forwards `preset_voice` as `voice`, while [the multi-chunk streaming helper][stream-helper] does not visibly forward that argument. This is a **suspected separate defect**, not a runtime-confirmed finding and not part of #4344.

Before proposing a separate fix, add a fake-engine test that records `voice` for every chunk in short streaming, long streaming, and non-streaming requests. Search the current queue again. If confirmed, handle it as a separate focused issue/PR or an explicitly declared dependency; do not silently bundle it into this capability change. See [the progressive-streaming plan](03-progressive-markup-streaming.md) for its related parameter-parity boundary.

## Immutable source references

[mlx-class]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/tts_backend.py#L3033
[mlx-presets]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/tts_backend.py#L3125
[mlx-cloning]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/services/tts_backend.py#L3251
[engine-payload]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/engines.py#L60
[tts-readiness]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/hooks/use-tts-readiness.ts
[clone-readiness]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/hooks/use-clone-readiness.ts
[request-identity]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/hooks/use-generate.ts#L479
[clone-notice]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/features/clone/clone-readiness-notice.tsx
[use-engines]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/electron/src/renderer/src/hooks/use-engines.ts
[model-catalog]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/config/models.yaml#L501
[preset-validation]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/generation.py#L2161
[backend-inference]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/generation.py#L1451
[stream-helper]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/api/routers/generation.py#L2464
[test-active]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_active_cloning_capability.py
[test-kokoro]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_mlx_kokoro_preset_voices.py
[test-presets]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_preset_voices_2938.py
[test-clone-gate]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_cloning_gate_model_dependent_2201.py
[test-design]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_voice_design_profile_and_capability.py
[agents]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/AGENTS.md
[claude]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/CLAUDE.md
[contributing]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/.github/CONTRIBUTING.md
