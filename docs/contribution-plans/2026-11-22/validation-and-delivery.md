# Validation and delivery

## Purpose and baseline

This guide turns the [ranked plan](README.md) into focused contributions while keeping the duplication checks current. The reviewed baseline is upstream commit [`2bb21302241793977055c44f7c52815bcbf0261e`](https://github.com/debpalash/VoiceStudio/commit/2bb21302241793977055c44f7c52815bcbf0261e). Commands below are proposed implementation commands; the planning review did not run the application or its runtime tests.

## Refresh before choosing or pushing work

For each selected task, record these results in the working notes:

| Check | Evidence to capture | What changes the decision |
|---|---|---|
| Current upstream main | Full commit SHA and date | New related changes require a fresh source review/reproduction |
| Existing issue | Body, latest comments, assignees, linked timeline events | A maintainer direction, assignment, accepted workaround, or closure |
| Open PRs | All pages, title/body, changed filenames, latest head SHA and discussion for related work | A matching fix or touching the same behavior requires comparison/coordination |
| Recent merged/closed PRs | Topic searches plus referenced landing/train PRs | Closed-unmerged can still mean absorbed; follow maintainer comments |
| Runtime reproduction | Version, platform, input fixture, exact observed failure | A failure only on an older version may need an upgrade/compatibility response |

Search by both concepts and implementation names. For example:

```text
repo:debpalash/VoiceStudio is:pr is:open mlx
repo:debpalash/VoiceStudio is:pr is:open cloning
repo:debpalash/VoiceStudio is:pr is:open MCP
repo:debpalash/VoiceStudio is:pr is:open stream
repo:debpalash/VoiceStudio is:pr 4344
repo:debpalash/VoiceStudio is:pr 4345
repo:debpalash/VoiceStudio is:pr "preset_voices"
repo:debpalash/VoiceStudio is:pr "mcp_shim"
repo:debpalash/VoiceStudio is:pr "paragraph_gap_ms"
```

Repeat targeted searches across closed/merged PRs and inspect the actual source when a title is ambiguous. Search results alone are not a complete changed-file audit. A new discussion/claim message is a separate communication action; the planning snapshot itself neither sends one nor reserves an issue.

## Branch setup

The published planning branch lives in the existing fork and starts from the inspected upstream commit. It contains only the planning documents as its own changes. Use it as a reference, then create each implementation branch from freshly fetched upstream main.

For a new local checkout:

```bash
git clone https://github.com/bultodepapas/OmniVoice-Studio-G.git
cd OmniVoice-Studio-G
git remote add upstream https://github.com/debpalash/VoiceStudio.git
git fetch upstream
git switch -c fix/mlx-cloning-capabilities upstream/main
```

For an existing checkout, first inspect `git status --short` and `git remote -v`; preserve existing work and use the already configured upstream remote. Do not recreate an existing branch or overwrite another task's changes. Refresh upstream again before each push, merge its current main into the implementation branch, and rerun the checks affected by that update.

Suggested branch names for later, separate contributions:

| Task | Suggested branch |
|---|---|
| #4344 | `fix/mlx-cloning-capabilities` |
| #4345 | `fix/mcp-stdio-session-lifecycle` |
| #4254 follow-up | `perf/generate-progressive-markup-preview` |
| #4347, only after overlap is resolved | `fix/dub-translation-readiness` |

## Development environment

Follow the pinned [contribution setup](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/.github/CONTRIBUTING.md). It requires Node 22 (22.12 or newer), Bun, uv, Python 3.11 or newer, ffmpeg, and Rust/native libraries where the changed surface requires them. Prefer the repository's locked dependencies. Check the current guide again if the implementation base has moved.

Keep correctness tests offline and independent of prepopulated model caches. Where the suite requires it, use `HF_HUB_OFFLINE=1` with a genuinely empty `HF_HUB_CACHE`. A cached local model can hide a new accidental download. Hardware/audio smoke tests form a separate evidence layer and should use explicitly prepared model state.

## Verification by task

| Task | Small first gate | Integration/hardware evidence | Completion claim supported |
|---|---|---|---|
| MLX capabilities | Backend capability matrix and frontend readiness/request regression | Supported/unsupported model switching; saved-profile linkage; Apple Silicon smoke | Correct capabilities and explicit cloning behavior |
| MCP sessions | Actual stdin-to-HTTP handshake failure and lifecycle test | Current Claude Code + current supported VoiceStudio, JSON/SSE, identity/auth forwarding | The identified session transition is repaired |
| Markup streaming | Incremental response test with a deterministic delayed final span | Native and adapter paths, cancellation, gaps/crossfades, waveform marking; controlled timing runs | Earlier first audio for eligible modes, preserved output semantics |
| Dubbing readiness | Unknown source and absent target translation fixture | Compare the live #4220/#4221 heads; target switching, manual edits, restore/resume | No accidental source fallback mislabeled as completed target translation |

Existing test files are mapped in each plan. Extend the closest behavior tests rather than adding a second parallel test system. A performance assertion should use deterministic ordering or generous noise-aware limits; measured wall-clock speedups belong in controlled benchmark evidence.

## Repository commands and gate timing

The following commands are present in the inspected contribution guide or package scripts:

```bash
bun install --frozen-lockfile
uv run pytest tests/test_active_cloning_capability.py tests/test_cloning_gate_model_dependent_2201.py tests/test_mlx_kokoro_preset_voices.py -q
uv run pytest tests/test_mcp_client_setup.py tests/test_mcp_transport_identity.py -q
uv run pytest tests/test_generate_markup.py -q
bun run --cwd electron locale:check
```

Select the relevant command for the changed behavior. The MCP/streaming examples are existing surrounding coverage; the new reproducer described in the individual plan must also be run after it exists.

Before landing a runtime change, use the full applicable project gates, including:

```bash
uv run pytest tests/ -q
uv run pytest backend/tests/ -q
bun run check:electron
```

The repository runs the backend suites separately. `check:electron` includes type checking, Electron tests, desktop/web builds, and packaging checks. Run additional platform, desktop, security, or dependency checks when the diff affects those consumers. Preserve the current CI scope policy; avoid running expensive unrelated builds during each small edit.

For this documentation-only branch, runtime tests and product builds are not validation evidence and are not needed to prove the documents were published correctly. Appropriate checks are document structure, internal links, upstream source paths, recorded inventory consistency, the changed-file list, and reading the committed files back from GitHub. This follows the current documentation-only CI policy in [AGENTS.md](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/AGENTS.md).

## Performance evidence template

Use the same machine, installed model revision, input fixture, seed, generation options, and power conditions before and after. Record engine/load state and distinguish cold-load trials from warmed inference. Store representative fixtures without personal recordings or transcripts.

| Measurement | Baseline | Candidate | Trials / notes |
|---|---|---|---|
| Time to first playable preview audio | Pending | Pending | Exclude metadata-only events |
| Total synthesis/finalization time | Pending | Pending | Include complete usable artifact |
| Peak process RAM | Pending | Pending | Same collection method |
| Peak accelerator memory, if applicable | Pending | Pending | Name the device/runtime |
| Engine call count and text-span plan | Pending | Pending | Explain any difference |
| Final sample count / intentional gaps | Pending | Pending | Deterministic fixture or tolerance |
| Correct voice/profile and audible quality | Pending | Pending | Fixed inputs plus human listening |

Report actual distributions or individual observations and sample sizes. Do not fill the table with inferred numbers. Earlier playback alone does not establish higher synthesis throughput, and a single device does not establish cross-platform performance.

## PR packaging

Each implementation PR should contain:

1. The reproduced user-visible problem, affected version, and issue link.
2. A concise explanation of the chosen correction and resulting behavior.
3. A regression that fails on the baseline and passes on the candidate.
4. Compatibility and relevant negative cases from the task's acceptance matrix.
5. Affected user/developer documentation and translated UI strings when needed.
6. A one-line `changelog.d/<PR-number>.<type>.md` entry when users will notice the change.
7. Actual verification results and any pending hardware validation, clearly separated.

Use the submitter's existing Git identity. Avoid unrelated repository-policy changes, dependency updates, version bumps, broad refactors, and new engine support inside a bug-fix PR. This follows the [current review and contribution rules](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/.github/CONTRIBUTING.md).

## Stop and reassess conditions

- A new PR already implements the same behavior: compare and contribute review or a focused follow-up instead of opening a duplicate.
- Current main already passes the proposed regression: identify the landing change and the release boundary before making a product edit.
- The reproducer depends on unavailable hardware: separate deterministic contract tests from the pending hardware claim.
- A fix requires changing public behavior beyond the agreed problem: narrow the change or record the decision needed before implementation.
- Main advances in a relevant file: rebase/merge current upstream according to project rules and revalidate the affected reasoning.
- A test exposes a neighboring independent defect: record it separately and decide explicitly whether it is necessary for this PR's correctness.

