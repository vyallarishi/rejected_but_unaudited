# Instance: `django__django-14631`

- runs: 1   termination: `ledger_informed`   think-high calls: 5

## Issue (truncated to 1200 chars)

```
BaseForm's _clean_fields() and changed_data should access values via BoundField
Description
	 
		(last modified by Chris Jerdonek)
	 
While working on #32917, I noticed that ​BaseForm._clean_fields() and ​BaseForm.changed_data don't currently access their values through a BoundField object. It would be better for consistency if they did, and to reduce the number of code paths.
One consequence of the current code is that form._clean_fields() can return a different value from form[name].initial when they should be the same. This case is almost, but not quite, covered by ​test_datetime_clean_initial_callable_disabled() (the test can be adjusted to cover this case).
As part of this ticket and in line with accessing data through the BoundField objects, I noticed that the code would also be simpler if the per-field logic of changed_data() were moved into a method of the BoundField class. It could be called something like bf.did_change(). This would be more appropriate because whether form data changed for a field is a property of its BoundField (as it depends on the underlying form data), as opposed to the unbound field. With this change, the method could change from its current ~20 line
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['inconsistent value access', 'form data change detection']`
- named APIs: `['BaseForm._clean_fields', 'BaseForm.changed_data', 'BoundField.did_change']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/forms/boundfield.py` | Implements BoundField, which the issue requests to be modified to access values. |
| 2 | `django/forms/forms.py` | Implements BaseForm, which the issue requests to be modified in _clean_fields() and changed_data. |
| 3 | `django/forms/fields.py` | May need to be modified to ensure consistency with BoundField changes. |
| 4 | `django/contrib/admin/options.py` | ModelAdmin uses forms and may need adjustments for BoundField access. |
| 5 | `django/contrib/admin/helpers.py` | AdminForm and Fieldset use forms and may need adjustments for BoundField access. |
| 6 | `django/contrib/auth/forms.py` | AdminPasswordChangeForm uses forms and may need adjustments for BoundField access. |
| 7 | `django/forms/widgets.py` | Widgets are used in forms and may need adjustments for BoundField access. |
| 8 | `django/core/management/commands/loaddata.py` | loaddata command uses forms and may need adjustments for BoundField access. |
| 9 | `django/core/management/commands/dumpdata.py` | dumpdata command uses forms and may need adjustments for BoundField access. |
| 10 | `django/contrib/admin/tests.py` | Tests for admin functionality, likely to need adjustments after the changes. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 2, considering: 0, rejected: 1

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/forms/forms.py::BaseForm._clean_fields`

- **Q1 Role.** This function iterates over all fields in a form, cleans the input data for each field, and populates the `cleaned_data` dictionary, handling validation errors along the way.
- **Q2 Connection to symptom.** Yes, this function directly causes the symptom of inconsistent value access. It iterates through `self.fields.items()` and gets the field's value using `self.get_initial_for_field` or `self._field_data_value`, bypassing the `BoundField` object (`form[name]`). This creates a separate, inconsistent code path for accessing a field's initial value compared to accessing `form[name].initial`, which is the core of the bug report.
- **Q3 Counterfactual.** `yes` — Refactoring this function to iterate over `BoundField` objects (e.g., via `self._bound_items()`) and using the `BoundField` to access the value would unify the code paths and ensure consistency, thus eliminating the symptom.
- **Q4 Alternatives considered.**
  - `forms.py::BaseForm.get_initial_for_field` — This is part of the problematic path, but the decision to call it is made in `_clean_fields`, making the latter the better place to fix the logic.
  - `forms.py::BoundField.initial` — The problem is not with `BoundField.initial` itself, but that `_clean_fields` fails to use it, creating an inconsistency.
- **Q5 Verdict.** `leading` (confidence: `high`) — The function directly implements the inconsistent data access described in the issue, and refactoring it as suggested would resolve the symptom.

#### ✓ LEADING — `django/forms/forms.py::BaseForm.changed_data`

- **Q1 Role.** This function determines which form fields have data that has changed from their initial values and returns a list of their names.
- **Q2 Connection to symptom.** Yes, this function is a direct cause of the 'form data change detection' symptom. It contains complex logic that manually determines a field's initial and current values by iterating over `self.fields.items()` instead of consistently delegating this responsibility to `BoundField` objects. This direct, non-`BoundField`-centric approach is exactly what the issue describes as a problem to be fixed for consistency and simplicity.
- **Q3 Counterfactual.** `yes` — Modifying this function to use a new `BoundField._did_change()` method, as proposed in the issue, would centralize the change-detection logic within the `BoundField` and simplify this method, directly resolving the reported issue.
- **Q4 Alternatives considered.**
  - `fields.py::Field.has_changed` — This method performs the final comparison, but the problem lies in how `changed_data` gathers the values to be compared, not the comparison itself.
  - `forms.py::BaseForm._field_data_value` — This is a helper used by `changed_data`, but the core issue is the overall orchestration within `changed_data` rather than this specific helper.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function is explicitly named as a source of complexity and inconsistency, and the proposed refactoring directly addresses the problem.

#### ✗ REJECTED — `django/forms/forms.py::BaseForm.hidden_fields`

- **Q1 Role.** This function returns a list of `BoundField` objects for all fields in the form that are configured as hidden.
- **Q2 Connection to symptom.** No path exists. This function is not involved in cleaning field data or detecting changed data. In fact, it correctly demonstrates the pattern of iterating over `BoundField` objects (`for field in self`), which is the recommended solution for the other functions. It is therefore unrelated to the cause of the symptoms.
- **Q3 Counterfactual.** `no` — Since this function is not involved in causing the symptoms of inconsistent value access or change detection, modifying it would have no effect on them.
- **Q4 Alternatives considered.**
  - `forms.py::BaseForm._clean_fields` — This is a confirmed cause of the symptoms.
  - `forms.py::BaseForm.changed_data` — This is the other confirmed cause of the symptoms.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is unrelated to field cleaning or change detection and already uses the pattern that is the solution, not the cause, of the problem.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/forms.py::BaseForm._clean_fields` | high | The function directly implements the inconsistent data access described in the issue, and refactoring it as suggested would resolve the symptom. | Refactor to iterate over `self._bound_items()` and use the `BoundField` object to get the value for cleaning, ensuring consistency with `form[name].initial`. |
| `django/forms/forms.py::BaseForm.changed_data` | high | This function is explicitly named as a source of complexity and inconsistency, and the proposed refactoring directly addresses the problem. | Refactor this method to delegate change detection to a new `BoundField._did_change()` method and iterate over `self._bound_items()`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/forms.py::BaseForm.hidden_fields` | high | This function is unrelated to field cleaning or change detection and already uses the pattern that is the solution, not the cause, of the problem. |  |

**Causal chains (per candidate)**

- `django/forms/forms.py::BaseForm._clean_fields`  (score=9.0)  \
  BaseForm._clean_fields iterates `self.fields.items()` instead of `BoundField` objects. → For a disabled field, it calls `self.get_initial_for_field(field, name)` to get a value. → This value can differ from the one computed by `BoundField.initial` for the same field. → The `field.clean()` method is then called with this potentially inconsistent initial value. → This leads to the symptom where `_clean_fields` produces a different result than expected from `form[name].initial`.
- `django/forms/forms.py::BaseForm.changed_data`  (score=9.0)  \
  BaseForm.changed_data iterates `self.fields.items()`. → It uses complex, multi-path logic to determine `initial_value`, sometimes using `self[name].initial` (a BoundField property) and other times manually reconstructing the value. → It gets the current value via `self._field_data_value`. → This inconsistent and complex data gathering, rather than delegating to a `BoundField` method, is the symptom of poor design mentioned in the ticket. → The proposal is to replace this with a simple loop over `BoundField`s calling a new `bf._did_change()` method.
- `django/forms/forms.py::BaseForm.hidden_fields`  (score=0.0)  \
  

**next_to_explore:** `['django/forms/boundfield.py::BoundField', 'django/forms/fields.py::Field.has_changed', 'django/forms/forms.py::BaseForm.get_initial_for_field', 'django/forms/forms.py::BaseForm._field_data_value', 'django/forms/forms.py::BaseForm._bound_items']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 0, rejected: 0

### Abductive step #3 (iteration=9)

- leading: 0, considering: 0, rejected: 1

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/forms/forms.py::BaseForm.has_changed`

- **Q1 Role.** Returns a boolean indicating whether any form data has been modified from its initial values.
- **Q2 Connection to symptom.** An execution path through this function directly surfaces the 'form data change detection' symptom. The function's logic is `return bool(self.changed_data)`. If `self.changed_data` is calculated incorrectly (the core of the bug), this function will return an incorrect boolean value, thus making the faulty change detection visible to the caller.
- **Q3 Counterfactual.** `no` — Modifying this function alone cannot fix the symptom because the root cause is in the calculation of the `changed_data` property, which this function merely consumes.
- **Q4 Alternatives considered.**
  - `forms.py::BaseForm.changed_data` — This is the direct dependency and is explicitly named in the issue as containing the faulty logic.
  - `forms.py::BaseForm._clean_fields` — This function is described as having the same class of problem, but is not on the execution path of `has_changed`.
  - `fields.py::Field.has_changed` — This is likely part of the current, incorrect implementation that `changed_data` uses.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a trivial consumer of the buggy `changed_data` property; it does not contain the faulty logic itself.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/forms.py::BaseForm.has_changed` | high | This function is a trivial consumer of the buggy `changed_data` property; it does not contain the faulty logic itself. |  |

**Causal chains (per candidate)**

- `django/forms/forms.py::BaseForm.has_changed`  (score=2.0)  \
  A call is made to `form.has_changed()`. → The function accesses the `self.changed_data` property. → The `changed_data` property incorrectly computes the list of changed fields because it does not access values via `BoundField`. → `bool()` is called on this incorrect list. → The function returns an incorrect boolean, manifesting the faulty change detection symptom.

**next_to_explore:** `['django/forms/forms.py::BaseForm.changed_data', 'django/forms/forms.py::BaseForm._clean_fields', 'django/forms/fields.py::Field.has_changed', 'django/forms/forms.py::BoundField', 'django/forms/forms.py::BaseForm.get_initial_for_field']`

### Abductive step #4 (iteration=12)

- leading: 0, considering: 0, rejected: 1

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/forms/forms.py::BaseForm._clean_form`

- **Q1 Role.** This function executes the form-wide `clean()` method, handles any `ValidationError` it raises, and sets `self.cleaned_data` with the result.
- **Q2 Connection to symptom.** No path. This function is called during form validation after `_clean_fields` has already run and populated `self.cleaned_data`. The symptoms relate to how `_clean_fields` and `changed_data` access initial field values, which occurs before or independently of `_clean_form`'s execution. This function operates on the already-cleaned data at a form level and does not access initial field values itself.
- **Q3 Counterfactual.** `no` — Modifying this function would have no effect on the symptoms, as they originate from the data access logic within `BaseForm._clean_fields` and `BaseForm.changed_data`, not from the form-level cleaning logic here.
- **Q4 Alternatives considered.**
  - `forms.py::BaseForm._clean_fields` — Preferred, as it's explicitly named in the issue as a source of inconsistent value access.
  - `forms.py::BaseForm.changed_data` — Preferred, as it's explicitly named in the issue regarding incorrect change detection logic.
  - `boundfield.py::BoundField` — Preferred, as the issue proposes moving logic into this class to ensure consistent data access.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function handles form-level validation and is downstream of the field-level cleaning where the inconsistent data access occurs.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/forms.py::BaseForm._clean_form` | high | This function handles form-level validation and is downstream of the field-level cleaning where the inconsistent data access occurs. |  |

**Causal chains (per candidate)**

- `django/forms/forms.py::BaseForm._clean_form`  (score=0.0)  \
  

**next_to_explore:** `['django/forms/forms.py::BaseForm._clean_fields', 'django/forms/forms.py::BaseForm.changed_data', 'django/forms/forms.py::BaseForm.get_initial_for_field', 'django/forms/fields.py::Field.has_changed', 'django/forms/boundfield.py::BoundField.initial']`

### Abductive step #5 (iteration=15)

- leading: 0, considering: 1, rejected: 2

**Per-candidate deliberation traces**

#### … CONSIDERING — `django/forms/boundfield.py::BoundField.initial`

- **Q1 Role.** This property retrieves the initial value for the bound field, applying special formatting for datetime objects.
- **Q2 Connection to symptom.** Yes, this function is one side of the observed inconsistency. The symptom is that `form._clean_fields()` can return a different value from `form[name].initial`. The path is: 1. A form field has an initial datetime value with microseconds. 2. `form[name].initial` is accessed, calling this function. 3. This function strips the microseconds. 4. `_clean_fields()` accesses the initial value through a different code path that does *not* strip microseconds. 5. The two values are different, which is the symptom.
- **Q3 Counterfactual.** `no` — This function implements the correct behavior. The problem is that other code paths, like `_clean_fields`, do not use this function, causing inconsistency. Modifying this function would not fix the root cause in `_clean_fields`.
- **Q4 Alternatives considered.**
  - `forms.py::BaseForm._clean_fields` — This is the more likely culprit, as the bug report states it accesses values directly instead of through a BoundField.
  - `forms.py::BaseForm.get_initial_for_field` — This is called by `BoundField.initial`, but the core issue is that `_clean_fields` doesn't follow this call path at all.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function defines the correct way to access an initial value; the symptom arises because `_clean_fields` does not use it, creating an inconsistency.

#### ✗ REJECTED — `django/forms/formsets.py::BaseFormSet.cleaned_data`

- **Q1 Role.** This function returns a list of `cleaned_data` dictionaries for every valid form in a formset.
- **Q2 Connection to symptom.** No path. This function operates on the results of form cleaning (`form.cleaned_data`) after the process is complete. The bug, an inconsistency during the cleaning process within a `BaseForm` instance, has already occurred. This function is too far downstream to be a cause.
- **Q3 Counterfactual.** `no` — The symptom is caused by the internal logic of `BaseForm`. This function is in `BaseFormSet` and merely aggregates data, so modifying it would have no effect on the cause of the bug.
- **Q4 Alternatives considered.**
  - `forms.py::BaseForm.cleaned_data` — This is closer, as it's the source of the data, but it's still just an accessor for the results of the buggy `_clean_fields` method.
  - `forms.py::BaseForm._clean_fields` — This is the function that actually populates `cleaned_data` and is the reported source of the bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a consumer of `cleaned_data` from forms in a formset and is too downstream to be the cause of an internal inconsistency within `BaseForm`.

#### ✗ REJECTED — `django/forms/forms.py::BaseForm.visible_fields`

- **Q1 Role.** This function returns a list of `BoundField` objects representing the form fields that are not hidden.
- **Q2 Connection to symptom.** No path. This function is a utility for accessing `BoundField` objects and is not called by `_clean_fields` or `changed_data`. The problem is precisely that those methods *don't* iterate over `BoundField`s, unlike what this method and the proposed fix do.
- **Q3 Counterfactual.** `no` — This function is not involved in the data cleaning or change detection logic where the inconsistency occurs. Modifying it would have no impact on the symptom.
- **Q4 Alternatives considered.**
  - `forms.py::BaseForm._clean_fields` — This is the actual location of the bug, which fails to use the pattern of iterating over BoundFields.
  - `forms.py::BaseForm.__iter__` — This method enables iteration over a form's BoundFields and is used by `visible_fields`, representing the correct pattern.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a simple utility method for retrieving visible fields and is not involved in the form cleaning or change detection logic where the bug exists.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/boundfield.py::BoundField.initial` | high | This function defines the correct way to access an initial value; the symptom arises because `_clean_fields` does not use it, creating an inconsistency. | This function is likely correct; the fix is to make `_clean_fields` and `changed_data` access initial values via `BoundField`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/formsets.py::BaseFormSet.cleaned_data` | high | This function is a consumer of `cleaned_data` from forms in a formset and is too downstream to be the cause of an internal inconsistency within `BaseForm`. |  |
| `django/forms/forms.py::BaseForm.visible_fields` | high | This is a simple utility method for retrieving visible fields and is not involved in the form cleaning or change detection logic where the bug exists. |  |

**Causal chains (per candidate)**

- `django/forms/boundfield.py::BoundField.initial`  (score=5.0)  \
  A form field's initial value is accessed via `form[name].initial`, which calls `BoundField.initial`. → This function normalizes the value (e.g., stripping microseconds from datetimes). → `BaseForm._clean_fields` accesses the same initial value via a different, direct path that does not perform normalization. → The two values are now different, causing the 'inconsistent value access' symptom.
- `django/forms/formsets.py::BaseFormSet.cleaned_data`  (score=0.0)  \
  
- `django/forms/forms.py::BaseForm.visible_fields`  (score=0.0)  \
  

**next_to_explore:** `['django.forms.forms.BaseForm.get_initial_for_field', 'django.forms.forms.BaseForm._bound_items', 'django.forms.forms.BaseForm.full_clean', 'django.forms.forms.BaseForm.__iter__']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/forms/forms.py::BaseForm.changed_data` | 1.0 |
| 2 | `django/forms/forms.py::BaseForm._clean_fields` | 1.0 |
| 3 | `django/forms/forms.py::BaseForm.get_initial_for_field` | 0.7 |
| 4 | `django/forms/forms.py::BaseForm.has_changed` | 0.4 |
| 5 | `django/forms/fields.py::Field.has_changed` | 0.2 |
| 6 | `django/forms/forms.py::BaseForm.full_clean` | 0.1 |
| 7 | `django/forms/forms.py::BaseForm._clean_form` | 0.0 |
| 8 | `django/forms/boundfield.py::BoundField.data` | 0.0 |
| 9 | `django/forms/boundfield.py::BoundField.value` | 0.0 |
| 10 | `django/forms/forms.py::BaseForm.hidden_fields` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/forms/forms.py::BaseForm.changed_data` | 1.000 | high | 1/1 | (438, 459) |
| 2 | `django/forms/forms.py::BaseForm._clean_fields` | 1.000 | high | 1/1 | (389, 406) |
| 3 | `django/forms/forms.py::BaseForm.get_initial_for_field` | 0.700 | high | 1/1 | (490, 498) |
| 4 | `django/forms/formsets.py::BaseFormSet.cleaned_data` | 0.430 | high | 1/1 | (220, 226) |
| 5 | `django/forms/forms.py::BaseForm._post_clean` | 0.417 | high | 1/1 | (417, 422) |
| 6 | `django/forms/boundfield.py::BoundField.initial` | 0.408 | high | 1/1 | (213, 220) |
| 7 | `django/forms/forms.py::BaseForm.has_changed` | 0.400 | high | 1/1 | (433, 435) |
| 8 | `django/forms/forms.py::BaseForm.visible_fields` | 0.381 | high | 1/1 | (483, 488) |
| 9 | `django/forms/forms.py::BaseForm.__getitem__` | 0.378 | high | 1/1 | (150, 168) |
| 10 | `django/forms/forms.py::BaseForm._field_data_value` | 0.378 | high | 1/1 | (200, 201) |
