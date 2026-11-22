# VoiceStudio contribution backlog and duplication audit

**Review snapshot:** 22 November 2026, **16:38:01 UTC / 11:38:01 America/Bogota**. Collection began at 16:24:40 UTC; the final inventory and PR heads were rechecked at the snapshot time.

**Upstream:** [debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio), branch `main`, commit [`2bb21302241793977055c44f7c52815bcbf0261e`](https://github.com/debpalash/VoiceStudio/commit/2bb21302241793977055c44f7c52815bcbf0261e).

**Complete open inventory: 28 issues and 15 pull requests.** This audit enumerates every open issue and PR, records every open PR's complete changed-file list, and checks relevant comments, candidate timelines and recent closed-topic overlaps. The structured counterpart is [backlog-inventory.json](backlog-inventory.json).

The findings are a dated planning basis. “No matching open PR found” does **not** mean work is unclaimed, reserved, or absent from unpublished branches. Issue reports and PR authors' test claims are source evidence; this backlog audit did not independently run the reported product scenarios. The detailed implementation documents distinguish source inspection from reproduction.

## Recommended contribution sequence

| Plan | Why it remains useful | Duplication boundary |
| --- | --- | --- |
| [1. MLX cloning capabilities](01-mlx-cloning-capabilities.md) — [#4344](https://github.com/debpalash/VoiceStudio/issues/4344) | A selected saved voice can be silently dropped when the active model cannot clone. The issue is open, unassigned, without comments or timeline events at this snapshot. | No matching capability fix appears in the complete open PR queue. [#4216](https://github.com/debpalash/VoiceStudio/pull/4216) owns an adjacent picker activation change and touches a clone picker test; preserve it. Existing Kokoro support is already shipped. |
| [2. MCP stdio session](02-mcp-stdio-session.md) — [#4345](https://github.com/debpalash/VoiceStudio/issues/4345) | The reported shim fails initialization/session use while direct HTTP works. The report is specific enough to build a protocol reproducer. | No matching session-lifecycle fix appears in the open queue or candidate timeline. The report uses 0.5.6; current-main reproduction is a gate. Preserve merged caller-tier/error-handling work. |
| [3. Progressive markup streaming](03-progressive-markup-streaming.md) — follow-up to [#4254](https://github.com/debpalash/VoiceStudio/pull/4254), within [#3924](https://github.com/debpalash/VoiceStudio/issues/3924) | The merged PR explicitly leaves span-by-span streaming unfinished. Current-source review confirms that the markup/pause path still renders the whole result before delivery. | This is a narrowly scoped follow-up proposal, not an existing standalone issue or claim. Do not recreate native Qwen streaming, add sentence segmentation, or take over dubbing's active planning series. |
| [Conditional: dubbing translation investigation](04-dubbing-translation-investigation.md) — [#4347](https://github.com/debpalash/VoiceStudio/issues/4347) | A new reporter follow-up describes untranslated source speech being persisted as a target-language track after a long render. It merits prompt reproduction and may become higher priority than plan 3. | [#4220](https://github.com/debpalash/VoiceStudio/pull/4220) changes `dub_generate.py`; [#4221](https://github.com/debpalash/VoiceStudio/pull/4221) changes `dub-session.ts` and `dub-translation-panel.tsx`. Coordinate before implementation; do not create a duplicate replacement of that work. |

The detailed plans and [validation/delivery guide](validation-and-delivery.md) govern implementation. The recommendations below are analysis; they do not change issue labels, assignees, priorities or state.

## Review coverage and completeness

| Read surface | Coverage at the snapshot | Limit |
| --- | --- | --- |
| [Open issue collection](https://api.github.com/repos/debpalash/VoiceStudio/issues?state=open&per_page=100&page=1&sort=updated&direction=desc) | 43 entries: 28 issues + 15 PRs. Page 1 returned fewer than the 100 requested entries, so there was no next page. | GitHub's issues endpoint includes PRs; counts are separated here. |
| [Open PR collection](https://api.github.com/repos/debpalash/VoiceStudio/pulls?state=open&per_page=100&page=1&sort=updated&direction=desc) | All 15 open PRs, independently confirmed. Complete changed-file lists (175 entries across PRs) and combined issue/review/inline comments were read for each. | Review observations are not an approval or a claim that current CI is green. |
| Open issue discussion | All 17 non-administrative open issues with comments were read. Other issue bodies were reviewed. | The CLA signing issue's body was read; individual signature comments were excluded from this planning artifact. |
| Candidate timelines | #4344: 0 events; #4345: 0; #4254: 29; #3924: 51. Also #4346: 0 and #4347: 1. Each page was shorter than 100. | No cross-reference event is not proof that an unpublished implementation does not exist. |
| Recent closed-topic search | `is:pr is:closed updated:>=2026-11-01` scoped to this repository, separately with `MCP` (26), `MLX` (25), `streaming` (46), and `performance` (58). Every query returned its reported total, with `incomplete_results=false`. | These are complete results for the stated queries, not an audit of every historical closed PR or every diff. Exact queries, source URLs and returned numbers are in the JSON inventory. |
| Final consistency read | Publication refresh found five new Dependabot PRs (#4350–#4354). After their bodies, full patches, file lists and discussion/review surfaces were read, the final recheck confirmed the same 43 open item numbers, 15 PR numbers/head SHAs and upstream `main` SHA as the 16:37:12 UTC refresh. | Revalidate again immediately before claiming work, beginning implementation and pushing. |

The five PRs added during publication verification change only pinned GitHub Actions and their version comments in `.github/workflows/`. Their 21 file entries are included below. They do not change application runtime, renderer, MCP or markup code, so the preferred contribution order remains unchanged. This is a duplication finding, not a CI compatibility approval.

Rules reviewed at the pinned commit: [AGENTS.md](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/AGENTS.md), [CLAUDE.md](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/CLAUDE.md), [CONTRIBUTING.md](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/.github/CONTRIBUTING.md), [AGENT_PR_GUIDE.md](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/.github/AGENT_PR_GUIDE.md), [issue tracker](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/docs/agents/issue-tracker.md), [triage labels](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/docs/agents/triage-labels.md).

Material planning rules are: Electron is the maintained desktop/web UI; one focused change per PR; at most five open PRs per contributor; start from fresh upstream `main`; preserve existing user data/model state and local-first behavior; translate UI keys in every current locale catalog; add a failing-before/passing-after regression for a runtime fix; preserve platform behavior while allowing hardware-specific acceleration; update affected docs and use a numbered changelog fragment for user-visible changes. Documentation-only work follows the explicit documentation-only CI skip policy, with identity/CLA/secret checks retained. The human contributor is responsible for the CLA; this audit performs no signature action.

## Every open issue

All 28 rows below were open at the snapshot. “Unassigned” is the API's assignee state, not an ownership guarantee. Labels are reproduced as metadata; the recommended action follows the latest substantive evidence, which can be newer than a label.

| Issue / English summary | State / assignee | Category / current labels | Recommended action and evidence |
| --- | --- | --- | --- |
| [#4347](https://github.com/debpalash/VoiceStudio/issues/4347) Unknown source language leaves Retry inert and can label untranslated speech as the target language | open; unassigned | Dubbing / translation provenance; no labels yet | High-impact investigation, conditional on coordination with #4220/#4221. Reproduce missing translation state before designing a provenance guard; equality of source/target strings alone is insufficient. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/4347#issuecomment-7081838333) [Evidence 2](https://github.com/debpalash/VoiceStudio/pull/4220) [Evidence 3](https://github.com/debpalash/VoiceStudio/pull/4221) |
| [#4346](https://github.com/debpalash/VoiceStudio/issues/4346) Completed dubbing cannot export with preserved background when separation is unavailable | open; unassigned | Dubbing / export and separation; no labels yet | Coordinate with #4218/#4220/#4221. Reproduce failed-separation cache reuse and preserve a speech-only export path; do not silently substitute source audio or assert the GPU kill cause without evidence. [Evidence 1](https://github.com/debpalash/VoiceStudio/pull/4218) [Evidence 2](https://github.com/debpalash/VoiceStudio/pull/4220) [Evidence 3](https://github.com/debpalash/VoiceStudio/pull/4221) |
| [#4345](https://github.com/debpalash/VoiceStudio/issues/4345) MCP stdio shim loses its HTTP session with Claude Code | open; unassigned | MCP transport; no labels yet | Preferred contribution 2: reproduce on pinned main and compare the reported older 0.5.6 image. Diagnose protocol ordering/header handling before changing it; retain HTTP authorization semantics. [Evidence 1](https://github.com/debpalash/VoiceStudio/pull/4128) [Evidence 2](https://github.com/debpalash/VoiceStudio/pull/4315) |
| [#4344](https://github.com/debpalash/VoiceStudio/issues/4344) Voice Cloning silently ignores the selected profile with MLX VoxCPM2 8-bit | open; unassigned | Engine capabilities / cloning UI; no labels yet | Preferred contribution 1: reject unsupported clone intent explicitly and resolve model-specific capability/preset data. Preserve valid Kokoro preset generation. Coordinate only if touching #4216's shared picker/test scope. [Evidence 1](https://github.com/debpalash/VoiceStudio/pull/4216) [Evidence 2](https://github.com/debpalash/VoiceStudio/pull/3833#issuecomment-6734787583) |
| [#4343](https://github.com/debpalash/VoiceStudio/issues/4343) Request additional models for low-end CPU/AMD hardware | open; unassigned | Engine proposal / support — `enhancement` | Clarify the named workload and existing Kokoro route first. Apply engine-acceptance criteria to any new Phonon integration; a broad model-catalog expansion is not a bounded next fix. [Evidence 1](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/docs/engine-acceptance.md) [Evidence 2](https://github.com/debpalash/VoiceStudio/pull/3833#issuecomment-6734787583) |
| [#4342](https://github.com/debpalash/VoiceStudio/issues/4342) CosyVoice 3 GGUF native runtime is unavailable after installation | open; unassigned | Windows / optional-engine setup — `needs-triage`, `install` | Collect a precise runtime probe and setup failure, reproduce on current beta/main, and distinguish weights downloaded from native runtime installed. No matching repair established from this sparse report. |
| [#4341](https://github.com/debpalash/VoiceStudio/issues/4341) audio.cpp dots.tts installation reports a missing or unreadable required file | open; unassigned | Windows / optional-engine setup — `needs-triage`, `install` | Obtain the failing install step and sanitized log, then reproduce. Avoid assuming that all native-engine failures share one cause with #4342. |
| [#4314](https://github.com/debpalash/VoiceStudio/issues/4314) Torch setup download remains at 0% | open; unassigned | Windows / runtime download — `needs-triage`, `install` | Review the newly supplied setup log before designing a fix; recheck proxy/retry changes and open #4348. Independently installed Torch is outside the managed runtime. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/4314#issuecomment-7070466762) [Evidence 2](https://github.com/debpalash/VoiceStudio/issues/4314#issuecomment-7076739436) [Evidence 3](https://github.com/debpalash/VoiceStudio/pull/4348) |
| [#4319](https://github.com/debpalash/VoiceStudio/issues/4319) Vietnamese numbers lose magnitude words in generated speech | open; unassigned | Speech quality / normalization — `bug`, `needs-triage` | Validate remaining tens, percentages and years after merged #4332. Preserve the reporter's finding that decimal word expansion can be worse; requires real audio and language review. [Evidence 1](https://github.com/debpalash/VoiceStudio/pull/4332) [Evidence 2](https://github.com/debpalash/VoiceStudio/issues/4319#issuecomment-7073280948) |
| [#2586](https://github.com/debpalash/VoiceStudio/issues/2586) Contributor License Agreement signing issue | open; unassigned | Contribution administration — `cla` | Not an implementation task. The human contributor verifies their own signature status before an upstream PR; this audit neither signs nor republishes signature records. [Evidence 1](https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/.github/CONTRIBUTING.md#contribution-licensing) |
| [#4262](https://github.com/debpalash/VoiceStudio/issues/4262) Overwrite update fails to start and does not recognize existing dependencies/models | open; unassigned | Setup / update recovery — `bug`, `needs-info` | Await concrete old/new versions and diagnosis. Maintainer points to #4265 for one proxy cause; #4348/#4349 concern related setup/cache paths but do not prove this report fixed. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/4262#issuecomment-7023119886) [Evidence 2](https://github.com/debpalash/VoiceStudio/pull/4348) [Evidence 3](https://github.com/debpalash/VoiceStudio/pull/4349) |
| [#4250](https://github.com/debpalash/VoiceStudio/issues/4250) Backend exits with code 3 during a long OmniVoice generation | open; unassigned | Long generation / backend lifecycle — `bug` | Obtain a current reproducible sequence and input length/language. Maintainer split gallery/licensing symptoms away; do not combine them into a crash rewrite or infer OOM. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/4250#issuecomment-7022986464) |
| [#4118](https://github.com/debpalash/VoiceStudio/issues/4118) Source checkout Python environment cannot import omnivoice | open; @debpalash | Source installation — `needs-info`, `install`, `install:source` | Support follow-up already owned by debpalash: confirm setup:api outcome and a fresh failure. Do not treat the older embedded native crash as the current missing-package cause. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/4118#issuecomment-6875510075) [Evidence 2](https://github.com/debpalash/VoiceStudio/issues/4118#issuecomment-6957030829) |
| [#4136](https://github.com/debpalash/VoiceStudio/issues/4136) Stories player reports missing audio after generation | open; @debpalash | Long-form playback — `bug`, `needs-info` | Coordinate with assigned maintainer; check merged #4138 and #4196 before changing playback. Underlying reporter failure still needs engine/backend and reproduction evidence. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/4136#issuecomment-6880226831) [Evidence 2](https://github.com/debpalash/VoiceStudio/pull/4196) |
| [#3635](https://github.com/debpalash/VoiceStudio/issues/3635) Windows Smart App Control blocks the unsigned Python runtime | open; unassigned | Runtime trust / distribution — `bug`, `ready-for-human`, `install`, `priority:P0`, `awaiting-owner-decision`, `install:windows` | Existing-Python selection already shipped in #3701/0.5.8. Remaining runtime/DLL trust requires a maintainer distribution decision and real SAC validation, not another interpreter selector. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/3635#issuecomment-6910485742) [Evidence 2](https://github.com/debpalash/VoiceStudio/issues/1779) |
| [#4199](https://github.com/debpalash/VoiceStudio/issues/4199) CosyVoice3 reference-conditioned generation adds or omits speech | open; @debpalash | Model output correctness — `bug`, `from-discord`, `needs-info`, `priority:P2` | Assigned investigation: reproduce the reported seed-dependent output with consented evidence and distinguish integration from upstream-model behavior. Do not claim sample-rate or profile-inheritance cause. |
| [#4090](https://github.com/debpalash/VoiceStudio/issues/4090) Mac Stories is slow and lacks a clear completion/player state after longer renders | open; unassigned | Long-form UX / performance — `bug`, `from-discord`, `needs-info` | Reporter confirms saved output exists. Reproduce the completion-state transition; consider existing recovery and stream-completion work without declaring a crash proven. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/4090#issuecomment-6896779747) [Evidence 2](https://github.com/debpalash/VoiceStudio/pull/4097) [Evidence 3](https://github.com/debpalash/VoiceStudio/pull/4286) |
| [#3924](https://github.com/debpalash/VoiceStudio/issues/3924) Performance tracker across startup, inference, memory, UI, installation and mobile | open; unassigned | Performance tracking — `enhancement`, `tracking` | Choose one measured remaining subproblem. Reconcile the unchecked checklist with merged PRs before implementing; progressive markup streaming is the planned scoped follow-up. [Evidence 1](https://github.com/debpalash/VoiceStudio/pull/4254) [Evidence 2](https://github.com/debpalash/VoiceStudio/pull/4320) [Evidence 3](https://github.com/debpalash/VoiceStudio/pull/4321) [Evidence 4](https://github.com/debpalash/VoiceStudio/pull/4322) [Evidence 5](https://github.com/debpalash/VoiceStudio/pull/4323) |
| [#4159](https://github.com/debpalash/VoiceStudio/issues/4159) Linux RX 6700 XT HIPBLAS initialization failure | open; @debpalash | Linux AMD / hardware diagnosis — `bug`, `from-discord`, `needs-info`, `install`, `install:linux` | Assigned issue: obtain actual failing runtime/GPU evidence. #4166/#4167 fix diagnosis/install behavior, not the underlying HIPBLAS failure; Windows proof is not Linux proof. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/4159#issuecomment-6889733960) |
| [#4094](https://github.com/debpalash/VoiceStudio/issues/4094) Discord review tracker for confirmed fixes and outstanding reports | open; unassigned | Support intake tracking — `from-discord`, `needs-triage`, `tracking` | Work on its linked concrete issues, preserving what is confirmed versus still needs information. Do not open duplicate tickets from the aggregate or call all symptoms solved by a nearby fix. |
| [#4142](https://github.com/debpalash/VoiceStudio/issues/4142) Windows native access violation while loading OmniVoice weights | open; unassigned | Native model-loading crash — `bug`, `needs-info`, `install`, `priority:P0`, `install:windows`, `install:native-crash` | High-severity investigation needs the current faulting-thread/runtime evidence. #4162 improved report capture only; no verified shared root cause or repair established. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/4142#issuecomment-6888908846) |
| [#1779](https://github.com/debpalash/VoiceStudio/issues/1779) Sign distributed binaries | open; unassigned | Distribution / signing — `enhancement`, `ready-for-human`, `priority:P0`, `awaiting-owner-decision` | macOS release evidence now reports notarization; Windows remains unsigned. Coordinate owner-controlled signing and runtime trust; signing only the installer does not establish SAC engine compatibility. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/1779#issuecomment-6883835020) [Evidence 2](https://github.com/debpalash/VoiceStudio/issues/3635) |
| [#4150](https://github.com/debpalash/VoiceStudio/issues/4150) VoxCPM2 installation failure from the older Discord report | open; unassigned | Optional-engine setup / needs evidence — `bug`, `from-discord`, `needs-info`, `install`, `install:engines` | Request exact current version, host and failure stage through the existing issue before code changes. Later installer fixes, including #4330, cannot resolve an unspecified original report by inference. [Evidence 1](https://github.com/debpalash/VoiceStudio/pull/4330) |
| [#3836](https://github.com/debpalash/VoiceStudio/issues/3836) Installation issue aggregation thread | open; unassigned | Installation tracking — `install`, `tracking` | Use the current-version diagnostic and unique signature to route to a specific issue. Several crash-reporting/fallback improvements already shipped in stable 0.5.8. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/3836#issuecomment-6820413768) |
| [#4092](https://github.com/debpalash/VoiceStudio/issues/4092) macOS update restart loses updates:getState handler and backend reachability | open; unassigned | Updater lifecycle — `bug`, `from-discord`, `needs-info`, `install`, `install:update` | #4098 already fixes a reproduced handler-teardown defect and is in beta.2. Original source/target versions and logs are still needed to confirm the reporter's incident. [Evidence 1](https://github.com/debpalash/VoiceStudio/pull/4098) |
| [#3129](https://github.com/debpalash/VoiceStudio/issues/3129) Drama-3 GGUF and MOSS-Audio engine request | open; unassigned | Engine integration / hardware validation — `enhancement`, `ready-for-human` | MOSS-Audio was explicitly declined. Drama-3 runtime requirement is already met; remaining family wiring, exact weight pin and real >=24 GB GPU smoke need coordination. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/3129#issuecomment-6438815706) [Evidence 2](https://github.com/debpalash/VoiceStudio/issues/3129#issuecomment-6794067917) |
| [#3420](https://github.com/debpalash/VoiceStudio/issues/3420) Opt-in real-time voice conversion and virtual microphone | open; unassigned | Large feature / latency experiment — `enhancement`, `from-discord`, `needs-triage`, `priority:P2`, `awaiting-owner-decision` | Read newer decisions rather than the stale owner-decision label. Opt-in build was approved; MeanVC2 failed the measured M2 bar. Next stated step is a five-minute Seed-VC test on RTX 3060-class hardware. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/3420#issuecomment-6757912907) [Evidence 2](https://github.com/debpalash/VoiceStudio/issues/3420#issuecomment-6790571974) |
| [#2468](https://github.com/debpalash/VoiceStudio/issues/2468) Native Windows AMD ROCm setup and remaining engine-parity gaps | open; unassigned | Hardware validation / tracking — `enhancement`, `ready-for-human`, `install`, `priority:P2`, `needs-hardware`, `tracking`, `install:amd` | Base ROCm support is already present. Coordinate remaining engine/hardware evidence and avoid duplicating open #4338's CTranslate2 isolation change. [Evidence 1](https://github.com/debpalash/VoiceStudio/issues/2468#issuecomment-6454642383) [Evidence 2](https://github.com/debpalash/VoiceStudio/pull/4338) |

### New dubbing reports require coordination

[#4347's follow-up](https://github.com/debpalash/VoiceStudio/issues/4347#issuecomment-7081838333) reports 653 segments with no Portuguese translation, source text copied into the Portuguese language map, and roughly 10.4 hours of rendering. Those figures belong to the report and have not been reproduced here. The earlier issue body described the segments as translated; the follow-up corrects that interpretation. Use the follow-up when scoping the investigation.

A guard based only on `text == text_original` would reject valid names, numbers, same-language narration and intentional manual text. The investigation must establish explicit translation/provenance state and legitimate bypasses. It must also compare the pending #4220/#4221 changes before proposing new state or controls.

[#4346](https://github.com/debpalash/VoiceStudio/issues/4346) concerns missing background-separation artifacts after a completed dub; the reporter confirms a speech-only export works. The existing drafts already change separation choice/cache identity (#4218), export/backend state (#4220), and guided export UI (#4221). Treat this as a coordinated defect investigation, not a new end-to-end dubbing redesign.

### Two labels need contextual reading

- **[#3420](https://github.com/debpalash/VoiceStudio/issues/3420):** `awaiting-owner-decision` remains attached, but the maintainer [approved an opt-in implementation](https://github.com/debpalash/VoiceStudio/issues/3420#issuecomment-6757912907), then [recorded the failed MeanVC2 experiment and next Seed-VC GPU experiment](https://github.com/debpalash/VoiceStudio/issues/3420#issuecomment-6790571974). The next useful contribution is the specified hardware experiment, not another general design proposal.
- **[#3129](https://github.com/debpalash/VoiceStudio/issues/3129):** the issue title contains two engine requests. The maintainer [declined MOSS-Audio](https://github.com/debpalash/VoiceStudio/issues/3129#issuecomment-6438815706) and later [confirmed that Drama-3's runtime prerequisite is met](https://github.com/debpalash/VoiceStudio/issues/3129#issuecomment-6794067917). Remaining Drama-3 wiring/pinning and a real >=24 GB GPU test are the relevant scope.

## Every open pull request

All open PRs have no assignee in the API snapshot; the named authors and their active branches are the ownership evidence. A draft or CLA hold is not an invitation to duplicate its implementation.

| PR | State / author | Scope already being worked on | Relevant overlap | Files / reviewed head |
| --- | --- | --- | --- | --- |
| [#4354](https://github.com/debpalash/VoiceStudio/pull/4354) chore(ci): bump actions/upload-pages-artifact from 3.0.1 to 5.0.0 | Open, ready for review; @dependabot[bot] | Update actions/upload-pages-artifact 3.0.1 to 5.0.0 in the Android repository publishing workflow. | CI artifact-upload action pin only; no runtime overlap with the preferred three plans. The existing published-site path is unchanged. | [1 files](https://github.com/debpalash/VoiceStudio/pull/4354/files); `3f8d8d08d` |
| [#4353](https://github.com/debpalash/VoiceStudio/pull/4353) chore(ci): bump gradle/actions/setup-gradle from 4.4.1 to 6.4.1 | Open, ready for review; @dependabot[bot] | Update gradle/actions/setup-gradle 4.4.1 to 6.4.1 in three Android/mobile workflows. | CI action pins only; no runtime overlap with cloning capabilities, MCP sessions or Generate markup streaming. | [3 files](https://github.com/debpalash/VoiceStudio/pull/4353/files); `bc721d905` |
| [#4352](https://github.com/debpalash/VoiceStudio/pull/4352) chore(ci): bump astral-sh/setup-uv from 6.8.0 to 10.4.0 | Open, ready for review; @dependabot[bot] | Update astral-sh/setup-uv 6.8.0 to 10.4.0 across eleven build, CI, install and release workflows. | CI setup-action pins only; no runtime implementation overlap. Existing explicit uv version and cache settings are unchanged in the patch. | [11 files](https://github.com/debpalash/VoiceStudio/pull/4352/files); `40712a73f` |
| [#4351](https://github.com/debpalash/VoiceStudio/pull/4351) chore(ci): bump actions/github-script from 7.1.0 to 9.0.0 | Open, ready for review; @dependabot[bot] | Update actions/github-script 7.1.0 to 9.0.0 in the docs-drift issue workflow. | CI action pin only; no runtime, MCP or markup implementation overlap. Existing docs-drift step conditions and script remain unchanged. | [1 files](https://github.com/debpalash/VoiceStudio/pull/4351/files); `8c2977f4d` |
| [#4350](https://github.com/debpalash/VoiceStudio/pull/4350) chore(ci): bump the github-actions group with 2 updates | Open, ready for review; @dependabot[bot] | Update setup-java 6.2.0 to 6.3.0 and SignPath signing action 3.0 to 3.1 in five workflows. | CI action pins only; no runtime overlap with the preferred three plans. Does not itself enable Windows signing or resolve #1779/#3635. | [5 files](https://github.com/debpalash/VoiceStudio/pull/4350/files); `68b7d8739` |
| [#4349](https://github.com/debpalash/VoiceStudio/pull/4349) fix(models): restore a healed cache through the selected endpoint | Open, ready for review; @DeryFerd | Repair Hugging Face cache using the selected endpoint while keeping gated repositories on the canonical endpoint unless explicitly overridden. | Setup/cache repair alternative work; no direct preferred-plan file overlap. | [3 files](https://github.com/debpalash/VoiceStudio/pull/4349/files); `69a0c6c65` |
| [#4348](https://github.com/debpalash/VoiceStudio/pull/4348) fix(electron): honour bare-IPv6 NO_PROXY entries in the setup proxy parser | Open, ready for review; @DeryFerd | Correct bare IPv6 NO_PROXY parsing in runtime downloads. | Direct overlap with any setup proxy parser fix; related to #4314/#4262 only if their reproduced cause matches. | [3 files](https://github.com/debpalash/VoiceStudio/pull/4348/files); `57774fcb1` |
| [#4338](https://github.com/debpalash/VoiceStudio/pull/4338) fix(windows-rocm): isolate CTranslate2 from Torch on ROCm 7.2.1 too | Open draft; @dytech0021 | Apply Windows ROCm CTranslate2/Torch isolation to ROCm 7.2.1 as well as ROCm 10. | Direct overlap with #2468-related ASR isolation work; not the #4345 MCP-session defect. | [8 files](https://github.com/debpalash/VoiceStudio/pull/4338/files); `3115c4810` |
| [#4337](https://github.com/debpalash/VoiceStudio/pull/4337) fix(transcription): decode M4A before speaker diarization | Open draft; @Error404-page | Decode M4A to in-memory audio before Pyannote diarization. | Owns the M4A diarization fix surface. No direct preferred-plan file overlap. | [3 files](https://github.com/debpalash/VoiceStudio/pull/4337/files); `b6cd2822d` |
| [#4221](https://github.com/debpalash/VoiceStudio/pull/4221) feat(dub): guide subtitle-led dubbing from preparation to listening and export | Open draft; @davidsiguenza | Guided subtitle-led dubbing from input preparation to playback/export; depends on #4218/#4219/#4220. | High overlap with #4347 (dub-session.ts, dub-translation-panel.tsx) and #4346 export UX. Shares locale files with cloning UI messages if added. | [68 files](https://github.com/debpalash/VoiceStudio/pull/4221/files); `c80774a3b` |
| [#4220](https://github.com/debpalash/VoiceStudio/pull/4220) feat(dub): plan reusable speech and fit narration to fixed subtitle windows | Open draft; @davidsiguenza | Reusable-speech planning, fixed subtitle windows and fitting; backend counterpart for #4221. | Direct file overlap with #4347 in dub_generate.py and #4346 in dub_export.py; generated API/CLI contracts also shared. | [24 files](https://github.com/debpalash/VoiceStudio/pull/4220/files); `751e562d6` |
| [#4219](https://github.com/debpalash/VoiceStudio/pull/4219) feat(dub): validate subtitles before preparation and create SRT-only jobs | Open draft; @davidsiguenza | Validate SRT uploads and create SRT-only jobs without ASR. | Subtitle input/provenance work can intersect #4347 edge cases; shares dub_core.py with #4218 and generated OpenAPI/route inventory. | [6 files](https://github.com/debpalash/VoiceStudio/pull/4219/files); `28e93390c` |
| [#4218](https://github.com/debpalash/VoiceStudio/pull/4218) feat(dub): allow media preparation without background separation | Open draft; @davidsiguenza | Allow preparation without background separation; distinguish skipped versus failed and adjust cache identity. | Direct conceptual overlap with #4346's missing-separation/cache state; owns dub_pipeline.py and dub_core.py changes. | [8 files](https://github.com/debpalash/VoiceStudio/pull/4218/files); `826fc55de` |
| [#4217](https://github.com/debpalash/VoiceStudio/pull/4217) feat(dub): delete saved projects from the sidebar | Open draft; @davidsiguenza | Delete saved dubbing projects from the sidebar with confirmation. | Shares localized catalogs with #4221 and any new cloning messages; otherwise independent of the preferred repairs. | [26 files](https://github.com/debpalash/VoiceStudio/pull/4217/files); `ed980714e` |
| [#4216](https://github.com/debpalash/VoiceStudio/pull/4216) fix(ui): commit searchable voice selections on click | Open draft; @davidsiguenza | Commit searchable voice selection on click while retaining focus and mounted options on press. | Adjacent to #4344: touches clone/preset-voice-picker.test.tsx, SearchableSelect.jsx and shared VoiceSelector tests. Does not address model capability leakage. | [5 files](https://github.com/debpalash/VoiceStudio/pull/4216/files); `e64f70af2` |

### Relevant review and dependency notes

- **[#4354](https://github.com/debpalash/VoiceStudio/pull/4354):** Full patch changes only the upload-pages-artifact action/version comment. No discussion or review records returned. No successful publishing run or approval is inferred. [Reviewed full patch](https://github.com/debpalash/VoiceStudio/pull/4354/files)
- **[#4353](https://github.com/debpalash/VoiceStudio/pull/4353):** Full patch changes only setup-gradle action pins/version comments. No discussion or review records returned. Review major-version compatibility separately from the proposed product fixes. [Reviewed full patch](https://github.com/debpalash/VoiceStudio/pull/4353/files)
- **[#4352](https://github.com/debpalash/VoiceStudio/pull/4352):** Full patch changes only setup-uv action pins/version comments. No discussion or review records returned. The release notes describe new options, but this PR does not add or change workflow inputs. [Reviewed full patch](https://github.com/debpalash/VoiceStudio/pull/4352/files)
- **[#4351](https://github.com/debpalash/VoiceStudio/pull/4351):** Full patch changes only the pinned github-script action/version comment. No discussion or review records returned. A major action upgrade requires its own workflow compatibility checks. [Reviewed full patch](https://github.com/debpalash/VoiceStudio/pull/4351/files)
- **[#4350](https://github.com/debpalash/VoiceStudio/pull/4350):** Full patch changes only pinned action SHAs/version comments. No discussion or review records returned. Validate action compatibility separately; setup-java release notes make its Java problem matcher opt-in. [Reviewed full patch](https://github.com/debpalash/VoiceStudio/pull/4350/files)
- **[#4349](https://github.com/debpalash/VoiceStudio/pull/4349):** Active review. Endpoint/gating and test-sensitivity findings received author fixes; do not infer merge approval or fresh CI success from comments. [Reviewed comment](https://github.com/debpalash/VoiceStudio/pull/4349#issuecomment-7081843997)
- **[#4348](https://github.com/debpalash/VoiceStudio/pull/4348):** Ready for review. CodeRabbit summary reports no actionable comments in its latest reviewed pass; maintainer approval is not inferred. [Reviewed comment](https://github.com/debpalash/VoiceStudio/pull/4348#issuecomment-7080851799)
- **[#4338](https://github.com/debpalash/VoiceStudio/pull/4338):** Draft; CLA gate comments wait for contributor signature. An existing draft still constitutes active work. [Reviewed comment](https://github.com/debpalash/VoiceStudio/pull/4338#issuecomment-7077099692)
- **[#4337](https://github.com/debpalash/VoiceStudio/pull/4337):** Draft. CLA/commit attribution and description completeness remain in comments; private/local identity details are intentionally omitted here. [Reviewed comment](https://github.com/debpalash/VoiceStudio/pull/4337#issuecomment-7076761262)
- **[#4221](https://github.com/debpalash/VoiceStudio/pull/4221):** Contributor says keep draft blocked until dependencies land. Comment thread contains CLA acknowledgment; branch-local checks are not fresh upstream CI approval.
- **[#4220](https://github.com/debpalash/VoiceStudio/pull/4220):** Draft; contributor lists validation limits and pending upstream/hardware gates. Coordinate on the existing branch.
- **[#4219](https://github.com/debpalash/VoiceStudio/pull/4219):** Draft; dependency of #4221. Do not independently implement SRT-only input.
- **[#4218](https://github.com/debpalash/VoiceStudio/pull/4218):** Draft; dependency of #4221. Failure versus intentional-skip semantics must be preserved in a follow-up.
- **[#4217](https://github.com/debpalash/VoiceStudio/pull/4217):** Draft; explicitly independent of the other prepared changes.
- **[#4216](https://github.com/debpalash/VoiceStudio/pull/4216):** Draft; explicitly independent. Reuse the shared control without taking over its click-activation change.

The exact base/head SHAs, every filename, source URLs and comment URLs are preserved in [backlog-inventory.json](backlog-inventory.json). The filename appendix below provides a readable full inventory. Inventory titles preserve the upstream wording except for #4118's reporter-local path, which is explicitly marked as redacted in the JSON. English paraphrases use the separate summary field. No private logs, local account details, raw comment bodies or CLA signature records are included.

### Direct overlap crosswalk

| Proposed or alternative work | Existing open surface | Implementation consequence |
| --- | --- | --- |
| #4344 cloning capability fix | #4216: `electron/src/renderer/src/features/clone/preset-voice-picker.test.tsx`, shared selector implementation/tests | A capability/request fix is distinct from click activation. Avoid reworking the shared selection interaction; merge/rebase carefully if the regression test file changes. |
| New cloning UI explanation | #4217 and #4221 change all locale catalogs | Localize in every current catalog and resolve key additions carefully. Shared locale files alone do not make two features duplicates. |
| #4345 session lifecycle | No open PR lists `backend/mcp_shim/__main__.py` | Proceed only after fresh reproduction and a new queue/timeline check; preserve merged auth and error-detail behavior. |
| Progressive Generate markup streaming | No open PR directly owns the main Generate streaming/markup implementation | Keep the change within that path. If schema/contract changes become necessary, recheck the contract files shared with #4218–#4220. |
| #4347 translation provenance / Retry | #4221: `dub-session.ts`, `dub-translation-panel.tsx`; #4220: `backend/api/routers/dub_generate.py` | Compare pending behavior and agree on a bounded follow-up. Do not implement a competing guided workflow. |
| #4346 missing-background export | #4218: `dub_pipeline.py`, `dub_core.py`; #4220: `dub_export.py`; #4221: export UX | Preserve distinctions among intentionally skipped, failed and successful separation and the active contributor's cache model. |
| Installer proxy / cache-repair alternatives | #4348: `runtime-download.ts`; #4349: `hf_cache_repair.py` | Diagnose the exact reporter failure before proposing changes; existing branches already own those fixes. |
| Windows ROCm ASR isolation | #4338: `backend/core/windows_rocm/` and `backend/engines/_asr_sidecar/runtime.py` | Assist/review or coordinate; do not duplicate this repair under the broad AMD tracker. |

## Candidate timelines and ownership findings

### #4344: model-specific cloning capability

The issue had no comments, labels, assignees or timeline events. Its absence from a PR cross-reference is consistent with the complete open PR list, but is not a guarantee of availability.

Recent history matters: [#3833](https://github.com/debpalash/VoiceStudio/pull/3833) is API-closed without a direct merge, yet the [maintainer explicitly says Kokoro preset behavior shipped through an earlier train](https://github.com/debpalash/VoiceStudio/pull/3833#issuecomment-6734787583). The new fix should prevent unsupported models inheriting those presets while keeping Kokoro's legitimate preset path. Current-source analysis, acceptance criteria and precise files are in [plan 1](01-mlx-cloning-capabilities.md).

### #4345: MCP stdio/HTTP session

The issue likewise had no comments, labels, assignees or timeline events. The reporter used the older 0.5.6 Docker image; the reported race/header explanation is a hypothesis. A current-main protocol test determines whether the failure persists and which message sequence causes it.

Merged [#4128](https://github.com/debpalash/VoiceStudio/pull/4128) and [#4315](https://github.com/debpalash/VoiceStudio/pull/4315) are adjacent security/authentication history, not evidence that this session bug is fixed. Preserve delegated caller identity, allowed credential forwarding and the difference between direct local stdio and an HTTP shim. [Plan 2](02-mcp-stdio-session.md) scopes reproduction and regression coverage.

### #4254: merged foundation, unfinished progressive delivery

The timeline records the owner [choosing paragraph gaps, trimming and SSML-lite while dropping sentence gaps](https://github.com/debpalash/VoiceStudio/pull/4254#issuecomment-7070476186), followed by the merge at 2026-11-22 02:44:16 UTC. The PR description still lists per-span streaming as unfinished; the current source confirms that this remains a real follow-up.

The proposed work does not infer unfinished implementation from an old checkbox alone. It combines the merged PR's scope with current-source review and targets first-audio delivery for already-planned spans. It must preserve ordering, pause lengths, seeds, cancellation, watermarking and final-file consistency, and must not reinstate sentence splitting with the rejected render-time cost. See [plan 3](03-progressive-markup-streaming.md).

### #3924: tracker, not an untouched to-do list

Its 51 timeline events include 29 cross-referenced items, many merged. It contains both historical benchmark comments and later implementation links. An unchecked checkbox can therefore describe work that already shipped. The table below is the duplication guard for new “performance” suggestions.

No open matching PR was identified for the preferred residual scopes. No issue was assigned, reserved, opened, closed or commented on by this audit.

## Relevant work already implemented, superseded or closed through another route

| Related PR | Verified API status / merge date (UTC) | What this changes in the plan |
| --- | --- | --- |
| [#4254](https://github.com/debpalash/VoiceStudio/pull/4254) feat(generate): sentence/paragraph gaps and SSML-lite tags in Generate and MCP | Merged 2026-11-22 | Paragraph gaps, trimming and SSML-lite are implemented. Only the bounded progressive-streaming follow-up is proposed; sentence gaps were removed by owner decision. |
| [#3833](https://github.com/debpalash/VoiceStudio/pull/3833) fix(mlx-audio): expose Kokoro preset voices and speak the requested language voice (#3802) | Closed; no direct merge | API reports closed without direct merge; maintainer says Kokoro preset behavior already shipped through an earlier train. Preserve that valid preset behavior while fixing model-specific leakage. |
| [#3981](https://github.com/debpalash/VoiceStudio/pull/3981) Coordinate native and buffered MLX speech generation | Merged 2026-11-10 | Native/buffered MLX coordination exists. Retain its shared-engine serialization and ownership assumptions. |
| [#3992](https://github.com/debpalash/VoiceStudio/pull/3992) Stream native Qwen speech chunks over WebSocket | Merged 2026-11-10 | Native Qwen WebSocket streaming already exists; do not replace it with a universal buffered path. |
| [#3976](https://github.com/debpalash/VoiceStudio/pull/3976) Stream OpenAI-compatible PCM speech and support Qwen3-TTS Base | Merged 2026-11-10 | OpenAI-compatible PCM streaming and Qwen3 Base support already exist; avoid a duplicate streaming feature. |
| [#4114](https://github.com/debpalash/VoiceStudio/pull/4114) fix(pronunciation): prepare spoken text across synthesis routes | Merged 2026-11-14 | Shared spoken-text preparation exists. Progressive spans must preserve dictionary/preparation semantics. |
| [#4128](https://github.com/debpalash/VoiceStudio/pull/4128) fix(mcp): stop the MCP bridge from laundering a consumption caller into loopback admin | Merged 2026-11-14 | MCP caller-tier/authentication repair exists. Session work must not borrow loopback administrator trust. |
| [#4303](https://github.com/debpalash/VoiceStudio/pull/4303) fix(api): make every loopback short-circuit honour the delegated-caller marker | Closed; no direct merge | API reports closed without direct merge; maintainer confirms integration through #4315 after branch rewriting. Do not reopen the marker-guard fix as missing. |
| [#4315](https://github.com/debpalash/VoiceStudio/pull/4315) Merge train: DeryFerd #4290, #4292, #4293, #4298, #4299, #4303 | Merged 2026-11-20 | Integrated the delegated-caller guard and other community fixes with maintainer repairs. |
| [#3916](https://github.com/debpalash/VoiceStudio/pull/3916) fix(mcp): pass on the backend's error detail instead of a bare HTTP status | Merged 2026-11-09 | MCP preserves useful backend error detail; keep it when changing transport failures. |
| [#4320](https://github.com/debpalash/VoiceStudio/pull/4320) perf: speed up Electron startup, UI responsiveness, and backend DB/engine boot | Merged 2026-11-21 | Startup minification, lazy UI loading, DB fast path and concurrent engine probes are already implemented. |
| [#4321](https://github.com/debpalash/VoiceStudio/pull/4321) perf: fewer renderer re-renders, lazy waveforms and lighter polling | Merged 2026-11-21 | Fewer renderer re-renders, lazy waveforms, transcript virtualization and reduced polling already landed. |
| [#4322](https://github.com/debpalash/VoiceStudio/pull/4322) ci: faster Python tests and ROCm image builds; smaller installers | Merged 2026-11-21 | CI sharding/cache work and smaller desktop packaging already landed; do not propose them as new. |
| [#4323](https://github.com/debpalash/VoiceStudio/pull/4323) perf: faster dub pipeline, transcription and job saves | Merged 2026-11-21 | Dub ingest, ASR/NLLB fast paths, lighter history and worker-thread saves already landed. Real-hardware wall-clock evidence remains a possible measured follow-up. |
| [#3940](https://github.com/debpalash/VoiceStudio/pull/3940) perf: offline benchmark harness, recorded baselines, lazy-load the setup wizard (#3924) | Merged 2026-11-09 | Offline benchmark harness and recorded baseline framework already exist; extend rather than recreate them. |
| [#3943](https://github.com/debpalash/VoiceStudio/pull/3943) perf: load media players on demand (#3924) | Merged 2026-11-09 | Media-player lazy loading already exists. |
| [#3946](https://github.com/debpalash/VoiceStudio/pull/3946) perf: check speech-recognition engines without importing them into the backend (#3924) | Merged 2026-11-09 | Import-light ASR availability probes already exist. |
| [#4041](https://github.com/debpalash/VoiceStudio/pull/4041) perf: cut idle polling (supervisor, cloud sync, Windows parent watcher) | Merged 2026-11-12 | Several idle polling reductions already exist. |
| [#4043](https://github.com/debpalash/VoiceStudio/pull/4043) perf(models): skip engine unload when a local model folder save changes nothing | Merged 2026-11-12 | Saving an unchanged local model directory already avoids unloading the model. |
| [#4073](https://github.com/debpalash/VoiceStudio/pull/4073) perf: pause idle timers while the window is hidden | Merged 2026-11-13 | Hidden-window idle timers already pause. |
| [#4074](https://github.com/debpalash/VoiceStudio/pull/4074) perf: virtualise long project, dub-project and transcription lists | Merged 2026-11-13 | Long project/dub/transcription list virtualization already exists. |
| [#4079](https://github.com/debpalash/VoiceStudio/pull/4079) perf(projects): virtualise the Projects grid view | Merged 2026-11-13 | Projects grid virtualization already exists. |
| [#4088](https://github.com/debpalash/VoiceStudio/pull/4088) perf(dub): resume a crashed dub from its finished segments (#3924) | Merged 2026-11-13 | Completed dubbing segments can already be resumed after a crash; preserve durability and recovery ordering. |
| [#4117](https://github.com/debpalash/VoiceStudio/pull/4117) fix(memory): free idle GPU memory before a generate when VRAM is low | Merged 2026-11-14 | Low dedicated VRAM now triggers safe pre-generation cleanup; do not duplicate this under the stale tracker checklist. |
| [#4169](https://github.com/debpalash/VoiceStudio/pull/4169) fix(gallery): bound mounted community voice cards | Merged 2026-11-16 | Community gallery virtualization already exists, including audio/focus retention fixes. |
| [#4198](https://github.com/debpalash/VoiceStudio/pull/4198) fix(dub): keep watermarking off the event loop | Merged 2026-11-16 | Fresh dub-segment watermarking already runs off the event loop; preserve marking and publication ordering. |
| [#4332](https://github.com/debpalash/VoiceStudio/pull/4332) fix(tts): read Vietnamese numbers reliably | Merged 2026-11-22 | Vietnamese dot-grouping and nghìn→ngàn normalization are implemented; remaining speech-quality cases require new evidence. |
| [#3970](https://github.com/debpalash/VoiceStudio/pull/3970) fix(dub): retry background separation leaner, then on CPU, and say so when it fails (#3751) | Merged 2026-11-10 | Lean/CPU background-separation retry already exists. #4346 concerns incomplete artifact state/export after failure; retry implementation alone is not a new fix. |
| [#4286](https://github.com/debpalash/VoiceStudio/pull/4286) fix(longform): attach the finished result when the render stream drops before done | Merged 2026-11-20 | Long-form completion recovery after a dropped stream already exists; compare #4090/#4136 reports before modifying similar state. |
| [#4330](https://github.com/debpalash/VoiceStudio/pull/4330) fix(install): VoxCPM2 kaldifst wheel pin and proxy bypass fallback | Merged 2026-11-22 | VoxCPM2 kaldifst wheel selection and proxy-bypass fallback are already repaired; sparse install reports still need exact reproduction. |
| [#4033](https://github.com/debpalash/VoiceStudio/pull/4033) fix(analytics): defer analytics startup work to improve app startup performance | Closed; no direct merge | Closed in favor of independent #4108; its contribution was not copied, per maintainer. Do not describe this original PR as merged. |
| [#4108](https://github.com/debpalash/VoiceStudio/pull/4108) fix(analytics): keep lifecycle I/O off backend readiness | Merged 2026-11-14 | Independent analytics lifecycle/readiness fix is merged; startup deferral is already covered. |

Two closure distinctions deserve explicit retention:

- [#4303](https://github.com/debpalash/VoiceStudio/pull/4303) has `merged=false`, but the maintainer [confirms it landed through #4315 after branch rewriting](https://github.com/debpalash/VoiceStudio/pull/4303#issuecomment-7051283242). Treat the behavior as already integrated.
- [#4033](https://github.com/debpalash/VoiceStudio/pull/4033) was [closed in favor of an independent implementation](https://github.com/debpalash/VoiceStudio/pull/4033#issuecomment-6874475081), [#4108](https://github.com/debpalash/VoiceStudio/pull/4108), which is merged. Do not describe the original contribution as merged or reuse an unsigned patch.

The recent search includes additional related histories in its result-number lists. The table selects the ones that materially change these contribution choices; it does not claim a full diff/security review of the historical repository.

## Revalidation and claim procedure

### Before choosing or claiming a task

1. Fetch upstream `main`; compare its SHA with this snapshot. Read the current repository guidance again if it changed.
2. Re-enumerate **all pages** of open issues and open PRs. Read the target issue's new comments/timeline and every newly relevant PR's body, changed filenames, review threads and current head.
3. Repeat the explicit recent-topic queries and search the target function/path plus user-visible symptom. Search indexing and issue cross-references can lag; file overlap is an independent check.
4. Reproduce against current upstream, then the affected release if needed. If main already solves it, validate the release gap and update the plan rather than creating another fix.
5. Where ownership overlaps, coordinate a narrow scope with the existing contributor/maintainer. An unassigned issue, stale update time, draft or missing CLA is not permission to replace someone else's work.

Read-only commands for a future checkout:

```bash
git fetch upstream
git rev-parse upstream/main

gh api --paginate 'repos/debpalash/VoiceStudio/issues?state=open&per_page=100'   --jq '.[] | select(.pull_request == null) | {number, title, state, labels: [.labels[].name], assignees: [.assignees[].login], updated_at}'

gh api --paginate 'repos/debpalash/VoiceStudio/pulls?state=open&per_page=100'   --jq '.[] | {number, title, draft, head: .head.sha, base: .base.sha, updated_at}'

gh issue view 4344 --repo debpalash/VoiceStudio --comments
gh issue view 4345 --repo debpalash/VoiceStudio --comments
gh issue view 3924 --repo debpalash/VoiceStudio --comments
gh issue view 4347 --repo debpalash/VoiceStudio --comments

gh api --paginate 'repos/debpalash/VoiceStudio/issues/4344/timeline?per_page=100'
gh api --paginate 'repos/debpalash/VoiceStudio/issues/4345/timeline?per_page=100'
gh api --paginate 'repos/debpalash/VoiceStudio/pulls/4216/files?per_page=100' --jq '.[].filename'
gh api --paginate 'repos/debpalash/VoiceStudio/pulls/4220/files?per_page=100' --jq '.[].filename'
gh api --paginate 'repos/debpalash/VoiceStudio/pulls/4221/files?per_page=100' --jq '.[].filename'
```

These commands only gather evidence. An issue-claim comment or assignment is a separate public action; none is implied by running the audit. A future scope message should identify the reproduction, intended boundary, existing overlapping PRs and acceptance criteria, without claiming a fix already exists.

### Before pushing an implementation PR

Refresh upstream again, reconcile current main, rerun the affected behavior/regressions and confirm the open-PR collision check still holds. Keep the PR focused and link the existing issue using `Closes` only if the complete reported defect is covered; otherwise use `Refs` and state the remaining scope. Preserve contributor credit and the real submitter's identity. Do not bump versions or mark a beta/stable release as fixed without confirming it contains the actual change.

Follow [validation-and-delivery.md](validation-and-delivery.md) for offline regression isolation, platform coverage, changelog/docs checks and review/CI gates. A documentation planning branch is not a tested product fix or an upstream implementation PR.

## Appendix: complete changed-file inventory for all 15 open PRs

### #4354: 1 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4354/files); reviewed head `3f8d8d08dc9354885fa283187ce0706104e34970`.

```text
.github/workflows/android-repository.yml
```

### #4353: 3 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4353/files); reviewed head `bc721d905c7331b7679e56854b806cb972d69040`.

```text
.github/workflows/android-play-internal.yml
.github/workflows/mobile-release.yml
.github/workflows/mobile.yml
```

### #4352: 11 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4352/files); reviewed head `40712a73ff54e31fd541030ace056e537f75e62b`.

```text
.github/workflows/android-repository.yml
.github/workflows/ci.yml
.github/workflows/contributors-refresh.yml
.github/workflows/cosyvoice-dependencies.yml
.github/workflows/electron-build.yml
.github/workflows/electron-release.yml
.github/workflows/install-smoke.yml
.github/workflows/mac-app-store.yml
.github/workflows/microsoft-store.yml
.github/workflows/security.yml
.github/workflows/snap-store.yml
```

### #4351: 1 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4351/files); reviewed head `8c2977f4dac179915c46a6fdeb33145058ad8f81`.

```text
.github/workflows/docs-drift.yml
```

### #4350: 5 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4350/files); reviewed head `68b7d87395cf3e98916f24335166065b22eb8912`.

```text
.github/workflows/android-play-internal.yml
.github/workflows/android-repository.yml
.github/workflows/electron-release.yml
.github/workflows/mobile-release.yml
.github/workflows/mobile.yml
```

### #4349: 3 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4349/files); reviewed head `69a0c6c6520c9be4d8a2d0ccd2fdf412857e65a8`.

```text
backend/services/hf_cache_repair.py
changelog.d/4349.fixed.md
tests/test_hf_cache_repair.py
```

### #4348: 3 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4348/files); reviewed head `57774fcb1a90393be195eabc0a25b3e776007652`.

```text
changelog.d/4348.fixed.md
electron/src/main/runtime-download.test.ts
electron/src/main/runtime-download.ts
```

### #4338: 8 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4338/files); reviewed head `3115c4810a64c504059dc6ce459a0910253a4176`.

```text
backend/core/windows_rocm/asr_isolation.py
backend/core/windows_rocm/isolation_policy.py
backend/core/windows_rocm/pipelines.py
backend/engines/_asr_sidecar/runtime.py
changelog.d/4338.fixed.md
docs/install/windows-rocm.md
tests/test_windows_rocm_argos_isolation.py
tests/test_windows_rocm_asr_worker.py
```

### #4337: 3 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4337/files); reviewed head `b6cd2822d27d3a5c02c5d70cf95369b7d79a0508`.

```text
backend/services/transcript_diarization.py
backend/tests/test_transcribe_diarization.py
docs/features/diarization.md
```

### #4221: 68 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4221/files); reviewed head `c80774a3b79376c1c374ef34bbff759b8fb733e0`.

```text
changelog.d/4221.changed.md
docs/electron-dubbing.md
electron/src/renderer/src/components/workspace-sidebar.test.tsx
electron/src/renderer/src/components/workspace-sidebar.tsx
electron/src/renderer/src/features/dub/casting-board.tsx
electron/src/renderer/src/features/dub/dub-draft.test.ts
electron/src/renderer/src/features/dub/dub-draft.ts
electron/src/renderer/src/features/dub/dub-empty-state.tsx
electron/src/renderer/src/features/dub/dub-export-destination.test.tsx
electron/src/renderer/src/features/dub/dub-export-panel.test.tsx
electron/src/renderer/src/features/dub/dub-export-panel.tsx
electron/src/renderer/src/features/dub/dub-flow-state.test.ts
electron/src/renderer/src/features/dub/dub-flow-state.ts
electron/src/renderer/src/features/dub/dub-generation-request.ts
electron/src/renderer/src/features/dub/dub-generation-review.test.tsx
electron/src/renderer/src/features/dub/dub-generation-review.tsx
electron/src/renderer/src/features/dub/dub-input-selection.ts
electron/src/renderer/src/features/dub/dub-issue-state.ts
electron/src/renderer/src/features/dub/dub-issues.test.tsx
electron/src/renderer/src/features/dub/dub-issues.tsx
electron/src/renderer/src/features/dub/dub-media-preview.test.tsx
electron/src/renderer/src/features/dub/dub-media-preview.tsx
electron/src/renderer/src/features/dub/dub-narration-panel.test.tsx
electron/src/renderer/src/features/dub/dub-narration-panel.tsx
electron/src/renderer/src/features/dub/dub-narration-session.test.ts
electron/src/renderer/src/features/dub/dub-narration.test.ts
electron/src/renderer/src/features/dub/dub-narration.ts
electron/src/renderer/src/features/dub/dub-page.tsx
electron/src/renderer/src/features/dub/dub-project-guide.test.tsx
electron/src/renderer/src/features/dub/dub-project-guide.tsx
electron/src/renderer/src/features/dub/dub-script-comparison.test.tsx
electron/src/renderer/src/features/dub/dub-script-comparison.tsx
electron/src/renderer/src/features/dub/dub-session.test.ts
electron/src/renderer/src/features/dub/dub-session.ts
electron/src/renderer/src/features/dub/dub-source-panel.tsx
electron/src/renderer/src/features/dub/dub-source-row.test.tsx
electron/src/renderer/src/features/dub/dub-speech-preview.ts
electron/src/renderer/src/features/dub/dub-speech-ready.test.tsx
electron/src/renderer/src/features/dub/dub-speech-ready.tsx
electron/src/renderer/src/features/dub/dub-srt-input.test.tsx
electron/src/renderer/src/features/dub/dub-srt-voice-selection.test.tsx
electron/src/renderer/src/features/dub/dub-timeline.tsx
electron/src/renderer/src/features/dub/dub-translation-panel.tsx
electron/src/renderer/src/features/dub/transcript-issue-navigation.tsx
electron/src/renderer/src/features/projects/project-format.ts
electron/src/renderer/src/i18n/locales/ar.json
electron/src/renderer/src/i18n/locales/de.json
electron/src/renderer/src/i18n/locales/en.json
electron/src/renderer/src/i18n/locales/es.json
electron/src/renderer/src/i18n/locales/fr.json
electron/src/renderer/src/i18n/locales/gl.json
electron/src/renderer/src/i18n/locales/hi.json
electron/src/renderer/src/i18n/locales/id.json
electron/src/renderer/src/i18n/locales/it.json
electron/src/renderer/src/i18n/locales/ja.json
electron/src/renderer/src/i18n/locales/ko.json
electron/src/renderer/src/i18n/locales/nl.json
electron/src/renderer/src/i18n/locales/pl.json
electron/src/renderer/src/i18n/locales/pt.json
electron/src/renderer/src/i18n/locales/ru.json
electron/src/renderer/src/i18n/locales/sv.json
electron/src/renderer/src/i18n/locales/th.json
electron/src/renderer/src/i18n/locales/tr.json
electron/src/renderer/src/i18n/locales/uk.json
electron/src/renderer/src/i18n/locales/vi.json
electron/src/renderer/src/i18n/locales/zh-CN.json
electron/src/renderer/src/i18n/locales/zh-TW.json
tests/test_no_hardcoded_cjk.py
```

### #4220: 24 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4220/files); reviewed head `751e562d6ee2184cc7beedfa764eb5283b5bef91`.

```text
backend/api/routers/dub_export.py
backend/api/routers/dub_generate.py
backend/core/diagnostic_reports.py
backend/schemas/requests.py
backend/services/dub_issues.py
backend/services/dub_resume.py
backend/services/dub_speech_checkpoints.py
backend/services/dub_speech_preview.py
backend/services/subtitle_audio.py
changelog.d/4220.fixed.md
cli/voicestudio_cli/contracts.json
docs/STRUCTURE.md
docs/dub-audio-generation.md
mobile/contract/openapi.json
tests/fixtures/api_routes.txt
tests/test_dub_complete_audio.py
tests/test_dub_prepared_speech.py
tests/test_dub_qc_track_language.py
tests/test_dub_speech_checkpoints.py
tests/test_dub_voice_match.py
tests/test_pronunciation_speech_routes.py
tests/test_redub_incremental.py
tests/test_smart_fit_generate.py
tests/test_subtitle_audio_layout.py
```

### #4219: 6 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4219/files); reviewed head `28e93390cbf1649c8c40030f0cf8af1246566122`.

```text
backend/api/routers/dub_core.py
changelog.d/4219.added.md
docs/dub-subtitle-input.md
mobile/contract/openapi.json
tests/fixtures/api_routes.txt
tests/test_dub_subtitle_only.py
```

### #4218: 8 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4218/files); reviewed head `826fc55de0e9f20af6782ec8581a7d7a5f3e5683`.

```text
backend/api/routers/dub_core.py
backend/services/dub_pipeline.py
changelog.d/4218.added.md
cli/voicestudio_cli/contracts.json
docs/dub-background-separation.md
mobile/contract/openapi.json
tests/test_dub_demucs_fallback.py
tests/test_dub_optional_background.py
```

### #4217: 26 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4217/files); reviewed head `ed980714ec69e9688dd958b1f0997974ee637ae5`.

```text
changelog.d/4217.added.md
docs/dub-project-management.md
electron/src/renderer/src/features/dub/dub-projects.test.tsx
electron/src/renderer/src/features/dub/dub-projects.tsx
electron/src/renderer/src/i18n/locales/ar.json
electron/src/renderer/src/i18n/locales/de.json
electron/src/renderer/src/i18n/locales/en.json
electron/src/renderer/src/i18n/locales/es.json
electron/src/renderer/src/i18n/locales/fr.json
electron/src/renderer/src/i18n/locales/gl.json
electron/src/renderer/src/i18n/locales/hi.json
electron/src/renderer/src/i18n/locales/id.json
electron/src/renderer/src/i18n/locales/it.json
electron/src/renderer/src/i18n/locales/ja.json
electron/src/renderer/src/i18n/locales/ko.json
electron/src/renderer/src/i18n/locales/nl.json
electron/src/renderer/src/i18n/locales/pl.json
electron/src/renderer/src/i18n/locales/pt.json
electron/src/renderer/src/i18n/locales/ru.json
electron/src/renderer/src/i18n/locales/sv.json
electron/src/renderer/src/i18n/locales/th.json
electron/src/renderer/src/i18n/locales/tr.json
electron/src/renderer/src/i18n/locales/uk.json
electron/src/renderer/src/i18n/locales/vi.json
electron/src/renderer/src/i18n/locales/zh-CN.json
electron/src/renderer/src/i18n/locales/zh-TW.json
```

### #4216: 5 changed files

Source: [PR files](https://github.com/debpalash/VoiceStudio/pull/4216/files); reviewed head `e64f70af26c4e91b8064594483b7171707e3ecc1`.

```text
changelog.d/4216.fixed.md
docs/searchable-select-activation.md
electron/src/renderer/src/features/clone/preset-voice-picker.test.tsx
electron/src/shared/components/SearchableSelect.jsx
electron/src/shared/test/VoiceSelector.test.jsx
```

