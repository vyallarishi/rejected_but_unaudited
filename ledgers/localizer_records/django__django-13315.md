# Instance: `django__django-13315`

- runs: 1   termination: `ledger_informed`   think-high calls: 3

## Issue (truncated to 1200 chars)

```
limit_choices_to on a ForeignKey can render duplicate options in formfield
Description
	
If you pass a Q object as limit_choices_to on a ForeignKey field involving a join, you may end up with duplicate options in your form.
See regressiontest in patch for a clear view on the problem.
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['duplicate options in form']`
- named APIs: `[]`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/contrib/admin/options.py` | Handles formfield generation and limit_choices_to in ModelAdmin, likely place to address duplicate options. |
| 2 | `django/db/models/fields/related.py` | Implements ForeignKey and its limit_choices_to, where the Q object is used. |
| 3 | `django/db/models/query.py` | QuerySet filtering logic is relevant to how limit_choices_to is applied. |
| 4 | `django/db/models/sql/query.py` | SQL query construction is where the join logic affecting limit_choices_to is implemented. |
| 5 | `django/contrib/admin/filters.py` | List filters interact with ForeignKey and may be related to the duplicate options issue. |
| 6 | `django/forms/models.py` | ModelForm and related functions are used to generate formfields, including those with ForeignKey. |
| 7 | `django/contrib/admin/widgets.py` | Widgets are used to render form fields, including ForeignKey fields, and may be involved in the issue. |
| 8 | `django/db/models/lookups.py` | Lookups are used in filtering, and may be relevant to how limit_choices_to is applied. |
| 9 | `django/core/management/commands/migrate.py` | While not directly related, migrations can affect database schema and relationships, so it's worth considering. |
| 10 | `django/contrib/admin/views/main.py` | ChangeList and related classes are used to display and filter data in the admin, and may be related to the issue. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 1, rejected: 1

**Per-candidate deliberation traces**

#### … CONSIDERING — `django/db/models/fields/related.py::RelatedField.formfield`

- **Q1 Role.** This function prepares a form field for a related model field, passing configuration like `limit_choices_to` from the model to the form field.
- **Q2 Connection to symptom.** This function is part of the causal chain but does not directly cause the symptom. Its role is to pass the `limit_choices_to` value (which may be a Q object that implies a join) to the form field's constructor. The actual filtering that leads to duplicates happens later when this value is used. The path is: 1. `formfield` is called. 2. It retrieves `self.remote_field.limit_choices_to`. 3. It includes this value in the `defaults` passed to `super().formfield()`. 4. The created form field now holds this `limit_choices_to` value for later use.
- **Q3 Counterfactual.** `no` — This function correctly passes the configuration from the model to the form. Modifying it to not pass `limit_choices_to` would break intended functionality, and the root cause is in how this value is later applied to the queryset, not in the act of passing it.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::apply_limit_choices_to_to_formfield` — Preferred, as this is where the filter is actually applied to the queryset, making it the location where duplicates are generated.
  - `django.forms.models.ModelChoiceField.__init__` — Considered, as it orchestrates the form field setup and likely calls the function that applies the filter.
  - `django.db.models.query.QuerySet.complex_filter` — Considered, as the logic for handling joins and distinctness could arguably reside within this lower-level method.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function is an intermediary that passes the problematic configuration; it's part of the causal path but not the root cause of the error.

#### ✓ LEADING — `django/forms/models.py::apply_limit_choices_to_to_formfield`

- **Q1 Role.** This function applies a `limit_choices_to` constraint, if one exists, to a form field's queryset.
- **Q2 Connection to symptom.** Yes, this function directly causes the symptom. 1. It receives a formfield whose `limit_choices_to` is a Q object requiring a join. 2. It calls `formfield.queryset.complex_filter(limit_choices_to)`. 3. This operation adds a JOIN to the underlying SQL query. 4. Because no `.distinct()` is called, the resulting queryset contains duplicate rows for the same object if the join is on a one-to-many or many-to-many relationship. 5. These duplicate objects in the queryset are then rendered as duplicate options in the form's select widget.
- **Q3 Counterfactual.** `yes` — Modifying this function to add `.distinct()` to the queryset after applying the `complex_filter` would eliminate the duplicate rows and thus fix the symptom.
- **Q4 Alternatives considered.**
  - `django.db.models.query.QuerySet.complex_filter` — A possible alternative location for the fix, as it could intelligently add `distinct` when it adds a join, but modifying the caller is more direct.
  - `django.db.models.fields.related.py::RelatedField.formfield` — Not preferred, as this function only passes data and does not perform the filtering operation itself.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function directly applies the filter that creates duplicates without adding `.distinct()`, and modifying it would solve the issue.

#### ✗ REJECTED — `django/db/models/fields/related.py::RelatedField.get_limit_choices_to`

- **Q1 Role.** This function is a getter that retrieves the `limit_choices_to` attribute from a related field, invoking it if it is a callable.
- **Q2 Connection to symptom.** No path exists. This function only retrieves a value (`limit_choices_to`, which might be a Q object). It does not interact with querysets or the database, and therefore cannot introduce duplicate rows. It simply returns the configuration that is used by other functions.
- **Q3 Counterfactual.** `no` — This function correctly performs its duty of returning a configured value. The fault lies in how the returned value is later used by `apply_limit_choices_to_to_formfield`.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::apply_limit_choices_to_to_formfield` — Preferred, as this is where the value returned by `get_limit_choices_to` is actually used to filter a queryset.
  - `django/db/models/fields/related.py::RelatedField.formfield` — Not preferred, but more relevant than this getter, as it's the next step in passing the configuration along.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a simple getter and is not involved in the queryset filtering that produces the duplicate options.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/models.py::apply_limit_choices_to_to_formfield` | high | This function directly applies the filter that creates duplicates without adding `.distinct()`, and modifying it would solve the issue. | Add `.distinct()` to the queryset after applying the filter, e.g., `formfield.queryset = formfield.queryset.complex_filter(limit_choices_to).distinct()`. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/fields/related.py::RelatedField.formfield` | high | This function is an intermediary that passes the problematic configuration; it's part of the causal path but not the root cause of the error. | The fix should be applied where `limit_choices_to` is used to filter the queryset, not here where it is merely passed along. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/fields/related.py::RelatedField.get_limit_choices_to` | high | This function is a simple getter and is not involved in the queryset filtering that produces the duplicate options. |  |

**Causal chains (per candidate)**

- `django/db/models/fields/related.py::RelatedField.formfield`  (score=4.0)  \
  A `ForeignKey` is defined with a `limit_choices_to` Q object that implies a join. → `RelatedField.formfield` is called to create the corresponding form widget. → The function retrieves the Q object from `self.remote_field.limit_choices_to`. → It passes this Q object in the `defaults` dictionary to the form field's constructor. → The form field is initialized with the `limit_choices_to` value, which is later used by `apply_limit_choices_to_to_formfield` to filter the queryset, causing duplicates.
- `django/forms/models.py::apply_limit_choices_to_to_formfield`  (score=9.0)  \
  This function is called with a form field that has a `limit_choices_to` Q object requiring a join. → The line `formfield.queryset = formfield.queryset.complex_filter(limit_choices_to)` is executed. → The ORM generates a SQL query with a JOIN based on the Q object. → The query runs and returns a result set with duplicate rows for the primary model. → The resulting queryset contains duplicate model instances. → When the form field is rendered, these duplicate instances create duplicate `<option>` tags in the HTML.
- `django/db/models/fields/related.py::RelatedField.get_limit_choices_to`  (score=0.0)  \
  

**next_to_explore:** `['django.forms.models.ModelChoiceField.__init__', 'django.db.models.query.QuerySet.complex_filter', 'django.forms.models.ModelChoiceField.queryset', 'django.db.models.query.QuerySet.distinct']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 0, rejected: 0

### Abductive step #3 (iteration=9)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/contrib/admin/filters.py::ListFilter.queryset`

- **Q1 Role.** This is an abstract base method in the admin's ListFilter class, which must be implemented by subclasses to filter a queryset based on the user's selection in the admin list view's sidebar.
- **Q2 Connection to symptom.** No path exists. This function is part of the admin's list view filtering mechanism, which is separate from the logic that populates choices in a model form field. The symptom of duplicate options occurs during form rendering, not list view rendering.
- **Q3 Counterfactual.** `no` — Modifying this abstract method would not affect form field choice generation because it is not called in that execution path.
- **Q4 Alternatives considered.**
  - `django.forms.models.ModelChoiceField.queryset` — Preferred, as this property is directly responsible for providing the list of choices to the form widget.
  - `django.db.models.fields.related.RelatedField.formfield` — Preferred, as this method orchestrates the creation of the form field and is a likely place to apply cross-cutting logic.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for admin list filters, a feature unrelated to rendering form field choices.

#### ✗ REJECTED — `django/forms/models.py::ModelChoiceField.get_limit_choices_to`

- **Q1 Role.** This method retrieves the `limit_choices_to` value for a ModelChoiceField, executing it if it's a callable.
- **Q2 Connection to symptom.** This function is on the causal path but does not cause the symptom. It correctly retrieves and returns the `Q` object that is specified in `limit_choices_to`. The problem arises later when the caller uses this `Q` object to filter a queryset without adding a `distinct()` call to handle potential joins.
- **Q3 Counterfactual.** `no` — This is a simple getter. The responsibility for handling the returned value lies with its caller, which is where the filtering logic resides.
- **Q4 Alternatives considered.**
  - `django.forms.models.ModelChoiceField.__init__` — Preferred, as the constructor receives both the queryset and `limit_choices_to` and is a candidate for applying the filter.
  - `django.forms.models.ModelChoiceField._get_queryset` — Preferred, as this property getter is often where `limit_choices_to` is applied to the queryset just before use.
  - `n57526049["models.py::apply_limit_choices_to_to_formfield"]` — Considered, as its name suggests it's a helper specifically for this purpose and could be the place where a `.distinct()` call is missing.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a simple, correct getter; the bug is in how its return value is used by the caller.

#### ✗ REJECTED — `django/contrib/admin/widgets.py::url_params_from_lookup_dict`

- **Q1 Role.** This function converts a `limit_choices_to` dictionary into a dictionary of URL query parameters for use in admin widgets like the related object lookup popup.
- **Q2 Connection to symptom.** No path exists. The symptom of duplicate options appears in a standard `<select>` dropdown, which is populated directly from a server-side queryset. This function is for generating URLs for a different UI component (the popup lookup widget, often used with `raw_id_fields`), not for populating the options of a select box.
- **Q3 Counterfactual.** `no` — Modifying this function would affect the behavior of the admin's related-object lookup links, not the choices in a standard form dropdown.
- **Q4 Alternatives considered.**
  - `django.forms.models.ModelChoiceField.choices` — Preferred, as this property iterates over the final queryset to generate the choices, and is the direct source of the form options.
  - `django.forms.widgets.Select.render` — Considered, but less likely as the widget just renders the choices it's given; the duplication originates in the queryset itself.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for a specific admin widget and is not involved in populating a standard form select field's options.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/admin/filters.py::ListFilter.queryset` | high | This function is for admin list filters, a feature unrelated to rendering form field choices. |  |
| `django/forms/models.py::ModelChoiceField.get_limit_choices_to` | high | This function is a simple, correct getter; the bug is in how its return value is used by the caller. |  |
| `django/contrib/admin/widgets.py::url_params_from_lookup_dict` | high | This function is for a specific admin widget and is not involved in populating a standard form select field's options. |  |

**Causal chains (per candidate)**

- `django/contrib/admin/filters.py::ListFilter.queryset`  (score=0.0)  \
  
- `django/forms/models.py::ModelChoiceField.get_limit_choices_to`  (score=0.0)  \
  
- `django/contrib/admin/widgets.py::url_params_from_lookup_dict`  (score=0.0)  \
  

**next_to_explore:** `['django.db.models.fields.related.RelatedField.formfield', 'django.forms.models.ModelChoiceField.__init__', 'django.forms.models.ModelChoiceField._get_queryset', 'django.db.models.query.QuerySet.filter', 'django.db.models.query.QuerySet.distinct']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/forms/models.py::apply_limit_choices_to_to_formfield` | 0.95 |
| 2 | `django/db/models/query.py::QuerySet.complex_filter` | 0.2 |
| 3 | `django/db/models/fields/related.py::RelatedField.formfield` | 0.1 |
| 4 | `django/forms/models.py::ModelChoiceField.__init__` | 0.05 |
| 5 | `django/forms/models.py::ModelChoiceField.get_limit_choices_to` | 0.02 |
| 6 | `django/db/models/fields/related.py::RelatedField.get_limit_choices_to` | 0.02 |
| 7 | `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_foreignkey` | 0.01 |
| 8 | `django/contrib/admin/widgets.py::url_params_from_lookup_dict` | 0.01 |
| 9 | `django/db/models/fields/related.py::ForeignKey.formfield` | 0.0 |
| 10 | `django/forms/models.py::InlineForeignKeyField.__init__` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/forms/models.py::apply_limit_choices_to_to_formfield` | 0.950 | high | 1/1 | (98, 103) |
| 2 | `django/contrib/admin/options.py::BaseModelAdmin.formfield_for_choice_field` | 0.355 | high | 1/1 | (189, 205) |
| 3 | `django/contrib/admin/options.py::ModelAdmin.get_list_select_related` | 0.340 | high | 1/1 | (973, 978) |
| 4 | `django/forms/models.py::ModelMultipleChoiceField.__init__` | 0.336 | high | 1/1 | (1306, 1314) |
| 5 | `django/forms/models.py::ModelMultipleChoiceField.to_python` | 0.324 | high | 1/1 | (1316, 1319) |
| 6 | `django/db/models/fields/related.py::ForeignKey.target_field` | 0.314 | high | 1/1 | (896, 897) |
| 7 | `django/db/models/fields/related.py::ForeignObject.get_lookups` | 0.273 | high | 1/1 | (740, 744) |
| 8 | `django/db/models/query.py::QuerySet.distinct` | 0.269 | high | 1/1 | (1150, 1159) |
| 9 | `django/db/models/query.py::QuerySet.complex_filter` | 0.200 | high | 1/1 | (968, 983) |
| 10 | `django/contrib/admin/filters.py::ListFilter.queryset` | 0.140 | high | 1/1 | (48, 52) |
