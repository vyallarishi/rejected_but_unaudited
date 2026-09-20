# Instance: `django__django-15916`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
Allow ModelForm meta to specify formfield_callback.
Description
	 
		(last modified by Klaas-Jan Gorter)
	 
The function django.forms.modelform_factory returns a form class based on the class it recieves as form argument. As an additional argument it accepts a formfield_callback function. When no callback is provided the class uses no callback instead of the formfield_callback of the base form provided.
Example:
from django import forms
form django.db import models
class MyModel(forms.Model):
	active = models.BooleanField()
	name = models.CharField(max_length=64, blank=True, null=True)
	
def all_required(field, **kwargs):
	formfield = field.formfield(**kwargs)
	formfield.required = True
	return formfield
class MyForm(forms.ModelForm):
	formfield_callback = all_required
	class Meta:
		model = MyModel
		formfield_callback = all_required
		fields = ['active', 'name']
FactoryForm = forms.modelform_factory(MyModel, form=MyForm)
The expected behavior would be that the FactoryForm uses the formfield_callback specified in the Meta attribute of MyForm and that therefore the fields would be required in both the FactoryForm and MyForm. However, under the current behavior of modelform_factory
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['formfield_callback is overwritten', 'fields are not required']`
- named APIs: `['django.forms.modelform_factory', 'field.formfield']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/forms/models.py` | Likely location for modelform_factory to be modified to handle formfield_callback in Meta. |
| 2 | `django/contrib/admin/options.py` | ModelAdmin.get_form uses modelform_factory; needs to pass formfield_callback. |
| 3 | `django/db/models/base.py` | Model Meta options are defined here, might need changes to support formfield_callback. |
| 4 | `django/forms/fields.py` | formfield method is used to create form fields, and formfield_callback is related to this process. |
| 5 | `django/forms/widgets.py` | Custom widgets might need to respect the formfield_callback. |
| 6 | `django/core/checks/model_checks.py` | Checks related to model definitions might need to be updated. |
| 7 | `django/core/management/commands/inspectdb.py` | inspectdb might need to handle the new formfield_callback option. |
| 8 | `django/contrib/admin/checks.py` | Admin checks might need to be updated to validate the new Meta option. |
| 9 | `django/contrib/admin/forms.py` | Custom admin forms might need to respect the formfield_callback. |
| 10 | `django/contrib/admin/helpers.py` | Admin form helpers might need to be updated to handle the new Meta option. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/db/models/fields/__init__.py::Field.formfield`

- **Q1 Role.** This is the base method for converting a model field instance into a corresponding form field instance.
- **Q2 Connection to symptom.** No path. The symptom is that a custom `formfield_callback` is ignored by `modelform_factory`. This `formfield` method is what the default callback (and the custom callback in the example) would call. The problem is not in this method, but upstream in the code that fails to use the custom callback in the first place. This function is downstream of the error and is not responsible for selecting the callback.
- **Q3 Counterfactual.** `no` — Modifying this function would not fix the problem, because the issue is that `modelform_factory` is not using the custom `formfield_callback` provided in the base form's Meta. The calling logic needs to be fixed, not this utility function.
- **Q4 Alternatives considered.**
  - `django.forms.models.modelform_factory` — This is the function explicitly identified in the bug report as the source of the problem and is the most likely location of the bug.
  - `django.forms.models.fields_for_model` — This is the default callback; the issue is that it's being used when a custom one should have been.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a utility called by a formfield callback; it does not choose which callback to use, which is where the bug lies.

#### ✗ REJECTED — `django/db/models/fields/__init__.py::DateField.formfield`

- **Q1 Role.** This method overrides the base `formfield` to ensure a model `DateField` is converted into a `forms.DateField`.
- **Q2 Connection to symptom.** No path. This is a specialization of `Field.formfield` for a specific field type that is not even used in the bug report's example. For the same reasons as `Field.formfield`, it is downstream of the actual bug, which is in the logic that selects the callback.
- **Q3 Counterfactual.** `no` — This function is irrelevant to the bug. The problem is in `modelform_factory`'s handling of `Meta` options, and this function has no role in that process.
- **Q4 Alternatives considered.**
  - `django.forms.models.modelform_factory` — Preferred, as it is explicitly named in the bug report as overwriting the callback.
  - `django.db.models.fields.Field.formfield` — Also rejected, as it's a general utility and not the decision-making code.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a field-specific helper, downstream of the actual bug in `modelform_factory` and irrelevant to the issue.

#### ✗ REJECTED — `django/db/models/fields/__init__.py::DateTimeField.formfield`

- **Q1 Role.** This method overrides the base `formfield` to ensure a model `DateTimeField` is converted into a `forms.DateTimeField`.
- **Q2 Connection to symptom.** No path. Similar to `DateField.formfield`, this is a specialized implementation for a field type not present in the example. It is downstream of the bug in `modelform_factory` and cannot be the cause.
- **Q3 Counterfactual.** `no` — This function is irrelevant to the bug. The problem is in `modelform_factory`'s handling of `Meta` options, and this function has no role in that process.
- **Q4 Alternatives considered.**
  - `django.forms.models.modelform_factory` — Preferred, as it is the function that is failing to respect the `Meta` attribute.
  - `django.db.models.fields.Field.formfield` — Also rejected, as it's a general utility and not the decision-making code.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a field-specific helper, downstream of the actual bug in `modelform_factory` and irrelevant to the issue.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/fields/__init__.py::Field.formfield` | high | This function is a utility called by a formfield callback; it does not choose which callback to use, which is where the bug lies. |  |
| `django/db/models/fields/__init__.py::DateField.formfield` | high | This is a field-specific helper, downstream of the actual bug in `modelform_factory` and irrelevant to the issue. |  |
| `django/db/models/fields/__init__.py::DateTimeField.formfield` | high | This is a field-specific helper, downstream of the actual bug in `modelform_factory` and irrelevant to the issue. |  |

**Causal chains (per candidate)**

- `django/db/models/fields/__init__.py::Field.formfield`  (score=0.0)  \
  
- `django/db/models/fields/__init__.py::DateField.formfield`  (score=0.0)  \
  
- `django/db/models/fields/__init__.py::DateTimeField.formfield`  (score=0.0)  \
  

**next_to_explore:** `['django/forms/models.py::modelform_factory']`

### Abductive step #2 (iteration=6)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/forms/models.py::modelform_factory`

- **Q1 Role.** This function dynamically creates a `ModelForm` class for a given Django model, with options to customize fields, widgets, and other form attributes.
- **Q2 Connection to symptom.** 1. `modelform_factory` accepts a `formfield_callback` argument which defaults to `None`.
2. When a base `form` is passed, but `formfield_callback` is not explicitly provided in the call, the function uses its default `None` value.
3. The function's logic does not check the passed `form`'s `Meta` options to see if a `formfield_callback` is already defined there.
4. This `None` value is then used to construct the new form, effectively overwriting the callback inherited from the base form's `Meta`, causing the fields to not be processed by the intended callback.
- **Q3 Counterfactual.** `yes` — If the function were modified to use the `formfield_callback` from the base form's `Meta` when its own `formfield_callback` argument is `None`, the correct callback would be applied and the fields would be required as expected.
- **Q4 Alternatives considered.**
  - `django.forms.models.ModelFormMetaclass` — This is where the callback is consumed, but `modelform_factory` is what provides the incorrect `None` value, making it the root cause.
  - `django.forms.models.fields_for_model` — This helper function uses the callback, but it's downstream from `modelform_factory` which decides which callback to use.
  - `MyForm.Meta` — The user's definition is correct; the problem is how `modelform_factory` ignores the inherited `Meta` attribute.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function's signature and default argument handling directly cause the `formfield_callback` from the base form's Meta to be ignored and overwritten with `None`.

#### ✗ REJECTED — `django/contrib/postgres/fields/ranges.py::RangeField.formfield`

- **Q1 Role.** This method creates a form field for a PostgreSQL-specific `RangeField` model field.
- **Q2 Connection to symptom.** No path. This function is an implementation of `formfield` for a specific field type not used in the bug report's example. The problem lies in the `formfield_callback` being `None` before this method is even called.
- **Q3 Counterfactual.** `no` — The example code does not use a `RangeField`, so modifying this function would have no effect on the observed symptom.
- **Q4 Alternatives considered.**
  - `django.db.models.Field.formfield` — This is the base implementation, but it's still downstream of the root cause.
  - `django.forms.models.modelform_factory` — Preferred, as it is the source of the incorrect `None` callback.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a field-specific implementation not used in the example and is downstream of the actual error.

#### ✗ REJECTED — `django/contrib/gis/db/models/fields.py::GeometryField.formfield`

- **Q1 Role.** This method creates a form field for a GeoDjango-specific `GeometryField` model field.
- **Q2 Connection to symptom.** No path. This function is specific to `GeometryField` and the bug report's example does not use it. The core issue is that the `formfield_callback` is overwritten with `None` at a higher level, in `modelform_factory`.
- **Q3 Counterfactual.** `no` — The example code does not use a `GeometryField`, so a change here would not affect the outcome of the user's code.
- **Q4 Alternatives considered.**
  - `django.db.models.Field.formfield` — This is the base implementation, but it's still downstream of the root cause.
  - `django.forms.models.modelform_factory` — Preferred, as it is the source of the incorrect `None` callback.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a field-specific implementation for a field not present in the bug report's example.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/models.py::modelform_factory` | high | This function's signature and default argument handling directly cause the `formfield_callback` from the base form's Meta to be ignored and overwritten with `None`. | If `formfield_callback` argument is `None`, check for `form._meta.formfield_callback` and use it if it exists before proceeding. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/postgres/fields/ranges.py::RangeField.formfield` | high | This is a field-specific implementation not used in the example and is downstream of the actual error. |  |
| `django/contrib/gis/db/models/fields.py::GeometryField.formfield` | high | This is a field-specific implementation for a field not present in the bug report's example. |  |

**Causal chains (per candidate)**

- `django/forms/models.py::modelform_factory`  (score=9.0)  \
  `modelform_factory` is called with a `form` argument but no `formfield_callback` argument. → The `formfield_callback` parameter defaults to `None`. → The function does not check for `form.Meta.formfield_callback` and use it as a fallback. → It constructs attributes for a new `Meta` class, including `formfield_callback=None` if it was passed. → A new form class is created, inheriting from the base `form` but with the new `Meta` attributes overriding the old ones. → When an instance of the new form is created, the `None` callback is used, and the user's `all_required` function is never called.
- `django/contrib/postgres/fields/ranges.py::RangeField.formfield`  (score=0.0)  \
  
- `django/contrib/gis/db/models/fields.py::GeometryField.formfield`  (score=0.0)  \
  

**next_to_explore:** `['django.forms.models.ModelFormMetaclass', 'django.forms.models.fields_for_model']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/forms/models.py::modelform_factory` | 1.0 |
| 2 | `django/forms/models.py::ModelFormMetaclass.__new__` | 0.2 |
| 3 | `django/forms/models.py::modelformset_factory` | 0.0 |
| 4 | `django/db/models/fields/__init__.py::Field.formfield` | 0.0 |
| 5 | `django/db/models/fields/__init__.py::DateField.formfield` | 0.0 |
| 6 | `django/forms/models.py::BaseModelFormSet._construct_form` | 0.0 |
| 7 | `django/db/models/fields/__init__.py::DateTimeField.formfield` | 0.0 |
| 8 | `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_dbfield` | 0.0 |
| 9 | `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_manytomany` | 0.0 |
| 10 | `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_choice_field` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/forms/models.py::modelform_factory` | 1.000 | high | 1/1 | (563, 648) |
| 2 | `django/contrib/postgres/fields/ranges.py::RangeField.formfield` | 0.339 | high | 1/1 | (123, 125) |
| 3 | `django/contrib/gis/db/models/fields.py::GeometryField.formfield` | 0.272 | high | 1/1 | (303, 314) |
| 4 | `django/contrib/contenttypes/forms.py::generic_inlineformset_factory` | 0.265 | high | 1/1 | (77, 133) |
| 5 | `django/contrib/contenttypes/forms.py::BaseGenericInlineFormSet.save_new` | 0.203 | high | 1/1 | (67, 74) |
| 6 | `django/forms/models.py::ModelFormMetaclass.__new__` | 0.200 | high | 1/1 | (259, 336) |
| 7 | `django/contrib/contenttypes/forms.py::BaseGenericInlineFormSet.__init__` | 0.193 | high | 1/1 | (12, 47) |
| 8 | `django/forms/models.py::modelformset_factory` | 0.000 | high | 1/1 | (1006, 1071) |
| 9 | `django/db/models/fields/__init__.py::Field.formfield` | 0.000 | high | 1/1 | (1008, 1055) |
| 10 | `django/db/models/fields/__init__.py::DateField.formfield` | 0.000 | high | 1/1 | (1445, 1451) |
