# MCP stdio session reliability — investigation and implementation plan

**Issue:** [#4345 — stdio shim returns 400 Missing session ID, then 404 Session not found][issue]  
**Status:** Ready for diagnosis; no application change or runtime reproduction is claimed by this document.  
**Source baseline:** upstream `main` at [`2bb21302241793977055c44f7c52815bcbf0261e`][baseline], committed November 22, 2026 at 10:41:49 UTC.  
**Evidence reviewed:** November 22, 2026. Issue state, comments, timeline, open PR queue, current source, tests, dependency lock, prior changes and the pinned SDK implementation.

## 1. Decision and scope

Investigate this as a focused transport reliability contribution. First establish the actual message sequence and reproduce it on current VoiceStudio. The strongest source-backed lead is that the shim adopts a session ID from an unsuccessful HTTP response and then keeps sending that expired ID. This can produce the reported 400 → 404 sequence without concurrent requests. It is a reachable mechanism in the reviewed code, **not yet a demonstrated explanation of the reporter's Claude Code session**.

The initial deliverable is a deterministic failure transcript and a regression test using the real shim and installed MCP SDK. Implement only the smallest change supported by that evidence. A general MCP client rewrite, SDK major upgrade, new authentication mode, new engine support, and frontend redesign are outside this contribution.

Completion means a supported stdio client can initialize, list tools and make repeated `check_health` calls through the mounted HTTP backend; rejected opening requests cannot contaminate the next initialization; request errors remain correlated; and existing authorization and per-agent voice identity survive unchanged.

## 2. What is verified

### Issue and version baseline

| Item | Verified state | Consequence |
|---|---|---|
| Issue #4345 | Open; no assignee; zero comments; empty timeline at review | No linked implementation was visible. Recheck before starting work. |
| Reported environment | Docker `ghcr.io/debpalash/omnivoice-studio:0.5.6`, MCP SDK `1.30.0`, Claude Code `2.1.328`, Linux | Preserve this exact combination as a comparison case, subject to image availability. Record the image digest, not only its tag. |
| Reported behavior | `python -m backend.mcp_shim` fails; direct HTTP works; a separate sequential SDK client initialized, listed seven tools and called `check_health` three times | This is reporter evidence, not a test run performed for this plan. Do not hardcode seven as today's required tool count. |
| Latest stable at review | [`v0.5.8`, published November 12, 2026][stable] | Reproduce on stable as well as the reported old image. |
| Pinned main | `package.json` and `pyproject.toml`: `0.5.9-beta.7` | Stable and main are separate comparison points. No version bump is needed for this investigation. |
| Declared SDK support | Python `>=3.11`; `mcp>=1.28.1,<2`; `httpx>=0.28.1` | Work within the project's existing v1 SDK contract. |
| Locked transport stack | MCP `1.30.0`, httpx `0.28.1`, AnyIO `4.14.2`, Starlette `1.6.0`, FastAPI `0.136.3`, uvicorn `0.52.4` | The reported SDK version matches main's lock. “Upgrade the MCP SDK” is not an established fix. |

The versions above come from the pinned [project manifest][pyproject], [package manifest][package] and [lockfile][lock]. The open PR collection was also reviewed: no visible open PR described this shim-session repair. That is a review-time observation, not a reservation of the issue.

### Current shim behavior

The following facts are visible in [`backend/mcp_shim/__main__.py`][shim]:

1. `_run()` reads one newline-delimited stdin message and **awaits `_handle_request()` before reading the next line**. Fast input can queue in the pipe, but this code does not launch overlapping HTTP POST tasks. Do not diagnose a parallel POST race from the issue description alone.
2. Every message is posted to `<base>/mcp/`. `OMNIVOICE_URL` takes precedence and preserves an HTTPS scheme and path prefix. Health polling uses `<base>/health`.
3. When `session_id[0]` is empty, `_handle_request()` saves an `mcp-session-id` response header **before testing the HTTP status**, and without checking that the message is `initialize` or that a successful initialization result was received.
4. Once nonempty, that stored ID is attached to subsequent requests. The shim does not clear it on 404, replace it after a failed opening exchange, or implement explicit reinitialization.
5. HTTP 202 produces no stdout message. On HTTP errors, request messages receive a generic JSON-RPC error with their original ID; notifications receive no synthesized response. Diagnostics go to stderr.
6. JSON and SSE response types are accepted. The SSE branch parses individual `data:` lines as JSON, rather than assembling complete SSE events. This needs targeted framing coverage if it is implicated; it does not by itself establish the session failure.
7. The shim does not track the initialization result's negotiated protocol version or send `MCP-Protocol-Version` on subsequent HTTP requests. It also has no independent GET event stream or DELETE-on-EOF path. These are separate transport-contract observations, not permission to broaden the fix automatically.
8. `OMNIVOICE_CLIENT_ID` is forwarded as `X-OmniVoice-Client-Id`. An explicitly configured API key is forwarded as a bearer credential only over HTTPS or loopback HTTP. The shim is an **HTTP caller**, even though its client-facing side uses stdio.

The [mounted server][server] uses the SDK's stateful Streamable HTTP session manager, configures its transport path as `/`, mounts it at `/mcp`, and retains a bare `/mcp` compatibility route. Do not disable stateful sessions, host validation or authorization to make the symptom disappear.

### A specific mechanism to test first

The pinned SDK's [session manager][sdk-manager] creates a candidate session for a request without a session header. Its [HTTP transport][sdk-transport] adds that candidate ID to error responses, including the 400 returned for a non-initialization request missing a session ID. The manager then discards an opening session whose response status is an error. The shim's current early header assignment therefore permits this sequence:

| Step | HTTP / shim event | State consequence |
|---|---|---|
| 1 | A valid JSON-RPC message other than `initialize` reaches a fresh shim first | Shim sends it without a session header. |
| 2 | SDK returns 400, with the newly allocated session ID in the response header | Shim stores that ID before it notices the error. |
| 3 | SDK disposes of the unsuccessful opening session | Stored ID now names no live session. |
| 4 | Client sends its `initialize` request | Shim attaches the stale ID. |
| 5 | SDK receives an unknown session ID | Server returns 404; shim retains the stale ID. |

A rejected initialization that carries a session header is another case to test. The SDK's own [v1.30 HTTP client][sdk-client] checks the response status and only extracts a session ID for an initialization request, which is a useful compatibility reference.

**Still unknown:** the first actual Claude Code message; whether any earlier message or malformed initialization was rejected; whether the emitted error header was captured; the exact container source/image digest; whether the backend restarted; and whether current stable/main reproduce the same failure. The reporter's “Missing session ID” text does not answer those questions.

Keep an unrelated 404 after a long idle period separate from this startup failure. SDK 1.30 adds a default 30-minute idle session expiry; the current shim does not hold a GET stream open. An accelerated expiry test is useful for recovery policy, but a thirty-minute timer does not explain an immediate first-connect failure without additional evidence. See the [version-specific release notes][sdk-release].

## 3. Existing work to preserve

| Prior change | What it established | Boundary for this contribution |
|---|---|---|
| [#2289][pr2289] | Bare `/mcp` routing, real backend ports, HTTPS/path-prefix support, stdio bearer forwarding and credential transport restrictions | Test both endpoint spellings on the server; keep the shim's trailing-slash default and environment precedence. |
| [#4128][pr4128], merged November 14 | HTTP tool calls preserve the actual caller's peer, origin and credential tier; separate HTTP backends receive reducing-only delegation markers | A session fix must never make HTTP shim traffic a privileged direct-stdio session. |
| November 20 [delegated guard expansion][delegated-guards] and [valid-admin follow-up][delegated-admin] | Other loopback guards respect delegated identity while valid admin credentials still work | Reuse current identity/delegation tests; do not copy the older pre-fix bridge behavior. |
| Current [MCP error handling tests][error-tests] | Credential/path scrubbing, bounded streamed error reads and refusal of redirects | Keep new diagnostics bounded and avoid leaking keys, session IDs or request content. |
| Current [startup timeout tests][startup-tests] | Optional MCP startup cannot wedge the whole backend | A transport repair must not make backend startup depend indefinitely on an MCP client. |

Direct `backend.mcp_server` stdio and the `backend.mcp_shim` HTTP proxy are intentionally different. Direct stdio retains local operator semantics; the shim retains HTTP authentication requirements. The [current MCP documentation][mcp-docs] explains that distinction. Replacing the shim with the direct server is not an equivalent fix or universally equivalent workaround.

## 4. Phase A — establish the failure boundary

### A1. Refresh ownership and immutable inputs

- Re-read #4345, its comments/timeline and the open PR queue. If a contributor has a matching implementation, review or help that branch rather than duplicating it.
- Start an implementation branch from freshly fetched upstream main, as required by [CONTRIBUTING][contributing] and [AGENTS.md][agents]. The SHA in this plan remains the investigation baseline; record any newer implementation base separately.
- Record image digest, application commit/version, Python and installed `mcp`, `httpx`, `anyio`, `starlette`, `fastapi`, `uvicorn` versions for each run. Report only relevant version metadata.
- Compare the reported image, stable `v0.5.8` and the pinned/current main. Do not relabel a mutable `latest` image as stable: project documentation defines `latest` as rolling main.
- Use a disposable data directory and a local health-only fixture first. This handshake does not require GPU inference, model downloads, saved voices or a real user's projects.

### A2. Capture a minimal client/transport transcript

Instrument the test harness or a temporary local diagnostic wrapper, not default production logging. For each message record:

- sequence number and monotonic timestamps at stdin receipt, HTTP headers, response completion and stdout emission;
- JSON-RPC method and request ID, with request/notification/response distinguished;
- HTTP status and content type;
- whether a session header was sent/received and an opaque per-run label such as `S1`, so equality can be checked without exposing the ID;
- negotiated protocol version and whether the subsequent version header matches it;
- configured fixture client ID and sanitized endpoint path.

Do not collect tool arguments, audio, environment dumps, bearer values, cookies, full URLs with credentials, or raw session IDs. This is enough to distinguish malformed input, premature messages, poisoned state, header stripping, response framing, backend restart and session expiry.

Run the reporter's client after the deterministic harness exists. The original shape is:

```json
{
  "mcpServers": {
    "vs": {
      "type": "stdio",
      "command": "docker",
      "args": ["exec", "-i", "voicestudio-mcp-repro", "python", "-m", "backend.mcp_shim"]
    }
  }
}
```

`voicestudio-mcp-repro` denotes a dedicated test container prepared from the selected image; this example does not start a container. Use `-i`, without an allocated TTY, so protocol stdout remains a pipe. With the reporter's installed client version available, the comparison command is:

```bash
claude -p --strict-mcp-config --mcp-config ./mcp-repro.json \
  "Call check_health on server vs three times and report whether all calls succeeded."
```

The LLM-driven run is supplementary interoperability evidence. A deterministic scripted client must establish the exact request order independently.

### A3. Decide whether application implementation is needed

| Finding | Next action |
|---|---|
| Report fails on 0.5.6; stable and current main pass under the same client/transcript | Identify the existing change that repairs it. Prepare upgrade/verification guidance and retain only useful regression coverage. Stop a duplicate runtime fix. |
| All versions pass; the issue's original sequence is missing | Request the small missing transcript/version detail. Do not invent a race, claim resolution, or make broad transport changes. |
| A current-main failure is deterministic | Preserve a failing test and exact source/version provenance; proceed to Phase B. |
| Only a proxy/container setup fails | Isolate headers, path, backend lifetime and process/interpreter selection before changing shim state. |
| A separate SDK or modern-protocol incompatibility is found | Document it separately. Do not migrate from the supported v1 SDK line as part of this fix without an agreed scope. |

## 5. Phase B — construct meaningful regression coverage

### B1. Real stdio → HTTP → mounted SDK integration

Add a proposed `tests/test_mcp_shim_integration.py`. It must exercise the real subprocess entrypoint, not call `server.call_tool()` directly and call that a shim test.

1. Build a fresh small FastAPI/Starlette fixture per case. Register `/health`, use the production `mount_mcp()`/`create_mcp_server()` path, and run that instance's `session_manager.run()` in its lifespan.
2. Serve the fixture with uvicorn on a retained loopback socket bound to port zero. Pass that socket to the server so there is no choose-port/close/rebind race. Await an explicit ready condition before starting assertions.
3. Spawn `sys.executable -u -m backend.mcp_shim` from the repository root with piped stdin/stdout/stderr. Supply the fixture base URL, a known client ID, isolated storage and offline model-cache settings. Strip unrelated inherited auth/proxy configuration unless the case explicitly tests it.
4. Drive newline-delimited JSON-RPC through stdin and read stdout concurrently with stderr. Use bounded timeouts and retain only the sanitized transcript. A slow startup must not count as a protocol timing failure.
5. The baseline sequence is `initialize` → matching initialization result → `notifications/initialized` → `tools/list` → three `tools/call` requests for `check_health`. Assert the expected tool names are present rather than requiring exactly the old report's seven tools.
6. Start with `protocolVersion: "2024-11-05"`, matching existing repository handshake fixtures, and include the SDK's current supported handshake version plus the actual client-observed version. Record the server's negotiated value; do not silently force every client to the oldest test version.
7. Observe the actual HTTP headers at the fixture boundary. After successful initialization, every message, including notifications, carries the established session and appropriate negotiated protocol header.
8. Close stdin, wait for clean exit, stop the HTTP server, and await every reader/task. Tear down in `finally`, including failing assertions. Never reuse a FastMCP session manager across pytest event loops; the repository already documents that contamination risk in `test_mcp_mount.py`.

Use both JSON and SSE response modes. Add a pipelined-input variant that writes the same valid sequence as a burst while the driver reads concurrently. The shim should maintain message ordering without requiring fixed sleeps. This demonstrates its existing serialization rather than speculating that a faster client creates concurrent POSTs.

### B2. Deterministic opening/error cases

Add a proposed `tests/test_mcp_shim.py` for controlled HTTP responses and stream boundaries. Tests should observe requests, output and backend side effects, rather than merely assert an internal state variable matches its setter.

- Send an early notification or other non-initialize message to a fresh real-SDK session, then send a valid initialization. Capture the 400 response header and the following request. Demonstrate whether the current shim forwards the discarded ID. A controlled responder can also cover rejected initialization with a session header.
- Delay successful initialization headers and its response body independently. Ensure later stdin messages cannot adopt unvalidated session state or overtake initialization.
- Return 400, 401, 403, 404, 429 and 5xx in both JSON and text error shapes. Assert request IDs are preserved, notifications receive no invented replies, and retries do not multiply requests.
- Return 202 with an empty body. The shim emits no blank/invalid JSON or synthetic success response.
- Split SSE transport bytes across arbitrary chunk boundaries; include comment/heartbeat lines, empty priming events, and server notifications before the correlated final response. Include a complete multi-line `data:` event if the selected parser is changed. One logical JSON-RPC message must yield one stdout line.
- Exercise an interrupted stream after a synthetic side-effect counter has incremented. The counter must remain one: a lost response is not proof that execution never happened.
- Close/expire a test session, then request again. Separate an invalid-session response from ordinary tool-level errors. Use a short fixture-controlled expiry rather than a thirty-minute test or a sleep-based race.
- Cover clean EOF, invalid stdin JSON, backend never ready, cancellation and child-process cleanup. Preserve the documented exit-code distinctions unless an intentionally revised contract is documented and tested.

### B3. Existing coverage to reuse

| Existing file | Relevant protection |
|---|---|
| `tests/test_backend_self_url.py` | Shim URL precedence, configured ports, HTTPS/path prefix and key transport policy |
| `tests/test_mcp_client_setup.py` | Real SDK initialization/tool listing and `claude-code`/`cursor` binding identity; these HTTP tests currently bypass the shim |
| `tests/test_mcp_bare_path.py` | Real app with SPA: both MCP paths, HTTP methods, no redirect fallthrough |
| `tests/test_mcp_transport_identity.py` | Installed-SDK HTTP and true stdio contexts, real router persistence, credential precedence, cookie CSRF, backend overrides |
| `tests/test_mcp_delegated_tier.py` | Reducing-only delegation and loopback/admin/native-access boundaries |
| `tests/test_mcp_mount.py` | Mounted server, tool surface, disabled MCP, loop isolation and host allowlist |
| `tests/test_mcp_backend_error_detail.py` | Bounded/redacted backend error responses and redirect refusal |
| `tests/test_mcp_startup_timeout.py` | Backend startup remains available when MCP startup fails |

No existing test discovered in this review drives `_run()` as a stdio subprocess through its HTTP handshake. The URL/auth helper tests are useful but do not establish that session propagation works end to end. Extend existing fixtures when practical; do not build a second unrelated authentication test framework.

## 6. Phase C — choose the smallest demonstrated repair

### Likely repair if failed-opening session adoption is reproduced

- Treat a session ID returned during initialization as a candidate. Commit it only after a successful HTTP response and a valid matching `InitializeResult`; accept the absence of an ID for a server that legitimately does not create stateful sessions.
- Never adopt an ID from a 202 notification acknowledgment, non-initialization exchange, rejected initialization or other error response.
- Keep initialization and its state transition atomic relative to forwarding later input. The existing single-request loop already serializes calls; a new global lock is not an evidence-based starting point.
- Define the behavior of early messages explicitly. Refuse unsupported pre-initialization requests with a correlated protocol error, and handle notifications without invented replies. Do not manufacture a successful initialization or silently reorder arbitrary tool calls.
- Keep the exact downstream request ID when forwarding the successful initialization result and every later response. A body-level JSON-RPC initialization error must not create a ready session merely because HTTP returned 200.

### Protocol version and framing

If the handshake repair tracks initialization results, carry the negotiated `protocolVersion` into subsequent HTTP headers and test against the installed v1 SDK contract. Do not substitute SDK v2's newer protocol assumptions for the project's declared `<2` dependency. Any response parser change must preserve JSON, SSE, notifications and response correlation under real streaming.

Use a focused helper/state representation only if it makes initialization validation clear. Choose between retaining the small proxy and using an existing SDK transport after the failing case is known. An SDK transport replacement changes notification routing, redirects, lifecycle and exception behavior; it is not a free refactor. Preserve the project's stricter credential/redirect policy even if a library default differs.

### Invalid-session recovery and replay

Decide and document recovery separately from the opening fix:

- A 404 for an established session invalidates that session. A later initialization must be sent without the stale ID.
- If transparent reinitialization is needed for client compatibility, cache only the necessary initialization metadata and reestablish the handshake on the same configured endpoint/credential scope. Bound attempts and prove the behavior with the actual client.
- **Never blindly replay `tools/call`, a generation request, a clone/design save, or another potentially mutating operation after a timeout, disconnect or 404.** Return the correlated failure when execution is uncertain; a new session does not prove the old operation was never executed.
- A narrowly permitted retry of a read-only operation must be explicit, bounded and tested. The default implementation should not add replay to arbitrary JSON-RPC methods.
- If the downstream client's lifecycle requires reconnecting the stdio process, specify a clean, actionable failure/reconnect contract instead of an endless stream of stale-session 404s.

An idle-session or process-restart fix can be a follow-up contribution if it is independently valuable and not necessary to resolve the reproduced startup failure. Do not enlarge this PR into generic resumability, background GET streams and arbitrary server-request multiplexing without evidence that they are required.

### Authorization and client identity

Retain URL/path-prefix and header behavior on every handshake/recovery request. Keep `X-OmniVoice-Client-Id` stable so voice binding does not fall back to another/default voice. Never replace a remote HTTP caller's credentials with the process's operator key, bypass cookie CSRF, trust forwarded peer headers as identity, or relabel an unavailable HTTP context as true local stdio. Keep credentials restricted to the configured HTTPS/loopback destination and refuse redirects that would widen that boundary. These are compatibility requirements from #4128 and current code, not new product authentication features.

## 7. Acceptance matrix

All rows describe required evidence for the relevant changed behavior; none is marked passed by this planning document.

| Case | Required observable outcome |
|---|---|
| Normal JSON initialization | Matching result, valid session adoption when supplied, tools listed, three successful health calls |
| Normal SSE initialization | Same outcome, one stdout JSON-RPC line per complete logical message |
| Valid burst input | Initialization remains first; subsequent messages use its session; no lost or duplicate replies |
| Premature message followed by initialize | Rejection cannot poison subsequent valid initialization with a discarded session ID |
| Failed initialize carrying a session header | Session remains unestablished; a fresh valid initialization is possible |
| HTTP 200 with JSON-RPC initialization error | No ready-session transition and no fabricated success |
| Negotiated version | Subsequent HTTP version headers match the accepted handshake version |
| Notification / response acknowledgment | 202 with empty body creates no stdout response |
| HTTP failure | Original request ID retained; notification failure does not create an unsolicited request response |
| Expired/deleted session | Bounded documented recovery or reconnect; stale ID is not reused indefinitely |
| Interrupted mutating tool | No automatic duplicate invocation; synthetic side-effect count stays one |
| Prefix / custom port / slash | Configured endpoint remains correct; no regression to hardcoded port or SPA/redirect fallthrough |
| Client identity | `claude-code` and `cursor` fixture IDs survive initialization and any recovery; existing voice binding assertions pass |
| HTTP authorization | Valid credentials work; wrong/absent credentials do not gain direct-stdio/local-admin privileges |
| Cookie / delegation boundaries | Current real-router tests preserve CSRF, independent PIN gates, trusted peer and reducing-only marker semantics |
| Credentials and diagnostics | No forwarding to remote plaintext or unintended redirect target; no credential/session values in captured public diagnostics |
| EOF / cancellation / no backend | Bounded exit and cleanup; no leaked child, task, socket or cross-test session manager |
| Reported image / stable / main | Results identify the exact tested image/commit and SDK stack; old-only failures are not presented as current failures |
| Windows / macOS / Linux | Same protocol behavior and portable subprocess cleanup; no inference hardware requirement |

## 8. Validation commands and gates

Run these from a prepared checkout using its project environment. `--no-sync` avoids silently changing that environment while comparing results. The repository's setup and [CI workflow][ci] define dependency preparation; do not substitute the host Python environment for the pinned project stack.

```bash
uv run --no-sync python -c "from importlib.metadata import version; print({p: version(p) for p in ('mcp', 'httpx', 'anyio', 'starlette', 'fastapi', 'uvicorn')})"

uv run --no-sync pytest \
  tests/test_backend_self_url.py \
  tests/test_mcp_client_setup.py \
  tests/test_mcp_bare_path.py \
  -q --tb=short
```

For every run set `HF_HUB_OFFLINE=1` and point `HF_HUB_CACHE` at a newly created empty temporary directory. The test harness should create equivalent per-run temporary state on all platforms. Confirm that test collection did not skip MCP because its package is absent; existing tests use `pytest.importorskip('mcp')`.

After adding the **proposed** test files:

```bash
uv run --no-sync pytest \
  tests/test_mcp_shim.py \
  tests/test_mcp_shim_integration.py \
  -q --tb=short
```

For a transport/runtime patch, run the relevant compatibility group:

```bash
uv run --no-sync pytest \
  tests/test_mcp_transport_identity.py \
  tests/test_mcp_delegated_tier.py \
  tests/test_mcp_mount.py \
  tests/test_mcp_backend_error_detail.py \
  tests/test_mcp_startup_timeout.py \
  -q --tb=short
```

Use the same focused tests for the declared SDK floor `1.28.1` in a disposable comparison environment if the fix uses SDK internals or APIs newer than that floor. Preserve the authoritative lockfile; do not downgrade the working checkout or claim the floor supported without a run. Keep `1.30.0` as the primary regression environment.

Before a runtime change lands, satisfy the current repository gates. The active CI commands include `uv run --no-sync pytest tests/ -q --tb=short -n 6` across two whole-module shards and a separate serial `uv run --no-sync pytest backend/tests/ -q --tb=short` session. Let the current scope policy select Electron, Docker and platform jobs; dependency/lock changes expand that scope. Read bot findings, require the aggregate **Tests (backend + frontend)** check and mergeability, and refresh stale branches before judging CI. [AGENTS.md][agents] and [CONTRIBUTING][contributing] are authoritative.

**For this planning branch:** documentation-only policy applies. No runtime tests or product build are claimed or required merely to publish this plan. Validate Markdown, references and the final diff; retain normal identity, CLA and secret checks.

## 9. Files and delivery boundaries

| Path | Expected action |
|---|---|
| `backend/mcp_shim/__main__.py` | Likely narrow runtime change only after the failure is reproduced |
| `tests/test_mcp_shim.py` | Proposed controlled session/response regression cases |
| `tests/test_mcp_shim_integration.py` | Proposed real stdio subprocess / HTTP / SDK handshake coverage |
| `tests/test_backend_self_url.py` and existing MCP tests | Reuse; extend only where a changed boundary lacks meaningful coverage |
| `docs/mcp.md` | Explain supported client setup, error/reconnect contract or verified workaround in the same runtime PR |
| `docs/mcp.json` | Change only if the actual config contract changes |
| `changelog.d/<PR-number>.fixed.md` | One user-facing line after a runtime PR number exists, following [fragment rules][fragments] |
| `pyproject.toml`, `uv.lock` | No planned change; dependency change requires evidence and separate compatibility justification |

Start with one focused PR once a current failure is demonstrated. A possible title, **only if the failed-opening mechanism is verified**, is:

> fix(mcp): prevent failed initialization from poisoning stdio sessions

The description should state the failing sequence, why the prior session ID became invalid, the resulting behavior, the exact fail-before/pass-after test and the auth/identity compatibility evidence. Use `Related to #4345` until the original report is reproduced or otherwise convincingly matched; use a closing reference only when the evidence supports resolving it. Do not publish a speculative root cause as a completed fix.

If only an older image fails, the useful deliverable is an evidence-backed issue response naming the tested working release/commit, a minimal current-version reproduction and upgrade instructions. If direct HTTP is the temporary workaround, use the existing documented `/mcp/` configuration with the correct client-ID/auth headers. Do not suggest the privileged direct stdio server as an equivalent substitute.

## 10. Evidence index

Repository source links below are pinned to the investigation SHA. Issue and PR pages are live; recheck their current state before implementation. SDK links intentionally target `v1.30.0`, not the SDK's current default branch.

- [Issue #4345][issue], [issue timeline][issue-timeline], [open pull requests][open-prs].
- [Pinned source baseline][baseline], [latest stable reviewed][stable].
- [Shim][shim], [MCP server][server], [MCP user documentation][mcp-docs].
- [Project manifest][pyproject], [package manifest][package], [dependency lock][lock].
- [Client setup tests][client-tests], [transport identity tests][identity-tests], [delegation tests][delegation-tests], [URL/credential tests][url-tests].
- [SDK session manager][sdk-manager], [SDK HTTP transport][sdk-transport], [SDK HTTP client][sdk-client], [SDK release notes][sdk-release].
- [Handshake-era Streamable HTTP specification][protocol]. Its initialization/session/header contract is relevant to the pinned v1 SDK; this plan does not propose a newer protocol migration.

[issue]: https://github.com/debpalash/VoiceStudio/issues/4345
[issue-timeline]: https://api.github.com/repos/debpalash/VoiceStudio/issues/4345/timeline
[open-prs]: https://github.com/debpalash/VoiceStudio/pulls
[baseline]: https://github.com/debpalash/VoiceStudio/commit/2bb21302241793977055c44f7c52815bcbf0261e
[stable]: https://github.com/debpalash/VoiceStudio/releases/tag/v0.5.8
[shim]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/mcp_shim/__main__.py
[server]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/backend/mcp_server.py
[mcp-docs]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/docs/mcp.md
[pyproject]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/pyproject.toml
[package]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/package.json
[lock]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/uv.lock
[agents]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/AGENTS.md
[contributing]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/.github/CONTRIBUTING.md
[ci]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/.github/workflows/ci.yml
[fragments]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/changelog.d/README.md
[client-tests]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_mcp_client_setup.py
[identity-tests]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_mcp_transport_identity.py
[delegation-tests]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_mcp_delegated_tier.py
[url-tests]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_backend_self_url.py
[error-tests]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_mcp_backend_error_detail.py
[startup-tests]: https://github.com/debpalash/VoiceStudio/blob/2bb21302241793977055c44f7c52815bcbf0261e/tests/test_mcp_startup_timeout.py
[pr2289]: https://github.com/debpalash/VoiceStudio/pull/2289
[pr4128]: https://github.com/debpalash/VoiceStudio/pull/4128
[delegated-guards]: https://github.com/debpalash/VoiceStudio/commit/d07129e159a9df4f9fa9fff41f1b4960292e9c11
[delegated-admin]: https://github.com/debpalash/VoiceStudio/commit/0d22076a90b2a5f66fb5381593777c4fef546456
[sdk-manager]: https://github.com/modelcontextprotocol/python-sdk/blob/v1.30.0/src/mcp/server/streamable_http_manager.py
[sdk-transport]: https://github.com/modelcontextprotocol/python-sdk/blob/v1.30.0/src/mcp/server/streamable_http.py
[sdk-client]: https://github.com/modelcontextprotocol/python-sdk/blob/v1.30.0/src/mcp/client/streamable_http.py
[sdk-release]: https://github.com/modelcontextprotocol/python-sdk/releases/tag/v1.30.0
[protocol]: https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
