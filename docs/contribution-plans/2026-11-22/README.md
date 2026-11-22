# VoiceStudio contribution plan — 2026-11-22

## New features and optimization research

The [feature and optimization research](05-feature-and-optimization-research.md) extends this plan with ten shortlisted directions and five secondary investigations. Its recommended first investigations are **saved audition sessions**, **spoken-script completeness review**, and **long-form CPU finalization outside the GPU worker**. A small benchmark timing correction is the recommended first measurement contribution.

The addendum was refreshed at **2026-11-22 17:18:54 UTC / 12:18:54 America/Bogota**: upstream main is unchanged, all 15 open PR heads still match the audit, and the issue count is now 29 after new low-VRAM report [#4355](https://github.com/debpalash/VoiceStudio/issues/4355). The original audit below remains a dated snapshot. The new document links detailed product, quality/automation, and performance appendices with source evidence, experiment plans and proceed/stop criteria.

## Bug-fix starting point

Start with [#4344](https://github.com/debpalash/VoiceStudio/issues/4344): make MLX model capabilities accurate and prevent a selected saved voice from being silently discarded. Establish a failing capability/request regression before changing behavior. The source provides a concrete explanation, the change can stay bounded, and the reviewed open PR queue contains no matching implementation.

The proposed sequence is **MLX cloning correctness → MCP session diagnosis and repair → progressive speech-span preview**. Run the coordination/reproduction work for the newly reported dubbing translation problem alongside this sequence; promote it ahead of streaming if an independent, unowned fix is confirmed.

This is a contributor planning snapshot. It records proposed work, source observations, evidence, and acceptance criteria. It does not claim maintainer assignment or approval, runtime reproduction, completed fixes, or measured performance gains.

## Snapshot and scope

| Field | Value |
|---|---|
| Upstream | [debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio) |
| Reviewed main commit | [`2bb21302241793977055c44f7c52815bcbf0261e`](https://github.com/debpalash/VoiceStudio/commit/2bb21302241793977055c44f7c52815bcbf0261e) |
| Commit timestamp | 2026-11-22 10:41:49 UTC / 05:41:49 America/Bogota |
| Planning date | 2026-11-22, America/Bogota |
| Refreshed inventory | 28 open issues and 15 open pull requests; see the audit for its precise retrieval time and final refresh |
| Stable release | [v0.5.8](https://github.com/debpalash/VoiceStudio/releases/tag/v0.5.8), published 2026-11-12 |
| Latest prerelease inspected | [v0.5.9-beta.7](https://github.com/debpalash/VoiceStudio/releases/tag/v0.5.9-beta.7), published 2026-11-20 |
| Checked-in application version | `0.5.9-beta.7`; main includes changes after the published tag |
| Planning branch | `docs/contribution-plan-2026-11-22` in `bultodepapas/OmniVoice-Studio-G` |

The audit covers every issue and PR open at retrieval, the changed-file lists for the open PRs, candidate discussions and timeline links, and topic-relevant closed/merged work. Five Dependabot workflow updates (#4350–#4354) appeared during the final publication check and were added to the audit. They are existing work to review, rather than new dependency-update contributions to duplicate. It is not a claim that every historical commit or private working branch was reviewed. GitHub labels, unchecked tracker items, a closed PR, and an empty assignee field are each insufficient by themselves to prove that work remains available.

## Document map

| Document | What it answers |
|---|---|
| [Backlog and duplication audit](backlog-audit.md) | What is open, what is already covered, what needs coordination, and which searches support the recommendation? |
| [Machine-readable inventory](backlog-inventory.json) | Upstream titles with an explicitly marked local-path redaction, issue/PR metadata, changed-file lists, retrieval times, and search coverage for refreshing the audit. |
| [01 — MLX cloning capabilities](01-mlx-cloning-capabilities.md) | How to stop silent profile loss while preserving valid preset generation. |
| [02 — MCP stdio sessions](02-mcp-stdio-session.md) | How to reproduce the exact exchange, test the session lifecycle, and choose a justified fix. |
| [03 — Progressive markup streaming](03-progressive-markup-streaming.md) | How to deliver earlier audio while preserving gaps, final processing, cancellation, and provenance marking. |
| [04 — Dubbing translation investigation](04-dubbing-translation-investigation.md) | How to investigate a potentially expensive incorrect-language render without duplicating the active dubbing series. |
| [05 — New features and optimization research](05-feature-and-optimization-research.md) | Which new creator, quality, automation and performance directions merit investigation, what already exists, and what evidence would justify implementation. |
| [Validation and delivery](validation-and-delivery.md) | How to refresh ownership, start implementation branches, collect evidence, and prepare focused PRs. |

## Ranked decisions

| Order | Work | Evidence confidence | Overlap / coordination | First useful deliverable | Relative effort |
|---|---|---|---|---|---|
| 1 | [#4344](https://github.com/debpalash/VoiceStudio/issues/4344): selected MLX model capabilities and cloning intent | Strong source chain plus a stable-release user report; hardware behavior still needs validation | No matching open PR found at the snapshot | A failing test showing that non-Kokoro MLX selection exposes inappropriate presets and drops cloning intent | Small–medium |
| 2 | [#4345](https://github.com/debpalash/VoiceStudio/issues/4345): stdio MCP initialization/session lifecycle | Reported failure and source-supported diagnostic leads; actual client sequence is unconfirmed | No matching open PR found; preserve earlier auth/identity work | An integration reproducer through the real stdio-to-HTTP shim | Medium, diagnosis dependent |
| 3 | Follow-up to [#4254](https://github.com/debpalash/VoiceStudio/pull/4254), under [#3924](https://github.com/debpalash/VoiceStudio/issues/3924): progressive preview with markup | Current source and merged PR explicitly retain whole-take delivery on the span path | No matching open follow-up found; some audio modes require deliberate fallback | A deterministic test that proves first playable audio precedes completion of the final eligible speech span | Medium–large |
| Conditional | [#4347](https://github.com/debpalash/VoiceStudio/issues/4347): missing translation/source-language state reaches generation | Serious reporter evidence plus source relationships; full end-to-end reproduction pending | Direct file overlap with [#4220](https://github.com/debpalash/VoiceStudio/pull/4220) and [#4221](https://github.com/debpalash/VoiceStudio/pull/4221) | Minimal reproduction and comparison against both draft PR heads | Investigate promptly; implementation scope unresolved |

The ordering weighs user impact, evidence quality, the chance of completing a focused change, and duplication risk. Relative effort is a planning judgment, not a calendar commitment. A shared file is an overlap signal; it does not prove that another PR fixes the same behavior. Conversely, the absence of a public PR does not reserve an issue.

## Why these contributions

### 1. Correct intent and capabilities before adding an engine feature

The MLX adapter exposes model-dependent cloning support but a shared Kokoro preset list. The renderer treats a non-cloning model with presets as preset-only and omits a selected profile. The initial contribution should align the capabilities, user guidance, and request with the selected model. Adding reference-conditioned MLX VoxCPM2 generation is a separate feature requiring its own audio validation.

The first plan includes a matrix for unsupported cloning, valid CSM/Qwen3 cloning, real preset engines, model changes, and profile/history preservation. It also distinguishes capability-level tests that can run on ordinary CI from Apple Silicon audio smoke evidence.

### 2. Diagnose the actual protocol exchange

The MCP report uses Docker 0.5.6, while current main has evolved. The shim awaits each handled input line, so rapid client startup is not proof of a concurrent-request race. The investigation must record message method/order and session-header presence through the actual shim, then establish which transition is invalid.

A useful plan must preserve API-key/client-identity handling and avoid replaying generation calls during recovery. If the report no longer reproduces on supported code, document the working version and keep only a meaningful regression that demonstrates the compatibility concern.

### 3. Improve first-audio latency without changing the synthesis workload

The span path currently waits for the full take. Reusing its plan to deliver finished eligible spans can improve perceived responsiveness even when total synthesis duration stays similar. Measure first playable audio separately from full rendering time and memory.

Two constraints shape the first PR: whole-take room-tone processing may require a supported fallback, and preview crossfades must not consume explicit silence. The plan must retain final whole-take processing and the synthetic-audio marking boundary. It should preserve the existing number of engine calls; #4254 already documents the cost of increasing sentence-level calls.

### 4. Treat the new dubbing report as a coordinated investigation

The follow-up on #4347 reports a long render whose segments remained in the source language while stored under a target-language track. That report deserves prompt reproduction. Its source files are already modified by the active dubbing PR series, so the correct first contribution is to determine whether those heads already address it and isolate any remaining behavior.

A proposed validity check should represent translation readiness or explicit source-language intent. Equality between translated and source text is not a reliable universal test: names, numbers, same-language narration, and manual translations can legitimately match.

## First implementation session: #4344

1. Refresh upstream main and reread #4344 comments, timeline, and the open PR file inventory.
2. Run the related capability, preset, and readiness tests to establish the baseline.
3. Add a deterministic failing test for the model-specific preset payload and the selected-profile request behavior. Demonstrate the failure before changing the implementation.
4. Make the smallest correct model-capability and UI/request change. Preserve legitimate Kokoro and other preset-engine behavior.
5. Validate model switching and the preserved saved-profile selection. Collect Apple Silicon reproduction evidence before claiming an audio fix.
6. Update affected documentation, real translations in active catalogs, and the issue-linked changelog fragment in the implementation PR.
7. Refresh the duplication search and upstream base again before pushing.

Use the detailed plan's acceptance matrix as the completion definition. A passing source guard alone does not establish that a user can complete the workflow.

## Contribution boundaries

Each implementation should use a fresh branch from current upstream main. This documentation branch is a reference; implementation branches should not inherit unrelated planning documents or each other's product changes. Each future PR should describe one reproduced problem and its resulting behavior.

The current repository guidance favors user-facing fixes, compatibility, a regression that fails before the change, documentation updates, genuine localized strings, and a user-facing changelog fragment when behavior changes. Main must remain current and pass the required review/check gates. Sources: [AGENTS.md](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/AGENTS.md), [CLAUDE.md](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/CLAUDE.md), and [CONTRIBUTING.md](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/.github/CONTRIBUTING.md).

## Completion record for this planning work

- Current-source observations and reporter statements are distinguished in the individual plans.
- Open work and relevant merged/absorbed work are cross-referenced in the audit.
- Acceptance tests, commands, benchmarks, and proposed fixes are plans unless a document explicitly records an executed result.
- This branch adds documentation only. Product fixes and benchmark results remain to be established on implementation branches.

