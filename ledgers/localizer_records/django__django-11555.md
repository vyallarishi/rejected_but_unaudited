# Instance: `django__django-11555`

- runs: 1   termination: `ledger_informed`   think-high calls: 3

## Issue (truncated to 1200 chars)

```
order_by() a parent model crash when Meta.ordering contains expressions.
Description
	 
		(last modified by Jonny Fuller)
	 
Hi friends,
During testing I discovered a strange bug when using a query expression for ordering during multi-table inheritance. You can find the full write up as well as reproducible test repository ​https://github.com/JonnyWaffles/djangoordermetabug. The bug occurs because the field is an OrderBy object, not a string, during get_order_dir. The linked stacktrace should make the issue obvious, but what I don't understand is why it only fails during test db setup, not during repl or script use. I wish I could help more and come up with a real solution. Hopefully, this is enough for someone wiser to find the culprit.
```

## Stage 3 — Symptoms extracted

- exception types: `['TypeError', 'KeyError']`
- error messages: `['the field is an OrderBy object, not a string, during get_order_dir']`
- behaviors: `['ordering during multi-table inheritance', 'test db setup fails', 'parent model crash']`
- named APIs: `['order_by()']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/db/models/query.py` | Likely location for order_by() implementation and query execution logic. |
| 2 | `django/db/models/expressions.py` | Defines the OrderBy expression and related classes. |
| 3 | `django/db/models/sql/compiler.py` | Compiles the SQL query, including handling ordering and expressions. |
| 4 | `django/db/backends/base/operations.py` | Abstracts database-specific operations, including quoting and ordering. |
| 5 | `django/db/backends/sqlite3/operations.py` | SQLite-specific database operations, potentially related to the crash. |
| 6 | `django/db/backends/postgresql/operations.py` | PostgreSQL-specific database operations, potentially related to the crash. |
| 7 | `django/db/backends/mysql/operations.py` | MySQL-specific database operations, potentially related to the crash. |
| 8 | `django/db/models/options.py` | Handles model metadata, including ordering. |
| 9 | `django/db/models/fields/related.py` | Deals with related fields and their interaction with ordering. |
| 10 | `django/db/models/sql/where.py` | Handles the WHERE clause and filter expressions, potentially interacting with ordering. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/db/models/query.py::QuerySet.ordered`

- **Q1 Role.** This function returns a boolean indicating if the QuerySet has a defined ordering, either from an `order_by()` call or default `Meta.ordering`.
- **Q2 Connection to symptom.** No path. This function merely checks for the existence of an ordering clause (`self.query.get_meta().ordering`) but does not inspect or process its contents. The crash happens when the contents of the ordering clause are processed, which occurs elsewhere. This function's boolean return value might trigger the downstream processing, but it is not the source of the type misinterpretation.
- **Q3 Counterfactual.** `no` — Modifying this function would not fix the bug. The function only checks for the presence of ordering; the bug is in how the ordering expression is later processed. Changing this function would either have no effect or would break ordering entirely.
- **Q4 Alternatives considered.**
  - `django/db/models/sql/compiler.py::SQLCompiler.get_order_by` — Preferred, as it's responsible for interpreting the `Meta.ordering` values and is where the incorrect logic path is taken.
  - `django/db/models/query.py::Query.get_meta` — Considered, as it provides the `ordering` data, but it's less likely to be the cause than the function that consumes the data.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function only checks for the existence of ordering and does not process the expression that causes the crash.

#### ✗ REJECTED — `django/db/models/sql/compiler.py::SQLCompiler._setup_joins`

- **Q1 Role.** This function is a helper method that prepares the necessary SQL joins for ordering or distinction clauses based on field lookups.
- **Q2 Connection to symptom.** No path. This function is called to resolve joins for string-based field paths. The bug occurs because an `OrderBy` expression object is incorrectly treated as a string *before* any join resolution would be necessary for it. The stack trace indicates the failure is in `get_order_dir`, which is called from `get_order_by` in a logic branch that does not involve `_setup_joins`.
- **Q3 Counterfactual.** `no` — The bug is a type misinterpretation of an ordering expression, which happens in `get_order_by` before this join-setup helper would be relevant. Modifying this function would have no effect on the symptom.
- **Q4 Alternatives considered.**
  - `django/db/models/sql/compiler.py::SQLCompiler.get_order_by` — Preferred, as it contains the logic that differentiates expressions from field strings and makes the wrong decision.
  - `django/db/models/sql/query.py::Query.setup_joins` — Not preferred, as this is the underlying implementation, but the issue is not with join setup itself.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a join setup helper, whereas the bug stems from misinterpreting an ordering expression's type before joins are considered.

#### ✓ LEADING — `django/db/models/sql/compiler.py::SQLCompiler.get_order_by`

- **Q1 Role.** This function constructs the list of expressions and directions for the SQL `ORDER BY` clause based on the query's `order_by` or the model's `Meta.ordering` attributes.
- **Q2 Connection to symptom.** A direct execution path produces the symptom. 
1. The function retrieves `ordering` from `self.query.get_meta().ordering`, which contains an `OrderBy` object from the parent model's `Meta`.
2. It iterates through the `ordering` list. The `field` variable becomes the `OrderBy` object.
3. The check `if hasattr(field, 'resolve_expression')` unexpectedly returns `False` in the context of test database setup, likely due to how model `Meta` is inherited or reconstructed.
4. Consequently, the `else` branch is taken, which assumes `field` is a string representing a column name.
5. `get_order_dir(field, asc)` is called, passing the `OrderBy` object.
6. `get_order_dir` attempts to call a string method (like `.startswith()`) on the `OrderBy` object, raising an `AttributeError` (reported as `TypeError`/`KeyError` in summary), which matches the observed symptom.
- **Q3 Counterfactual.** `yes` — This function contains the faulty branching logic that misclassifies an expression object. Correcting the condition to properly identify `OrderBy` objects, even in the test setup context, would route them to the correct handling path and prevent the call to `get_order_dir`, thus eliminating the crash.
- **Q4 Alternatives considered.**
  - `django/db/models/sql/utils.py::get_order_dir` — Considered as the site of the crash, but fixing it there would be treating the symptom, not the cause; it should not receive expression objects.
  - `django/db/models/options.py::Meta._prepare` — Considered as a possible upstream cause where the `OrderBy` object from `Meta.ordering` is altered during model creation for tests, but the immediate faulty logic is in `get_order_by`.
  - `django/db/models/query.py::Query.get_meta` — Considered, as it supplies the `ordering` list, but `get_order_by` is responsible for correctly interpreting what it receives.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function contains the explicit branching logic that incorrectly routes an OrderBy expression to a code path for strings, directly causing the crash described.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/sql/compiler.py::SQLCompiler.get_order_by` | high | This function contains the explicit branching logic that incorrectly routes an OrderBy expression to a code path for strings, directly causing the crash described. | The check for expression objects should be made more robust. For example, modify `if hasattr(field, 'resolve_expression')` to also handle cases where the object |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/query.py::QuerySet.ordered` | high | This function only checks for the existence of ordering and does not process the expression that causes the crash. |  |
| `django/db/models/sql/compiler.py::SQLCompiler._setup_joins` | high | This is a join setup helper, whereas the bug stems from misinterpreting an ordering expression's type before joins are considered. |  |

**Causal chains (per candidate)**

- `django/db/models/query.py::QuerySet.ordered`  (score=0.0)  \
  
- `django/db/models/sql/compiler.py::SQLCompiler._setup_joins`  (score=0.0)  \
  
- `django/db/models/sql/compiler.py::SQLCompiler.get_order_by`  (score=9.0)  \
  The `ordering` list is populated from `self.query.get_meta().ordering`, containing an `OrderBy` object. → The code iterates through this list, and the `field` variable becomes the `OrderBy` object. → The condition `if hasattr(field, 'resolve_expression')` evaluates to False, which is incorrect for an `OrderBy` object but happens in the specific test context. → The `else` block is executed, which is intended for string-based field names. → The function `get_order_dir` is called with the `OrderBy` object as its first argument. → An `AttributeError` is raised inside `get_order_dir` when it attempts a string operation on the object, causing the crash.

**next_to_explore:** `['django/db/models/sql/utils.py::get_order_dir', 'django/db/models/options.py::Meta._prepare', 'django/db/models/query.py::Query.get_meta', 'django/db/models/expressions.py::OrderBy.deconstruct', 'django/utils/functional.py::Promise']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 1, rejected: 1

**Per-candidate deliberation traces**

#### … CONSIDERING — `django/db/models/sql/query.py::get_order_dir`

- **Q1 Role.** This function parses a string representing an ordering field to extract the field name and sorting direction (ASC/DESC).
- **Q2 Connection to symptom.** Yes, this is the exact location of the crash. The symptom description states 'the field is an OrderBy object, not a string, during get_order_dir'. The function's code at `if field[0] == '-':` attempts to subscript the `field` argument. If `field` is an `OrderBy` object as described, this operation will raise a `TypeError` because `OrderBy` objects are not subscriptable, which directly matches the observed exception.
- **Q3 Counterfactual.** `partially` — Adding a check to handle `OrderBy` objects would prevent the crash. However, this function's contract appears to be string-based, so the root cause is likely an upstream caller that should have resolved the `OrderBy` object before calling this function.
- **Q4 Alternatives considered.**
  - `django.db.models.sql.compiler.SQLCompiler.get_order_by` — This is a likely caller and is responsible for preparing the ordering clause, making it a strong candidate for the root cause.
  - `django.db.models.sql.query.Query.add_ordering` — This function adds ordering specifications to the query and might be where the unresolved `OrderBy` object is first introduced.
  - `The test database setup process` — The bug only manifests in this context, suggesting a specific code path is taken during test setup that is not taken during normal operation.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function is the site of the crash, but it is likely the victim of being passed an incorrect type, not the root cause of the bug.

#### ✗ REJECTED — `django/db/models/sql/query.py::Query.get_meta`

- **Q1 Role.** This function returns the model's `_meta` attribute (the `Options` instance) associated with the query.
- **Q2 Connection to symptom.** No direct path exists. The function correctly returns the `self.model._meta` object. A caller then accesses the `ordering` attribute on this object, which contains the problematic `OrderBy` expression. The function itself behaves as expected; the fault lies in how its return value is later processed by a different function.
- **Q3 Counterfactual.** `no` — This is a simple, correct getter function. Modifying it would not fix the bug, as the problem is not in what it returns but in how a caller uses the returned object's attributes.
- **Q4 Alternatives considered.**
  - `Callers of Query.get_meta` — The function that calls `get_meta` and then processes `meta.ordering` is the place to investigate, as it's responsible for handling expressions.
  - `django.db.models.sql.compiler.SQLCompiler.get_order_by` — A likely consumer of the data provided by `get_meta`, this function probably contains the logic that fails to handle `OrderBy` objects correctly.
  - `django.db.models.options.Options` — The class that holds the `ordering` attribute could be involved, but `get_meta` just returns it, it doesn't create or modify it.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a simple getter that is functioning correctly; it is part of the causal background but is not the source of the error.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/sql/query.py::get_order_dir` | high | This function is the site of the crash, but it is likely the victim of being passed an incorrect type, not the root cause of the bug. | Add a type check to handle `OrderBy` objects, but prioritize investigating the caller for the true root cause. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/sql/query.py::Query.get_meta` | high | This function is a simple getter that is functioning correctly; it is part of the causal background but is not the source of the error. |  |

**Causal chains (per candidate)**

- `django/db/models/sql/query.py::get_order_dir`  (score=6.0)  \
  An upstream function (likely SQLCompiler.get_order_by) processes the query's ordering fields from Meta.ordering. → It encounters an OrderBy object and, instead of resolving it, passes it directly to get_order_dir. → get_order_dir receives the OrderBy object as the 'field' argument. → The code attempts `field[0]`, which raises a TypeError because OrderBy objects are not subscriptable.
- `django/db/models/sql/query.py::Query.get_meta`  (score=1.0)  \
  A function processing the query's ordering calls query.get_meta() to access the model's options. → The function correctly returns the model's _meta object. → The caller then accesses the .ordering attribute on this object. → This attribute contains an OrderBy expression, which is later passed incorrectly to get_order_dir.

**next_to_explore:** `['django.db.models.sql.compiler.SQLCompiler.get_order_by', 'django.db.models.sql.query.Query.add_ordering', 'django.db.models.sql.compiler.SQLCompiler._setup_joins', 'django.db.models.options.Options.contribute_to_class', 'django.db.models.query.QuerySet.ordered']`

### Abductive step #3 (iteration=9)

- leading: 1, considering: 1, rejected: 1

**Per-candidate deliberation traces**

#### … CONSIDERING — `django/db/models/sql/query.py::Query.add_ordering`

- **Q1 Role.** This function adds ordering criteria, which can be field names or OrderBy expressions, to the query's 'order by' clause.
- **Q2 Connection to symptom.** This function is on the causal path to the symptom. It is responsible for adding items to the `self.order_by` list. When `Meta.ordering` contains an `OrderBy` expression, this function will add that object to the `self.order_by` list. A downstream function, `get_order_dir`, then fails because it receives this object when it expects a string. The validation logic in `add_ordering` explicitly allows expression objects, so the function itself is likely behaving as designed.
- **Q3 Counterfactual.** `no` — Modifying this function to reject or alter `OrderBy` expressions would likely break other, correct functionality. The problem lies with a downstream consumer of `self.order_by` not being able to handle all the valid types this function correctly adds.
- **Q4 Alternatives considered.**
  - `django/db/models/sql/query.py::get_order_dir` — Preferred, as this is the function that reportedly crashes and should be updated to handle `OrderBy` objects.
  - `django/db/models/sql/compiler.py::SQLCompiler.get_order_by` — Also a strong candidate, as it's the caller of `get_order_dir` and could be responsible for resolving expressions before passing them on.
  - `django/db/models/options.py::Options.contribute_to_class` — Considered a more likely root cause, as it's responsible for initializing the `Meta.ordering` value that starts the problematic chain of events.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function adds the `OrderBy` object to the list that is later processed incorrectly, placing it on the causal path, but the fault is likely in the downstream consumer.

#### ✗ REJECTED — `django/utils/functional.py::Promise`

- **Q1 Role.** This is an empty base class used as a marker to identify lazy objects that will be evaluated at a later time.
- **Q2 Connection to symptom.** No path. This class has no methods or logic that execute. While the bug might involve lazy evaluation of `Meta.ordering` (especially given the context-dependent failure), this class is merely a type marker. The logic for resolving the promise and causing the error would be in other functions that create or handle promise objects.
- **Q3 Counterfactual.** `no` — Modifying this empty class definition would have no effect on the program's logic or the observed symptom.
- **Q4 Alternatives considered.**
  - `django.utils.functional.lazy` — This function actually creates lazy objects and would be a more relevant place to investigate if lazy evaluation is the problem.
  - `django/db/models/sql/query.py::Query.get_initial_ordering` — This function is a likely consumer of a potentially lazy `_meta.ordering` attribute, making it a better candidate.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is an empty marker class with no executable logic related to the bug; it cannot be the cause.

#### ✓ LEADING — `django/db/models/options.py::Options.contribute_to_class`

- **Q1 Role.** This function initializes a model's `_meta` options object by processing and copying attributes from the model's inner `Meta` class.
- **Q2 Connection to symptom.** This function is the first step in the causal chain. It reads the `ordering` attribute from a model's `Meta` class, which in the bug report contains an `OrderBy` expression. It then sets `self.ordering` (which becomes `model._meta.ordering`) to this value without any processing or normalization. This unprepared value is later consumed by query-building code, which eventually leads to the crash in `get_order_dir`. The bug's context-dependency on test setup points to an initialization-time issue, which is exactly this function's domain.
- **Q3 Counterfactual.** `yes` — This function already normalizes other options like `unique_together`. Adding similar normalization logic for the `ordering` option to handle expressions would ensure `_meta.ordering` has a consistent, expected format, which would prevent the downstream crash.
- **Q4 Alternatives considered.**
  - `django/db/models/sql/query.py::Query.get_initial_ordering` — A strong alternative, as it's the first piece of query code to consume `_meta.ordering`, but fixing it here might be less clean than normalizing at the source.
  - `django/db/models/sql/compiler.py::SQLCompiler.get_order_by` — This is another place the fix could go, but it feels more like a patch than addressing the root cause of inconsistent data structure from the model's meta options.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function is the ideal place to normalize `Meta.ordering` values, and its failure to do so for expressions is the likely root cause of the downstream type error.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/options.py::Options.contribute_to_class` | high | This function is the ideal place to normalize `Meta.ordering` values, and its failure to do so for expressions is the likely root cause of the downstream type error. | Add normalization for the 'ordering' option, similar to 'unique_together', to consistently handle expression objects. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/sql/query.py::Query.add_ordering` | medium | This function adds the `OrderBy` object to the list that is later processed incorrectly, placing it on the causal path, but the fault is likely in the downstream consumer. | Ensure consumers of `query.order_by` can handle `OrderBy` objects. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/utils/functional.py::Promise` | high | This is an empty marker class with no executable logic related to the bug; it cannot be the cause. |  |

**Causal chains (per candidate)**

- `django/db/models/sql/query.py::Query.add_ordering`  (score=6.0)  \
  A query's ordering is set, e.g. via `Query.get_initial_ordering` reading from `_meta.ordering`. → Query.add_ordering is called with an `OrderBy` object. → The `OrderBy` object is appended to `self.order_by`. → Later, `SQLCompiler.get_order_by` iterates `self.order_by` and calls `get_order_dir` for each item. → `get_order_dir` receives the `OrderBy` object, expects a string, and raises a TypeError.
- `django/utils/functional.py::Promise`  (score=0.0)  \
  
- `django/db/models/options.py::Options.contribute_to_class`  (score=8.0)  \
  A model is defined with `class Meta: ordering = [OrderBy(...)]`. → During model initialization, `Options.contribute_to_class` is called. → The function copies the `ordering` list containing the `OrderBy` object to `cls._meta.ordering` without normalization. → A query is constructed for this model, and `Query.get_initial_ordering` reads `cls._meta.ordering`. → The `OrderBy` object is passed to `Query.add_ordering`, which adds it to the query's `order_by` list. → Downstream processing of the `order_by` list in `get_order_dir` fails with a TypeError.

**next_to_explore:** `['django/db/models/sql/query.py::Query.get_initial_ordering', 'django/db/models/sql/compiler.py::SQLCompiler.get_order_by', 'django/db/models/sql/query.py::get_order_dir', 'django/db/models/query.py::QuerySet.order_by', 'django/core/management/commands/test.py']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/db/models/sql/compiler.py::SQLCompiler.get_order_by` | 0.9 |
| 2 | `django/db/models/sql/query.py::get_order_dir` | 0.7 |
| 3 | `django/db/models/options.py::Options.contribute_to_class` | 0.5 |
| 4 | `django/db/models/sql/query.py::Query.add_ordering` | 0.4 |
| 5 | `django/db/models/sql/compiler.py::SQLCompiler._setup_joins` | 0.0 |
| 6 | `django/db/models/query.py::QuerySet.ordered` | 0.0 |
| 7 | `django/db/models/sql/compiler.py::SQLCompiler.find_ordering_name` | 0.0 |
| 8 | `django/db/models/query.py::QuerySet.order_by` | 0.0 |
| 9 | `django/db/backends/base/operations.py::BaseDatabaseOperations.force_no_ordering` | 0.0 |
| 10 | `django/db/models/sql/compiler.py::SQLCompiler.get_group_by` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/db/models/sql/compiler.py::SQLCompiler.get_order_by` | 0.900 | high | 1/1 | (254, 376) |
| 2 | `django/db/models/sql/query.py::get_order_dir` | 0.700 | high | 1/1 | (2212, 2223) |
| 3 | `django/db/models/options.py::Options.contribute_to_class` | 0.500 | high | 1/1 | (149, 208) |
| 4 | `django/db/models/sql/query.py::Query.add_ordering` | 0.400 | high | 1/1 | (1846, 1869) |
| 5 | `django/db/models/sql/query.py::Query.get_meta` | 0.271 | high | 1/1 | (284, 290) |
| 6 | `django/db/models/query.py::QuerySet.reverse` | 0.270 | high | 1/1 | (1094, 1100) |
| 7 | `django/db/models/sql/compiler.py::SQLUpdateCompiler.pre_sql_setup` | 0.262 | high | 1/1 | (1450, 1490) |
| 8 | `django/db/backends/base/operations.py::BaseDatabaseOperations.cache_key_culling_sql` | 0.238 | high | 1/1 | (73, 81) |
| 9 | `django/db/backends/base/operations.py::BaseDatabaseOperations.unification_cast_sql` | 0.229 | high | 1/1 | (83, 89) |
| 10 | `django/db/models/query.py::QuerySet.__or__` | 0.227 | high | 1/1 | (324, 336) |
