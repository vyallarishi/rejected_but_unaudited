# Instance: `django__django-13033`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
Self referencing foreign key doesn't correctly order by a relation "_id" field.
Description
	
Initially discovered on 2.2.10 but verified still happens on 3.0.6. Given the following models:
class OneModel(models.Model):
	class Meta:
		ordering = ("-id",)
	id = models.BigAutoField(primary_key=True)
	root = models.ForeignKey("OneModel", on_delete=models.CASCADE, null=True)
	oneval = models.BigIntegerField(null=True)
class TwoModel(models.Model):
	id = models.BigAutoField(primary_key=True)
	record = models.ForeignKey(OneModel, on_delete=models.CASCADE)
	twoval = models.BigIntegerField(null=True)
The following queryset gives unexpected results and appears to be an incorrect SQL query:
qs = TwoModel.objects.filter(record__oneval__in=[1,2,3])
qs = qs.order_by("record__root_id")
print(qs.query)
SELECT "orion_twomodel"."id", "orion_twomodel"."record_id", "orion_twomodel"."twoval" FROM "orion_twomodel" INNER JOIN "orion_onemodel" ON ("orion_twomodel"."record_id" = "orion_onemodel"."id") LEFT OUTER JOIN "orion_onemodel" T3 ON ("orion_onemodel"."root_id" = T3."id") WHERE "orion_onemodel"."oneval" IN (1, 2, 3) ORDER BY T3."id" DESC
The query has an unexpected DESCENDING sort. That appears to c
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `['incorrect SQL query', 'unexpected DESCENDING sort', 'unnecessary extra join']`
- behaviors: `['incorrect ordering by relation field', 'unexpected descending sort order', 'unnecessary joins in SQL query']`
- named APIs: `['models.Model', 'models.BigAutoField', 'models.ForeignKey', 'models.CASCADE', 'TwoModel.objects.filter', 'qs.order_by', 'qs.query', 'qs.annotate', 'F']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/db/models/sql/query.py` | Modifying the SQL query generation to handle self-referencing foreign keys correctly. |
| 2 | `django/db/models/sql/compiler.py` | Related to SQL compilation and potential issues with join generation. |
| 3 | `django/db/models/fields/related.py` | The issue involves foreign keys, so this file is relevant. |
| 4 | `django/db/models/base.py` | Model definition and related meta options might be involved. |
| 5 | `django/db/models/lookups.py` | Custom lookups might be needed to handle the ordering correctly. |
| 6 | `django/db/backends/base/operations.py` | Database operations are relevant to SQL generation. |
| 7 | `django/db/backends/base/schema.py` | Schema generation might be affected by the incorrect SQL. |
| 8 | `django/db/models/query_utils.py` | Q object combination and filter application might be involved. |
| 9 | `django/db/models/options.py` | Model options and ordering might be related to the issue. |
| 10 | `django/db/models/fields/__init__.py` | Field definitions are relevant to the issue. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 0, considering: 1, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/db/models/fields/related.py::ForeignObject.get_reverse_joining_columns`

- **Q1 Role.** This function is a simple wrapper that returns the names of the database columns used to join from a related model back to the current model.
- **Q2 Connection to symptom.** No plausible path exists. This function merely provides column names for a reverse join. It has no role in deciding *whether* to create a join, what kind of join to create (INNER vs OUTER), or how to apply ordering clauses. The bug is about incorrect join creation and ordering logic, which happens at a much higher level in the query construction process.
- **Q3 Counterfactual.** `no` — Modifying this function would likely break all reverse relations in Django. It would not fix the specific issue of an unnecessary join and incorrect sort order being generated for a specific `order_by` pattern, as this function does not contain that logic.
- **Q4 Alternatives considered.**
  - `django.db.models.sql.query.Query.setup_joins` — Preferred, as this is where the decision to add joins based on a field path is made.
  - `django.db.models.sql.query.Query.add_ordering` — Preferred, as this function interprets the user's `order_by` arguments and orchestrates join setup and expression creation.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a low-level helper for relation joins and is unrelated to the high-level logic for query ordering.

#### … CONSIDERING — `django/db/models/sql/compiler.py::SQLCompiler.get_order_by`

- **Q1 Role.** This function generates the final list of SQL expressions and parameters that will form the `ORDER BY` clause of the SQL query.
- **Q2 Connection to symptom.** Yes, a plausible path exists. Upstream logic in `Query.add_ordering` incorrectly processes `order_by("record__root_id")` on a self-referencing FK with a default ordering. It creates an `OrderBy` expression with `descending=True` based on the related model's `Meta.ordering`. This function, `get_order_by`, receives this faulty `OrderBy` expression from `self.query.order_by`, trusts its `descending=True` flag, and consequently generates the `ORDER BY ... DESC` SQL, thus producing the observed symptom.
- **Q3 Counterfactual.** `partially` — A patch in this function could ignore the `descending` flag from the upstream expression and re-determine the sort direction, fixing the symptom. However, the root cause is the incorrect creation of the `OrderBy` expression upstream.
- **Q4 Alternatives considered.**
  - `django.db.models.sql.query.Query.add_ordering` — Preferred as the likely root cause, since it's responsible for parsing `order_by` strings and creating the `OrderBy` expressions.
  - `django.db.models.sql.query.Query.setup_joins` — A strong candidate, as it's called by `add_ordering` and is where the extra join is created and the related model's `Meta` is likely inspected.
  - `django.db.models.query.QuerySet.order_by` — Not preferred, as it's mostly a public API wrapper that calls `Query.add_ordering`.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function is the final step that renders the incorrect ordering into SQL, but the faulty logic that determines the ordering direction is located upstream.

#### ✗ REJECTED — `django/db/models/base.py::make_foreign_order_accessors`

- **Q1 Role.** This function dynamically attaches `get_..._order()` and `set_..._order()` methods to a model, which are used to manage the explicit ordering of related objects when `order_with_respect_to` is used on a `ForeignKey` or `ManyToManyField`.
- **Q2 Connection to symptom.** No plausible path exists. The feature this function supports, `order_with_respect_to`, is not used in the models provided in the bug report. The bug is related to `QuerySet.order_by()`, which is a completely separate ordering mechanism. Therefore, this function is not executed in the code path that produces the symptom.
- **Q3 Counterfactual.** `no` — Since this function is not involved in the execution path for `QuerySet.order_by()`, modifying it would have no effect on the reported bug.
- **Q4 Alternatives considered.**
  - `django.db.models.sql.query.Query.add_ordering` — The correct area to investigate, as it handles `QuerySet.order_by()` calls.
  - `django.db.models.options.Options` — The `Meta` class implementation is relevant, but the logic that *uses* its `ordering` attribute incorrectly is the actual bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is part of an unrelated Django feature (`order_with_respect_to`) and is not involved in the bug.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/sql/compiler.py::SQLCompiler.get_order_by` | high | This function is the final step that renders the incorrect ordering into SQL, but the faulty logic that determines the ordering direction is located upstream. | A patch could be added here to override the `descending` property of the incoming `OrderBy` expression if it was generated from a user's explicit `order_by` cal |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/fields/related.py::ForeignObject.get_reverse_joining_columns` | high | This is a low-level helper for relation joins and is unrelated to the high-level logic for query ordering. |  |
| `django/db/models/base.py::make_foreign_order_accessors` | high | This function is part of an unrelated Django feature (`order_with_respect_to`) and is not involved in the bug. |  |

**Causal chains (per candidate)**

- `django/db/models/fields/related.py::ForeignObject.get_reverse_joining_columns`  (score=0.0)  \
  
- `django/db/models/sql/compiler.py::SQLCompiler.get_order_by`  (score=6.0)  \
  An upstream function (likely `Query.add_ordering`) incorrectly interprets `order_by('record__root_id')`. → It creates an extra join and an `OrderBy` expression that wrongly inherits `descending=True` from the related model's `Meta.ordering`. → `get_order_by` receives this faulty `OrderBy` expression via `self.query.order_by`. → The function processes the expression and generates the `ORDER BY ... DESC` clause in the final SQL. → This directly causes the symptom of an unexpected descending sort.
- `django/db/models/base.py::make_foreign_order_accessors`  (score=0.0)  \
  

**next_to_explore:** `['django.db.models.sql.query.Query.add_ordering', 'django.db.models.sql.query.Query.setup_joins', 'django.db.models.sql.query.Query.resolve_ref', 'django.db.models.options.Options.get_field']`

### Abductive step #2 (iteration=6)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/db/models/sql/query.py::Query.add_ordering`

- **Q1 Role.** This function adds field names or expressions to be used in the SQL ORDER BY clause to the query's internal ordering list.
- **Q2 Connection to symptom.** No path. This function is called by `qs.order_by(...)` and it correctly appends the ordering string, like `"record__root_id"`, to an internal list (`self.order_by`). It performs some basic validation by calling `self.names_to_path`, but the core logic that interprets this string to generate joins and SQL `ORDER BY` clauses happens much later in the query compilation process. The function itself does not generate any part of the incorrect SQL.
- **Q3 Counterfactual.** `no` — Modifying this function would not fix the bug, as it correctly captures the user's requested ordering. The problem lies downstream in how the stored ordering string is interpreted.
- **Q4 Alternatives considered.**
  - `django.db.models.sql.compiler.SQLCompiler.get_order_by` — This is a much more likely candidate as it's responsible for converting the ordering list into SQL, which is where the misinterpretation must occur.
  - `django.db.models.sql.query.Query.setup_joins` — This function is called during compilation to create joins, and since an incorrect join is a symptom, it is directly implicated.
  - `django.db.models.sql.query.Query.names_to_path` — This function, called by `add_ordering`, resolves lookup paths and could be the first place the misinterpretation of `root_id` happens.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function merely adds the ordering string to a list; the complex logic for path resolution and SQL generation happens elsewhere.

#### ✓ LEADING — `django/db/models/sql/query.py::Query.setup_joins`

- **Q1 Role.** This function computes and adds the necessary table joins to the query for a given lookup path.
- **Q2 Connection to symptom.** Yes, a plausible path exists. The `order_by` compilation logic will call `setup_joins` with the path `['record', 'root_id']`. When processing the `root_id` segment on the `OneModel` table, this function incorrectly decides to create a new join to the `OneModel` table for the `root` relation, instead of recognizing `root_id` as a column on the already-joined table. This action directly produces the "unnecessary extra join" symptom. This incorrect join is then used by the compiler to apply the related model's default ordering, leading to the "unexpected DESCENDING sort".
- **Q3 Counterfactual.** `yes` — If `setup_joins` were modified to correctly identify that a lookup ending in `_id` (matching a foreign key's `attname`) refers to a column and should not trigger a join, the incorrect join would not be created. This would force the compiler to use the correct column and default to ASC ordering, fixing both symptoms.
- **Q4 Alternatives considered.**
  - `django.db.models.sql.compiler.SQLCompiler.get_order_by` — This is the caller of `setup_joins` (or similar logic) and is likely where the decision to follow the relation is made. The bug might be better fixed there, but a change in `setup_joins` would also work.
  - `django.db.models.sql.query.Query.resolve_ref` — This function also calls `setup_joins` but for a code path (`F()` expressions) that works correctly, suggesting `setup_joins` is capable of correct behavior given the right context.
  - `django.db.models.options.Options.get_field` — The logic for resolving a name to a field, which `setup_joins` uses, could be where `root_id` is incorrectly resolved to the `root` relation.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function is directly responsible for creating the erroneous join, which is a primary symptom. Modifying it to correctly handle `_id` lookups would fix the issue.

#### ✗ REJECTED — `django/db/models/sql/query.py::Query.resolve_ref`

- **Q1 Role.** This function resolves a lookup string (like one inside an F() expression) into a column or expression object, creating joins as necessary by calling `setup_joins`.
- **Q2 Connection to symptom.** No path. The bug report indicates that a workaround using `annotate(F('record__root_id'))` works correctly. `F()` expressions are resolved using `resolve_ref`. This demonstrates that when `resolve_ref` calls `setup_joins` with the path `['record', 'root_id']`, the correct, efficient SQL is generated. Therefore, `resolve_ref` is part of a *correctly* functioning code path, not the one that produces the bug.
- **Q3 Counterfactual.** `no` — Modifying this function would have no effect on the failing `order_by('...')` call, as it uses a different code path for resolving the ordering string.
- **Q4 Alternatives considered.**
  - `django.db.models.sql.compiler.SQLCompiler.get_order_by` — This is the entry point for the failing code path, which is distinct from the path `resolve_ref` is on.
  - `django.db.models.sql.query.Query.setup_joins` — `resolve_ref` calls this, but the bug is triggered by how the `order_by` logic calls it, not how `resolve_ref` does.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is part of a code path that works correctly, as shown by the `F()` expression workaround, and is not invoked by the failing `order_by` string case.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/sql/query.py::Query.setup_joins` | high | This function is directly responsible for creating the erroneous join, which is a primary symptom. Modifying it to correctly handle `_id` lookups would fix the issue. | When resolving a path segment that ends in `_id` and corresponds to a foreign key's `attname`, treat it as a direct column access and prevent the generation of  |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/sql/query.py::Query.add_ordering` | high | This function merely adds the ordering string to a list; the complex logic for path resolution and SQL generation happens elsewhere. |  |
| `django/db/models/sql/query.py::Query.resolve_ref` | high | This function is part of a code path that works correctly, as shown by the `F()` expression workaround, and is not invoked by the failing `order_by` string case. |  |

**Causal chains (per candidate)**

- `django/db/models/sql/query.py::Query.add_ordering`  (score=0.0)  \
  
- `django/db/models/sql/query.py::Query.setup_joins`  (score=9.0)  \
  The user calls `qs.order_by("record__root_id")`. → The query compiler's ordering logic (e.g., in `SQLCompiler.get_order_by`) begins processing the string `"record__root_id"`. → This logic calls `Query.setup_joins` with the path `['record', 'root_id']` to resolve the lookup and create necessary joins. → Inside `setup_joins`, while processing the `root_id` segment on the `OneModel` table, it incorrectly interprets this as a request to join through the `root` relation, likely because the target model has a default ordering. → This results in an unnecessary `LEFT OUTER JOIN` to the `OneModel` table (aliased as `T3`) being added to the query. → The function returns information about this new join, leading the compiler to target `T3.id` for ordering.
- `django/db/models/sql/query.py::Query.resolve_ref`  (score=0.0)  \
  

**next_to_explore:** `['django.db.models.sql.compiler.SQLCompiler.get_order_by', 'django.db.models.sql.query.Query.names_to_path', 'django.db.models.options.Options.get_field', 'django.db.models.sql.query.Query.trim_joins', 'django.db.models.fields.related.ForeignObject.get_path_info']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/db/models/sql/query.py::Query.setup_joins` | 0.9 |
| 2 | `django/db/models/sql/query.py::Query.add_ordering` | 0.8 |
| 3 | `django/db/models/sql/compiler.py::SQLCompiler.get_order_by` | 0.6 |
| 4 | `django/db/models/sql/compiler.py::SQLCompiler.find_ordering_name` | 0.1 |
| 5 | `django/db/models/fields/related.py::ForeignObject.get_reverse_joining_columns` | 0.05 |
| 6 | `django/db/models/base.py::make_foreign_order_accessors` | 0.0 |
| 7 | `django/db/models/base.py::Model._get_next_or_previous_in_order` | 0.0 |
| 8 | `django/db/models/base.py::Model._check_model_name_db_lookup_clashes` | 0.0 |
| 9 | `django/db/models/sql/query.py::Query.join_parent_model` | 0.0 |
| 10 | `django/db/models/sql/query.py::Query.demote_joins` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/db/models/sql/query.py::Query.setup_joins` | 0.900 | high | 1/1 | (1520, 1620) |
| 2 | `django/db/models/sql/query.py::Query.add_ordering` | 0.800 | high | 1/1 | (1889, 1933) |
| 3 | `django/db/models/sql/compiler.py::SQLCompiler.get_order_by` | 0.600 | high | 1/1 | (271, 396) |
| 4 | `django/db/models/sql/compiler.py::SQLCompiler._setup_joins` | 0.254 | high | 1/1 | (751, 762) |
| 5 | `django/db/models/sql/query.py::Query.clear_ordering` | 0.232 | high | 1/1 | (1935, 1943) |
| 6 | `django/db/models/base.py::Model.__eq__` | 0.228 | high | 1/1 | (524, 532) |
| 7 | `django/db/models/sql/query.py::Query.resolve_ref` | 0.216 | high | 1/1 | (1662, 1696) |
| 8 | `django/db/models/sql/compiler.py::SQLCompiler.collapse_group_by` | 0.195 | high | 1/1 | (149, 197) |
| 9 | `django/db/models/sql/compiler.py::SQLCompiler.find_ordering_name` | 0.100 | high | 1/1 | (715, 749) |
| 10 | `django/db/models/fields/related.py::ForeignObject.get_reverse_joining_columns` | 0.050 | high | 1/1 | (674, 675) |
