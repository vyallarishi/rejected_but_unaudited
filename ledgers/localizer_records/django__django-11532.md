# Instance: `django__django-11532`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
Email messages crash on non-ASCII domain when email encoding is non-unicode.
Description
	
When the computer hostname is set in unicode (in my case "正宗"), the following test fails: ​https://github.com/django/django/blob/master/tests/mail/tests.py#L368
Specifically, since the encoding is set to iso-8859-1, Python attempts to convert all of the headers to that encoding, including the Message-ID header which has been set here: ​https://github.com/django/django/blob/master/django/core/mail/message.py#L260
This is not just a problem in the tests, Django should be handling the encoding of the message properly
Steps to recreate:
Set hostname to non iso-8859-1 value (i.e. hostname 正宗)
run the mail tests
Fix:
have django.core.mail.utils or django.core.mail.message convert domain name to punycode before using
Test:
from unittest.mock import patch
from django.core.mail import EmailMessage
with patch("django.core.mailmessage.DNS_NAME", "漢字"):
	email = EmailMessage('subject', '', 'from@example.com', ['to@example.com'])
	email.encoding = 'iso-8859-1'
	message = email.message()
	self.assertIn('xn--p8s937b', message['Message-ID'])
Traceback:
Traceback (most recent call last):
 File "/Users/chason/
```

## Stage 3 — Symptoms extracted

- exception types: `['UnicodeEncodeError']`
- error messages: `["'ascii' codec can't encode characters in position 39-40: ordinal not in range(128)", "'latin-1' codec can't encode characters in position 39-40: ordinal not in range(256)"]`
- behaviors: `['email messages crash', 'encoding issues with non-ASCII domain names', 'failure to convert domain name to punycode']`
- named APIs: `['EmailMessage.message', 'Header.encode']`
- stack frames: `[{'file': '/Users/chason/projects/django/django/core/mail/message.py', 'func': 'forbid_multi_line_headers', 'line': 62}, {'file': '/Users/chason/projects/django/tests/mail/tests.py', 'func': 'test_unicode_dns', 'line': 373}, {'file': '/Users/chason/projects/django/django/core/mail/message.py', 'func': 'message', 'line': 260}, {'file': '/Users/chason/projects/django/django/core/mail/message.py', 'func': '__setitem__', 'line': 157}, {'file': '/Users/chason/projects/django/django/core/mail/message.py', 'func': 'forbid_multi_line_headers', 'line': 67}, {'file': '/usr/local/Cellar/python/3.7.3/Frameworks/Python.framework/Versions/3.7/lib/python3.7/email/header.py', 'func': '__init__', 'line': 217}, {'file': '/usr/local/Cellar/python/3.7.3/Frameworks/Python.framework/Versions/3.7/lib/python3.7/email/header.py', 'func': 'append', 'line': 301}]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/core/mail/message.py` | This file is directly mentioned in the issue description as the location where the Message-ID header is set and where encoding problems occur. |
| 2 | `django/core/mail/utils.py` | The issue suggests converting the domain name to punycode in this file, indicating it's involved in email address handling. |
| 3 | `django/utils/encoding.py` | Deals with encoding and decoding strings, which is relevant to the non-ASCII domain issue. |
| 4 | `django/core/mail/backends/smtp.py` | Handles sending emails via SMTP, so it's likely involved in the encoding process. |
| 5 | `django/tests/mail/tests.py` | This test file is explicitly mentioned in the issue description and contains the failing test case. |
| 6 | `django/core/handlers/wsgi.py` | WSGI handler might be involved in setting the hostname, which is causing the issue. |
| 7 | `django/core/handlers/asgi.py` | ASGI handler might be involved in setting the hostname, which is causing the issue. |
| 8 | `django/conf/settings.py` | Settings might be relevant if there are encoding-related settings that need to be adjusted. |
| 9 | `django/conf/__init__.py` | Settings loading and configuration might be relevant to encoding settings. |
| 10 | `django/utils/idna.py` | May be useful for punycode conversion. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/core/mail/message.py::EmailMessage.message`

- **Q1 Role.** This method assembles a Python `email.message.Message` object from a Django `EmailMessage` instance, setting various headers like Subject, From, To, Date, and Message-ID.
- **Q2 Connection to symptom.** Yes, this function is directly on the causal path. It calls `make_msgid(domain=DNS_NAME)` with a non-ASCII `DNS_NAME`. The resulting string, containing the non-ASCII domain, is then assigned to the 'Message-ID' header (`msg['Message-ID'] = ...`). This assignment triggers underlying validation code (`forbid_multi_line_headers`) which attempts to encode the non-ASCII string using an incompatible encoding (first 'ascii', then the message's encoding like 'iso-8859-1'), leading to the `UnicodeEncodeError`.
- **Q3 Counterfactual.** `yes` — If this function were modified to punycode-encode the `DNS_NAME` before passing it to `make_msgid`, the resulting Message-ID string would be ASCII-compatible, and the subsequent encoding attempts would succeed.
- **Q4 Alternatives considered.**
  - `django.core.mail.message.make_msgid` — This is a strong alternative; the fix could be applied inside `make_msgid` to make it robust against non-ASCII domains.
  - `django.core.mail.message.forbid_multi_line_headers` — This is where the error is raised, but it's just enforcing a rule. Fixing it here would be a patch, not a root cause fix.
  - `django.core.mail.utils.get_fqdn` — The source of `DNS_NAME`. Fixing it here would have global effects that might be undesirable.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function initiates the creation of the problematic Message-ID header with an unencoded non-ASCII domain, directly causing the error.

#### ✗ REJECTED — `tests/forms_tests/field_tests/test_datefield.py::DateFieldTest.test_datefield_strptime`

- **Q1 Role.** This is a unit test function that verifies that a Django form `DateField`'s `strptime` method correctly handles non-ASCII date strings.
- **Q2 Connection to symptom.** No path exists. This function tests date parsing in Django's forms library, which is completely separate from the email sending functionality where the bug occurs. Its only relation is the historical mention of a `UnicodeEncodeError` in a comment, which is coincidental.
- **Q3 Counterfactual.** `no` — Modifying this test function would have no effect on the behavior of the email backend, as they are unrelated components.
- **Q4 Alternatives considered.**
  - `django/core/mail/message.py::EmailMessage.message` — This is the function directly implicated by the stack trace and bug description.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a test for an unrelated feature (form field date parsing) and has no causal connection to the email encoding bug.

#### ✗ REJECTED — `django/core/mail/message.py::EmailMessage._set_list_header_if_not_empty`

- **Q1 Role.** This is a helper method used to set a message header (like 'To' or 'Cc') from a list of values, joining them into a single string.
- **Q2 Connection to symptom.** No path exists. This function is used for setting headers like 'To' and 'Cc'. The stack trace clearly shows the error occurs when setting the 'Message-ID' header, a code path that does not involve this helper function.
- **Q3 Counterfactual.** `no` — Since this function is not called when setting the 'Message-ID' header, modifying it would not prevent the `UnicodeEncodeError`.
- **Q4 Alternatives considered.**
  - `django/core/mail/message.py::EmailMessage.message` — The calling function, which contains the logic for setting the 'Message-ID' header, is the correct place to investigate.
  - `django/core/mail/message.py::make_msgid` — This function is directly involved in creating the problematic header value, unlike `_set_list_header_if_not_empty`.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This helper function is not on the execution path that sets the 'Message-ID' header and triggers the error.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/core/mail/message.py::EmailMessage.message` | high | This function initiates the creation of the problematic Message-ID header with an unencoded non-ASCII domain, directly causing the error. | Punycode-encode the `DNS_NAME` variable before passing it as the domain to `make_msgid`. For example: `DNS_NAME.encode('idna').decode('ascii')`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `tests/forms_tests/field_tests/test_datefield.py::DateFieldTest.test_datefield_strptime` | high | This is a test for an unrelated feature (form field date parsing) and has no causal connection to the email encoding bug. |  |
| `django/core/mail/message.py::EmailMessage._set_list_header_if_not_empty` | high | This helper function is not on the execution path that sets the 'Message-ID' header and triggers the error. |  |

**Causal chains (per candidate)**

- `django/core/mail/message.py::EmailMessage.message`  (score=10.0)  \
  The method is called to prepare an email for sending. → It determines that a 'Message-ID' header needs to be generated. → It retrieves the system hostname via the `DNS_NAME` constant, which is a non-ASCII string (e.g., '正宗'). → It calls `make_msgid(domain=DNS_NAME)`, which creates a header value string containing the raw non-ASCII domain (e.g., '<random@正宗>'). → The assignment `msg['Message-ID'] = ...` triggers header validation. → The validation code attempts to encode the non-ASCII string using an incompatible, 7-bit or 8-bit encoding (ascii or latin-1).
- `tests/forms_tests/field_tests/test_datefield.py::DateFieldTest.test_datefield_strptime`  (score=0.0)  \
  
- `django/core/mail/message.py::EmailMessage._set_list_header_if_not_empty`  (score=0.0)  \
  

**next_to_explore:** `['django.core.mail.message.make_msgid', 'django.core.mail.message.forbid_multi_line_headers', 'django.core.mail.utils.get_fqdn']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 2, rejected: 1

**Per-candidate deliberation traces**

#### … CONSIDERING — `django/core/mail/message.py::forbid_multi_line_headers`

- **Q1 Role.** This function validates and sanitizes a given email header value to prevent header injection and ensures it is properly encoded for transport.
- **Q2 Connection to symptom.** Yes, this function directly produces the symptom. It is called with the `Message-ID` header value containing a non-ASCII domain. Its first attempt to encode the value to 'ascii' fails, raising the first `UnicodeEncodeError`. In the `except` block, it then tries to use `email.header.Header` with the specified message encoding ('iso-8859-1'), which also fails to encode the non-ASCII characters, raising the second `UnicodeEncodeError` seen in the traceback.
- **Q3 Counterfactual.** `yes` — Modifying this function to specifically handle the `Message-ID` header by Punycode-encoding its domain part before passing it to `email.header.Header` would prevent the crash. However, this may be considered a patch, as the root cause is the unprepared data it receives from its caller.
- **Q4 Alternatives considered.**
  - `django.core.mail.message.make_msgid` — Preferred, as it's responsible for creating the Message-ID value and is the most logical place to ensure it's correctly formatted (i.e., Punycode-encoded).
  - `django.core.mail.utils.CachedDnsName.get_fqdn` — A possible fix location, but modifying the source of the domain name might have unintended side effects if other code expects the raw Unicode hostname.
  - `django.core.mail.message.EmailMessage.message` — Also a strong candidate, as it orchestrates the creation of the Message-ID; the fix could be applied here before calling `make_msgid`.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function is where the encoding fails and the exception is raised, but the root cause is likely upstream where the non-ASCII header value is generated.

#### … CONSIDERING — `django/core/mail/utils.py::CachedDnsName.get_fqdn`

- **Q1 Role.** This function retrieves and caches the machine's fully qualified domain name (FQDN) using the standard library's `socket.getfqdn()`.
- **Q2 Connection to symptom.** Yes, this function is the original source of the problematic data. It calls `socket.getfqdn()`, which returns a non-ASCII hostname ('正宗'). This value is then passed up the call chain and used to construct the `Message-ID` header, eventually causing the `UnicodeEncodeError` during encoding.
- **Q3 Counterfactual.** `yes` — If this function were modified to always return a Punycode-encoded (IDNA) version of the FQDN, the downstream code would receive an ASCII-compatible string, and the error would be prevented.
- **Q4 Alternatives considered.**
  - `django.core.mail.message.make_msgid` — Preferred, as it localizes the Punycode logic to where it's specifically needed for an email header, avoiding broad changes to how the FQDN is represented system-wide in Django.
  - `forbid_multi_line_headers` — Not preferred; fixing it here would be a patch for a problem created by the data this function provides.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function supplies the raw non-ASCII data that causes the crash, but modifying it to always return Punycode may be too broad and have unintended side effects.

#### ✗ REJECTED — `django/core/mail/message.py::EmailMessage.__init__`

- **Q1 Role.** This function is the constructor for the `EmailMessage` class, initializing its properties such as recipients, subject, and body.
- **Q2 Connection to symptom.** No path. The traceback clearly shows the error occurs when the `email.message()` method is called, which happens after the object has been successfully initialized. This function does not access the machine's hostname or perform any encoding that could lead to the observed `UnicodeEncodeError`.
- **Q3 Counterfactual.** `no` — The error occurs during message serialization, not object initialization. Modifying this constructor would have no effect on the logic within the `message()` method that generates the `Message-ID`.
- **Q4 Alternatives considered.**
  - `django.core.mail.message.EmailMessage.message` — This is where the error is triggered, making it a directly relevant function to investigate.
  - `django.core.mail.message.make_msgid` — This function is called by `message()` and is responsible for creating the problematic header value.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is not on the execution path that leads to the symptom; it completes successfully before the error-producing code is ever called.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/core/mail/message.py::forbid_multi_line_headers` | high | This function is where the encoding fails and the exception is raised, but the root cause is likely upstream where the non-ASCII header value is generated. | Before encoding, check if the header is 'message-id' and, if so, punycode-encode the domain part of the value. |
| `django/core/mail/utils.py::CachedDnsName.get_fqdn` | medium | This function supplies the raw non-ASCII data that causes the crash, but modifying it to always return Punycode may be too broad and have unintended side effects. | Encode the result of socket.getfqdn() to IDNA before caching and returning it, e.g., `self._fqdn = socket.getfqdn().encode('idna').decode('ascii')`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/core/mail/message.py::EmailMessage.__init__` | high | This function is not on the execution path that leads to the symptom; it completes successfully before the error-producing code is ever called. |  |

**Causal chains (per candidate)**

- `django/core/mail/message.py::forbid_multi_line_headers`  (score=8.0)  \
  EmailMessage.message() is called to serialize the email. → It calls make_msgid(domain=DNS_NAME) where DNS_NAME is a non-ASCII string like '正宗'. → The returned Message-ID string (e.g., '<...@正宗>') is assigned to the message object. → This assignment calls __setitem__, which in turn calls forbid_multi_line_headers. → Inside forbid_multi_line_headers, val.encode('ascii') is attempted on the string containing '正宗' and fails. → The except block is entered, and Header(val, 'iso-8859-1').encode() is called.
- `django/core/mail/utils.py::CachedDnsName.get_fqdn`  (score=9.0)  \
  CachedDnsName.get_fqdn() is called to get the system's hostname, which is cached as DNS_NAME. → It calls socket.getfqdn() and returns a non-ASCII string ('正宗'). → This DNS_NAME is used as the domain argument for make_msgid when EmailMessage.message() is called. → The resulting non-ASCII Message-ID string is passed to forbid_multi_line_headers. → forbid_multi_line_headers fails to encode the non-ASCII string, causing a UnicodeEncodeError.
- `django/core/mail/message.py::EmailMessage.__init__`  (score=0.0)  \
  An EmailMessage object is instantiated. → The __init__ method runs, setting properties like to, from_email, subject, etc. → The method completes successfully. → At a later time, the .message() method is called on the instance, which is an entirely separate execution path that leads to the error.

**next_to_explore:** `['django/core/mail/message.py::make_msgid', 'django/core/mail/message.py::EmailMessage.message', 'django/core/mail/message.py::EmailMessage.__setitem__', 'email/header.py::Header.encode']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/core/mail/message.py::EmailMessage.message` | 0.95 |
| 2 | `django/core/mail/message.py::forbid_multi_line_headers` | 0.6 |
| 3 | `django/core/mail/message.py::EmailMessage.__init__` | 0.1 |
| 4 | `django/core/mail/message.py::EmailMessage._create_message` | 0.05 |
| 5 | `django/core/mail/message.py::EmailMessage._set_list_header_if_not_empty` | 0.0 |
| 6 | `django/utils/encoding.py::DjangoUnicodeDecodeError.__str__` | 0.0 |
| 7 | `django/utils/encoding.py::repercent_broken_unicode` | 0.0 |
| 8 | `django/utils/encoding.py::DjangoUnicodeDecodeError.__init__` | 0.0 |
| 9 | `django/core/mail/message.py::EmailMessage._create_mime_attachment` | 0.0 |
| 10 | `tests/forms_tests/field_tests/test_datefield.py::DateFieldTest.test_datefield_strptime` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/core/mail/message.py::EmailMessage.message` | 0.950 | high | 1/1 | (239, 264) |
| 2 | `django/core/mail/message.py::forbid_multi_line_headers` | 0.600 | high | 1/1 | (55, 71) |
| 3 | `django/core/mail/message.py::EmailMessage.attach_file` | 0.239 | high | 1/1 | (313, 327) |
| 4 | `django/core/mail/backends/smtp.py::EmailBackend.open` | 0.181 | high | 1/1 | (41, 73) |
| 5 | `django/core/mail/backends/smtp.py::EmailBackend.close` | 0.155 | high | 1/1 | (75, 92) |
| 6 | `django/core/mail/utils.py::CachedDnsName.get_fqdn` | 0.132 | high | 1/1 | (14, 17) |
| 7 | `django/core/mail/backends/smtp.py::EmailBackend.send_messages` | 0.130 | high | 1/1 | (94, 114) |
| 8 | `django/core/mail/message.py::EmailMessage.__init__` | 0.100 | high | 1/1 | (189, 231) |
| 9 | `django/core/mail/message.py::EmailMessage._create_message` | 0.050 | high | 1/1 | (329, 330) |
| 10 | `django/core/mail/message.py::EmailMessage._set_list_header_if_not_empty` | 0.000 | high | 1/1 | (390, 400) |
