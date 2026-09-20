# Instance: `django__django-10554`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
Union queryset with ordering breaks on ordering with derived querysets
Description
	 
		(last modified by Sergei Maertens)
	 
May be related to #29692
Simple reproduction (the exact models are not relevant I think):
>>> Dimension.objects.values_list('id', flat=True)
<QuerySet [10, 11, 12, 13, 14, 15, 16, 17, 18]>
>>> qs = (
	Dimension.objects.filter(pk__in=[10, 11])
	.union(Dimension.objects.filter(pk__in=[16, 17])
	.order_by('order')
)
>>> qs
<QuerySet [<Dimension: boeksoort>, <Dimension: grootboek>, <Dimension: kenteken>, <Dimension: activa>]>
# this causes re-evaluation of the original qs to break
>>> qs.order_by().values_list('pk', flat=True)
<QuerySet [16, 11, 10, 17]>
>>> qs
[breaks]
Traceback:
Traceback (most recent call last):
 File "<input>", line 1, in <module>
	qs
 File "/home/bbt/.virtualenvs/ispnext/lib/python3.6/site-packages/django/db/models/query.py", line 248, in __repr__
	data = list(self[:REPR_OUTPUT_SIZE + 1])
 File "/home/bbt/.virtualenvs/ispnext/lib/python3.6/site-packages/django/db/models/query.py", line 272, in __iter__
	self._fetch_all()
 File "/home/bbt/.virtualenvs/ispnext/lib/python3.6/site-packages/django/db/models/query.py", line 1179, in _fetch_all
	s
```

## Stage 3 — Symptoms extracted

- exception types: `['ProgrammingError']`
- error messages: `['ORDER BY position 4 is not in select list', 'LINE 1: ...dimensions_dimension"."id" IN (16, 17)) ORDER BY (4) ASC LIM...', 'qs']`
- behaviors: `['queryset evaluation failure', 'ordering with derived querysets breaks']`
- named APIs: `['Dimension.objects.values_list', 'Dimension.objects.filter', 'QuerySet.union', 'QuerySet.order_by']`
- stack frames: `[{'file': '/home/bbt/.virtualenvs/ispnext/lib/python3.6/site-packages/django/db/models/query.py', 'func': '__repr__', 'line': 248}, {'file': '/home/bbt/.virtualenvs/ispnext/lib/python3.6/site-packages/django/db/models/query.py', 'func': '__iter__', 'line': 272}, {'file': '/home/bbt/.virtualenvs/ispnext/lib/python3.6/site-packages/django/db/models/query.py', 'func': '_fetch_all', 'line': 1179}, {'file': '/home/bbt/.virtualenvs/ispnext/lib/python3.6/site-packages/django/db/models/query.py', 'func': '__iter__', 'line': 53}, {'file': '/home/bbt/.virtualenvs/ispnext/lib/python3.6/site-packages/django/db/models/sql/compiler.py', 'func': 'execute_sql', 'line': 1068}, {'file': '/home/bbt/.virtualenvs/ispnext/lib/python3.6/site-packages/django/db/backends/utils.py', 'func': 'execute', 'line': 100}, {'file': '/home/bbt/.virtualenvs/ispnext/lib/python3.6/site-packages/django/db/backends/utils.py', 'func': 'execute', 'line': 68}, {'file': '/home/bbt/.virtualenvs/ispnext/lib/python3.6/site-packages/django/db/backends/utils.py', 'func': '_execute_with_wrappers', 'line': 77}, {'file': '/home/bbt/.virtualenvs/ispnext/lib/python3.6/site-packages/django/db/backends/utils.py', 'func': '_execute', 'line': 85}, {'file': '/home/bbt/.virtualenvs/ispnext/lib/python3.6/site-packages/django/db/backends/utils.py', 'func': '_execute', 'line': 85}]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/db/models/sql/compiler.py` | The issue involves SQL compilation and ordering, suggesting edits in the SQLCompiler. |
| 2 | `django/db/models/sql/query.py` | The issue involves querysets and ordering, suggesting edits in the Query class. |
| 3 | `django/db/backends/base/operations.py` | The issue involves database operations and ordering, suggesting edits in the BaseDatabaseOperations. |
| 4 | `django/db/backends/postgresql/operations.py` | The issue involves postgresql and ordering, suggesting edits in the postgresql DatabaseOperations. |
| 5 | `django/db/models/expressions.py` | The issue involves expressions and ordering, suggesting edits in the expressions. |
| 6 | `django/db/models/query_utils.py` | The issue involves query utils and ordering, suggesting edits in the query_utils. |
| 7 | `django/db/models/base.py` | The issue involves models and ordering, suggesting edits in the base. |
| 8 | `django/db/models/options.py` | The issue involves model options and ordering, suggesting edits in the options. |
| 9 | `django/db/models/fields/related.py` | The issue involves related fields and ordering, suggesting edits in the related. |
| 10 | `django/db/models/fields/__init__.py` | The issue involves fields and ordering, suggesting edits in the fields. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 0, considering: 2, rejected: 1

**Per-candidate deliberation traces**

#### … CONSIDERING — `django/db/models/query.py::QuerySet.union`

- **Q1 Role.** This function combines the current QuerySet with one or more other QuerySets using the SQL UNION operator.
- **Q2 Connection to symptom.** Yes, this function is the starting point of the causal chain. It calls `_combinator_query`, which in turn calls `sql.query.Query.combined_query`. This `combined_query` method creates a list of sub-queries (`combined_queries`) that are shared, not cloned. When this union `QuerySet` is later cloned (e.g., by `order_by`), the clone and the original share this same list of mutable sub-query objects. The evaluation of one `QuerySet` can then mutate these shared sub-queries via the SQL compiler, corrupting the state for the other `QuerySet` and leading to the `ProgrammingError` when it's subsequently evaluated.
- **Q3 Counterfactual.** `partially` — Yes, if this method (or the callees that set up the combined query) were changed to clone the sub-queries, the shared state would not exist and the bug would be prevented. However, the fix might be more appropriately placed in the `Query.clone` method.
- **Q4 Alternatives considered.**
  - `django/db/models/sql/query.py::Query.combined_query` — Preferred, as this is where the shared list of sub-queries is actually created.
  - `django/db/models/sql/query.py::Query.clone` — Also preferred, as making the clone operation deeper would fix this and potentially other similar bugs.
  - `django/db/models/sql/compiler.py::SQLCompiler.as_sql` — Considered, as the compiler could be made stateless regarding the query object, but this is a larger architectural change.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function initiates the creation of the shared query state that is at the root of the bug, though the faulty logic is in a callee.

#### … CONSIDERING — `django/db/models/query.py::QuerySet.order_by`

- **Q1 Role.** This function returns a new QuerySet instance with the ordering changed.
- **Q2 Connection to symptom.** Yes, this function is directly involved in the bug reproduction steps. It calls `self._chain()` to create a clone of the `QuerySet` and its underlying `query` object. The bug occurs because the cloning process is shallow; specifically, the `Query.clone()` method does not create a new copy of the `combined_queries` list from a union query. This results in both the original and the new `QuerySet` sharing the same mutable sub-query objects, allowing the evaluation of one to corrupt the state of the other, which leads to the `ProgrammingError`.
- **Q3 Counterfactual.** `partially` — Modifying `order_by` to enforce a deep copy of its query object would prevent the symptom. However, the root of the problem lies in the `Query.clone` method it relies on, which is the more appropriate place for a fix.
- **Q4 Alternatives considered.**
  - `django/db/models/sql/query.py::Query.clone` — Preferred, as this is where the shallow copy occurs. Fixing it here would solve the problem for all callers.
  - `django/db/models/query.py::QuerySet._chain` — This is the direct caller of `Query.clone`, so it's a valid alternative place to analyze, but the logic is in `clone`.
  - `django/db/models/sql/query.py::Query.clear_ordering` — Not preferred, as this method's logic is simple and correct, assuming it operates on a properly isolated query object.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function's use of a shallow clone propagates the shared state that leads to the bug, but the faulty cloning logic is in a callee.

#### ✗ REJECTED — `django/db/models/sql/query.py::Query.add_ordering`

- **Q1 Role.** This function adds ordering fields or expressions to the internal query object's `order_by` list.
- **Q2 Connection to symptom.** An execution path passes through this function to apply `.order_by('order')` to the initial queryset. This ordering information is later used by the SQL compiler. When the compiler attempts to apply this ordering to a query object whose state has been corrupted by a previous compilation, the `ProgrammingError` occurs. Therefore, this function sets up a necessary precondition for the bug to manifest but is not the cause of the state corruption itself.
- **Q3 Counterfactual.** `no` — This function correctly modifies the `order_by` attribute. The bug is caused by state corruption due to shallow cloning of querysets, not by how ordering is added.
- **Q4 Alternatives considered.**
  - `django/db/models/sql/query.py::Query.clone` — Preferred, as the failure to properly clone query state is the core issue.
  - `django/db/models/sql/compiler.py::SQLCompiler` — Preferred, as the compiler's mutation of shared query objects is the direct trigger for the bug.
  - `django/db/models/query.py::QuerySet.union` — Preferred, as it's responsible for creating the shared-state data structure in the first place.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function correctly adds ordering criteria; it does not cause the state corruption between different querysets that leads to the error.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/query.py::QuerySet.union` | medium | This function initiates the creation of the shared query state that is at the root of the bug, though the faulty logic is in a callee. | The fix is likely in `Query.combined_query` to clone sub-queries before adding them to the `combined_queries` list. |
| `django/db/models/query.py::QuerySet.order_by` | medium | This function's use of a shallow clone propagates the shared state that leads to the bug, but the faulty cloning logic is in a callee. | The fix is likely in `Query.clone` to perform a deep copy of `self.combined_queries` when cloning a combined query. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/sql/query.py::Query.add_ordering` | high | This function correctly adds ordering criteria; it does not cause the state corruption between different querysets that leads to the error. |  |

**Causal chains (per candidate)**

- `django/db/models/query.py::QuerySet.union`  (score=7.0)  \
  QuerySet.union calls _combinator_query, which calls Query.combined_query. → Query.combined_query creates a `combined_queries` list containing non-cloned, shared sub-query objects. → A subsequent call to `order_by()` clones the union QuerySet, but the clone operation is shallow and shares the `combined_queries` list. → Evaluation of the derived queryset causes the SQL compiler to mutate the shared sub-query objects. → Subsequent evaluation of the original queryset uses this corrupted state. → The compiler for the original queryset generates SQL with a positional ORDER BY that does not match the now-modified SELECT list, causing a ProgrammingError.
- `django/db/models/query.py::QuerySet.order_by`  (score=6.0)  \
  QuerySet.order_by calls _chain(), which calls Query.clone() to create a copy of the query object. → For a union query, Query.clone() performs a shallow copy, so the original and cloned query objects share the same list of sub-queries (`combined_queries`). → The cloned queryset is modified (e.g., with `values_list`) and evaluated. → The SQL compiler, processing the clone, mutates the shared sub-query objects. → When the original queryset is later evaluated, its compiler encounters this mutated state. → The compiler generates inconsistent SQL, leading to the `ProgrammingError`.
- `django/db/models/sql/query.py::Query.add_ordering`  (score=2.0)  \
  QuerySet.order_by('order') calls Query.add_ordering('order'). → This sets the `order_by` attribute on the query object, which is a precondition for the bug. → A separate evaluation of a derived queryset corrupts shared state within the query object (see other chains). → When the original queryset is evaluated, the compiler tries to process the `order_by` attribute on the corrupted state, leading to an error.

**next_to_explore:** `['django/db/models/sql/query.py::Query.clone', 'django/db/models/sql/query.py::Query.combined_query', 'django/db/models/sql/compiler.py::SQLCompiler.as_sql', 'django/db/models/query.py::QuerySet._chain']`

### Abductive step #2 (iteration=6)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/db/models/query.py::QuerySet._chain`

- **Q1 Role.** This function creates a new, cloned QuerySet instance that is ready for a subsequent operation like `filter` or `order_by`.
- **Q2 Connection to symptom.** The bug report shows `qs.order_by()`, which internally calls `_chain` to create a new QuerySet that can be modified without affecting the original. The observed symptom is that the original `qs` *is* affected, suggesting a failure in the isolation that `_chain` is supposed to provide. The path is: `qs.order_by()` -> `_chain()` -> `self._clone()`. If the cloning process initiated here is incomplete, state from the new queryset can leak back to the original, causing the subsequent failure.
- **Q3 Counterfactual.** `no` — This function only orchestrates the cloning by calling `self._clone()`. The actual logic for copying the underlying query state is in `Query.clone()`. Fixing `_chain` would require it to implement a different cloning strategy, but the real bug is in the `_clone()` method it calls.
- **Q4 Alternatives considered.**
  - `django/db/models/query.py::QuerySet._clone` — This is called by `_chain` and is a more direct precursor to the actual cloning logic.
  - `django/db/models/sql/query.py::Query.clone` — This is the function that actually copies the query's data structures and is the most likely source of an incomplete copy.
  - `django/db/models/query.py::QuerySet.order_by` — This is the user-facing API that starts the process, but it relies on `_chain` to function correctly.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a high-level orchestrator; the actual bug lies in the lower-level cloning mechanism it invokes (`Query.clone`).

#### ✗ REJECTED — `django/db/models/sql/compiler.py::SQLCompiler.as_sql`

- **Q1 Role.** This function compiles a `Query` object's internal representation into a final SQL string and a list of parameters for execution by the database backend.
- **Q2 Connection to symptom.** No direct path. This function is executed at the end of the process, after the `Query` object's state has already been corrupted. It receives the corrupted state and, as a result, generates the invalid SQL (`ORDER BY position 4 is not in select list`). The error is a symptom of the invalid input this function receives, not a bug in the function's own logic.
- **Q3 Counterfactual.** `no` — Modifying this function would mean adding code to detect and fix the corrupted query state. This would be treating the symptom, not the cause, which is the state corruption happening upstream.
- **Q4 Alternatives considered.**
  - `django/db/models/sql/query.py::Query.clone` — Preferred, as this is where the state corruption likely originates due to an incomplete copy.
  - `django/db/models/sql/compiler.py::SQLCompiler.get_combinator_sql` — This is more specific to UNION queries, but like `as_sql`, it's still downstream of the state corruption.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is downstream of the error; it correctly translates a corrupted query object into invalid SQL, but it does not cause the corruption.

#### ✓ LEADING — `django/db/models/sql/query.py::Query.clone`

- **Q1 Role.** This function creates a lightweight copy of a `Query` object, which encapsulates all the components of a database query like tables, filters, and ordering.
- **Q2 Connection to symptom.** This function is the most likely root cause. The symptom—a derived queryset modifying its parent—strongly suggests an incomplete clone. The method uses `self.__dict__.copy()`, a shallow copy. If `self.combined_queries` (a tuple of `Query` objects for the UNION) is not explicitly deep-copied, both the original and cloned `Query` objects will share references to the same sub-query objects. A subsequent operation on the clone (like `order_by()`) could modify one of these shared sub-queries in-place, corrupting the state of the original `Query` object and leading to the `ProgrammingError` on re-evaluation.
- **Q3 Counterfactual.** `yes` — If this function were modified to recursively clone the `Query` objects held within `self.combined_queries`, the state of the original and derived querysets would be fully isolated, preventing the state corruption and eliminating the symptom.
- **Q4 Alternatives considered.**
  - `django/db/models/query.py::QuerySet._chain` — This is a caller of `clone`, but the fault is not in the calling but in the implementation of `clone` itself.
  - `django/db/models/query.py::QuerySet.order_by` — This method triggers the clone and modification, but it correctly relies on the cloning mechanism to provide isolation.
  - `django/db/models/query.py::Query.add_ordering` — This modifies the ordering state, but the problem is that it modifies a shared object, which is `clone`'s fault.
- **Q5 Verdict.** `leading` (confidence: `high`) — The symptom is a classic side effect of a shallow copy where a deep copy is needed, and this function is responsible for that copy.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/sql/query.py::Query.clone` | high | The symptom is a classic side effect of a shallow copy where a deep copy is needed, and this function is responsible for that copy. | If `self.combined_queries` exists, it should be recursively cloned, e.g., `obj.combined_queries = tuple(q.clone() for q in self.combined_queries)`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/query.py::QuerySet._chain` | high | This function is a high-level orchestrator; the actual bug lies in the lower-level cloning mechanism it invokes (`Query.clone`). |  |
| `django/db/models/sql/compiler.py::SQLCompiler.as_sql` | high | This function is downstream of the error; it correctly translates a corrupted query object into invalid SQL, but it does not cause the corruption. |  |

**Causal chains (per candidate)**

- `django/db/models/query.py::QuerySet._chain`  (score=4.0)  \
  The user calls `qs.order_by()`, which invokes `qs._chain()` to create a clone. → `_chain` calls `self._clone()`, which calls `self.query.clone()`. → The `Query.clone()` method performs an incomplete, shallow copy. → A subsequent operation on the new queryset mutates state that is shared with the original `qs`. → When `qs` is re-evaluated, it uses this corrupted state, leading to an error. → The function is part of the causal chain but is not the root cause.
- `django/db/models/sql/compiler.py::SQLCompiler.as_sql`  (score=1.0)  \
  The `Query` object for the original queryset `qs` is corrupted by an operation on a derived queryset. → The user re-evaluates `qs`, triggering a call to `compiler.execute_sql`. → `execute_sql` uses a compiler, which calls `as_sql` (or similar logic) to generate the SQL query. → `as_sql` receives the corrupted `Query` object. → It generates an invalid SQL statement based on this inconsistent state. → The database backend raises a `ProgrammingError`.
- `django/db/models/sql/query.py::Query.clone`  (score=10.0)  \
  A `UNION` queryset `qs` is created. → `qs.order_by()` is called, which needs to clone `qs` to avoid side effects. → `Query.clone` is called on the underlying `Query` object. → The method performs a shallow copy of its `__dict__`, so the `combined_queries` attribute (containing sub-queries for the union) is shared between the original and the clone. → The `order_by()` operation on the clone modifies one of the shared sub-query objects in-place. → This corrupts the state of the original `qs.query` object.

**next_to_explore:** `['django/db/models/query.py::QuerySet.order_by', 'django/db/models/sql/query.py::Query.add_ordering', 'django/db/models/query.py::QuerySet._clone', 'django/db/models/sql/compiler.py::SQLCompiler.get_combinator_sql', 'django/db/models/query.py::QuerySet.union']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/db/models/sql/query.py::Query.clone` | 0.95 |
| 2 | `django/db/models/query.py::QuerySet.union` | 0.8 |
| 3 | `django/db/models/query.py::QuerySet.order_by` | 0.6 |
| 4 | `django/db/models/query.py::QuerySet._chain` | 0.5 |
| 5 | `django/db/models/sql/compiler.py::SQLCompiler.as_sql` | 0.2 |
| 6 | `django/db/models/sql/query.py::Query.add_ordering` | 0.1 |
| 7 | `django/db/models/sql/query.py::Query.clear_ordering` | 0.0 |
| 8 | `django/db/models/sql/compiler.py::SQLCompiler.find_ordering_name` | 0.0 |
| 9 | `django/db/backends/base/operations.py::BaseDatabaseOperations.force_no_ordering` | 0.0 |
| 10 | `django/db/models/sql/compiler.py::SQLCompiler.get_order_by` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/db/models/sql/query.py::Query.clone` | 0.950 | high | 1/1 | (292, 336) |
| 2 | `django/db/models/query.py::QuerySet.union` | 0.800 | high | 1/1 | (939, 944) |
| 3 | `django/db/models/query.py::QuerySet.order_by` | 0.600 | high | 1/1 | (1066, 1073) |
| 4 | `django/db/models/query.py::QuerySet._chain` | 0.500 | high | 1/1 | (1212, 1222) |
| 5 | `django/db/models/sql/compiler.py::SQLCompiler.as_sql` | 0.200 | high | 1/1 | (465, 625) |
| 6 | `django/db/backends/base/operations.py::BaseDatabaseOperations.unification_cast_sql` | 0.198 | high | 1/1 | (83, 89) |
| 7 | `django/db/models/sql/query.py::Query.demote_joins` | 0.190 | high | 1/1 | (794, 811) |
| 8 | `django/db/models/sql/query.py::get_order_dir` | 0.188 | high | 1/1 | (2192, 2203) |
| 9 | `django/db/models/sql/compiler.py::SQLCompiler._setup_joins` | 0.184 | high | 1/1 | (726, 737) |
| 10 | `django/db/backends/base/operations.py::BaseDatabaseOperations.cache_key_culling_sql` | 0.103 | high | 1/1 | (73, 81) |
