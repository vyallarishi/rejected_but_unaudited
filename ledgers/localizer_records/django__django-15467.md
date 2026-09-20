# Instance: `django__django-15467`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
ModelAdmin with defined radio_fields override empty_label
Description
	
ModelAdmin drops my "empty_label" and set "default_empty_label". For example:
class MyModelAdmin(ModelAdmin):
	radio_fields = 'myfield',
	def formfield_for_foreignkey(self, db_field, *args, **kwargs):
		if db_field.name == 'myfield':
			kwargs['empty_label'] = "I WANT TO SET MY OWN EMPTY LABEL"
		return super().formfield_for_foreignkey(db_field, *args, **kwargs)
You get never the "I WANT TO SET MY OWN EMPTY LABEL"
How to fix it:
In django\contrib\admin\options.py, row 234:
kwargs['empty_label'] = _('None') if db_field.blank else None
Should be changed on:
kwargs['empty_label'] = (kwargs.get('empty_label') or _('None')) if db_field.blank else None
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `['I WANT TO SET MY OWN EMPTY LABEL']`
- behaviors: `['empty_label override', 'default_empty_label setting']`
- named APIs: `['ModelAdmin.formfield_for_foreignkey', 'super().formfield_for_foreignkey', 'kwargs.get']`
- stack frames: `[{'file': 'django\\contrib\\admin\\options.py', 'func': 'None', 'line': 234}]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/contrib/admin/options.py` | Fixes ModelAdmin radio_fields override of empty_label by prioritizing user-defined empty_label over default. |
| 2 | `django/contrib/admin/forms.py` | May need to adjust AdminAuthenticationForm or AdminPasswordChangeForm if they interact with the affected radio_fields. |
| 3 | `django/forms/fields.py` | May need to adjust the Field class if it interacts with the affected radio_fields. |
| 4 | `django/forms/widgets.py` | May need to adjust the RadioSelect widget if it interacts with the affected radio_fields. |
| 5 | `django/contrib/admin/widgets.py` | May need to adjust the AdminRadioSelect widget if it interacts with the affected radio_fields. |
| 6 | `django/db/models/fields/related.py` | May need to adjust the ForeignKey or OneToOneField if they interact with the affected radio_fields. |
| 7 | `django/db/models/fields/mixins.py` | May need to adjust the FieldCacheMixin class if it interacts with the affected radio_fields. |
| 8 | `django/db/models/fields/__init__.py` | May need to adjust the Field class if it interacts with the affected radio_fields. |
| 9 | `django/core/checks/model_checks.py` | ModelAdmin checks may need updating to reflect the fix. |
| 10 | `django/utils/translation/trans_real.py` | May need to adjust the translation if it interacts with the affected radio_fields. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_foreignkey`

- **Q1 Role.** This function is a hook in ModelAdmin to customize the form field used for a ForeignKey field in the Django admin interface.
- **Q2 Connection to symptom.** Yes, a path exists. 1. The user's overridden `formfield_for_foreignkey` sets a custom `kwargs['empty_label']`. 2. It then calls `super()`, invoking this function. 3. This function checks if the field is in `self.radio_fields`, which is true in the bug report. 4. It then unconditionally executes `kwargs['empty_label'] = _('None') if db_field.blank else None`, overwriting the custom label set by the user with a default value. This directly causes the observed symptom.
- **Q3 Counterfactual.** `yes` — Modifying this function to check for a pre-existing `empty_label` in `kwargs` before setting its own default would fix the issue, as the user's custom label would be preserved.
- **Q4 Alternatives considered.**
  - `MyModelAdmin.formfield_for_foreignkey` — This is where the user correctly sets the desired value, but the problem lies in the superclass method it calls, not the user's code itself.
  - `db_field.formfield(**kwargs)` — This is the final step of field creation, but the `kwargs` passed to it are already incorrect, so it's not the source of the problem.
  - `django.contrib.admin.options.BaseModelAdmin.formfield_for_choice_field` — This handles choice fields, not ForeignKeys, and is not on the execution path for this bug.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function contains the exact line of code that unconditionally overwrites the user's custom `empty_label`, directly causing the bug.

#### ✗ REJECTED — `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_choice_field`

- **Q1 Role.** This function is a hook in ModelAdmin to customize the form field for a database field that has `choices` defined.
- **Q2 Connection to symptom.** No path exists. This function is invoked for fields with `choices`, not for a standard `ForeignKey`. The bug report clearly involves a `ForeignKey` being handled by `formfield_for_foreignkey`. Furthermore, this function does not modify `kwargs['empty_label']`, which is the specific symptom.
- **Q3 Counterfactual.** `no` — Modifying this function would have no effect as it is not on the execution path for the bug involving a `ForeignKey` field.
- **Q4 Alternatives considered.**
  - `django.contrib.admin.options.BaseModelAdmin.formfield_for_foreignkey` — This is the correct function for handling `ForeignKey` fields and is the actual source of the bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is not on the execution path for a standard ForeignKey and does not exhibit the problematic behavior of overwriting `empty_label`.

#### ✗ REJECTED — `django/forms/widgets.py::RadioSelect.id_for_label`

- **Q1 Role.** This method customizes the HTML `id` generated for the `<label>` tag associated with a `RadioSelect` widget, primarily for accessibility purposes.
- **Q2 Connection to symptom.** No path exists. This function is involved in the final HTML rendering of the widget, specifically its `id` attribute. The bug concerns the `empty_label` text, which is determined during form field creation, long before this rendering method is called.
- **Q3 Counterfactual.** `no` — Modifying this function would only change HTML attributes (`id` and `for`) and would have no impact on the text content of the empty choice label.
- **Q4 Alternatives considered.**
  - `django.contrib.admin.options.BaseModelAdmin.formfield_for_foreignkey` — Preferred, as it's where the `empty_label` parameter is incorrectly overwritten during form field setup.
  - `django.forms.fields.ModelChoiceField.__init__` — This field constructor receives `empty_label`, but the problem is the incorrect value it's being passed, not how it's handled.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function operates at the HTML rendering layer and has no influence on the `empty_label` parameter set during form field construction.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_foreignkey` | high | This function contains the exact line of code that unconditionally overwrites the user's custom `empty_label`, directly causing the bug. | Change `kwargs['empty_label'] = ...` to `kwargs.setdefault('empty_label', ...)` or check for existence before setting, e.g., `if 'empty_label' not in kwargs: .. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_choice_field` | high | This function is not on the execution path for a standard ForeignKey and does not exhibit the problematic behavior of overwriting `empty_label`. |  |
| `django/forms/widgets.py::RadioSelect.id_for_label` | high | This function operates at the HTML rendering layer and has no influence on the `empty_label` parameter set during form field construction. |  |

**Causal chains (per candidate)**

- `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_foreignkey`  (score=10.0)  \
  User's `MyModelAdmin.formfield_for_foreignkey` is called for the 'myfield' ForeignKey. → Inside the user's method, `kwargs['empty_label']` is set to 'I WANT TO SET MY OWN EMPTY LABEL'. → The user's method calls `super().formfield_for_foreignkey`, invoking `BaseModelAdmin.formfield_for_foreignkey`. → Inside the `BaseModelAdmin` method, the condition `db_field.name in self.radio_fields` evaluates to true. → The line `kwargs['empty_label'] = _('None') if db_field.blank else None` is executed. → This overwrites the custom `empty_label` in `kwargs` with the default value `_('None')`.
- `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_choice_field`  (score=0.0)  \
  
- `django/forms/widgets.py::RadioSelect.id_for_label`  (score=0.0)  \
  

**next_to_explore:** `['django.contrib.admin.options.ModelAdmin.get_form', 'django.contrib.admin.options.BaseModelAdmin.formfield_for_db_field', 'django.db.models.fields.Field.formfield', 'django.forms.fields.ModelChoiceField.__init__']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 1, rejected: 2

**Per-candidate deliberation traces**

#### … CONSIDERING — `django/contrib/admin/options.py::ModelAdmin.get_form`

- **Q1 Role.** This function constructs and returns a ModelForm class for use in the admin add and change views, configuring it with fields, exclusions, and a formfield_callback.
- **Q2 Connection to symptom.** Yes, a path exists. This function initiates the process that leads to the bug. It sets the `formfield_callback` argument for `modelform_factory` to `self.formfield_for_dbfield`. This callback eventually calls `formfield_for_foreignkey`, where the user's custom `empty_label` is set in `kwargs` and then immediately overridden by the call to `super()`, which executes the logic in `BaseModelAdmin.formfield_for_foreignkey` that ignores the existing value.
- **Q3 Counterfactual.** `no` — Modifying this function would be an indirect fix. The function's role is to set up the form creation process, and its logic is correct; the actual bug is in the implementation of the callback it assigns (`formfield_for_foreignkey`).
- **Q4 Alternatives considered.**
  - `django.contrib.admin.options.BaseModelAdmin.formfield_for_foreignkey` — This is the function that almost certainly contains the faulty override logic and is the correct place for a fix.
  - `django.forms.models.modelform_factory` — This function consumes the callback but is unlikely to be the cause, as it just executes the provided callback.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function is on the causal path by setting the formfield_callback, but it does not contain the logic that overrides the 'empty_label'.

#### ✗ REJECTED — `django/forms/models.py::ModelChoiceField.__init__`

- **Q1 Role.** This is the constructor for ModelChoiceField, a form field that represents a model relationship and handles choices from a queryset.
- **Q2 Connection to symptom.** A path exists, but it's downstream of the error. This constructor is called with `kwargs` that have already been modified by `BaseModelAdmin.formfield_for_foreignkey`. By the time `ModelChoiceField.__init__` executes, the user's custom `empty_label` has been replaced with the default `_('None')`, so this function simply instantiates the field with the incorrect label it was given.
- **Q3 Counterfactual.** `no` — The `empty_label` value is already wrong when it arrives as an argument to this function. Modifying this constructor would not fix the root cause, which is the upstream modification of `kwargs`.
- **Q4 Alternatives considered.**
  - `django.contrib.admin.options.BaseModelAdmin.formfield_for_foreignkey` — Preferred, as this is where the `kwargs` are modified before being passed down the call stack.
  - `django.db.models.fields.Field.formfield` — This function calls the `ModelChoiceField` constructor, but it too just passes along the already-modified `kwargs`.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a recipient of the incorrect `empty_label`, not the cause of the override.

#### ✗ REJECTED — `django/db/models/fields/__init__.py::Field.formfield`

- **Q1 Role.** This method on a model field creates and returns a corresponding default `django.forms.Field` instance for use in a form.
- **Q2 Connection to symptom.** Yes, this function is on the execution path. It is called by `ModelAdmin.formfield_for_foreignkey` after the `kwargs` dictionary has been prepared. It receives the `kwargs` with the `empty_label` already overridden. Its job is to then create the form field instance (a `ModelChoiceField` in this case), passing those `kwargs` along to its constructor. Therefore, it propagates the error but does not cause it.
- **Q3 Counterfactual.** `no` — This function correctly uses the `kwargs` it is given. The problem is that the `kwargs` are incorrect upon arrival, due to a bug in the calling function, `BaseModelAdmin.formfield_for_foreignkey`.
- **Q4 Alternatives considered.**
  - `django.contrib.admin.options.BaseModelAdmin.formfield_for_foreignkey` — This is the direct caller and the source of the incorrect `kwargs`, making it the correct place to fix the bug.
  - `django.forms.models.ModelChoiceField.__init__` — This function is called by `Field.formfield`, so it is even further downstream from the root cause.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function merely propagates the overridden 'empty_label' from its `kwargs` to the form field constructor; it does not perform the override.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/admin/options.py::ModelAdmin.get_form` | high | This function is on the causal path by setting the formfield_callback, but it does not contain the logic that overrides the 'empty_label'. | The `formfield_callback` set here leads to the override, but the fix is in the callback's implementation (`formfield_for_foreignkey`), not here. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/models.py::ModelChoiceField.__init__` | high | This function is a recipient of the incorrect `empty_label`, not the cause of the override. |  |
| `django/db/models/fields/__init__.py::Field.formfield` | high | This function merely propagates the overridden 'empty_label' from its `kwargs` to the form field constructor; it does not perform the override. |  |

**Causal chains (per candidate)**

- `django/contrib/admin/options.py::ModelAdmin.get_form`  (score=6.0)  \
  ModelAdmin.get_form sets `formfield_callback` to a partial of `self.formfield_for_dbfield`. → `modelform_factory` uses this callback to generate a field for `myfield`. → The callback invokes the user's `MyModelAdmin.formfield_for_foreignkey`, which sets `kwargs['empty_label']`. → The user's method calls `super()`, executing `BaseModelAdmin.formfield_for_foreignkey`. → `BaseModelAdmin.formfield_for_foreignkey` unconditionally overwrites `kwargs['empty_label']` because the field is in `radio_fields`. → The custom empty label is lost.
- `django/forms/models.py::ModelChoiceField.__init__`  (score=1.0)  \
  `BaseModelAdmin.formfield_for_foreignkey` incorrectly overwrites `kwargs['empty_label']`. → `BaseModelAdmin.formfield_for_foreignkey` calls `db_field.formfield()` with the modified `kwargs`. → `db_field.formfield()` calls `ModelChoiceField.__init__`, passing along the `empty_label`. → This function initializes the field with the incorrect label it received.
- `django/db/models/fields/__init__.py::Field.formfield`  (score=2.0)  \
  `BaseModelAdmin.formfield_for_foreignkey` incorrectly overwrites `kwargs['empty_label']`. → `BaseModelAdmin.formfield_for_foreignkey` calls `db_field.formfield()` (this function) with the modified `kwargs`. → This function merges the passed `kwargs` with its defaults and calls the `ModelChoiceField` constructor. → The incorrect `empty_label` is passed to the constructor.

**next_to_explore:** `['django.contrib.admin.options.BaseModelAdmin.formfield_for_foreignkey', 'django.contrib.admin.options.BaseModelAdmin.formfield_for_dbfield', 'django.forms.models.modelform_factory']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_foreignkey` | 1.0 |
| 2 | `django/contrib/admin/options.py::ModelAdmin.get_form` | 0.7 |
| 3 | `django/db/models/fields/__init__.py::Field.formfield` | 0.5 |
| 4 | `django/forms/models.py::ModelChoiceField.__init__` | 0.4 |
| 5 | `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_choice_field` | 0.1 |
| 6 | `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_dbfield` | 0.0 |
| 7 | `django/forms/widgets.py::RadioSelect.id_for_label` | 0.0 |
| 8 | `django/contrib/admin/options.py::ModelAdmin.get_formset_kwargs` | 0.0 |
| 9 | `django/contrib/admin/options.py::BaseModelAdmin.get_empty_value_display` | 0.0 |
| 10 | `django/contrib/admin/widgets.py::ForeignKeyRawIdWidget.label_and_url_for_value` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_foreignkey` | 1.000 | high | 1/1 | (251, 279) |
| 2 | `django/contrib/admin/options.py::ModelAdmin.get_form` | 0.700 | high | 1/1 | (755, 809) |
| 3 | `django/db/models/fields/__init__.py::Field.formfield` | 0.500 | high | 1/1 | (990, 1037) |
| 4 | `django/forms/models.py::ModelChoiceField.__init__` | 0.400 | high | 1/1 | (1438, 1472) |
| 5 | `django/forms/widgets.py::Select._choice_has_empty_value` | 0.288 | high | 1/1 | (739, 742) |
| 6 | `django/contrib/admin/widgets.py::AdminIntegerFieldWidget.__init__` | 0.282 | high | 1/1 | (386, 387) |
| 7 | `django/contrib/admin/widgets.py::RelatedFieldWidgetWrapper.id_for_label` | 0.278 | high | 1/1 | (341, 342) |
| 8 | `django/forms/widgets.py::ChoiceWidget.options` | 0.247 | high | 1/1 | (622, 625) |
| 9 | `django/forms/widgets.py::Select.use_required_attribute` | 0.235 | high | 1/1 | (744, 759) |
| 10 | `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_choice_field` | 0.100 | high | 1/1 | (217, 234) |
