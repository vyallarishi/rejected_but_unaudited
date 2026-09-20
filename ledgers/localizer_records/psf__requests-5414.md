# Instance: `psf__requests-5414`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
Getting http://.example.com raises UnicodeError
Attempting to get e.g. `http://.example.com` results in a `UnicodeError`. It seems like the intention so far has been to raise `InvalidUrl` instead (see e.g. [this line](https://github.com/psf/requests/blob/ca6f9af5dba09591007b15a7368bc0f006b7cc50/requests/models.py#L401)).

I see there was some hesitation in fixing a similar issue (#4168) and would like to add that even catching the error just to rethrow as a requests exception would be beneficial.

## Expected Result

Based on PR #774: `InvalidUrl: URL has an invalid label.`

## Actual Result

`UnicodeError: encoding with 'idna' codec failed (UnicodeError: label empty or too long)`

## Reproduction Steps

```python3
import requests
requests.get("http://.example.com")
```

## System Information

    $ python -m requests.help

```
{
  "chardet": {
    "version": "3.0.4"
  },
  "cryptography": {
    "version": "2.8"
  },
  "idna": {
    "version": "2.8"
  },
  "implementation": {
    "name": "CPython",
    "version": "3.8.0"
  },
  "platform": {
    "release": "5.3.0-40-generic",
    "system": "Linux"
  },
  "pyOpenSSL": {
    "openssl_version
```

## Stage 3 — Symptoms extracted

- exception types: `['UnicodeError']`
- error messages: `["encoding with 'idna' codec failed (UnicodeError: label empty or too long)"]`
- behaviors: `['raising UnicodeError', 'invalid URL handling']`
- named APIs: `['requests.get']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `requests/models.py` | Handles URL preparation and likely where the UnicodeError is raised during IDNA encoding. |
| 2 | `requests/api.py` | Provides the high-level API (e.g., requests.get) that triggers the URL processing. |
| 3 | `requests/sessions.py` | Manages request sessions and prepares requests, potentially interacting with URL handling. |
| 4 | `requests/adapters.py` | Handles the actual sending of requests and may perform some URL processing. |
| 5 | `requests/utils.py` | Contains utility functions for URL manipulation and encoding. |
| 6 | `requests/exceptions.py` | Defines the InvalidUrl exception that should be raised instead of UnicodeError. |
| 7 | `tests/test_requests.py` | Contains tests related to URL handling and error conditions, needs to be updated to reflect the fix. |
| 8 | `requests/__init__.py` | Top level module, might need changes related to exception imports. |
| 9 | `requests/compat.py` | Deals with compatibility across Python versions, potentially affecting string encoding. |
| 10 | `tests/utils.py` | Contains utility functions for tests, including URL-related functions. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `tests/test_requests.py::TestRequests.test_https_warnings`

- **Q1 Role.** This function is a test case that verifies that appropriate warnings are emitted when making an HTTPS request to a server with a certificate that doesn't have a Subject Alternative Name (SAN).
- **Q2 Connection to symptom.** No plausible path. This is a test function that calls `requests.get` with a different URL (`https://localhost:{}/`) for a different purpose (checking warnings). It is not part of the execution path for the failing code snippet provided in the bug report.
- **Q3 Counterfactual.** `no` — Modifying this test function will not change the behavior of `requests.get` in the main library code, as it is test code, not production code.
- **Q4 Alternatives considered.**
  - `requests.get` — The entry point for the user's code, which is definitely on the causal path.
  - `requests.adapters.HTTPAdapter.get_connection` — A function deeper in the call stack that handles connection pooling and is a more likely source of the error.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a test function for an unrelated feature and is not on the execution path of the bug.

#### ✗ REJECTED — `requests/adapters.py::HTTPAdapter.build_response`

- **Q1 Role.** This function constructs a `requests.Response` object from a lower-level `urllib3` response object after a request has been successfully completed.
- **Q2 Connection to symptom.** No plausible path. This function is only called after a successful HTTP response is received from the server. The `UnicodeError` occurs during the connection setup phase, long before any response is available, so this function is never reached.
- **Q3 Counterfactual.** `no` — The error occurs before this function is ever called, so modifying it cannot prevent the error.
- **Q4 Alternatives considered.**
  - `requests.adapters.HTTPAdapter.send` — This function orchestrates the request sending and is called before `build_response`, making it a more likely place to find the cause.
  - `requests.adapters.HTTPAdapter.get_connection` — This function is called by `send` to get a connection and is where the URL is passed to `urllib3`, making it a prime suspect.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is executed after a successful request, but the bug occurs before the request can be sent.

#### ✓ LEADING — `requests/adapters.py::HTTPAdapter.get_connection`

- **Q1 Role.** This function retrieves a `urllib3` connection pool for a given URL, handling proxies if necessary.
- **Q2 Connection to symptom.** Yes, a plausible path exists. This function calls `self.poolmanager.connection_from_url(url)`. The underlying `urllib3` code attempts to IDNA-encode the hostname `.example.com`. The leading dot creates an empty label, which causes the `idna` library to raise a `UnicodeError`. This exception is not caught within `get_connection` and propagates up to the user.
- **Q3 Counterfactual.** `yes` — Wrapping the call to `self.poolmanager.connection_from_url` in a try/except block to catch `UnicodeError` and raise a `requests.exceptions.InvalidURL` would fix the symptom.
- **Q4 Alternatives considered.**
  - `requests.models.PreparedRequest.prepare_url` — This is an alternative location for the fix; validating the URL earlier during preparation might be a cleaner design.
  - `requests.adapters.HTTPAdapter.send` — The fix could be in the caller, but placing it here is more specific as it's closer to the source of the external call that fails.
  - `urllib3.poolmanager.PoolManager.connection_from_url` — The error originates here, but `requests` policy is to wrap underlying exceptions, so the fix belongs in `requests`.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function makes the direct call to `urllib3` that raises the uncaught `UnicodeError`, and modifying it is the most direct way to fix the issue.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `requests/adapters.py::HTTPAdapter.get_connection` | high | This function makes the direct call to `urllib3` that raises the uncaught `UnicodeError`, and modifying it is the most direct way to fix the issue. | Wrap the call to `self.poolmanager.connection_from_url(url)` in a try/except block to catch `UnicodeError` and raise `requests.exceptions.InvalidURL` instead. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `tests/test_requests.py::TestRequests.test_https_warnings` | high | This is a test function for an unrelated feature and is not on the execution path of the bug. |  |
| `requests/adapters.py::HTTPAdapter.build_response` | high | This function is executed after a successful request, but the bug occurs before the request can be sent. |  |

**Causal chains (per candidate)**

- `tests/test_requests.py::TestRequests.test_https_warnings`  (score=0.0)  \
  
- `requests/adapters.py::HTTPAdapter.build_response`  (score=0.0)  \
  
- `requests/adapters.py::HTTPAdapter.get_connection`  (score=9.0)  \
  requests.get('http://.example.com') → requests.Session.send(PreparedRequest(url='http://.example.com')) → requests.adapters.HTTPAdapter.send(PreparedRequest(url='http://.example.com')) → requests.adapters.HTTPAdapter.get_connection(url='http://.example.com') → urllib3.PoolManager.connection_from_url(url='http://.example.com') → urllib3's internal hostname processing calls idna.encode('.example.com')

**next_to_explore:** `['urllib3.poolmanager.PoolManager.connection_from_url', 'requests.adapters.HTTPAdapter.send', 'requests.models.PreparedRequest.prepare_url', 'requests.sessions.Session.send', 'urllib3.util.url.parse_url']`

### Abductive step #2 (iteration=6)

- leading: 1, considering: 1, rejected: 1

**Per-candidate deliberation traces**

#### ✓ LEADING — `requests/models.py::PreparedRequest.prepare_url`

- **Q1 Role.** This function takes a URL string and parameters, parses them, validates them, and prepares the final URL for the request, including IDNA encoding for hostnames.
- **Q2 Connection to symptom.** Yes, a path exists. 1. `prepare_url` is called with `url="http://.example.com"`. 2. `parse_url` extracts `host=".example.com"`. 3. The host is ASCII, so the `if not unicode_is_ascii(host):` block, which contains the `try...except UnicodeError` for IDNA encoding, is skipped. 4. The function completes, leaving the invalid hostname in the `PreparedRequest` object. 5. Later, `urllib3` attempts to use this hostname, calls the `idna` codec, which correctly identifies the empty label and raises the `UnicodeError` that is observed. The function's omission of validation for this case is the direct cause of the downstream error.
- **Q3 Counterfactual.** `yes` — If this function were modified to validate all hostnames for valid labels, not just non-ASCII ones, it could catch the `UnicodeError` from the IDNA codec and raise the expected `InvalidURL` exception, thus eliminating the symptom.
- **Q4 Alternatives considered.**
  - `requests.adapters.HTTPAdapter.send` — This is where the exception propagates from, and it could be caught here, but it's better to validate the URL earlier.
  - `urllib3.connectionpool.py::HTTPConnectionPool.urlopen` — This is likely where the `idna` encoding is called, but the responsibility for handling `requests`-specific exceptions lies within the `requests` library.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function is responsible for URL validation but omits checking ASCII hostnames for label validity, directly causing the downstream uncaught exception.

#### … CONSIDERING — `requests/adapters.py::HTTPAdapter.send`

- **Q1 Role.** This function takes a prepared request and sends it over the network using an appropriate connection from the connection pool, returning a response object.
- **Q2 Connection to symptom.** Yes. This function calls `self.get_connection(request.url, proxies)`. The `get_connection` method (or a function it calls within `urllib3`) will attempt to IDNA-encode the invalid hostname `.example.com`. This triggers the `UnicodeError`. Since `HTTPAdapter.send` does not have a `try...except UnicodeError` block, the exception propagates up the call stack to the user.
- **Q3 Counterfactual.** `partially` — A `try...except UnicodeError` block could be added here to wrap the `get_connection` call and re-raise an `InvalidURL`. This would fix the symptom, but the validation is conceptually better placed in `prepare_url`.
- **Q4 Alternatives considered.**
  - `requests.models.py::PreparedRequest.prepare_url` — Preferred, as it's the designated place for URL validation, which should happen before attempting to send a request.
  - `requests.adapters.py::HTTPAdapter.get_connection` — This is the direct caller of the failing code. A fix here is also possible but still downstream of the ideal validation step.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function is on the execution path and could be modified to fix the symptom, but it's not the root cause, which is a lack of earlier validation.

#### ✗ REJECTED — `requests/sessions.py::Session.send`

- **Q1 Role.** This function is the main entry point for sending a request within a session, handling hooks, redirects, and delegating the actual sending to an adapter.
- **Q2 Connection to symptom.** Yes, this function is on the call stack. It calls `adapter.send()`, which, as established, propagates a `UnicodeError`. `Session.send` does not catch this specific exception, so it continues up the stack to the user. Its role is purely that of a caller in the chain.
- **Q3 Counterfactual.** `no` — While one could technically add an exception handler here, it would be poor design. This function's role is high-level orchestration, not low-level error handling of URL specifics.
- **Q4 Alternatives considered.**
  - `requests.models.py::PreparedRequest.prepare_url` — This is the correct location for the fix, as it handles URL preparation and validation.
  - `requests.adapters.py::HTTPAdapter.send` — A more plausible, though still not ideal, location for a fix than `Session.send`.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is too high-level in the call stack; fixing the issue here would be architecturally incorrect as it's not responsible for URL validation.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `requests/models.py::PreparedRequest.prepare_url` | high | This function is responsible for URL validation but omits checking ASCII hostnames for label validity, directly causing the downstream uncaught exception. | Always attempt IDNA encoding on the host, even if it's ASCII, within the existing try/except block to catch invalid labels and raise InvalidURL. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `requests/adapters.py::HTTPAdapter.send` | high | This function is on the execution path and could be modified to fix the symptom, but it's not the root cause, which is a lack of earlier validation. | Wrap the call to `get_connection` in a `try...except UnicodeError` block to raise `InvalidURL`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `requests/sessions.py::Session.send` | high | This function is too high-level in the call stack; fixing the issue here would be architecturally incorrect as it's not responsible for URL validation. |  |

**Causal chains (per candidate)**

- `requests/models.py::PreparedRequest.prepare_url`  (score=9.0)  \
  requests.get() calls Session.request(), which calls PreparedRequest.prepare() → PreparedRequest.prepare() calls self.prepare_url() with 'http://.example.com' → prepare_url() parses the host as '.example.com' → The check for non-ASCII hosts is skipped because the host is ASCII → No validation is performed for empty labels in ASCII hosts → The PreparedRequest is returned with the invalid host
- `requests/adapters.py::HTTPAdapter.send`  (score=6.0)  \
  HTTPAdapter.send() is called with a PreparedRequest containing the invalid host '.example.com' → send() calls self.get_connection() → self.get_connection() (via urllib3) attempts to resolve the hostname → The idna codec is invoked, raising a UnicodeError → HTTPAdapter.send() does not catch the UnicodeError, so it propagates
- `requests/sessions.py::Session.send`  (score=2.0)  \
  Session.send() is called with a PreparedRequest → send() retrieves an adapter and calls adapter.send() → adapter.send() raises a UnicodeError → Session.send() does not catch the UnicodeError, so it propagates

**next_to_explore:** `['requests.models.py::PreparedRequest._get_idna_encoded_host', 'requests.adapters.py::HTTPAdapter.get_connection', 'urllib3.util.url::parse_url', 'urllib3.connectionpool.py::HTTPConnectionPool.urlopen']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `requests/models.py::PreparedRequest.prepare_url` | 0.9 |
| 2 | `requests/adapters.py::HTTPAdapter.send` | 0.7 |
| 3 | `requests/sessions.py::Session.send` | 0.5 |
| 4 | `requests/adapters.py::HTTPAdapter.get_connection` | 0.3 |
| 5 | `tests/test_requests.py::TestRequests.test_https_warnings` | 0.0 |
| 6 | `requests/adapters.py::HTTPAdapter.build_response` | 0.0 |
| 7 | `requests/models.py::Response.json` | 0.0 |
| 8 | `requests/utils.py::default_headers` | 0.0 |
| 9 | `requests/exceptions.py::RequestException.__init__` | 0.0 |
| 10 | `requests/models.py::Request.__repr__` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `requests/models.py::PreparedRequest.prepare_url` | 0.900 | high | 1/1 | (360, 444) |
| 2 | `requests/adapters.py::HTTPAdapter.send` | 0.700 | high | 1/1 | (395, 538) |
| 3 | `requests/sessions.py::Session.send` | 0.500 | high | 1/1 | (613, 689) |
| 4 | `requests/adapters.py::HTTPAdapter.get_connection` | 0.300 | high | 1/1 | (293, 318) |
| 5 | `requests/models.py::Response.raise_for_status` | 0.214 | high | 1/1 | (937, 960) |
| 6 | `requests/utils.py::select_proxy` | 0.201 | high | 1/1 | (810, 833) |
| 7 | `requests/utils.py::get_netrc_auth` | 0.194 | high | 1/1 | (178, 232) |
| 8 | `tests/test_requests.py::TestRequests.test_https_warnings` | 0.000 | high | 1/1 | (886, 905) |
| 9 | `requests/adapters.py::HTTPAdapter.build_response` | 0.000 | high | 1/1 | (256, 291) |
| 10 | `requests/models.py::Response.json` | 0.000 | high | 1/1 | (883, 917) |
