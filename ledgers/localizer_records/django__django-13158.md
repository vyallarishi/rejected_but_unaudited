# Instance: `django__django-13158`

- runs: 1   termination: `ledger_informed`   think-high calls: 3

## Issue (truncated to 1200 chars)

```
QuerySet.none() on combined queries returns all results.
Description
	
I came across this issue on Stack Overflow. I'm not 100% sure it's a bug, but it does seem strange. With this code (excuse the bizarre example filtering):
class Publication(models.Model):
	pass
class Article(models.Model):
	publications = models.ManyToManyField(to=Publication, blank=True, null=True)
class ArticleForm(forms.ModelForm):
	publications = forms.ModelMultipleChoiceField(
		Publication.objects.filter(id__lt=2) | Publication.objects.filter(id__gt=5),
		required=False,
	)
	class Meta:
		model = Article
		fields = ["publications"]
class ArticleAdmin(admin.ModelAdmin):
	form = ArticleForm
This works well. However, changing the ModelMultipleChoiceField queryset to use union() breaks things.
publications = forms.ModelMultipleChoiceField(
	Publication.objects.filter(id__lt=2).union(
		Publication.objects.filter(id__gt=5)
	),
	required=False,
)
The form correctly shows only the matching objects. However, if you submit this form while empty (i.e. you didn't select any publications), ALL objects matching the queryset will be added. Using the OR query, NO objects are added, as I'd expect.
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['returns all results', 'form shows only matching objects', 'all objects matching the queryset will be added', 'no objects are added']`
- named APIs: `['QuerySet.none', 'Publication.objects.filter', 'forms.ModelMultipleChoiceField', 'Publication.objects.filter.union']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/forms/models.py` | The issue involves ModelForms and their interaction with QuerySets, suggesting edits in form processing. |
| 2 | `django/contrib/admin/options.py` | The admin interface is where the ModelMultipleChoiceField is used, and the issue occurs when submitting the form, indicating a problem with admin form handling. |
| 3 | `django/db/models/query.py` | The core issue is that QuerySet.none() is not behaving as expected when combined with union(), suggesting a problem with QuerySet evaluation. |
| 4 | `django/db/models/fields/related.py` | ModelMultipleChoiceField uses related fields, and the issue involves how these fields are handled in forms. |
| 5 | `django/forms/fields.py` | The issue involves ModelMultipleChoiceField, which is a form field, and how it interacts with QuerySets. |
| 6 | `django/db/models/expressions.py` | union() is used to combine QuerySets, so the expression evaluation might be the cause. |
| 7 | `django/db/models/sql/query.py` | The issue is related to how SQL queries are constructed and executed, especially when using union(). |
| 8 | `django/db/models/sql/compiler.py` | SQLCompiler is responsible for converting query expressions into SQL, and the issue might be related to how union() queries are compiled. |
| 9 | `django/db/models/lookups.py` | Lookups are used to filter QuerySets, and the issue might be related to how lookups are handled in union() queries. |
| 10 | `django/core/management/commands/migrate.py` | While not directly related, migrations can sometimes expose underlying database issues, and it's worth considering if the issue is related to migration handling |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 1, rejected: 1

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/db/models/query.py::QuerySet.none`

- **Q1 Role.** This function returns a new, empty QuerySet based on the current one.
- **Q2 Connection to symptom.** A plausible execution path is that the form processing logic for an empty `ModelMultipleChoiceField` calls `.none()` on the field's queryset to represent an empty selection. The queryset in this case was created with `.union()`. The `none()` method calls `clone.query.set_empty()`. If `set_empty()` does not correctly handle query objects with a `combinator` (like 'union'), it would fail to make the query empty. When this supposedly empty queryset is later evaluated, it would execute the original `union` query, thus returning all results and causing the bug.
- **Q3 Counterfactual.** `yes` — If this function were modified to detect if the queryset is a combined one (e.g., `if self.query.combinator:`) and then return a fresh, guaranteed-empty queryset for the model (e.g., `return self.model._default_manager.none()`), the symptom would be eliminated.
- **Q4 Alternatives considered.**
  - `django.db.models.sql.query.Query.set_empty` — This is the likely root cause, as it's responsible for emptying the query, but fixing it in `QuerySet.none` is also a valid, higher-level solution.
  - `forms.ModelMultipleChoiceField.clean` — This is the likely caller of `QuerySet.none`, but the fault lies in how `none()` behaves, not in the caller's logic.
  - `QuerySet.union` — This creates the problematic state, but the failure is in handling that state, not creating it.
- **Q5 Verdict.** `leading` (confidence: `high`) — This API method fails on combined queries because its implementation via `query.set_empty()` is insufficient for them, and it can be fixed here.

#### ✗ REJECTED — `django/db/models/query.py::QuerySet._not_support_combined_queries`

- **Q1 Role.** This is a helper function to raise a `NotSupportedError` if a specific operation is called on a combined queryset.
- **Q2 Connection to symptom.** No path exists. The symptom (incorrect data) occurs precisely because an error is *not* raised. If `QuerySet.none()` had called this helper, the user would have seen a `NotSupportedError` instead of the silent failure. The absence of a call to this function allows the bug to manifest.
- **Q3 Counterfactual.** `no` — Modifying only this function would have no effect, as it is not being called in the problematic execution path. The fix would require adding a call to it from another function, like `QuerySet.none()`.
- **Q4 Alternatives considered.**
  - `QuerySet.none` — This is the function that should be calling this helper (or otherwise handling the combined query case).
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a utility function that is not called; the bug is in the caller (`QuerySet.none`) which should either use this or handle the case correctly.

#### … CONSIDERING — `django/db/models/query.py::QuerySet.union`

- **Q1 Role.** This function combines the current QuerySet with other querysets using the SQL UNION operator.
- **Q2 Connection to symptom.** This function creates the combined queryset that triggers the bug. It does so by calling `_combinator_query`, which sets the `query.combinator` attribute on the underlying query object. This attribute is what causes the subsequent call to `QuerySet.none()` to fail, as the `set_empty()` method it calls does not correctly handle this state.
- **Q3 Counterfactual.** `partially` — One could modify this function to return a special subclass of `QuerySet` with a corrected `none()` method. However, the more direct fix is to correct `QuerySet.none()` itself to handle all `QuerySet` instances properly.
- **Q4 Alternatives considered.**
  - `QuerySet.none` — This is a more direct location for the fix, as it's the method whose contract is being violated.
  - `QuerySet._combinator_query` — This is the internal generic method for `union`, `intersection`, etc. It's a slightly better target than `union` alone.
  - `django.db.models.sql.query.Query.set_empty` — This is the most likely root cause, as it fails to handle the query state created by `union`.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function creates the combined queryset state that `QuerySet.none()` mishandles, making it a necessary precondition for the bug.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/query.py::QuerySet.none` | high | This API method fails on combined queries because its implementation via `query.set_empty()` is insufficient for them, and it can be fixed here. | Check for `self.query.combinator` and if present, return a fresh empty queryset like `self.model._default_manager.none()` instead of calling `set_empty()`. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/query.py::QuerySet.union` | medium | This function creates the combined queryset state that `QuerySet.none()` mishandles, making it a necessary precondition for the bug. | Consider returning a `CombinedQuerySet` subclass with a corrected `none()` implementation. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/query.py::QuerySet._not_support_combined_queries` | high | This is a utility function that is not called; the bug is in the caller (`QuerySet.none`) which should either use this or handle the case correctly. |  |

**Causal chains (per candidate)**

- `django/db/models/query.py::QuerySet.none`  (score=9.0)  \
  A ModelMultipleChoiceField with a union() queryset is submitted with no selections. → The form's clean() method calls .none() on this queryset. → QuerySet.none() calls self.query.set_empty() on the combined query. → Query.set_empty() fails to clear the components of the combined query. → The 'empty' queryset is evaluated, executing the original union query and returning all results.
- `django/db/models/query.py::QuerySet._not_support_combined_queries`  (score=0.0)  \
  
- `django/db/models/query.py::QuerySet.union`  (score=7.0)  \
  User code calls .union() on a queryset. → This function creates a QuerySet whose underlying query has `combinator='union'`. → This combined queryset is passed to a ModelMultipleChoiceField. → A subsequent call to .none() on this queryset fails (see chain for QuerySet.none).

**next_to_explore:** `['django.db.models.sql.query.Query.set_empty', 'django.forms.models.ModelMultipleChoiceField.clean', 'django.db.models.query.QuerySet._combinator_query', 'django.db.models.query.QuerySet.__or__', 'django.db.models.query.QuerySet._chain']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 0, rejected: 0

### Abductive step #3 (iteration=12)

- leading: 1, considering: 0, rejected: 4

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/db/models/sql/query.py::Query.set_empty`

- **Q1 Role.** This function modifies a Query object to ensure it returns no results by adding a `NothingNode` to its WHERE clause.
- **Q2 Connection to symptom.** Yes, an execution path plausibly exists. When `QuerySet.none()` is called on a `union()` queryset, it eventually calls this function. The path is `ModelMultipleChoiceField.clean()` -> `QuerySet.none()` -> `Query.set_empty()`. This function adds a `NothingNode` to the main query's `where` clause. However, for a `union` query (which is a `CombinedQuery`), the final result set is determined by its constituent subqueries, and the `where` clause of the top-level query object might be ignored during SQL generation. This would render the `NothingNode` ineffective, causing the original `union` query to be executed and return all its results.
- **Q3 Counterfactual.** `yes` — If this function were modified to handle combined queries by applying the `set_empty` logic to each subquery instead of the top-level query, `QuerySet.none()` would correctly produce an empty queryset.
- **Q4 Alternatives considered.**
  - `django/db/models/query.py::QuerySet.none` — This is the caller, but the implementation detail of how to make a query empty resides in `Query.set_empty`, making it the more fundamental location for the fix.
  - `django/db/models/query.py::QuerySet.union` — This function creates the problematic query structure, but the issue is about making an *existing* query empty, which is the responsibility of `none()`/`set_empty()`.
  - `django/forms/models.py::ModelMultipleChoiceField.clean` — This function triggers the bug but its logic is sound; it correctly attempts to return an empty queryset for an empty, non-required field.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function's implementation of adding a `NothingNode` is likely ineffective for combined queries like `union`, directly explaining the observed symptom.

#### ✗ REJECTED — `django/forms/models.py::ModelMultipleChoiceField.clean`

- **Q1 Role.** This method validates the input for a multiple-choice model field and returns a queryset of the selected objects.
- **Q2 Connection to symptom.** Yes, this function is on the causal path. When the form is submitted with no selection for a non-required field, the code path `elif not self.required and not value:` is taken, which executes `return self.queryset.none()`. Since `self.queryset` is the problematic `union()` queryset, this call triggers the bug where `.none()` fails and returns all results.
- **Q3 Counterfactual.** `no` — Modifying this function would be a workaround. The function's intent to return an empty queryset is correct; the underlying problem is that `queryset.none()` is not behaving as expected for this specific type of queryset.
- **Q4 Alternatives considered.**
  - `django/db/models/query.py::QuerySet.none` — This is the method called by `clean` that exhibits the bug, making it a more likely root cause.
  - `django/db/models/sql/query.py::Query.set_empty` — This is the underlying implementation of `none()`, and its interaction with combined queries is the most probable cause of the failure.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function correctly triggers the 'return empty queryset' logic but is not the source of the bug, which lies in the implementation of `QuerySet.none()`.

#### ✗ REJECTED — `django/forms/models.py::BaseModelFormSet.get_queryset`

- **Q1 Role.** This method retrieves the queryset for a model formset, which represents the set of objects to be edited by the formset.
- **Q2 Connection to symptom.** No path exists. The issue is with a `ModelMultipleChoiceField` inside a `ModelForm`, which concerns the choices for a single field. This function deals with the queryset for a `ModelFormSet`, which is about managing a collection of forms, a different and unrelated concept.
- **Q3 Counterfactual.** `no` — This function is not on the execution path for the reported bug, so modifying it would have no effect on the symptom.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::ModelChoiceField._get_queryset` — This is related to getting a queryset for a form field, which is more relevant than the formset's queryset.
  - `django/forms/models.py::ModelMultipleChoiceField.clean` — This is the function that processes the field's input and is directly involved in the bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for `ModelFormSet` instances, not the `ModelMultipleChoiceField`'s choices, and is therefore irrelevant to the bug.

#### ✗ REJECTED — `django/forms/models.py::ModelChoiceField._get_queryset`

- **Q1 Role.** This is a simple internal getter method that returns the queryset assigned to the `ModelChoiceField`.
- **Q2 Connection to symptom.** No path exists that would cause the symptom. This function is a simple accessor (`return self._queryset`). While it is called to retrieve the `union()` queryset that `clean()` will operate on, it has no logic and simply passes the object through. It does not contribute to the bug's behavior.
- **Q3 Counterfactual.** `no` — This is a simple, correct getter. There is no modification to be made here that would fix the bug without breaking its fundamental purpose.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::ModelMultipleChoiceField.clean` — The caller of this getter (via the `queryset` property) is where the logic that triggers the bug resides.
  - `django/db/models/query.py::QuerySet.none` — The bug is in the behavior of a method on the object returned by this getter, not in the getter itself.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a trivial getter function that correctly returns the configured queryset; it has no logic that could cause the bug.

#### ✗ REJECTED — `django/contrib/admin/options.py::ModelAdmin.delete_queryset`

- **Q1 Role.** This method, part of the `ModelAdmin` class, deletes a given queryset of objects from the database.
- **Q2 Connection to symptom.** No path exists. The bug report describes an issue with saving a `ManyToManyField` through a form, which results in objects being unexpectedly added. This function is for an entirely different operation: bulk-deleting objects, typically via an admin action. It is not involved in form validation or saving.
- **Q3 Counterfactual.** `no` — This function is not in the execution path of the reported bug, so modifying it would have no effect.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::ModelMultipleChoiceField.clean` — The bug is related to form cleaning, not object deletion.
  - `django/db/models/base.py::Model.save` — The saving process is where the incorrect queryset would be used, but the error originates earlier.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function handles bulk deletion and is completely unrelated to the form submission and M2M assignment process where the bug occurs.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/sql/query.py::Query.set_empty` | high | This function's implementation of adding a `NothingNode` is likely ineffective for combined queries like `union`, directly explaining the observed symptom. | Check if `self` is a combined query; if so, recursively call `set_empty` on all sub-queries instead of modifying the top-level `where` clause. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/models.py::ModelMultipleChoiceField.clean` | high | This function correctly triggers the 'return empty queryset' logic but is not the source of the bug, which lies in the implementation of `QuerySet.none()`. |  |
| `django/forms/models.py::BaseModelFormSet.get_queryset` | high | This function is for `ModelFormSet` instances, not the `ModelMultipleChoiceField`'s choices, and is therefore irrelevant to the bug. |  |
| `django/forms/models.py::ModelChoiceField._get_queryset` | high | This is a trivial getter function that correctly returns the configured queryset; it has no logic that could cause the bug. |  |
| `django/contrib/admin/options.py::ModelAdmin.delete_queryset` | high | This function handles bulk deletion and is completely unrelated to the form submission and M2M assignment process where the bug occurs. |  |

**Causal chains (per candidate)**

- `django/db/models/sql/query.py::Query.set_empty`  (score=9.0)  \
  A `ModelMultipleChoiceField` with `required=False` is submitted with no value. → `ModelMultipleChoiceField.clean` is called and its logic decides to return an empty queryset. → It calls `self.queryset.none()`, where `self.queryset` is one created with `union()`. → `QuerySet.none()` clones the queryset and calls `query.set_empty()` on the clone's query object. → `Query.set_empty()` adds a `NothingNode` to the `where` clause of the top-level `Query` object. → For a `CombinedQuery` (like `union`), the SQL compilation process ignores the top-level `where` clause, instead relying on the subqueries.
- `django/forms/models.py::ModelMultipleChoiceField.clean`  (score=0.0)  \
  
- `django/forms/models.py::BaseModelFormSet.get_queryset`  (score=0.0)  \
  
- `django/forms/models.py::ModelChoiceField._get_queryset`  (score=0.0)  \
  
- `django/contrib/admin/options.py::ModelAdmin.delete_queryset`  (score=0.0)  \
  

**next_to_explore:** `['django/db/models/query.py::QuerySet.none', 'django/db/models/query.py::QuerySet.union', 'django/db/models/sql/compiler.py::SQLCompiler.as_sql', 'django/db/models/sql/query.py::Query._clone', 'django/db/models/sql/query.py::CombinedQuery']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/db/models/sql/query.py::Query.set_empty` | 0.95 |
| 2 | `django/db/models/query.py::QuerySet.none` | 0.85 |
| 3 | `django/db/models/query.py::QuerySet.union` | 0.5 |
| 4 | `django/db/models/query.py::QuerySet._combinator_query` | 0.2 |
| 5 | `django/db/models/query.py::QuerySet._not_support_combined_queries` | 0.1 |
| 6 | `django/db/models/query.py::QuerySet.__or__` | 0.01 |
| 7 | `django/db/models/query.py::QuerySet.intersection` | 0.0 |
| 8 | `django/db/models/query.py::QuerySet.first` | 0.0 |
| 9 | `django/db/models/query.py::QuerySet.__and__` | 0.0 |
| 10 | `django/forms/models.py::BaseModelFormSet.get_queryset` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/db/models/sql/query.py::Query.set_empty` | 0.950 | high | 1/1 | (1778, 1779) |
| 2 | `django/db/models/query.py::QuerySet.none` | 0.850 | high | 1/1 | (919, 923) |
| 3 | `django/db/models/query.py::QuerySet.union` | 0.500 | high | 1/1 | (999, 1004) |
| 4 | `django/forms/models.py::ModelMultipleChoiceField.clean` | 0.329 | high | 1/1 | (1321, 1336) |
| 5 | `django/contrib/admin/options.py::ModelAdmin.delete_queryset` | 0.313 | high | 1/1 | (1105, 1107) |
| 6 | `django/db/models/query.py::QuerySet._chain` | 0.307 | high | 1/1 | (1277, 1287) |
| 7 | `django/forms/models.py::ModelChoiceField._set_queryset` | 0.248 | high | 1/1 | (1231, 1233) |
| 8 | `django/forms/models.py::ModelChoiceField._get_queryset` | 0.245 | high | 1/1 | (1228, 1229) |
| 9 | `django/contrib/admin/options.py::InlineModelAdmin.get_queryset` | 0.242 | high | 1/1 | (2142, 2146) |
| 10 | `django/contrib/admin/options.py::ModelAdmin.get_search_results` | 0.235 | high | 1/1 | (987, 1035) |
