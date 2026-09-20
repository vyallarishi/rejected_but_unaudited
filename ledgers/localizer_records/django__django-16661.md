# Instance: `django__django-16661`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
ModelAdmin.lookup_allowed() incorrectly raises DisallowedModelAdminLookup lookup with foreign key as primary key
Description
	 
		(last modified by Tim Graham)
	 
Wrote a failing test for tests/modeladmin/tests.py to demonstrate - same test/code passes on 1.8
@isolate_apps('modeladmin')
def test_lookup_allowed_foreign_primary(self):
	class Country(models.Model):
		name = models.CharField(max_length=256)
	class Place(models.Model):
		country = models.ForeignKey(Country, models.CASCADE)
	class Restaurant(models.Model):
		place = models.OneToOneField(Place, models.CASCADE, primary_key=True)
	class Waiter(models.Model):
		restaurant = models.ForeignKey(Restaurant, models.CASCADE)
	class WaiterAdmin(ModelAdmin):
		list_filter = [
			'restaurant__place__country',
		]
	ma = WaiterAdmin(Waiter, self.site)
	self.assertIs(ma.lookup_allowed('restaurant__place__country', 'test_value'), True)
I think this is caused by the admin thinking that having a foreign key field as a primary key is the same as concrete inheritance. So when you try and check lookups for restaurant__place__country it thinks 'place' is the concrete parent of 'restaurant' and shortcuts it to restaurant__country which isn't in
```

## Stage 3 — Symptoms extracted

- exception types: `['DisallowedModelAdminLookup']`
- error messages: `[]`
- behaviors: `['incorrect lookup', 'incorrectly identifies foreign key field as concrete inheritance', 'shortcuts lookup']`
- named APIs: `['ModelAdmin.lookup_allowed', 'models.Model', 'models.CharField', 'models.ForeignKey', 'models.OneToOneField', 'ModelAdmin']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/contrib/admin/options.py` | ModelAdmin.lookup_allowed() is the function reported as having the bug. |
| 2 | `django/contrib/admin/views/main.py` | ChangeList.get_results() calls lookup_allowed() to filter the queryset. |
| 3 | `django/contrib/admin/exceptions.py` | Defines the DisallowedModelAdminLookup exception raised by lookup_allowed(). |
| 4 | `django/contrib/admin/filters.py` | ModelAdmin list_filter uses this to generate filters. |
| 5 | `django/contrib/admin/tests.py` | Contains tests for the admin functionality, including modeladmin. |
| 6 | `django/contrib/admin/utils.py` | Utility functions used by the admin, including functions to get fields from paths. |
| 7 | `django/contrib/admin/checks.py` | ModelAdmin checks include checks for list_filter. |
| 8 | `django/db/models/fields/related.py` | Foreign key fields are involved in the lookup issue. |
| 9 | `django/db/models/fields/__init__.py` | Base field class. |
| 10 | `tests/modeladmin/tests.py` | Contains the failing test case demonstrating the issue. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/contrib/admin/checks.py::BaseModelAdminChecks._check_autocomplete_fields_item`

- **Q1 Role.** This function validates a single item within a ModelAdmin's `autocomplete_fields` option during Django's system check process.
- **Q2 Connection to symptom.** No plausible path exists. This function is part of the system check framework, which runs on application startup to validate ModelAdmin configuration. The symptom, a `DisallowedModelAdminLookup` exception, occurs at runtime when `lookup_allowed` is called during a request. The failing test case does not involve `autocomplete_fields`, so this function is not executed on the path to the bug.
- **Q3 Counterfactual.** `no` — Modifying this function would have no effect on the symptom because it is not called in the code path that leads to the bug. The bug is in runtime lookup logic, not static configuration checks.
- **Q4 Alternatives considered.**
  - `django.contrib.admin.options.ModelAdmin.lookup_allowed` — This is the function that raises the exception and is the most likely location of the bug's logic.
  - `django.contrib.admin.utils.get_fields_from_path` — This utility is likely used by `lookup_allowed` to traverse relationship paths and may contain the faulty logic that misinterprets the OneToOneField.
  - `Model._meta.get_field` — The properties of the field object returned by this method, such as `parent_link`, might be the source of the misinterpretation.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function performs static checks on `autocomplete_fields` and is not involved in the runtime `lookup_allowed` logic that causes the bug.

#### ✗ REJECTED — `django/contrib/admin/checks.py::BaseModelAdminChecks._check_prepopulated_fields`

- **Q1 Role.** This function validates the `prepopulated_fields` attribute of a ModelAdmin during Django's system check process.
- **Q2 Connection to symptom.** No plausible path exists. This function, like the others in this file, is part of the system check framework and runs at startup, not during the runtime request that triggers the bug. The test case does not use `prepopulated_fields`, and this function is not on the execution path leading to the `DisallowedModelAdminLookup` exception.
- **Q3 Counterfactual.** `no` — Modifying this function would not fix the symptom because it is unrelated to the runtime execution of `lookup_allowed`.
- **Q4 Alternatives considered.**
  - `django.contrib.admin.options.ModelAdmin.lookup_allowed` — This is the function that raises the exception and is the most likely location of the bug's logic.
  - `django.contrib.admin.utils.get_fields_from_path` — This utility is likely used by `lookup_allowed` to traverse relationship paths and may contain the faulty logic that misinterprets the OneToOneField.
  - `Model._meta.get_field` — The properties of the field object returned by this method, such as `parent_link`, might be the source of the misinterpretation.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function performs static checks on `prepopulated_fields` and is not part of the runtime path that triggers the exception.

#### ✗ REJECTED — `django/contrib/admin/checks.py::BaseModelAdminChecks._check_fields`

- **Q1 Role.** This function validates the `fields` and `fieldsets` attributes of a ModelAdmin during Django's system check process.
- **Q2 Connection to symptom.** No plausible path exists. This is a system check function that validates admin form field configurations at startup. The bug occurs at runtime in the admin list view when processing `list_filter` lookups. This function is not on the execution path that triggers the `DisallowedModelAdminLookup` exception.
- **Q3 Counterfactual.** `no` — Modifying this function would have no impact on the bug, as it's not part of the execution path. The problem is in how `lookup_allowed` interprets model relationships.
- **Q4 Alternatives considered.**
  - `django.contrib.admin.options.ModelAdmin.lookup_allowed` — This is the function that raises the exception and is the most likely location of the bug's logic.
  - `django.contrib.admin.utils.get_fields_from_path` — This utility is likely used by `lookup_allowed` to traverse relationship paths and may contain the faulty logic that misinterprets the OneToOneField.
  - `Model._meta.get_field` — The properties of the field object returned by this method, such as `parent_link`, might be the source of the misinterpretation.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a static check function for admin form fields and is irrelevant to the runtime `list_filter` lookup logic where the bug occurs.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/admin/checks.py::BaseModelAdminChecks._check_autocomplete_fields_item` | high | This function performs static checks on `autocomplete_fields` and is not involved in the runtime `lookup_allowed` logic that causes the bug. |  |
| `django/contrib/admin/checks.py::BaseModelAdminChecks._check_prepopulated_fields` | high | This function performs static checks on `prepopulated_fields` and is not part of the runtime path that triggers the exception. |  |
| `django/contrib/admin/checks.py::BaseModelAdminChecks._check_fields` | high | This is a static check function for admin form fields and is irrelevant to the runtime `list_filter` lookup logic where the bug occurs. |  |

**Causal chains (per candidate)**

- `django/contrib/admin/checks.py::BaseModelAdminChecks._check_autocomplete_fields_item`  (score=0.0)  \
  
- `django/contrib/admin/checks.py::BaseModelAdminChecks._check_prepopulated_fields`  (score=0.0)  \
  
- `django/contrib/admin/checks.py::BaseModelAdminChecks._check_fields`  (score=0.0)  \
  

**next_to_explore:** `['django.contrib.admin.options.ModelAdmin.lookup_allowed', 'django.contrib.admin.utils.get_fields_from_path', 'django.db.models.options.Options.get_field']`

### Abductive step #2 (iteration=6)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/contrib/admin/options.py::BaseModelAdmin.lookup_allowed`

- **Q1 Role.** This function determines if a given lookup path is permitted for filtering in the admin, primarily by checking against `list_filter`.
- **Q2 Connection to symptom.** Yes, a path exists. The function is called with `lookup='restaurant__place__country'`. When iterating through the path, it processes 'place' after 'restaurant'. Because the 'place' field is the primary key of the `Restaurant` model, it is also the target field of the 'restaurant' foreign key relation. The logic `field not in prev_field.path_infos[-1].target_fields` then evaluates to false, causing 'place' to be omitted from `relation_parts`. This results in a shortened, incorrect lookup path 'restaurant__country', which is not found in `list_filter`, leading to a failure that results in a `DisallowedModelAdminLookup` exception.
- **Q3 Counterfactual.** `yes` — If the logic were corrected to not skip path components that are themselves relations (like the OneToOneField primary key), the full path 'restaurant__place__country' would be validated against `list_filter`, it would be found, and the function would return True, eliminating the symptom.
- **Q4 Alternatives considered.**
  - `django/db/models/options.py::Options.get_field` — This provides the field objects, but the objects themselves are correct; the fault is in how `lookup_allowed` interprets them.
  - `Field.path_infos` — The metadata on the field could be wrong, but it's more likely that the logic consuming the metadata is flawed, as it's a complex edge case.
  - `django/contrib/admin/utils.py::get_fields_from_path` — This function is not called in the failing code path, so it's irrelevant to the direct cause.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function contains the specific logic that incorrectly shortens the lookup path due to misinterpreting a OneToOneField primary key, which directly causes the validation failure.

#### ✗ REJECTED — `django/contrib/admin/utils.py::get_fields_from_path`

- **Q1 Role.** This utility function traverses a lookup path string relative to a model and returns the corresponding list of Field objects.
- **Q2 Connection to symptom.** No path exists. This function is not called by `BaseModelAdmin.lookup_allowed`, which contains the faulty logic. The bug occurs because `lookup_allowed` implements its own, different path traversal logic instead of using a utility like this one.
- **Q3 Counterfactual.** `no` — Modifying this function would have no effect on the symptom, as it is not part of the execution path that triggers the bug.
- **Q4 Alternatives considered.**
  - `django/contrib/admin/options.py::BaseModelAdmin.lookup_allowed` — This is the function that actually contains the bug and should be the focus.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is not in the call stack for the failing operation and therefore cannot be the cause of the symptom.

#### ✗ REJECTED — `django/db/models/options.py::Options.get_field`

- **Q1 Role.** This method on a model's `_meta` options retrieves a field instance by its name, searching both forward and reverse relations.
- **Q2 Connection to symptom.** No path exists. While this function is called by `lookup_allowed` to retrieve field objects for 'restaurant', 'place', and 'country', it correctly returns the appropriate field objects. The bug is not in the data provided by `get_field`, but in the subsequent logic within `lookup_allowed` that interprets the returned field objects' properties.
- **Q3 Counterfactual.** `no` — This is a core ORM utility that is behaving as expected. Modifying it to work around the caller's incorrect logic would likely break other parts of Django.
- **Q4 Alternatives considered.**
  - `django/contrib/admin/options.py::BaseModelAdmin.lookup_allowed` — Preferred, as it is the consumer of `get_field`'s output and contains the faulty conditional logic.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a standard utility that correctly supplies field metadata; the fault lies with the caller's interpretation of that metadata.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/admin/options.py::BaseModelAdmin.lookup_allowed` | high | This function contains the specific logic that incorrectly shortens the lookup path due to misinterpreting a OneToOneField primary key, which directly causes the validation failure. | The conditional that appends to `relation_parts` must be changed to not collapse a path segment if that segment is itself a relation, even if it is also the tar |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/admin/utils.py::get_fields_from_path` | high | This function is not in the call stack for the failing operation and therefore cannot be the cause of the symptom. |  |
| `django/db/models/options.py::Options.get_field` | high | This function is a standard utility that correctly supplies field metadata; the fault lies with the caller's interpretation of that metadata. |  |

**Causal chains (per candidate)**

- `django/contrib/admin/options.py::BaseModelAdmin.lookup_allowed`  (score=10.0)  \
  The function receives the lookup 'restaurant__place__country'. → It iterates on the path parts. When processing 'place', the previous field is the FK 'restaurant' and the current field is the OneToOneField 'place'. → The 'place' field is the primary key of the Restaurant model, so it is one of the `target_fields` for the incoming 'restaurant' relation. → The condition `field not in prev_field.path_infos[-1].target_fields` evaluates to `False`. → Consequently, 'place' is not appended to `relation_parts`, which becomes `['restaurant', 'country']`. → The reconstructed path 'restaurant__country' is checked against `list_filter`.
- `django/contrib/admin/utils.py::get_fields_from_path`  (score=0.0)  \
  
- `django/db/models/options.py::Options.get_field`  (score=0.0)  \
  

**next_to_explore:** `['django.contrib.admin.views.main.ChangeList.get_filters', 'django.db.models.fields.related.RelatedField.contribute_to_class', 'django.db.models.fields.related.PathInfo']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/contrib/admin/options.py::BaseModelAdmin.lookup_allowed` | 1.0 |
| 2 | `django/contrib/admin/utils.py::get_fields_from_path` | 0.1 |
| 3 | `django/db/models/options.py::Options.get_field` | 0.05 |
| 4 | `django/contrib/admin/options.py::BaseModelAdmin.to_field_allowed` | 0.01 |
| 5 | `django/contrib/admin/options.py::BaseModelAdmin.get_field_queryset` | 0.01 |
| 6 | `django/contrib/admin/filters.py::RelatedFieldListFilter.field_admin_ordering` | 0.01 |
| 7 | `django/contrib/admin/options.py::ModelAdmin.get_object` | 0.01 |
| 8 | `django/contrib/admin/checks.py::BaseModelAdminChecks._check_autocomplete_fields_item` | 0.0 |
| 9 | `django/contrib/admin/checks.py::BaseModelAdminChecks._check_prepopulated_fields` | 0.0 |
| 10 | `django/contrib/admin/checks.py::BaseModelAdminChecks._check_fields` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/contrib/admin/options.py::BaseModelAdmin.lookup_allowed` | 1.000 | high | 1/1 | (439, 497) |
| 2 | `django/contrib/admin/filters.py::EmptyFieldListFilter.get_lookup_condition` | 0.282 | high | 1/1 | (663, 669) |
| 3 | `django/contrib/admin/filters.py::SimpleListFilter.lookups` | 0.253 | high | 1/1 | (120, 127) |
| 4 | `django/contrib/admin/views/main.py::ChangeList.get_ordering_field` | 0.186 | high | 1/1 | (339, 361) |
| 5 | `django/contrib/admin/views/main.py::ChangeList.has_related_field_in_list_display` | 0.171 | high | 1/1 | (591, 602) |
| 6 | `django/contrib/admin/views/main.py::ChangeList.apply_select_related` | 0.113 | high | 1/1 | (579, 589) |
| 7 | `django/contrib/admin/utils.py::get_fields_from_path` | 0.100 | high | 1/1 | (517, 534) |
| 8 | `django/db/models/options.py::Options.get_field` | 0.050 | high | 1/1 | (660, 685) |
| 9 | `django/contrib/admin/options.py::BaseModelAdmin.to_field_allowed` | 0.010 | high | 1/1 | (499, 543) |
| 10 | `django/contrib/admin/options.py::BaseModelAdmin.get_field_queryset` | 0.010 | high | 1/1 | (243, 256) |
