# Instance: `django__django-11433`

- runs: 1   termination: `ledger_informed`   think-high calls: 8

## Issue (truncated to 1200 chars)

```
Allow `cleaned_data` to overwrite fields' default values.
Description
	
See comments here: ​https://github.com/django/django/pull/7068/files#r289432409
Currently, when submitting a form, if 'some_field' isn't in the data payload (e.g. it wasn't included in the form, perhaps because its value is derived from another field), and 'some_field' has a default value on the model, it cannot be overwritten with 'self.cleaned_data'.
This does not really follow the paradigm of modifying data in 'cleaned_data'. It requires the user to copy and overwrite the raw data submitted with the form.
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `["overwriting fields' default values", "modifying data in 'cleaned_data'"]`
- named APIs: `['self.cleaned_data']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/forms/forms.py` | Handles form cleaning and validation, likely place to modify cleaned_data. |
| 2 | `django/db/models/base.py` | Models define default values, which are relevant to the issue. |
| 3 | `django/forms/fields.py` | Fields define the to_python method, which is responsible for converting values. |
| 4 | `django/core/management/commands/loaddata.py` | May be relevant if default values are not being loaded correctly. |
| 5 | `django/contrib/admin/options.py` | ModelAdmin handles form submission and saving data, potentially related. |
| 6 | `django/contrib/admin/forms.py` | Admin forms are used in the admin interface, where this issue might be encountered. |
| 7 | `django/db/models/fields/__init__.py` | Defines the base Field class and its methods for data handling. |
| 8 | `django/db/models/fields/related.py` | Related fields (ForeignKey, etc.) might have special handling of default values. |
| 9 | `django/db/models/query.py` | QuerySets are used to retrieve data, so might be involved in the issue. |
| 10 | `django/core/serializers/base.py` | Serializers are used to convert data to different formats, which could be relevant. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/forms/forms.py::BaseForm.full_clean`

- **Q1 Role.** This function is the main entry point for validating a form's data, orchestrating the cleaning process and populating `self.cleaned_data` and `self._errors`.
- **Q2 Connection to symptom.** This function orchestrates the form cleaning process. It calls `_clean_fields`, `_clean_form`, and `_post_clean`. A user can modify `self.cleaned_data` in `_clean_form` or a `clean_<field_name>` method called from `_clean_fields`. The symptom, where a value in `cleaned_data` is ignored if the field was not in the initial request, manifests after this function's callees have run, specifically within `ModelForm._post_clean`. Therefore, `full_clean` is part of the overall process but does not contain the faulty logic itself.
- **Q3 Counterfactual.** `no` — This function is an orchestrator. The specific logic for handling fields or saving the model instance resides in its callees (`_clean_fields`, `_post_clean`), so modifying `full_clean` would not fix the root cause.
- **Q4 Alternatives considered.**
  - `django.forms.forms.py::BaseForm._clean_fields` — This is a better candidate as it populates cleaned_data, but the issue seems to be in how cleaned_data is used, not created.
  - `django.forms.models.py::ModelForm._post_clean` — This is the most likely location of the bug, as it's where cleaned_data is used to update the model instance.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a high-level orchestrator; the bug is in the specific implementation of a callee (`ModelForm._post_clean`).

#### ✗ REJECTED — `django/forms/formsets.py::BaseFormSet.cleaned_data`

- **Q1 Role.** This function is a property that returns a list of `cleaned_data` dictionaries, one for each valid form within the formset.
- **Q2 Connection to symptom.** No path exists. This function is a read-only accessor that collects the `cleaned_data` attribute from already-cleaned forms in a formset. It does not participate in the cleaning process of an individual form where the symptom originates.
- **Q3 Counterfactual.** `no` — Modifying this function would only affect how `cleaned_data` is retrieved from a formset, not how it's generated or used within an individual form.
- **Q4 Alternatives considered.**
  - `django.forms.forms.py::BaseForm.full_clean` — This is the entry point for cleaning a single form, making it far more relevant.
  - `django.forms.forms.py::BaseForm._clean_fields` — This function actually populates `cleaned_data` for a form, making it a direct part of the causal chain.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for formsets and only reads `cleaned_data`; the bug is in the cleaning logic of a single `BaseForm`.

#### ✗ REJECTED — `django/forms/forms.py::BaseForm._clean_fields`

- **Q1 Role.** This function iterates over all fields in a form, extracts their raw values from the submitted data, cleans them, and populates `self.cleaned_data`.
- **Q2 Connection to symptom.** This function is part of the causal chain. It populates `self.cleaned_data`. For a field not in the form submission, it correctly calls the field's `clean` method and any `clean_<field_name>` method, placing the result in `self.cleaned_data`. The symptom—that this value is ignored—is produced by a downstream consumer (`ModelForm._post_clean`) that incorrectly filters `self.cleaned_data` against the original form submission data (`self.data`). Thus, this function produces the data that is later misused, but it is not the source of the error.
- **Q3 Counterfactual.** `no` — This function appears to correctly populate `cleaned_data`. The bug is in `ModelForm._post_clean`, which incorrectly filters the data generated by this function before saving the model.
- **Q4 Alternatives considered.**
  - `django.forms.models.py::ModelForm._post_clean` — This is the actual location of the bug, as it filters `cleaned_data` based on whether the field was in the original request.
  - `django.forms.fields.Field.clean` — Considered, but this function's output is correctly placed in `cleaned_data`; the problem is how `cleaned_data` is used later.
  - `django.forms.widgets.Widget.value_from_datadict` — This determines the initial value, but the core issue is not what the initial value is, but that the final cleaned value is ignored.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function correctly populates `cleaned_data`; the bug is in a downstream consumer (`ModelForm._post_clean`) that misuses this data.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/forms.py::BaseForm.full_clean` | high | This function is a high-level orchestrator; the bug is in the specific implementation of a callee (`ModelForm._post_clean`). |  |
| `django/forms/formsets.py::BaseFormSet.cleaned_data` | high | This function is for formsets and only reads `cleaned_data`; the bug is in the cleaning logic of a single `BaseForm`. |  |
| `django/forms/forms.py::BaseForm._clean_fields` | high | This function correctly populates `cleaned_data`; the bug is in a downstream consumer (`ModelForm._post_clean`) that misuses this data. |  |

**Causal chains (per candidate)**

- `django/forms/forms.py::BaseForm.full_clean`  (score=2.0)  \
  BaseForm.full_clean is called. → It calls self._clean_fields() which populates self.cleaned_data. → It calls self._post_clean(). → Inside ModelForm._post_clean, the value from cleaned_data is ignored because the field was not in self.data. → The model instance is saved with its default value, not the one from cleaned_data.
- `django/forms/formsets.py::BaseFormSet.cleaned_data`  (score=0.0)  \
  
- `django/forms/forms.py::BaseForm._clean_fields`  (score=4.0)  \
  BaseForm._clean_fields iterates over all form fields. → For a field not in self.data, it gets a value (e.g., None) and calls field.clean() and clean_<field_name>(). → The resulting derived value is correctly stored in self.cleaned_data. → Later, in ModelForm._post_clean, this value is discarded because the field name is not in self.data. → The symptom (default value not being overwritten) appears.

**next_to_explore:** `['django.forms.models.py::ModelForm._post_clean', 'django.forms.models.py::construct_instance', 'django.forms.fields.py::Field.clean', 'django.forms.widgets.py::Widget.value_from_datadict']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 0, rejected: 0

### Abductive step #3 (iteration=9)

- leading: 0, considering: 0, rejected: 0

### Abductive step #4 (iteration=12)

- leading: 0, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/forms/forms.py::BaseForm._post_clean`

- **Q1 Role.** This function is an empty hook in `BaseForm` intended for subclasses to perform additional cleaning after the main form and field cleaning is complete.
- **Q2 Connection to symptom.** No path exists. In `BaseForm`, this function does nothing as it only contains a `pass` statement. While it is overridden in `ModelForm` to perform model validation, the symptom described is not a validation failure but an issue where correctly cleaned data is ignored during the model instance creation/saving process, which happens downstream from this validation step.
- **Q3 Counterfactual.** `no` — Modifying this empty base-class method would have no effect. The bug lies in how `cleaned_data` is later used to construct the model instance, not in this preliminary validation hook.
- **Q4 Alternatives considered.**
  - `django.forms.models.construct_instance` — Preferred, as this function is responsible for building the model instance from `cleaned_data` and is the most likely place for logic that incorrectly prioritizes model defaults.
  - `django.forms.models.ModelForm._post_clean` — This is the actual implementation for model forms, but it's focused on validation, not instance construction, making it less likely to be the root cause.
  - `django.forms.models.ModelForm.save` — This method orchestrates the saving process and calls `construct_instance`, making it a key part of the causal path to investigate.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is an empty hook in the base class and is not involved in the data persistence logic that causes the symptom.

#### ✗ REJECTED — `django/forms/forms.py::BaseForm._clean_form`

- **Q1 Role.** This function calls the form's `clean()` method for form-wide validation and data modification, and then updates `self.cleaned_data` with the result.
- **Q2 Connection to symptom.** This function is on the causal path because it's responsible for updating `self.cleaned_data` with the values modified in the `clean()` method. The path is: `full_clean()` calls `_clean_form()`, which calls `self.clean()` and assigns its return value to `self.cleaned_data`. The symptom occurs because a downstream function later ignores this updated `cleaned_data`. The function itself operates correctly.
- **Q3 Counterfactual.** `no` — This function correctly updates `self.cleaned_data`. The problem is not in this function, but in a downstream consumer of `self.cleaned_data` that fails to respect its contents.
- **Q4 Alternatives considered.**
  - `django.forms.models.construct_instance` — Strongly preferred, as it is the function that consumes `cleaned_data` to build the model instance and likely contains the faulty logic.
  - `django.forms.models.ModelForm.save` — A good candidate to investigate as it is the entry point for the save operation and calls `construct_instance`.
  - `django.forms.forms.BaseForm.full_clean` — Not preferred, as it's an orchestrator of the cleaning process and is unlikely to contain the specific logic error.
- **Q5 Verdict.** `rejected` (confidence: `high`) — The function correctly updates `cleaned_data`; the bug is in a downstream function that ignores this data.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/forms.py::BaseForm._post_clean` | high | This is an empty hook in the base class and is not involved in the data persistence logic that causes the symptom. |  |
| `django/forms/forms.py::BaseForm._clean_form` | high | The function correctly updates `cleaned_data`; the bug is in a downstream function that ignores this data. |  |

**Causal chains (per candidate)**

- `django/forms/forms.py::BaseForm._post_clean`  (score=0.0)  \
  BaseForm.full_clean() calls BaseForm._post_clean(). → In BaseForm, this method does nothing. → In a ModelForm subclass, it triggers model validation, which is not related to the symptom of data being ignored during save.
- `django/forms/forms.py::BaseForm._clean_form`  (score=2.0)  \
  BaseForm.full_clean() calls BaseForm._clean_form(). → This method calls the user-defined self.clean(), allowing modification of form data. → It then correctly updates self.cleaned_data with the modified data. → Later, a downstream function (likely construct_instance) incorrectly ignores the value in self.cleaned_data for fields not in the original request data, instead using the model's default value.

**next_to_explore:** `['django.forms.models.construct_instance', 'django.forms.models.ModelForm.save', 'django.forms.models.ModelForm._post_clean']`

### Abductive step #5 (iteration=15)

- leading: 0, considering: 1, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django.contrib.auth.base_user.py::AbstractBaseUser.save`

- **Q1 Role.** This function saves a user instance and handles password-related post-save logic, such as invalidating sessions.
- **Q2 Connection to symptom.** No path. This function executes after a model instance has already been constructed and populated from form data. The described bug occurs during the form cleaning and instance construction phase, which is upstream of this model `save` method. This function's logic is specific to password management and does not influence how form data is mapped to model fields.
- **Q3 Counterfactual.** `no` — Modifying this function would not affect how a ModelForm uses `cleaned_data` to populate a model instance, as that process happens before this `save` method is ever called.
- **Q4 Alternatives considered.**
  - `django.forms.models.construct_instance` — Preferred, as this function is responsible for creating the model instance from form data, which is where the issue lies.
  - `django.forms.models.ModelForm._post_clean` — Preferred, as this is the method on a ModelForm that orchestrates instance creation/update after cleaning.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for user password handling during save, which is unrelated to and downstream from the form data processing bug.

#### … CONSIDERING — `django.forms.forms.py::BaseForm.changed_data`

- **Q1 Role.** This function returns a list of field names whose data in the submitted form differs from their initial values.
- **Q2 Connection to symptom.** Yes, a plausible path exists. The function determines if a field has changed by comparing the submitted data with the initial value. If a field is not in the submission payload (e.g., omitted from the HTML form), `value_from_datadict` will return `None`. If the initial value is also `None`, `has_changed` will return `False`, and the field name won't be in `changed_data`. If a downstream function like `construct_instance` relies on `changed_data` to decide which fields from `cleaned_data` to apply to a model instance, then a value programmatically added to `cleaned_data` for an omitted field will be ignored, causing the symptom.
- **Q3 Counterfactual.** `partially` — Modifying this to include fields present in `cleaned_data` but not `data` could work. However, the root cause is more likely in the consumer of this function, which should probably iterate over `cleaned_data` directly instead of `changed_data`.
- **Q4 Alternatives considered.**
  - `django.forms.models.construct_instance` — Preferred as the likely consumer of `changed_data` and the most appropriate place to fix the logic to correctly use all of `cleaned_data`.
  - `django.forms.models.ModelForm._post_clean` — This is the caller of `construct_instance` and a key part of the causal chain, making it a strong candidate for investigation.
  - `django.forms.fields.Field.has_changed` — This is called by `changed_data` and is part of the mechanism, but changing its core logic would have wide-ranging effects.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function's output directly leads to the symptom, but the function itself may be behaving as designed; the true fault likely lies in its consumer.

#### ✗ REJECTED — `django.forms.formsets.py::BaseFormSet.full_clean`

- **Q1 Role.** This function orchestrates the validation of all forms within a formset, collecting errors and running cross-form validation.
- **Q2 Connection to symptom.** No path. This function operates at the formset level, managing a collection of forms. The bug described concerns the internal data handling of a single `ModelForm` when constructing a model instance. This function calls the cleaning methods on individual forms but does not interfere with their internal logic of how `cleaned_data` is used to populate a model instance.
- **Q3 Counterfactual.** `no` — Modifying the formset's cleaning process would not alter the behavior of an individual `ModelForm`'s instance construction logic, which is where the bug is located.
- **Q4 Alternatives considered.**
  - `django.forms.forms.py::BaseForm.full_clean` — Preferred, as this is the analogous cleaning orchestrator for a single form and is on the causal path.
  - `django.forms.models.construct_instance` — Preferred, as this is where the instance is created from the form's data, which is the locus of the problem.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function operates at the formset level, which is the wrong level of abstraction for a bug within a single form's data handling.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django.forms.forms.py::BaseForm.changed_data` | high | This function's output directly leads to the symptom, but the function itself may be behaving as designed; the true fault likely lies in its consumer. | The consumer of this function (likely `construct_instance`) should iterate over `cleaned_data` instead of relying on `changed_data`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django.contrib.auth.base_user.py::AbstractBaseUser.save` | high | This function is for user password handling during save, which is unrelated to and downstream from the form data processing bug. |  |
| `django.forms.formsets.py::BaseFormSet.full_clean` | high | This function operates at the formset level, which is the wrong level of abstraction for a bug within a single form's data handling. |  |

**Causal chains (per candidate)**

- `django.contrib.auth.base_user.py::AbstractBaseUser.save`  (score=0.0)  \
  
- `django.forms.forms.py::BaseForm.changed_data`  (score=8.0)  \
  A field is omitted from a form submission, so it is not in `self.data`. → `BaseForm.changed_data` is called. → Inside the loop, `field.widget.value_from_datadict(self.data, ...)` returns `None` for the omitted field. → `field.has_changed(initial_value, None)` returns `False`. → The omitted field's name is not added to the list of changed data. → The caller, `construct_instance`, checks if the field is in `changed_data` before using the value from `cleaned_data`.
- `django.forms.formsets.py::BaseFormSet.full_clean`  (score=0.0)  \
  

**next_to_explore:** `['django.forms.models.py::construct_instance', 'django.forms.models.py::ModelForm._post_clean', 'django.forms.fields.py::Field.has_changed']`

### Abductive step #6 (iteration=18)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/forms/fields.py::Field.has_changed`

- **Q1 Role.** This function determines if a field's value has changed from its initial value by comparing the `initial` value with the submitted `data`.
- **Q2 Connection to symptom.** This function is called to populate `form.changed_data`. The symptom occurs when a field's value, modified in `form.clean()`, is not persisted. This happens because `construct_instance` only updates fields listed in `changed_data`. A path to the symptom is:
1. A field is not present in the submitted form data, so `data` passed to `has_changed` is `None`.
2. The field has a default value, which becomes the `initial` value.
3. For certain field types (e.g., `BooleanField`), `self.to_python(None)` can return a value equal to the `initial` value (e.g., `False`).
4. `has_changed` then returns `False`.
5. The field is omitted from `changed_data`.
6. Consequently, `construct_instance` ignores any value set for this field in `cleaned_data` during the `clean()` method, and the model instance retains its default value.
- **Q3 Counterfactual.** `no` — The function correctly compares initial and submitted data. The problem is that `changed_data` is calculated before `form.clean()` can modify `cleaned_data`, and this function has no access to `cleaned_data` to account for such changes.
- **Q4 Alternatives considered.**
  - `django.forms.models.construct_instance` — Preferred, as it's the consumer of `changed_data` and could be changed to also inspect `cleaned_data`.
  - `django.forms.forms.BaseForm.changed_data` — A possible alternative, as it computes the list of changed fields, but the timing of its calculation is the main issue.
  - `django.forms.forms.BaseForm._post_clean` — Considered, as `changed_data` could be re-evaluated here, but it feels less direct than fixing the consumer.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function's logic is correct for its inputs, but it's used in a way that ignores later modifications to `cleaned_data`.

#### ✗ REJECTED — `django/forms/forms.py::BaseForm.get_initial_for_field`

- **Q1 Role.** This function retrieves the initial value for a given form field, checking the form's `initial` dictionary first, then the field's `initial` attribute, and evaluating callables.
- **Q2 Connection to symptom.** This function supplies the `initial` value that is passed to `field.has_changed`. This `initial` value, often derived from a model's `default`, is compared against the submitted data. While this function is part of the causal pathway that leads to `has_changed` being called, its own logic is not faulty; it correctly retrieves the initial value as specified.
- **Q3 Counterfactual.** `no` — The function correctly performs its duty of retrieving a field's initial value. The bug is caused by how the 'changed' status is determined and used, not by how the initial value is retrieved.
- **Q4 Alternatives considered.**
  - `django.forms.models.construct_instance` — Preferred, as this is where the decision to ignore `cleaned_data` values is made based on `changed_data`.
  - `django.forms.forms.BaseForm.changed_data` — A better candidate, as it's the direct caller that uses the value from `get_initial_for_field` to determine if a field has changed.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a simple getter and behaves correctly; the fault lies downstream in how its return value is used.

#### ✗ REJECTED — `django/forms/fields.py::TypedChoiceField.clean`

- **Q1 Role.** This method cleans the value for a `TypedChoiceField`, first by calling the parent `clean` method and then coercing the value to the correct Python type.
- **Q2 Connection to symptom.** No plausible path exists. The described symptom is a general issue with how Django forms handle data that is modified in `cleaned_data` but wasn't in the initial submission. This `clean` method is specific to `TypedChoiceField` and is part of populating `cleaned_data`, not part of the mechanism that later ignores the `cleaned_data` value. The root cause is in the generic form processing logic, not in a specific field's implementation.
- **Q3 Counterfactual.** `no` — The bug is in the general form machinery, not specific to `TypedChoiceField`. Modifying this function would not address the root cause.
- **Q4 Alternatives considered.**
  - `django.forms.models.construct_instance` — Preferred, as it's the component that incorrectly uses `changed_data` to exclude valid `cleaned_data` modifications.
  - `django.forms.forms.BaseForm.changed_data` — A strong candidate because it calculates the `changed_data` list that `construct_instance` relies on.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a field-specific clean method, whereas the bug is in the general form processing logic.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/fields.py::Field.has_changed` | high | This function's logic is correct for its inputs, but it's used in a way that ignores later modifications to `cleaned_data`. |  |
| `django/forms/forms.py::BaseForm.get_initial_for_field` | high | This function is a simple getter and behaves correctly; the fault lies downstream in how its return value is used. |  |
| `django/forms/fields.py::TypedChoiceField.clean` | high | This is a field-specific clean method, whereas the bug is in the general form processing logic. |  |

**Causal chains (per candidate)**

- `django/forms/fields.py::Field.has_changed`  (score=4.0)  \
  A field with a default value is not submitted in a form. → BaseForm.changed_data iterates fields to check for changes. → It calls field.has_changed(initial=default_value, data=None). → For some field types, to_python(None) returns a value equal to the default. → has_changed returns False. → The field is not added to form.changed_data.
- `django/forms/forms.py::BaseForm.get_initial_for_field`  (score=1.0)  \
  A ModelForm is created for a model with a default value on a field. → The form's initial data is populated with this default. → BaseForm.changed_data calls get_initial_for_field to retrieve this value. → The value is passed to field.has_changed for comparison. → This is an indirect contribution; the function itself is not the cause of the bug.
- `django/forms/fields.py::TypedChoiceField.clean`  (score=0.0)  \
  

**next_to_explore:** `['django.forms.models.construct_instance', 'django.forms.forms.BaseForm.changed_data']`

### Abductive step #7 (iteration=21)

- leading: 0, considering: 1, rejected: 2

**Per-candidate deliberation traces**

#### … CONSIDERING — `django/forms/forms.py::BaseForm.has_changed`

- **Q1 Role.** This function checks if any form data has changed compared to its initial values by checking the `self.changed_data` property.
- **Q2 Connection to symptom.** Yes, a plausible path exists. The `ModelForm.save` method uses `has_changed()` to decide whether to save the model instance to the database. `has_changed()` returns `bool(self.changed_data)`, and `self.changed_data` is populated only for fields present in the submitted form data. If a field is added or modified exclusively in the `clean()` method (and was not in the submitted data), `self.changed_data` can be empty, causing `has_changed()` to return `False`. This leads to `ModelForm.save` skipping the database save operation, effectively ignoring the change made in `cleaned_data`.
- **Q3 Counterfactual.** `partially` — Modifying this function to be aware of changes made in `clean()` would fix the symptom. However, the more robust fix is in the caller (`ModelForm.save`) to not rely solely on this check, which is how the bug was actually fixed.
- **Q4 Alternatives considered.**
  - `django.forms.models.BaseModelForm.save` — Preferred, as this is the caller with the faulty conditional logic and where the actual fix was implemented.
  - `django.forms.forms.BaseForm._clean_fields` — This populates `changed_data`, but it cannot anticipate changes made later in the `clean()` method.
  - `django.forms.models.construct_instance` — Initially considered based on user comments, but it correctly uses `cleaned_data`; the problem is that its result is not saved.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function is a critical link in the causal chain, as its return value incorrectly causes the save operation to be skipped.

#### ✗ REJECTED — `django/forms/fields.py::TypedMultipleChoiceField.clean`

- **Q1 Role.** This function cleans the value for a `TypedMultipleChoiceField` by first calling the parent's `clean` method and then coercing the result to the correct type.
- **Q2 Connection to symptom.** No path exists. The symptom described is a general problem with the `ModelForm` saving mechanism, not an issue specific to the cleaning logic of `TypedMultipleChoiceField`. The problem occurs after the cleaning phase is complete.
- **Q3 Counterfactual.** `no` — Modifying this function would only affect instances of `TypedMultipleChoiceField` and would not fix the general problem in `ModelForm.save`.
- **Q4 Alternatives considered.**
  - `django.forms.models.BaseModelForm.save` — This is the actual location of the bug, which is in the generic saving logic.
  - `django.forms.forms.BaseForm.has_changed` — This function is part of the faulty condition within `save()`.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a field-specific cleaning method, whereas the bug is in the generic form saving logic.

#### ✗ REJECTED — `django/forms/fields.py::MultiValueField.clean`

- **Q1 Role.** This function validates a list of values for a `MultiValueField` by cleaning each sub-value against its corresponding sub-field.
- **Q2 Connection to symptom.** No path exists. The symptom is about the general behavior of `ModelForm` when saving data, not about the specific validation logic of a `MultiValueField`. The bug manifests after all field cleaning has finished.
- **Q3 Counterfactual.** `no` — The problem is not specific to `MultiValueField`, so a change here would not fix the root cause in the `ModelForm`'s save process.
- **Q4 Alternatives considered.**
  - `django.forms.models.BaseModelForm.save` — This is where the faulty logic resides, affecting all model forms.
  - `django.forms.forms.BaseForm.has_changed` — This function provides the incorrect signal that leads to the bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function's logic is for a specific field type and is unrelated to the general `ModelForm.save` issue.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/forms.py::BaseForm.has_changed` | high | This function is a critical link in the causal chain, as its return value incorrectly causes the save operation to be skipped. | The caller, `ModelForm.save`, should not rely solely on this function, perhaps by also checking if `commit=True`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/fields.py::TypedMultipleChoiceField.clean` | high | This is a field-specific cleaning method, whereas the bug is in the generic form saving logic. |  |
| `django/forms/fields.py::MultiValueField.clean` | high | This function's logic is for a specific field type and is unrelated to the general `ModelForm.save` issue. |  |

**Causal chains (per candidate)**

- `django/forms/forms.py::BaseForm.has_changed`  (score=9.0)  \
  A field is modified in `form.clean()` but was not part of the submitted data. → `_clean_fields` does not add this field to `self.changed_data`. → `ModelForm.save()` calls `self.has_changed()` to decide if a DB write is needed. → `has_changed()` returns `False` because `self.changed_data` is empty. → `ModelForm.save()` skips saving the model instance. → The modification from `cleaned_data` is never persisted to the database.
- `django/forms/fields.py::TypedMultipleChoiceField.clean`  (score=0.0)  \
  
- `django/forms/fields.py::MultiValueField.clean`  (score=0.0)  \
  

**next_to_explore:** `['django.forms.models.BaseModelForm.save', 'django.forms.forms.BaseForm._clean_fields', 'django.forms.models.BaseModelForm._post_clean', 'django.forms.models.construct_instance']`

### Abductive step #8 (iteration=27)

- leading: 1, considering: 0, rejected: 4

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/forms/models.py::BaseModelForm._post_clean`

- **Q1 Role.** This method finalizes form cleaning for a BaseModelForm by constructing the model instance from cleaned data and running model-level validation.
- **Q2 Connection to symptom.** Yes, this is a highly plausible location for the cause. The path is: `full_clean` -> `_post_clean`. Inside this function, the line `self.instance = construct_instance(...)` is called. The symptom is that a value added to `self.cleaned_data` (for a field not in the original request) is ignored. This suggests that `construct_instance` does not look at `self.cleaned_data` for fields that were not submitted. This function calls the problematic `construct_instance` and handles the resulting `self.instance`, making it central to the issue.
- **Q3 Counterfactual.** `yes` — Modifying this function to manually update `self.instance` with values from `self.cleaned_data` after `construct_instance` returns would fix the problem by ensuring the cleaned data is respected before model validation runs.
- **Q4 Alternatives considered.**
  - `django.forms.models.construct_instance` — This is the most likely direct cause, but since it's not provided for analysis, its caller `_post_clean` is the best proxy.
  - `django/forms/models.py::BaseModelForm.save` — This is too late in the process; the instance is already incorrectly populated by the time `save` is called.
  - `django/db/models/base.py::Model.full_clean` — This validates the already-constructed instance; it doesn't populate it.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function orchestrates model instance creation from form data and is the direct caller of `construct_instance`, which is inferred to be the source of the faulty logic.

#### ✗ REJECTED — `django/forms/models.py::BaseModelForm.save`

- **Q1 Role.** This method saves the form's underlying model instance to the database if the form is valid.
- **Q2 Connection to symptom.** No path. This function is called after all cleaning and validation, including `_post_clean` where the model instance is constructed. By the time `save()` is executed, `self.instance` has already been populated incorrectly. This function merely persists the incorrect state to the database; it does not cause it.
- **Q3 Counterfactual.** `no` — The model instance `self.instance` is already incorrect when this method is called. Modifying `save` would be a workaround, not a fix for the root cause, which lies in instance construction.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::BaseModelForm._post_clean` — Preferred, as it's responsible for creating the instance that `save` uses, making it the source of the problem.
  - `django/db/models/base.py::Model.save` — This is even further downstream and simply executes the database query.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is downstream of the error; it saves the already incorrectly-populated model instance.

#### ✗ REJECTED — `django/forms/fields.py::Field.bound_data`

- **Q1 Role.** This method returns the value for a field that should be displayed when rendering a bound form.
- **Q2 Connection to symptom.** No path. This function is involved in rendering a form back to the user, not in the server-side processing of submitted data for cleaning, validation, or saving. The bug occurs during the data processing pipeline, not the rendering pipeline.
- **Q3 Counterfactual.** `no` — Changing this function would only affect how a field's value is displayed in an HTML form, not how the submitted data is processed to create a model instance.
- **Q4 Alternatives considered.**
  - `django/forms/fields.py::Field.clean` — This is part of the data processing pipeline and thus more relevant than a rendering helper.
  - `django/forms/models.py::BaseModelForm._post_clean` — This is where the processed data is used to build a model, which is central to the bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is related to form rendering, which is unrelated to the data processing bug during form submission.

#### ✗ REJECTED — `django/db/models/base.py::Model.full_clean`

- **Q1 Role.** This method runs all validation on a model instance, including field validation, model-level cleaning, and uniqueness checks.
- **Q2 Connection to symptom.** No path. This method is called within `BaseModelForm._post_clean` on the model instance *after* it has been constructed by `construct_instance`. The problem is that the instance was not populated correctly from `cleaned_data`. This function only validates the already-incorrect instance; it does not populate it.
- **Q3 Counterfactual.** `no` — This function's responsibility is validation, not data population. Modifying it would not change how the model instance is created from the form's data upstream.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::BaseModelForm._post_clean` — Preferred, as it is the caller of this function and is responsible for creating the instance that gets validated.
  - `django.forms.models.construct_instance` — This is the function that populates the instance before validation, making it the likely root cause.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function validates a model instance after it has been populated; it is downstream of the root cause.

#### ✗ REJECTED — `django/contrib/admin/options.py::ModelAdmin.get_changeform_initial_data`

- **Q1 Role.** This method retrieves initial data for a form in the Django admin, usually from GET parameters.
- **Q2 Connection to symptom.** No path. This function is used to populate a form with *initial* data before it is displayed to the user. The bug is about processing *submitted* data from a bound form. This function is not in the execution path for handling a POST request with form data.
- **Q3 Counterfactual.** `no` — This function is for pre-populating a form on GET requests, not processing submitted data on POST requests. Modifying it would have no effect on the bug.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::BaseModelForm._post_clean` — This function is part of the POST request handling and is directly related to the bug's context.
  - `django/forms/forms.py::BaseForm.full_clean` — This is the main entry point for processing submitted form data, unlike the current function.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function deals with initial form data for rendering, not processing submitted data, which is where the bug occurs.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/models.py::BaseModelForm._post_clean` | high | This function orchestrates model instance creation from form data and is the direct caller of `construct_instance`, which is inferred to be the source of the faulty logic. | After `construct_instance` returns, iterate through `self.cleaned_data` and use `setattr` to apply any values to `self.instance` that were not part of the initi |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/models.py::BaseModelForm.save` | high | This function is downstream of the error; it saves the already incorrectly-populated model instance. |  |
| `django/forms/fields.py::Field.bound_data` | high | This function is related to form rendering, which is unrelated to the data processing bug during form submission. |  |
| `django/db/models/base.py::Model.full_clean` | high | This function validates a model instance after it has been populated; it is downstream of the root cause. |  |
| `django/contrib/admin/options.py::ModelAdmin.get_changeform_initial_data` | high | This function deals with initial form data for rendering, not processing submitted data, which is where the bug occurs. |  |

**Causal chains (per candidate)**

- `django/forms/models.py::BaseModelForm._post_clean`  (score=9.0)  \
  A user submits a ModelForm but omits a field that has a `default` on the model. → The form's `clean()` method programmatically adds a value for the omitted field into `self.cleaned_data`. → `BaseModelForm._post_clean` is called during form validation. → `_post_clean` calls `construct_instance` to populate a model instance. → The (inferred) logic of `construct_instance` only considers fields present in the original submission, not all fields in `cleaned_data`. → The model instance is returned with the omitted field unset.
- `django/forms/models.py::BaseModelForm.save`  (score=0.0)  \
  
- `django/forms/fields.py::Field.bound_data`  (score=0.0)  \
  
- `django/db/models/base.py::Model.full_clean`  (score=0.0)  \
  
- `django/contrib/admin/options.py::ModelAdmin.get_changeform_initial_data`  (score=0.0)  \
  

**next_to_explore:** `['django.forms.models.construct_instance', 'django.forms.forms.py::BaseForm.full_clean', 'django.forms.forms.py::BaseForm._clean_form', 'django.forms.forms.py::BaseForm._clean_fields']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/forms/models.py::construct_instance` | 1.0 |
| 2 | `django/forms/models.py::BaseModelForm._post_clean` | 0.9 |
| 3 | `django/forms/forms.py::BaseForm._clean_fields` | 0.6 |
| 4 | `django/forms/forms.py::BaseForm._clean_form` | 0.5 |
| 5 | `django/forms/forms.py::BaseForm.full_clean` | 0.4 |
| 6 | `django/forms/forms.py::BaseForm.changed_data` | 0.2 |
| 7 | `django/forms/forms.py::BaseForm.has_changed` | 0.1 |
| 8 | `django/forms/forms.py::BaseForm._post_clean` | 0.0 |
| 9 | `django/forms/forms.py::BaseForm.clean` | 0.0 |
| 10 | `django/forms/formsets.py::BaseFormSet.cleaned_data` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/forms/models.py::construct_instance` | 1.000 | high | 1/1 | (31, 64) |
| 2 | `django/forms/models.py::BaseModelForm._post_clean` | 0.900 | high | 1/1 | (379, 407) |
| 3 | `django/forms/forms.py::BaseForm._clean_fields` | 0.600 | high | 1/1 | (380, 400) |
| 4 | `django/forms/forms.py::BaseForm._clean_form` | 0.500 | high | 1/1 | (402, 409) |
| 5 | `django/db/models/base.py::Model.full_clean` | 0.468 | high | 1/1 | (1175, 1209) |
| 6 | `django/db/models/base.py::Model.clean_fields` | 0.441 | high | 1/1 | (1211, 1234) |
| 7 | `django/forms/fields.py::Field.has_changed` | 0.440 | high | 1/1 | (174, 191) |
| 8 | `django/forms/fields.py::Field.clean` | 0.437 | high | 1/1 | (143, 151) |
| 9 | `django/forms/forms.py::BaseForm.get_initial_for_field` | 0.420 | high | 1/1 | (484, 492) |
| 10 | `django/forms/fields.py::TypedChoiceField.clean` | 0.419 | high | 1/1 | (843, 845) |
