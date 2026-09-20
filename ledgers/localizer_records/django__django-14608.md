# Instance: `django__django-14608`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
Add `nonform` CSS class for non form errors in FormSets
Description
	 
		(last modified by Ties Jan Hefting)
	 
Forms add the nonfield CSS class for non field errors in ErrorList instances. This is documented in a section on ​rendering form error messages. Similarly, in FormSets I'd expect to see the nonform CSS class added for non form errors. This would allow a custom ErrorList to make a distinction in form field errors, non field errors (forms) and non form errors (FormSets) when rendering error messages. Therefore I'd suggest to add this nonform CSS class and document it for developers to use.
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['rendering form error messages', 'custom ErrorList', 'form field errors', 'non field errors', 'non form errors']`
- named APIs: `[]`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/forms/formsets.py` | FormSets are directly related to the issue of adding a CSS class for non-form errors. |
| 2 | `django/contrib/admin/helpers.py` | This file contains the InlineAdminFormSet class, which is a wrapper around an inline formset and likely needs modification to add the CSS class. |
| 3 | `django/contrib/admin/templates/admin/includes/fieldset.html` | This template is used to render fieldsets in the admin interface, and will need to be modified to include the new CSS class. |
| 4 | `django/contrib/admin/static/admin/css/base.css` | This CSS file will need to be updated to style the new 'nonform' CSS class. |
| 5 | `django/forms/forms.py` | Forms add the nonfield CSS class for non field errors in ErrorList instances, so this file is relevant for comparison. |
| 6 | `django/forms/utils.py` | This file contains the ErrorList class, which is used to render error messages and may need modification. |
| 7 | `django/contrib/admin/options.py` | This file defines ModelAdmin and InlineModelAdmin, which are used to configure the admin interface and may need changes to handle the new CSS class. |
| 8 | `django/contrib/admin/templates/admin/includes/errors.html` | This template is used to render errors in the admin interface and may need to be modified to include the new CSS class. |
| 9 | `django/contrib/admin/forms.py` | This file defines AdminAuthenticationForm and AdminPasswordChangeForm, which are used in the admin app and may need changes to handle the new CSS class. |
| 10 | `django/contrib/admin/tests.py` | Tests will need to be added or modified to ensure the new CSS class is correctly added and styled. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `tests.test_client_regress.tests.py::AssertFormErrorTests.test_unknown_nonfield_error`

- **Q1 Role.** This function is a unit test to verify that `assertFormError` correctly raises an `AssertionError` when a specified non-field error is not present in a form.
- **Q2 Connection to symptom.** No path. This function tests the `assertFormError` test helper for form non-field errors. The observed symptom is about the rendering of `FormSet` non-form errors, specifically a missing CSS class in the final HTML, which is unrelated to the behavior of this test assertion.
- **Q3 Counterfactual.** `no` — Modifying this test case would have no effect on how FormSet errors are rendered in a web response, as it only validates the behavior of a test utility.
- **Q4 Alternatives considered.**
  - `django/forms/formsets.py::BaseFormSet.non_form_errors` — Preferred, as it is the direct accessor for the errors that are missing the CSS class.
  - `django/forms/forms.py::BaseForm.non_field_errors` — Considered as a model for the correct behavior, but it is not the source of the bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a test function for a testing utility and is not involved in the rendering of formset errors.

#### ✓ LEADING — `django/forms/formsets.py::BaseFormSet.non_form_errors`

- **Q1 Role.** This function returns an `ErrorList` of errors that are not associated with a particular form in a FormSet, i.e., global errors for the entire FormSet.
- **Q2 Connection to symptom.** Yes, a direct path exists. When a template renders `formset.non_form_errors`, this method is called. It returns `self._non_form_errors`, which is an `ErrorList` instance. This instance is created without the `error_class='nonform'` property, so when it is rendered into HTML, the surrounding `<ul>` tag lacks the `nonform` CSS class, causing the observed symptom.
- **Q3 Counterfactual.** `yes` — Modifying this function to wrap the returned `ErrorList` in a new one with `error_class='nonform'` would ensure the CSS class is present during rendering, fixing the symptom.
- **Q4 Alternatives considered.**
  - `django/forms/formsets.py::BaseFormSet.full_clean` — This is a strong alternative, as it's where `_non_form_errors` is created; the fix could be applied there at the source.
  - `django/forms/utils.py::ErrorList.as_ul` — This is where the HTML is generated, but it's likely just missing the `error_class` input, so it's not the root cause.
  - `django/forms/forms.py::BaseForm.non_field_errors` — This function provides the pattern for the fix but is not part of the buggy execution path.
- **Q5 Verdict.** `leading` (confidence: `high`) — This is the public accessor for non-form errors and is the direct analogue to the correctly-behaving `non_field_errors` on forms; modifying it provides a clean fix.

#### ✗ REJECTED — `django/forms/forms.py::BaseForm.non_field_errors`

- **Q1 Role.** This function returns an `ErrorList` of errors that are not associated with a particular field in a Form.
- **Q2 Connection to symptom.** No path. This function exhibits the *correct* behavior for `Form` non-field errors, which serves as a model for the desired `FormSet` behavior. It does not cause the symptom, which is specific to `FormSet`s.
- **Q3 Counterfactual.** `no` — This function is not called when processing FormSet errors, so modifying it would not affect the FormSet's output.
- **Q4 Alternatives considered.**
  - `django/forms/formsets.py::BaseFormSet.non_form_errors` — Preferred, as this is the function in the FormSet that corresponds to this one and contains the bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function pertains to Forms, not FormSets, and demonstrates the correct behavior rather than causing the bug.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/formsets.py::BaseFormSet.non_form_errors` | high | This is the public accessor for non-form errors and is the direct analogue to the correctly-behaving `non_field_errors` on forms; modifying it provides a clean fix. | Return `self.error_class(self._non_form_errors, error_class='nonform')` to wrap the errors in an `ErrorList` that has the required CSS class. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `tests.test_client_regress.tests.py::AssertFormErrorTests.test_unknown_nonfield_error` | high | This is a test function for a testing utility and is not involved in the rendering of formset errors. |  |
| `django/forms/forms.py::BaseForm.non_field_errors` | high | This function pertains to Forms, not FormSets, and demonstrates the correct behavior rather than causing the bug. |  |

**Causal chains (per candidate)**

- `tests.test_client_regress.tests.py::AssertFormErrorTests.test_unknown_nonfield_error`  (score=0.0)  \
  
- `django/forms/formsets.py::BaseFormSet.non_form_errors`  (score=9.0)  \
  A template accesses `formset.non_form_errors` to render non-form specific errors. → The `BaseFormSet.non_form_errors` method is invoked. → The method ensures `full_clean` has run and then returns the `self._non_form_errors` attribute, which is an `ErrorList`. → This `ErrorList` instance was created upstream (in `full_clean`) without an `error_class` specified. → When the template renders the `ErrorList` (e.g., via `as_ul`), the resulting HTML `<ul>` tag is missing the `class="nonform"` attribute. → This results in the observed symptom where non-form errors cannot be styled distinctly from other errors.
- `django/forms/forms.py::BaseForm.non_field_errors`  (score=0.0)  \
  

**next_to_explore:** `['django.forms.formsets.BaseFormSet.full_clean', 'django.forms.utils.ErrorList.as_ul', 'django.forms.utils.ErrorList.__init__']`

### Abductive step #2 (iteration=6)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/forms/utils.py::ErrorList.__init__`

- **Q1 Role.** This function initializes an ErrorList object, which is a list-like object for storing and displaying form errors, and sets its `error_class` attribute for CSS styling.
- **Q2 Connection to symptom.** An execution path through this function is part of the causal chain, but it is not the cause. 
1. `BaseFormSet.full_clean` instantiates an `ErrorList` for non-form errors via `self.error_class()`, which resolves to `ErrorList()`.
2. This calls `ErrorList.__init__` with `error_class=None`.
3. Inside `__init__`, `self.error_class` is set to the default `'errorlist'`. 
The symptom (missing 'nonform' class) occurs because no specific `error_class` was passed during initialization. The function itself behaves correctly given its inputs.
- **Q3 Counterfactual.** `no` — This function just applies the `error_class` it's given; the problem is that it's not being given the correct class by its caller. Modifying it would require adding context-specific logic that belongs upstream.
- **Q4 Alternatives considered.**
  - `django/forms/formsets.py::BaseFormSet.full_clean` — Preferred, as it is the caller that instantiates the ErrorList and should provide the correct context (the 'nonform' class).
  - `django/forms/utils.py::ErrorList.as_ul` — Not preferred, as this function is downstream and only renders the already-incorrect state.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function correctly sets the CSS class based on its input; the problem is that it's not receiving the desired 'nonform' class from its caller.

#### ✗ REJECTED — `django/forms/utils.py::ErrorList.as_ul`

- **Q1 Role.** This function renders the ErrorList as an HTML `<ul>` element, applying the CSS class stored in `self.error_class`.
- **Q2 Connection to symptom.** This function is where the symptom becomes externally visible. 
1. An `ErrorList` for non-form errors is created with `self.error_class` set to `'errorlist'`. 
2. When this error list is rendered in a template, `as_ul()` is called. 
3. The function generates an HTML `<ul>` tag with `class="errorlist"`, which is missing the desired `nonform` class. 
This function produces the incorrect output, but the root cause is the value of `self.error_class` which is set upstream.
- **Q3 Counterfactual.** `no` — While a hacky modification could add the class here, it would be incorrect as it would apply to all `ErrorList` instances, not just formset non-form errors. The fix must be more specific.
- **Q4 Alternatives considered.**
  - `django/forms/formsets.py::BaseFormSet.full_clean` — Preferred, as this is where the ErrorList is created and the class should be specified.
  - `django/forms/utils.py::ErrorList.__init__` — Not preferred; this function is closer to the cause but still just processes its inputs.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function renders the HTML and visibly produces the symptom, but the root cause is the incorrect `error_class` value set upstream.

#### ✓ LEADING — `django/forms/formsets.py::BaseFormSet.full_clean`

- **Q1 Role.** This function validates all data for the formset, populating `self._errors` (for form-specific errors) and `self._non_form_errors` (for formset-level errors).
- **Q2 Connection to symptom.** Yes, a direct path exists. 
1. This function is responsible for validating the formset and collecting errors.
2. It initializes the list for non-form errors with the line: `self._non_form_errors = self.error_class()`.
3. `self.error_class` defaults to `ErrorList`, so this creates an `ErrorList` instance without passing any special `error_class` argument.
4. The resulting `ErrorList` instance therefore lacks the `'nonform'` CSS class, which directly causes the observed symptom when it is rendered.
- **Q3 Counterfactual.** `yes` — Changing `self._non_form_errors = self.error_class()` to `self._non_form_errors = self.error_class(error_class='nonform')` would correctly initialize the ErrorList with the desired class.
- **Q4 Alternatives considered.**
  - `django/forms/formsets.py::BaseFormSet.non_form_errors` — Considered, but this property simply returns the `_non_form_errors` list that `full_clean` creates. The instantiation happens in `full_clean`.
  - `django/forms/forms.py::BaseForm.non_field_errors` — This is the analogous property for Forms and serves as a model for the fix, but it's not part of the FormSet execution path.
  - `django/forms/utils.py::ErrorList.__init__` — Rejected, as it's the responsibility of the caller (`full_clean`) to provide the correct class.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function instantiates the `ErrorList` for non-form errors without passing the 'nonform' CSS class, which is the direct root cause of the symptom.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/formsets.py::BaseFormSet.full_clean` | high | This function instantiates the `ErrorList` for non-form errors without passing the 'nonform' CSS class, which is the direct root cause of the symptom. | Change `self._non_form_errors = self.error_class()` to `self._non_form_errors = self.error_class(error_class='nonform')`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/utils.py::ErrorList.__init__` | high | This function correctly sets the CSS class based on its input; the problem is that it's not receiving the desired 'nonform' class from its caller. |  |
| `django/forms/utils.py::ErrorList.as_ul` | high | This function renders the HTML and visibly produces the symptom, but the root cause is the incorrect `error_class` value set upstream. |  |

**Causal chains (per candidate)**

- `django/forms/utils.py::ErrorList.__init__`  (score=3.0)  \
  BaseFormSet.full_clean calls `self.error_class()` which is `ErrorList()`. → ErrorList.__init__ is called with `error_class=None`. → The instance's `error_class` attribute is set to the default 'errorlist'. → This is correct behavior for the given input, but the input from the caller is missing the required information.
- `django/forms/utils.py::ErrorList.as_ul`  (score=4.0)  \
  BaseFormSet.full_clean creates an ErrorList whose `error_class` attribute is 'errorlist'. → When rendered, `as_ul` is called on this ErrorList instance. → The function formats an HTML string using `self.error_class`, producing `<ul class="errorlist">...</ul>`. → This is the point where the symptom (missing 'nonform' class) is visibly produced in the output.
- `django/forms/formsets.py::BaseFormSet.full_clean`  (score=10.0)  \
  BaseFormSet.full_clean is called to validate the formset. → It executes the line `self._non_form_errors = self.error_class()`. → This instantiates `ErrorList` without providing an `error_class` argument. → The resulting `ErrorList` object does not have the 'nonform' CSS class associated with it. → This missing class information is the direct cause of the final rendered HTML being incorrect.

**next_to_explore:** `['django/forms/formsets.py::BaseFormSet.non_form_errors', 'django/forms/forms.py::BaseForm.non_field_errors', 'django/forms/formsets.py::BaseFormSet.__init__']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/forms/formsets.py::BaseFormSet.full_clean` | 1.0 |
| 2 | `django/forms/formsets.py::BaseFormSet.non_form_errors` | 0.8 |
| 3 | `django/forms/utils.py::ErrorList.__init__` | 0.5 |
| 4 | `django/forms/utils.py::ErrorList.as_ul` | 0.3 |
| 5 | `django/forms/forms.py::BaseForm.non_field_errors` | 0.1 |
| 6 | `django/forms/formsets.py::BaseFormSet.errors` | 0.0 |
| 7 | `django/forms/formsets.py::BaseFormSet.total_error_count` | 0.0 |
| 8 | `django/contrib/admin/helpers.py::InlineAdminFormSet.non_form_errors` | 0.0 |
| 9 | `django/forms/forms.py::BaseForm.errors` | 0.0 |
| 10 | `django/contrib/admin/helpers.py::AdminForm.non_field_errors` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/forms/formsets.py::BaseFormSet.full_clean` | 1.000 | high | 1/1 | (330, 383) |
| 2 | `django/forms/formsets.py::BaseFormSet.non_form_errors` | 0.800 | high | 1/1 | (290, 298) |
| 3 | `django/forms/utils.py::ErrorList.__init__` | 0.500 | high | 1/1 | (84, 90) |
| 4 | `django/forms/formsets.py::formset_factory` | 0.411 | high | 1/1 | (460, 490) |
| 5 | `django/forms/forms.py::BaseForm.has_error` | 0.401 | high | 1/1 | (366, 370) |
| 6 | `django/forms/forms.py::BaseForm.add_error` | 0.387 | high | 1/1 | (319, 364) |
| 7 | `tests/test_client_regress/tests.py::AssertFormErrorTests.test_unknown_nonfield_error` | 0.350 | high | 1/1 | (605, 636) |
| 8 | `django/contrib/admin/helpers.py::AdminForm.errors` | 0.311 | high | 1/1 | (64, 65) |
| 9 | `django/forms/utils.py::ErrorList.as_ul` | 0.300 | high | 1/1 | (113, 121) |
| 10 | `django/forms/forms.py::BaseForm.non_field_errors` | 0.100 | high | 1/1 | (311, 317) |
