# Instance: `django__django-15127`

- runs: 1   termination: `ledger_informed`   think-high calls: 4

## Issue (truncated to 1200 chars)

```
LEVEL_TAGS not updated when using @override_settings
Description
	
When reading messages inside tests, new message tags created using @override_settings is not updated.
That causes the django.contrib.messages.storage.base.Message.level_tag property results to be an empty string and not know the new tags.
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `['level_tag property results to be an empty string']`
- behaviors: `['message tags not updated', 'level tags not updated']`
- named APIs: `['django.contrib.messages.storage.base.Message.level_tag']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/contrib/messages/storage/base.py` | Contains the Message class and BaseStorage class, including the level_tag property. |
| 2 | `django/contrib/messages/api.py` | Contains the add_message function, which is used to add messages to the request. |
| 3 | `django/contrib/messages/context_processors.py` | Provides the messages context processor, which makes messages available in templates. |
| 4 | `django/contrib/messages/middleware.py` | Handles temporary messages by storing and retrieving them from the request. |
| 5 | `django/contrib/messages/utils.py` | Contains the get_level_tags function, which is used to return the message level tags. |
| 6 | `django/conf/__init__.py` | Deals with settings overriding, which is part of the issue description. |
| 7 | `django/test/testcases.py` | Likely place to add a test case for the described issue. |
| 8 | `django/test/utils.py` | Contains override_settings decorator, which is part of the issue description. |
| 9 | `django/utils/translation/__init__.py` | May be related to translation of message tags. |
| 10 | `django/utils/translation/trans_real.py` | May be related to translation of message tags. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/contrib/messages/utils.py::get_level_tags`

- **Q1 Role.** This function computes and returns a dictionary of message level tags by merging default tags with custom tags from Django settings.
- **Q2 Connection to symptom.** This function's return value is cached at the module level in `django.contrib.messages.storage.base.py`. When settings are changed during a test using `@override_settings`, this cached value becomes stale. An execution path is: 1. `get_level_tags()` is called at module import time. 2. The result is stored in a module-level variable `LEVEL_TAGS`. 3. A test overrides `MESSAGE_TAGS`. 4. `Message.level_tag` uses the stale `LEVEL_TAGS` variable, fails to find a new tag, and returns an empty string.
- **Q3 Counterfactual.** `no` — The function's logic is correct as it properly reads from the settings. The issue is that its caller caches the result at module load time, so modifying this function alone would not solve the stale data problem.
- **Q4 Alternatives considered.**
  - `django.contrib.messages.storage.base.py::Message.level_tag` — This is a better candidate because it's the function that uses the stale data, and modifying it to fetch fresh data would fix the symptom.
  - `Module-level code in django.contrib.messages.storage.base.py` — This is the true root cause, where `get_level_tags()` is called and its result cached. However, it is not a function that can be selected for modification.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function's implementation is correct; the bug stems from its result being cached indefinitely by the caller at module import time.

#### ✓ LEADING — `django/contrib/messages/storage/base.py::Message.level_tag`

- **Q1 Role.** This method returns the CSS class tag corresponding to the message's level (e.g., 'info', 'success').
- **Q2 Connection to symptom.** Yes, this function directly produces the symptom. 1. It is called on a `Message` instance whose level was added via `@override_settings`. 2. It looks up `self.level` in the module-level `LEVEL_TAGS` dictionary. 3. Because `LEVEL_TAGS` was populated at import time, it is stale and does not contain the new level. 4. The dictionary's `.get()` method returns the default value, `''`, which is the observed symptom.
- **Q3 Counterfactual.** `yes` — If this method were modified to call `utils.get_level_tags()` directly instead of using the stale `LEVEL_TAGS` variable, it would get the up-to-date tags and return the correct value.
- **Q4 Alternatives considered.**
  - `django.contrib.messages.utils.py::get_level_tags` — This function correctly generates the tags but is not responsible for how its output is cached.
  - `django.test.signals.setting_changed` — Connecting a signal handler to update `LEVEL_TAGS` would be a more complex, framework-level fix, while modifying this method is a direct, local solution.
  - `django.contrib.messages.storage.base.py::Message.tags` — This method is a consumer of `level_tag`'s output and is downstream of the bug.
- **Q5 Verdict.** `leading` (confidence: `high`) — This method directly causes the symptom by using a stale, module-level `LEVEL_TAGS` dictionary, and modifying it to fetch fresh data is a direct fix.

#### ✗ REJECTED — `django/contrib/messages/storage/base.py::Message.tags`

- **Q1 Role.** This method constructs a space-separated string of all tags for a message, combining the level tag and any extra tags.
- **Q2 Connection to symptom.** This function is a consumer of the buggy output from `self.level_tag`. When `self.level_tag` returns an empty string (the symptom), this function's list comprehension filters it out, resulting in a final tag string that is missing the expected level tag. It does not produce the empty string itself.
- **Q3 Counterfactual.** `no` — Modifying this function cannot fix the problem, as the root cause is that `self.level_tag` returns an empty string. This function is downstream of the error.
- **Q4 Alternatives considered.**
  - `django.contrib.messages.storage.base.py::Message.level_tag` — Preferred, as this is the direct source of the empty string that `tags` consumes.
  - `django.contrib.messages.utils.py::get_level_tags` — Not preferred, as this function is even further upstream and its own logic is correct.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a consumer of the buggy value from `level_tag` and is therefore downstream from the root cause.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/messages/storage/base.py::Message.level_tag` | high | This method directly causes the symptom by using a stale, module-level `LEVEL_TAGS` dictionary, and modifying it to fetch fresh data is a direct fix. | Replace the use of the module-level `LEVEL_TAGS` with a call to `utils.get_level_tags()` to ensure fresh settings are used. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/messages/utils.py::get_level_tags` | high | This function's implementation is correct; the bug stems from its result being cached indefinitely by the caller at module import time. |  |
| `django/contrib/messages/storage/base.py::Message.tags` | high | This function is a consumer of the buggy value from `level_tag` and is therefore downstream from the root cause. |  |

**Causal chains (per candidate)**

- `django/contrib/messages/utils.py::get_level_tags`  (score=4.0)  \
  The result of `get_level_tags()` is cached in a module-level variable `LEVEL_TAGS` in `storage/base.py` at import time. → A test uses `@override_settings` to modify `MESSAGE_TAGS`, making the cached `LEVEL_TAGS` stale. → `Message.level_tag` uses the stale `LEVEL_TAGS` to look up a message level. → The lookup fails, and `Message.level_tag` returns an empty string.
- `django/contrib/messages/storage/base.py::Message.level_tag`  (score=9.0)  \
  The `LEVEL_TAGS` module-level variable is defined at import time by calling `get_level_tags()`. → In a test, `@override_settings` changes the `MESSAGE_TAGS` setting, but `LEVEL_TAGS` is not updated. → The `level_tag` method is called for a message with a level corresponding to a new, overridden tag. → The method looks up the level in the stale `LEVEL_TAGS` dictionary. → The lookup fails, so the `.get()` call returns its default value, an empty string.
- `django/contrib/messages/storage/base.py::Message.tags`  (score=0.0)  \
  `Message.level_tag` returns an empty string due to using stale settings. → `Message.tags` calls `self.level_tag` and receives the empty string. → The empty string is filtered out by a list comprehension. → The final string returned by `tags` is missing the level tag.

**next_to_explore:** `['django.test.utils.override_settings', 'django.contrib.messages.apps.MessagesConfig::ready', 'django.contrib.messages.storage.base.Message.__init__', 'django.test.signals.setting_changed']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/contrib/messages/storage/base.py::Message.__init__`

- **Q1 Role.** It is the constructor for the `Message` class, initializing a message object with its level, content, and optional extra tags.
- **Q2 Connection to symptom.** No path exists. This function only assigns constructor arguments (`level`, `message`, `extra_tags`) to instance attributes. The symptom, an empty `level_tag`, arises from a failed lookup when the `level_tag` property is accessed later, which is unrelated to the object's initialization.
- **Q3 Counterfactual.** `no` — Modifying the constructor would not affect how the `level_tag` property later retrieves level tags from Django's settings, which is where the stale data issue lies.
- **Q4 Alternatives considered.**
  - `django.contrib.messages.utils.get_level_tags` — Preferred: This function is likely responsible for fetching and caching the level tags from settings.
  - `django.contrib.messages.storage.base.Message.level_tag` — Considered: This property directly produces the symptom, but likely by calling another utility function.
  - `django.contrib.messages.apps.MessagesConfig.ready` — Considered: This app initialization hook is a likely place to set up caching and signal handlers.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This constructor simply initializes a data object and is not involved in the settings-dependent logic that causes the bug.

#### ✗ REJECTED — `django/apps/config.py::AppConfig.ready`

- **Q1 Role.** It is a hook method that subclasses of `AppConfig` can override to execute code once the Django application registry is fully populated.
- **Q2 Connection to symptom.** No path exists. This base method is empty and contains no logic. The relevant logic would be in an overridden method in a subclass, such as `MessagesConfig.ready`, which is responsible for setting up the application's initial state.
- **Q3 Counterfactual.** `no` — Modifying this empty base method would have no effect on the system's behavior, as the relevant logic resides in its subclass's implementation.
- **Q4 Alternatives considered.**
  - `django.contrib.messages.apps.MessagesConfig.ready` — Preferred: This is the concrete implementation for the 'messages' app and likely contains the relevant initialization logic.
  - `django.contrib.messages.utils.update_level_tags` — Considered: This is the signal handler that should clear the cache, and it might be faulty.
  - `django.test.utils.override_settings` — Considered: This decorator is the trigger for the entire process; its interaction with signals is critical.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is an empty base method intended for subclassing; it contains no logic and therefore cannot be the source of the bug.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/messages/storage/base.py::Message.__init__` | high | This constructor simply initializes a data object and is not involved in the settings-dependent logic that causes the bug. |  |
| `django/apps/config.py::AppConfig.ready` | high | This is an empty base method intended for subclassing; it contains no logic and therefore cannot be the source of the bug. |  |

**Causal chains (per candidate)**

- `django/contrib/messages/storage/base.py::Message.__init__`  (score=0.0)  \
  
- `django/apps/config.py::AppConfig.ready`  (score=0.0)  \
  

**next_to_explore:** `['django.contrib.messages.apps.MessagesConfig.ready', 'django.contrib.messages.utils.update_level_tags', 'django.test.utils.override_settings', 'django.dispatch.dispatcher.Signal.connect']`

### Abductive step #3 (iteration=9)

- leading: 0, considering: 0, rejected: 0

### Abductive step #4 (iteration=12)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/contrib/messages/storage/base.py::BaseStorage._loaded_messages`

- **Q1 Role.** This function lazily retrieves and returns a list of stored messages, caching them in `self._loaded_data` to avoid repeated retrieval.
- **Q2 Connection to symptom.** Yes, a path exists. If messages are loaded and cached in `_loaded_data` by this function, and then settings are changed with `@override_settings`, subsequent accesses to the messages might occur without re-triggering message loading. When a property like `level_tag` is accessed on these pre-loaded `Message` objects, it calls `get_level_tags()`. If the cache for `get_level_tags()` was not properly invalidated by `@override_settings`, it would return stale tag information, leading to the observed symptom. This function's own cache (`_loaded_data`) could contribute to the problem's manifestation, but it is not the root cause.
- **Q3 Counterfactual.** `no` — Modifying this function to not use its cache would only force `_get()` to be called more often. The root cause appears to be a failure to invalidate the `@lru_cache` on `get_level_tags()`, which is external to this function.
- **Q4 Alternatives considered.**
  - `django.contrib.messages.utils.get_level_tags` — Preferred, as its `@lru_cache` is the direct source of the stale data.
  - `django.test.utils.override_settings.enable` — Preferred, as it is responsible for clearing settings-dependent caches like the one on `get_level_tags`.
  - `django.contrib.messages.storage.base.BaseStorage._get` — Not preferred, as this function retrieves raw data; the creation of `Message` objects and subsequent access to their properties is where the stale data is used.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function's cache is on the storage instance and is a red herring; the true issue lies with the module-level `@lru_cache` on `get_level_tags()` not being invalidated.

#### ✗ REJECTED — `django/contrib/messages/storage/base.py::BaseStorage._set_level`

- **Q1 Role.** This function sets a custom minimum message level for the storage instance, overriding the default level defined in settings.
- **Q2 Connection to symptom.** No path exists. This function controls the minimum message level to be stored (related to the `MESSAGE_LEVEL` setting), not the tags associated with those levels (`MESSAGE_TAGS`). The symptom is an incorrect `level_tag`, which is derived from `MESSAGE_TAGS`, a setting this function does not interact with.
- **Q3 Counterfactual.** `no` — The function is unrelated to message tags. Modifying it would have no effect on the `level_tag` property's logic or the `MESSAGE_TAGS` setting.
- **Q4 Alternatives considered.**
  - `django.contrib.messages.utils.get_level_tags` — This is the likely area of the bug, as it computes tags from settings.
  - `django.contrib.messages.storage.base.Message.level_tag` — This property uses the tags, but the problem is the data it receives, not its own logic.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function deals with the message recording level, which is entirely separate from the message tags that are causing the symptom.

#### ✗ REJECTED — `django/test/utils.py::override_settings.save_options`

- **Q1 Role.** This function saves the settings to be overridden onto the decorated test function, merging them with any settings from parent classes' decorators.
- **Q2 Connection to symptom.** No direct path exists. This function runs during test collection/setup to attach configuration to a test function object. It does not apply settings or clear caches. The symptom arises from a failure to clear a cache when the settings are actually applied at runtime, which is handled by other methods of the `override_settings` class (e.g., `enable`). Therefore, this function is part of the overall mechanism but is not where the failure occurs.
- **Q3 Counterfactual.** `no` — This function only prepares the configuration for the decorator. The failure is in the application of that configuration, which happens in `override_settings.enable`.
- **Q4 Alternatives considered.**
  - `django.test.utils.override_settings.enable` — Preferred, as this method is directly responsible for applying settings and triggering cache clearing.
  - `django.contrib.messages.apps.MessagesConfig.ready` — Also a strong candidate; if the signal handler that clears the cache isn't connected, `enable`'s signal would have no effect.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function only saves settings options to the test function; it doesn't apply them or clear caches, so it cannot be the source of the bug.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/messages/storage/base.py::BaseStorage._loaded_messages` | high | This function's cache is on the storage instance and is a red herring; the true issue lies with the module-level `@lru_cache` on `get_level_tags()` not being invalidated. |  |
| `django/contrib/messages/storage/base.py::BaseStorage._set_level` | high | This function deals with the message recording level, which is entirely separate from the message tags that are causing the symptom. |  |
| `django/test/utils.py::override_settings.save_options` | high | This function only saves settings options to the test function; it doesn't apply them or clear caches, so it cannot be the source of the bug. |  |

**Causal chains (per candidate)**

- `django/contrib/messages/storage/base.py::BaseStorage._loaded_messages`  (score=3.0)  \
  A test calls `list(response.context['messages'])`, which triggers `BaseStorage.__iter__` and then `_loaded_messages`. → The function calls `_get()` to deserialize message data and create `Message` objects, which are then cached in `self._loaded_data`. → The test is running inside an `@override_settings` context that changes `MESSAGE_TAGS`. → Code then accesses the `level_tag` property of a cached `Message` object. → The `level_tag` property calls `get_level_tags()`, which is decorated with `@lru_cache`. → Because the `@lru_cache` was not cleared when settings were changed, it returns stale data.
- `django/contrib/messages/storage/base.py::BaseStorage._set_level`  (score=0.0)  \
  
- `django/test/utils.py::override_settings.save_options`  (score=1.0)  \
  A test function is decorated with `@override_settings(MESSAGE_TAGS=...)`. → `save_options` is called, attaching the new `MESSAGE_TAGS` value to the test function object. → The test runner later calls `override_settings.enable()` before executing the test. → `enable()` is supposed to send a `setting_changed` signal to clear the cache for `get_level_tags`. → This cache clearing fails for some reason. → The test code eventually calls `get_level_tags` and receives stale data, leading to the symptom.

**next_to_explore:** `['django.test.utils.override_settings.enable', 'django.contrib.messages.utils.get_level_tags', 'django.contrib.messages.apps.MessagesConfig.ready', 'django.contrib.messages.apps.clear_level_tags_cache', 'django.test.utils.override_settings.disable']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/contrib/messages/storage/base.py::Message.level_tag` | 0.9 |
| 2 | `django/contrib/messages/utils.py::get_level_tags` | 0.85 |
| 3 | `django/test/utils.py::override_settings.save_options` | 0.3 |
| 4 | `django/contrib/messages/storage/base.py::Message.tags` | 0.1 |
| 5 | `django/contrib/messages/storage/base.py::BaseStorage._loaded_messages` | 0.05 |
| 6 | `django/contrib/messages/storage/base.py::Message.__init__` | 0.01 |
| 7 | `django/contrib/messages/storage/base.py::_prepare_messages` | 0.01 |
| 8 | `django/contrib/messages/api.py::get_messages` | 0.01 |
| 9 | `django/contrib/messages/storage/base.py::BaseStorage._set_level` | 0.01 |
| 10 | `django/contrib/messages/storage/base.py::BaseStorage.update` | 0.01 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/contrib/messages/storage/base.py::Message.level_tag` | 0.900 | high | 1/1 | (40, 41) |
| 2 | `django/contrib/messages/utils.py::get_level_tags` | 0.850 | high | 1/1 | (5, 12) |
| 3 | `django/contrib/messages/storage/base.py::BaseStorage._prepare_messages` | 0.396 | high | 1/1 | (112, 117) |
| 4 | `django/contrib/messages/storage/base.py::BaseStorage._get_level` | 0.335 | high | 1/1 | (151, 160) |
| 5 | `django/test/utils.py::override_settings.save_options` | 0.300 | high | 1/1 | (506, 514) |
| 6 | `django/contrib/messages/api.py::get_level` | 0.288 | high | 1/1 | (45, 53) |
| 7 | `django/contrib/messages/api.py::set_level` | 0.278 | high | 1/1 | (56, 66) |
| 8 | `django/apps/config.py::AppConfig.ready` | 0.174 | high | 1/1 | (266, 269) |
| 9 | `django/dispatch/dispatcher.py::Signal.connect` | 0.167 | high | 1/1 | (46, 108) |
| 10 | `django/contrib/messages/storage/base.py::Message.tags` | 0.100 | high | 1/1 | (36, 37) |
