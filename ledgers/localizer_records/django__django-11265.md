# Instance: `django__django-11265`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
Using exclude on annotated FilteredRelation doesn't work
Description
	
It looks like using exclude on queryset with annotated FilteredRelation give a FieldError on the annotation name.
For exemple, in Django tests (django/tests/filtered_relation/tests.py) if we change this :
def test_with_join(self):
	self.assertSequenceEqual(
		Author.objects.annotate(
			book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
		).filter(book_alice__isnull=False),
		[self.author1]
	)
to this
def test_with_join(self):
	self.assertSequenceEqual(
		Author.objects.annotate(
			book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
		).exclude(book_alice__isnull=False),
		[]
	)
You get the error :
Traceback (most recent call last):
 File "/usr/lib/python3.6/unittest/case.py", line 59, in testPartExecutor
	yield
 File "/usr/lib/python3.6/unittest/case.py", line 605, in run
	testMethod()
 File "/home/lucas/dev/test/django/tests/filtered_relation/tests.py", line 99, in test_with_join_exclude
	).filter(~Q(book_alice__isnull=False)),
 File "/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/query.py", line 844, i
```

## Stage 3 — Symptoms extracted

- exception types: `['FieldError']`
- error messages: `["Cannot resolve keyword 'book_alice' into field. Choices are: book, content_object, content_type, content_type_id, favorite_books, id, name, object_id"]`
- behaviors: `['exclude on annotated FilteredRelation fails', 'FieldError raised when using exclude on annotated FilteredRelation']`
- named APIs: `['Author.objects.annotate', 'FilteredRelation', 'Q', 'Author.objects.exclude']`
- stack frames: `[{'file': '/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/sql/query.py', 'func': 'names_to_path', 'line': 1389}, {'file': '/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/sql/query.py', 'func': 'solve_lookup_type', 'line': 1028}, {'file': '/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/sql/query.py', 'func': 'build_filter', 'line': 1164}, {'file': '/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/sql/query.py', 'func': '_add_q', 'line': 1287}, {'file': '/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/sql/query.py', 'func': 'add_q', 'line': 1263}, {'file': '/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/sql/query.py', 'func': 'add_filter', 'line': 1249}, {'file': '/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/sql/query.py', 'func': 'split_exclude', 'line': 1604}, {'file': '/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/sql/query.py', 'func': 'build_filter', 'line': 1204}, {'file': '/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/sql/query.py', 'func': '_add_q', 'line': 1287}, {'file': '/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/sql/query.py', 'func': 'add_q', 'line': 1263}, {'file': '/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/query.py', 'func': '_add_q', 'line': 1281}, {'file': '/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/query.py', 'func': 'add_q', 'line': 1263}, {'file': '/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/query.py', 'func': '_filter_or_exclude', 'line': 862}, {'file': '/home/lucas/dev/overmind/venvs/release/lib/python3.6/site-packages/django/db/models/query.py', 'func': 'filter', 'line': 844}, {'file': '/home/lucas/dev/test/django/tests/filtered_relation/tests.py', 'func': 'test_with_join_exclude', 'line': 99}]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/db/models/sql/query.py` | Faulty exclude logic likely resides in the Query class's _filter_or_exclude and related methods. |
| 2 | `django/db/models/sql/where.py` | The WhereNode class is responsible for building the SQL WHERE clause, and might be involved in incorrect negation. |
| 3 | `django/db/models/query_utils.py` | The FilteredRelation class and related functions are used to specify custom filtering in the ON clause of SQL joins, which is where the issue occurs. |
| 4 | `django/db/models/fields/related.py` | The ForeignObject class and its subclasses define how related fields are handled in queries, and might be involved in the issue. |
| 5 | `django/db/models/expressions.py` | Expressions are used to represent SQL expressions, and might be involved in the incorrect negation of the FilteredRelation condition. |
| 6 | `django/db/backends/base/operations.py` | Database operations are used to generate the SQL for queries, and might be involved in the issue. |
| 7 | `django/db/backends/postgresql/operations.py` | PostgreSQL operations are used to generate the SQL for queries, and might be involved in the issue. |
| 8 | `django/db/backends/sqlite3/operations.py` | SQLite operations are used to generate the SQL for queries, and might be involved in the issue. |
| 9 | `django/contrib/admin/options.py` | The ModelAdmin class uses querysets to display and filter data in the admin interface, and might be involved in the issue. |
| 10 | `django/tests/filtered_relation/tests.py` | The provided test case needs to be modified to check if exclude works correctly. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/db/models/query_utils.py::FilteredRelation.resolve_expression`

- **Q1 Role.** This is a placeholder method on the FilteredRelation class that raises NotImplementedError, indicating it's not meant to be called as part of the standard expression resolution pathway.
- **Q2 Connection to symptom.** No path. The observed symptom is a `FieldError`, not a `NotImplementedError`. The traceback does not include this function, and its code explicitly states it is unused, so it cannot be on the execution path that produces the symptom.
- **Q3 Counterfactual.** `no` — Modifying this function would have no effect, as it is not called during the execution that leads to the `FieldError`.
- **Q4 Alternatives considered.**
  - `django.db.models.sql.query.Query.split_exclude` — Preferred, as the traceback and user analysis point to it as the place where query context (annotations) is lost.
  - `django.db.models.sql.query.Query.names_to_path` — This function raises the error, but the root cause is that it receives a query object missing the necessary annotation data.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is explicitly unused and not on the execution path leading to the FieldError.

#### ✗ REJECTED — `tests/filtered_relation/tests.py::FilteredRelationTests.test_exclude_relation_with_join`

- **Q1 Role.** This is a unit test that verifies filtering on an annotated `FilteredRelation` works correctly when the condition inside the `FilteredRelation` is negated.
- **Q2 Connection to symptom.** No path. This test demonstrates a working scenario using `.filter()`. The bug report is about `.exclude()`. While related, this specific test passes and does not trigger the `FieldError`.
- **Q3 Counterfactual.** `no` — This is a test function; modifying it would not fix the underlying bug in the Django ORM's query processing logic.
- **Q4 Alternatives considered.**
  - `The failing test case from the bug report` — The actual code that triggers the bug is `...annotate(...).exclude(book_alice__isnull=False)`, which is a modification of a different test.
  - `django.db.models.sql.query.Query.split_exclude` — Preferred, as this is the ORM code suspected of mishandling the exclusion.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a test for a working scenario and is not the cause of the bug.

#### ✗ REJECTED — `tests/filtered_relation/tests.py::FilteredRelationTests.test_internal_queryset_alias_mapping`

- **Q1 Role.** This is a unit test that verifies the correct SQL `INNER JOIN` is generated for a `FilteredRelation` annotation when followed by a `.filter()` call.
- **Q2 Connection to symptom.** No path. This test, like the previous one, demonstrates a working scenario using `.filter()`. It confirms that the annotation alias is correctly handled in the filter case, which contrasts with the failing exclude case but does not cause it.
- **Q3 Counterfactual.** `no` — This is a test function; modifying it cannot fix the bug in the ORM.
- **Q4 Alternatives considered.**
  - `django.db.models.sql.query.Query.split_exclude` — Preferred, as this is the likely location of the logic error that fails to preserve annotations.
  - `django.db.models.query.QuerySet._filter_or_exclude` — This is the entry point from the public API, but the logic difference appears deeper in the call stack.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a test for a working scenario and is not the cause of the bug.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/query_utils.py::FilteredRelation.resolve_expression` | high | This function is explicitly unused and not on the execution path leading to the FieldError. |  |
| `tests/filtered_relation/tests.py::FilteredRelationTests.test_exclude_relation_with_join` | high | This is a test for a working scenario and is not the cause of the bug. |  |
| `tests/filtered_relation/tests.py::FilteredRelationTests.test_internal_queryset_alias_mapping` | high | This is a test for a working scenario and is not the cause of the bug. |  |

**Causal chains (per candidate)**

- `django/db/models/query_utils.py::FilteredRelation.resolve_expression`  (score=0.0)  \
  
- `tests/filtered_relation/tests.py::FilteredRelationTests.test_exclude_relation_with_join`  (score=0.0)  \
  
- `tests/filtered_relation/tests.py::FilteredRelationTests.test_internal_queryset_alias_mapping`  (score=0.0)  \
  

**next_to_explore:** `['django/db/models/sql/query.py::Query.split_exclude', 'django/db/models/sql/query.py::Query.build_filter', 'django/db/models/sql/query.py::Query.names_to_path', 'django/db/models/sql/query.py::Query._add_q', 'django/db/models/query.py::QuerySet._filter_or_exclude']`

### Abductive step #2 (iteration=6)

- leading: 1, considering: 1, rejected: 1

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/db/models/query.py::QuerySet._filter_or_exclude`

- **Q1 Role.** This method is the core implementation for both `filter()` and `exclude()` on a `QuerySet`, applying the given filter conditions either positively or negatively.
- **Q2 Connection to symptom.** Yes, this function is the entry point in the failing execution path. The call to `exclude()` in the test case invokes this method with `negate=True`. It then creates a negated `Q` object (`~Q(book_alice__isnull=False)`) and passes it to `clone.query.add_q()`, which begins the query construction process that ultimately leads to the `FieldError`.
- **Q3 Counterfactual.** `no` — The problem lies in how the negated filter on an annotation is processed deep within the SQL query construction, not in this top-level `QuerySet` method which simply dispatches the filter.
- **Q4 Alternatives considered.**
  - `django.db.models.query.QuerySet.exclude` — This is just a public wrapper for `_filter_or_exclude`, so it's even less likely to be the root cause.
  - `django.db.models.sql.query.Query.add_q` — This is the next step in the call chain and is closer to the error, but the specific logic for handling this type of exclusion is further downstream.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a simple dispatcher on the call stack; the actual error originates from deeper query processing logic.

#### ✓ LEADING — `django/db/models/sql/query.py::Query.split_exclude`

- **Q1 Role.** This function rewrites an `exclude` filter on a multi-valued relation into a `NOT IN` subquery to ensure correct SQL generation and semantics.
- **Q2 Connection to symptom.** Yes, this is the most likely source of the error. The traceback shows it's called. Inside this function, a new, clean query object is created via `query = Query(self.model)`. This new query for the subquery does not inherit the annotations (like `book_alice`) from the original query (`self`). When `query.add_filter()` is called on this new query, it fails to resolve `'book_alice'` because the annotation is missing, leading directly to the `FieldError`.
- **Q3 Counterfactual.** `yes` — If this function were modified to copy the annotations from the original query (`self`) to the new subquery (`query`), the name `'book_alice'` would be resolvable, and the `FieldError` would not occur.
- **Q4 Alternatives considered.**
  - `django.db.models.sql.query.Query.build_filter` — This function calls `split_exclude`, but the core issue is the loss of context within `split_exclude` itself, not the decision to call it.
  - `django.db.models.sql.query.Query.names_to_path` — This function correctly raises the error because the field isn't found; it's reporting the problem, not causing it.
  - `django.db.models.sql.query.Query.__init__` — The constructor could be changed to facilitate cloning, but the responsibility to copy the context lies with the caller, `split_exclude`.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function creates a new query for a subquery but fails to propagate the annotations from the parent query, directly causing the name resolution failure.

#### … CONSIDERING — `django/db/models/sql/query.py::Query.build_filter`

- **Q1 Role.** This function constructs a `WhereNode` object, representing a piece of an SQL `WHERE` clause, from a single filter expression.
- **Q2 Connection to symptom.** Yes, this function is on the call stack twice. The first time, it correctly identifies that the negated filter on a `FilteredRelation` requires special handling and calls `split_exclude`. The second time, it's called from within `split_exclude` on the new, annotation-less query, where it fails during the call to `solve_lookup_type` because it cannot resolve the annotation name.
- **Q3 Counterfactual.** `partially` — Modifying this function to not call `split_exclude` for this case would prevent the crash but likely produce incorrect query results. The more correct fix is within `split_exclude`.
- **Q4 Alternatives considered.**
  - `django.db.models.sql.query.Query.split_exclude` — Preferred, as it's the function where the necessary context (the annotations) is actually lost.
  - `django.db.models.sql.query.Query.add_q` — This is an orchestrator; the specific logic for handling the negated join is delegated to `build_filter` and `split_exclude`.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function triggers the call to the faulty `split_exclude` logic and is part of the failing path, but the root cause is the context loss in the callee.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/sql/query.py::Query.split_exclude` | high | This function creates a new query for a subquery but fails to propagate the annotations from the parent query, directly causing the name resolution failure. | Copy annotations from `self.annotations` to the newly created `query` object, e.g., `query.annotations = self.annotations.copy()`. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/sql/query.py::Query.build_filter` | medium | This function triggers the call to the faulty `split_exclude` logic and is part of the failing path, but the root cause is the context loss in the callee. | Ensure `split_exclude` is passed the necessary context, or that the condition for calling it is correct for annotated relations. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/query.py::QuerySet._filter_or_exclude` | high | This function is a simple dispatcher on the call stack; the actual error originates from deeper query processing logic. |  |

**Causal chains (per candidate)**

- `django/db/models/query.py::QuerySet._filter_or_exclude`  (score=2.0)  \
  The user calls `queryset.exclude(book_alice__isnull=False)`. → This function is called with `negate=True`. → It creates a negated Q object: `~Q(book_alice__isnull=False)`. → It calls `query.add_q()` with the negated Q object, starting the chain that leads to the error.
- `django/db/models/sql/query.py::Query.split_exclude`  (score=10.0)  \
  An `exclude` on a `FilteredRelation` annotation is processed. → `build_filter` determines this requires a subquery and calls `split_exclude`. → `split_exclude` creates a new, empty query object: `query = Query(self.model)`. → This new `query` object does not have the `book_alice` annotation from the original query. → `split_exclude` calls `query.add_filter(('book_alice__isnull', False))` on this new query. → The filtering logic eventually calls `names_to_path` to resolve 'book_alice'.
- `django/db/models/sql/query.py::Query.build_filter`  (score=6.0)  \
  `add_q` calls `build_filter` to process the negated Q object. → `build_filter` analyzes the lookup `book_alice__isnull` and determines it involves a join that needs to be handled via a subquery for exclusion. → It calls `self.split_exclude` to create this subquery. → This delegates the problem to `split_exclude`, which loses the annotation context. → Later, `build_filter` is called again inside `split_exclude`, and this second execution fails because the annotation it needs to resolve is missing.

**next_to_explore:** `['django/db/models/sql/query.py::Query.names_to_path', 'django/db/models/sql/query.py::Query.add_q', 'django/db/models/sql/query.py::Query.solve_lookup_type', 'django/db/models/expressions.py::FilteredRelation.resolve_expression', 'django/db/models/sql/query.py::Query.__init__']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/db/models/sql/query.py::Query.split_exclude` | 0.95 |
| 2 | `django/db/models/sql/query.py::Query.build_filter` | 0.6 |
| 3 | `django/db/models/query.py::QuerySet._filter_or_exclude` | 0.2 |
| 4 | `tests/filtered_relation/tests.py::FilteredRelationTests.test_exclude_relation_with_join` | 0.0 |
| 5 | `tests/filtered_relation/tests.py::FilteredRelationTests.test_internal_queryset_alias_mapping` | 0.0 |
| 6 | `django/db/models/query_utils.py::FilteredRelation.resolve_expression` | 0.0 |
| 7 | `django/db/models/sql/query.py::Query.add_filtered_relation` | 0.0 |
| 8 | `django/db/models/sql/query.py::Query.build_filtered_relation_q` | 0.0 |
| 9 | `django/db/models/query_utils.py::FilteredRelation.__init__` | 0.0 |
| 10 | `django/db/models/query_utils.py::FilteredRelation.clone` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/db/models/sql/query.py::Query.split_exclude` | 0.950 | high | 1/1 | (1645, 1713) |
| 2 | `django/db/models/sql/query.py::Query.build_filter` | 0.600 | high | 1/1 | (1183, 1302) |
| 3 | `django/db/models/query_utils.py::FilteredRelation.as_sql` | 0.268 | high | 1/1 | (332, 336) |
| 4 | `django/db/models/sql/query.py::Query.append_annotation_mask` | 0.258 | high | 1/1 | (2014, 2016) |
| 5 | `django/db/models/fields/related.py::RelatedField._check_clashes` | 0.252 | high | 1/1 | (190, 282) |
| 6 | `django/db/models/fields/related.py::ForeignObject.get_extra_descriptor_filter` | 0.240 | high | 1/1 | (669, 682) |
| 7 | `django/db/models/fields/related.py::RelatedField.related_query_name` | 0.231 | high | 1/1 | (421, 426) |
| 8 | `django/db/models/query.py::QuerySet._filter_or_exclude` | 0.200 | high | 1/1 | (890, 900) |
| 9 | `tests/filtered_relation/tests.py::FilteredRelationTests.test_exclude_relation_with_join` | 0.000 | high | 1/1 | (142, 148) |
| 10 | `tests/filtered_relation/tests.py::FilteredRelationTests.test_internal_queryset_alias_mapping` | 0.000 | high | 1/1 | (114, 121) |
