# Instance: `django__django-11848`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
django.utils.http.parse_http_date two digit year check is incorrect
Description
	 
		(last modified by Ad Timmering)
	 
RFC 850 does not mention this, but in RFC 7231 (and there's something similar in RFC 2822), there's the following quote:
Recipients of a timestamp value in rfc850-date format, which uses a
two-digit year, MUST interpret a timestamp that appears to be more
than 50 years in the future as representing the most recent year in
the past that had the same last two digits.
Current logic is hard coded to consider 0-69 to be in 2000-2069, and 70-99 to be 1970-1999, instead of comparing versus the current year.
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['incorrect date parsing', 'incorrect year interpretation']`
- named APIs: `['django.utils.http.parse_http_date']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/utils/http.py` | Implements the parse_http_date function which has the two digit year check. |
| 2 | `django/utils/tests/test_http.py` | Contains tests for django.utils.http, including parse_http_date. |
| 3 | `django/core/validators.py` | May contain date validation logic that could be related. |
| 4 | `django/forms/fields.py` | Date and time related form fields may use the function. |
| 5 | `django/utils/timezone.py` | Timezone handling may be relevant to date parsing. |
| 6 | `django/conf/settings.py` | Settings related to date formats might influence the parsing. |
| 7 | `django/utils/formats.py` | Date and time formatting utilities might be used in parsing. |
| 8 | `django/core/mail/message.py` | Email headers often contain dates, so this file might use the function. |
| 9 | `django/contrib/sitemaps/views.py` | Sitemaps may use date formats. |
| 10 | `django/contrib/syndication/views.py` | Syndication feeds often contain dates, so this file might use the function. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 1, rejected: 1

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/utils/http.py::parse_http_date`

- **Q1 Role.** Parses a date string from an HTTP header and returns the number of seconds since the epoch.
- **Q2 Connection to symptom.** Yes, this function contains the logic that directly produces the symptom. 
1. The function is called with a date string containing a two-digit year.
2. The `year` is extracted as an integer less than 100.
3. The code block `if year < 70: year += 2000 else: year += 1900` applies a fixed-window rule to determine the century.
4. This hardcoded logic is incorrect according to RFC 7231, which requires a sliding window based on the current time, thus producing an incorrect year and a wrong final timestamp.
- **Q3 Counterfactual.** `yes` — The incorrect hardcoded logic for handling two-digit years is entirely contained within this function. Replacing it with the correct sliding-window logic would fix the symptom.
- **Q4 Alternatives considered.**
  - `django/utils/http.py::parse_http_date_safe` — This is a wrapper; fixing it would be a patch, not a root cause fix, as direct calls to `parse_http_date` would remain buggy.
  - `RFC850_DATE regex` — The regex correctly extracts the two-digit year; the error is in the subsequent interpretation of that value.
- **Q5 Verdict.** `leading` (confidence: `high`) — The function contains the exact hardcoded logic (`if year < 70`) described in the bug report as the cause of the incorrect year interpretation.

#### ✗ REJECTED — `django/utils/http.py::http_date`

- **Q1 Role.** Formats a timestamp into an RFC 1123 compliant date string for use in HTTP headers.
- **Q2 Connection to symptom.** No path exists. This function formats dates for output, always with a four-digit year. The bug is about parsing and interpreting incoming dates with two-digit years.
- **Q3 Counterfactual.** `no` — This function is not involved in parsing dates, so modifying it would have no effect on the incorrect parsing behavior.
- **Q4 Alternatives considered.**
  - `django/utils/http.py::parse_http_date` — Preferred, as this function handles parsing and is the source of the error.
  - `email.utils.formatdate` — This is a callee for formatting, not parsing, so it's also irrelevant to the bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function formats dates for output, while the bug is about parsing input dates; it is not on the causal path.

#### … CONSIDERING — `django/utils/http.py::parse_http_date_safe`

- **Q1 Role.** Acts as a safe wrapper around `parse_http_date`, returning `None` on parsing failure instead of raising an exception.
- **Q2 Connection to symptom.** Yes, an execution path through this function produces the symptom. It calls `parse_http_date`, which performs the incorrect calculation, and then `parse_http_date_safe` returns the resulting incorrect value. It propagates the error.
- **Q3 Counterfactual.** `no` — The faulty logic resides in `parse_http_date`. While a fix could be hacked into this wrapper, the root cause would remain, and direct calls to `parse_http_date` would still be broken.
- **Q4 Alternatives considered.**
  - `django/utils/http.py::parse_http_date` — Preferred, as this is the callee containing the actual bug logic. Fixing it there corrects all callers, including this one.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function is a simple wrapper that propagates the incorrect result from `parse_http_date`, which contains the actual bug logic.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/utils/http.py::parse_http_date` | high | The function contains the exact hardcoded logic (`if year < 70`) described in the bug report as the cause of the incorrect year interpretation. | Replace the fixed `year < 70` check with logic that uses the current year to implement the 50-year sliding window from RFC 7231. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/utils/http.py::parse_http_date_safe` | high | This function is a simple wrapper that propagates the incorrect result from `parse_http_date`, which contains the actual bug logic. | No edit needed here; the fix should be in the callee `parse_http_date`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/utils/http.py::http_date` | high | This function formats dates for output, while the bug is about parsing input dates; it is not on the causal path. |  |

**Causal chains (per candidate)**

- `django/utils/http.py::parse_http_date`  (score=10.0)  \
  Function is called with a date string containing a two-digit year (e.g., RFC 850 format). → The `year` is extracted and converted to an integer. → The `if year < 70: year += 2000 else: year += 1900` logic is executed. → This hardcoded threshold incorrectly determines the century, violating the RFC 7231 requirement for a sliding window relative to the current time. → An incorrect epoch integer, based on the wrongly interpreted year, is returned.
- `django/utils/http.py::http_date`  (score=0.0)  \
  
- `django/utils/http.py::parse_http_date_safe`  (score=5.0)  \
  Function is called with a date string containing a two-digit year. → It calls `parse_http_date` with the same string. → `parse_http_date` returns an incorrect epoch timestamp due to its internal faulty logic. → `parse_http_date_safe` returns this incorrect value to its caller.

### Abductive step #2 (iteration=6)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/utils/http.py::urlunquote`

- **Q1 Role.** This function is a deprecated legacy compatibility wrapper for Python's `urllib.parse.unquote()` function, used for URL decoding.
- **Q2 Connection to symptom.** No path exists. The observed symptom is an incorrect interpretation of two-digit years when parsing HTTP date strings, which is a date/time parsing issue. This function deals with URL decoding, a completely separate concern, and would not be involved in processing a raw HTTP date header.
- **Q3 Counterfactual.** `no` — Modifying a URL decoding function would have no effect on the date parsing logic within `parse_http_date`, as the two operations are unrelated.
- **Q4 Alternatives considered.**
  - `django.utils.http.py::parse_http_date` — Preferred, as it is explicitly named in the bug report as the source of the incorrect behavior.
  - `django.utils.http.py::parse_http_date_safe` — Considered, as it is likely a wrapper around `parse_http_date` and part of the same API surface.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function performs URL decoding, which is unrelated to the logic for parsing two-digit years in HTTP dates.

#### ✗ REJECTED — `django/utils/http.py::urlquote_plus`

- **Q1 Role.** This function is a deprecated legacy compatibility wrapper for Python's `urllib.parse.quote_plus()` function, used for URL encoding.
- **Q2 Connection to symptom.** No path exists. The symptom relates to how `parse_http_date` interprets years in date strings. This function, which performs URL encoding (e.g., for query strings), is not involved in parsing HTTP headers like 'Date' or 'Last-Modified'.
- **Q3 Counterfactual.** `no` — The logic for handling two-digit years is contained within the date parsing function, so changing this unrelated URL encoding function would not fix the bug.
- **Q4 Alternatives considered.**
  - `django.utils.http.py::parse_http_date` — Preferred, as the bug description directly implicates its date parsing logic.
  - `time.strptime` — Considered as a potential underlying function, but the custom 50-year rule suggests Django-specific logic is the cause.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function performs URL encoding, which is irrelevant to the incorrect parsing of HTTP date strings.

#### ✗ REJECTED — `django/utils/http.py::urlquote`

- **Q1 Role.** This function is a deprecated legacy compatibility wrapper for Python's `urllib.parse.quote()` function, used for URL encoding.
- **Q2 Connection to symptom.** No path exists. The bug is in the interpretation of a date format, specifically the year. This function's purpose is to URL-encode strings, which is not a step in parsing a standard HTTP date header.
- **Q3 Counterfactual.** `no` — Fixing the bug requires changing the date parsing logic. Modifying this URL encoding utility will not affect how dates are processed.
- **Q4 Alternatives considered.**
  - `django.utils.http.py::parse_http_date` — Preferred, as it is the function identified in the issue description with the faulty logic.
  - `datetime.datetime.now` — Considered, as a correct implementation would need to compare the parsed year against the current year.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for URL encoding and has no connection to the date parsing logic described in the bug report.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/utils/http.py::urlunquote` | high | This function performs URL decoding, which is unrelated to the logic for parsing two-digit years in HTTP dates. |  |
| `django/utils/http.py::urlquote_plus` | high | This function performs URL encoding, which is irrelevant to the incorrect parsing of HTTP date strings. |  |
| `django/utils/http.py::urlquote` | high | This function is for URL encoding and has no connection to the date parsing logic described in the bug report. |  |

**Causal chains (per candidate)**

- `django/utils/http.py::urlunquote`  (score=0.0)  \
  No plausible causal chain exists.
- `django/utils/http.py::urlquote_plus`  (score=0.0)  \
  No plausible causal chain exists.
- `django/utils/http.py::urlquote`  (score=0.0)  \
  No plausible causal chain exists.

**next_to_explore:** `['django/utils/http.py::parse_http_date', 'django/utils/http.py::parse_http_date_safe']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/utils/http.py::parse_http_date` | 1.0 |
| 2 | `django/utils/http.py::parse_http_date_safe` | 0.8 |
| 3 | `django/utils/http.py::http_date` | 0.0 |
| 4 | `django/utils/http.py::urlquote_plus` | 0.0 |
| 5 | `django/utils/http.py::urlunquote` | 0.0 |
| 6 | `django/utils/http.py::urlquote` | 0.0 |
| 7 | `django/utils/http.py::urlunquote_plus` | 0.0 |
| 8 | `django/utils/http.py::urlencode` | 0.0 |
| 9 | `django/utils/http.py::_urlparse` | 0.0 |
| 10 | `django/forms/fields.py::DateField.to_python` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/utils/http.py::parse_http_date` | 1.000 | high | 1/1 | (158, 191) |
| 2 | `django/utils/http.py::parse_http_date_safe` | 0.800 | high | 1/1 | (194, 201) |
| 3 | `django/forms/fields.py::TimeField.to_python` | 0.239 | high | 1/1 | (421, 430) |
| 4 | `django/forms/fields.py::DateField.strptime` | 0.212 | high | 1/1 | (410, 411) |
| 5 | `django/core/validators.py::EmailValidator.validate_domain_part` | 0.202 | high | 1/1 | (211, 223) |
| 6 | `django/core/validators.py::validate_ipv46_address` | 0.170 | high | 1/1 | (264, 271) |
| 7 | `django/core/validators.py::validate_ipv6_address` | 0.152 | high | 1/1 | (259, 261) |
| 8 | `django/utils/http.py::http_date` | 0.000 | high | 1/1 | (144, 155) |
| 9 | `django/utils/http.py::urlquote_plus` | 0.000 | high | 1/1 | (62, 72) |
| 10 | `django/utils/http.py::urlunquote` | 0.000 | high | 1/1 | (76, 86) |
