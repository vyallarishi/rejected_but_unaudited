# Instance: `django__django-15525`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
loaddata fails on non-default database when natural keys uses foreign keys.
Description
	 
		(last modified by François Granade)
	 
I've got a one-to-many relationship between two models Book and Author, that define a natural keys in both models. I'm loading some data from a fixture. It works in the default database, but when I use it a second database, then I get an exception. 
I'm relatively new to natural keys and to serializers, but I wouldn't expect things to work differently in the default DB and others ?
I've committed a test project here: ​https://github.com/farialima/django-bug
(The problem doesn't appear if the data is already present in the default DB)
The error:
% cat books.json | ./manage.py loaddata --database other --format json -
Traceback (most recent call last):
 File "/Users/francois/Library/Caches/pypoetry/virtualenvs/exportbug-PGt-cwXF-py3.9/lib/python3.9/site-packages/django/db/models/fields/related_descriptors.py", line 187, in __get__
	rel_obj = self.field.get_cached_value(instance)
 File "/Users/francois/Library/Caches/pypoetry/virtualenvs/exportbug-PGt-cwXF-py3.9/lib/python3.9/site-packages/django/db/models/fields/mixins.py", line 15, in get_cached_value
```

## Stage 3 — Symptoms extracted

- exception types: `['KeyError', 'DoesNotExist']`
- error messages: `["KeyError: 'author'", 'Author matching query does not exist.']`
- behaviors: `['loaddata fails', 'natural keys with foreign keys', 'non-default database']`
- named APIs: `['models.Manager.get_by_natural_key', 'models.Model.natural_key', 'serializers.serialize', 'Author.natural_key', 'Book.natural_key']`
- stack frames: `[{'file': '/Users/francois/Library/Caches/pypoetry/virtualenvs/exportbug-PGt-cwXF-py3.9/lib/python3.9/site-packages/django/db/models/fields/related_descriptors.py', 'func': '__get__', 'line': 187}, {'file': '/Users/francois/Library/Caches/pypoetry/virtualenvs/exportbug-PGt-cwXF-py3.9/lib/python3.9/site-packages/django/db/models/fields/mixins.py', 'func': 'get_cached_value', 'line': 15}, {'file': '/Users/francois/Library/Caches/pypoetry/virtualenvs/exportbug-PGt-cwXF-py3.9/lib/python3.9/site-packages/django/core/serializers/json.py', 'func': 'Deserializer', 'line': 70}, {'file': '/Users/francois/Library/Caches/pypoetry/virtualenvs/exportbug-PGt-cwXF-py3.9/lib/python3.9/site-packages/django/core/serializers/python.py', 'func': 'Deserializer', 'line': 174}, {'file': '/Users/francois/Library/Caches/pypoetry/virtualenvs/exportbug-PGt-cwXF-py3.9/lib/python3.9/site-packages/django/core/serializers/base.py', 'func': 'build_instance', 'line': 332}, {'file': '/Users/francois/lmad/src/django-bug/testbug/models.py', 'func': 'natural_key', 'line': 33}, {'file': '/Users/francois/Library/Caches/pypoetry/virtualenvs/exportbug-PGt-cwXF-py3.9/lib/python3.9/site-packages/django/db/models/fields/related_descriptors.py', 'func': '__get__', 'line': 205}, {'file': '/Users/francois/Library/Caches/pypoetry/virtualenvs/exportbug-PGt-cwXF-py3.9/lib/python3.9/site-packages/django/db/models/fields/related_descriptors.py', 'func': 'get_object', 'line': 168}, {'file': '/Users/francois/Library/Caches/pypoetry/virtualenvs/exportbug-PGt-cwXF-py3.9/lib/python3.9/site-packages/django/db/models/query.py', 'func': 'get', 'line': 496}]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/core/serializers/base.py` | Handles deserialization and object building, potentially related to natural key handling. |
| 2 | `django/core/serializers/python.py` | Implements the Python serializer, which is used as a base for JSON and handles object deserialization. |
| 3 | `django/core/serializers/json.py` | Implements the JSON serializer and deserializer, which is directly involved in loading data from JSON fixtures. |
| 4 | `django/db/models/fields/related.py` | Manages ForeignKey and ManyToManyField relations, crucial for natural key handling with foreign keys. |
| 5 | `django/db/models/base.py` | Defines the base Model class and its metaclass, involved in object creation and field handling. |
| 6 | `django/db/models/manager.py` | Manages querysets and object retrieval, potentially involved in natural key lookups. |
| 7 | `django/db/models/query.py` | Defines QuerySet, which is used to retrieve objects and resolve relations. |
| 8 | `django/db/backends/base/operations.py` | Provides database-specific operations, including quoting and data type handling. |
| 9 | `django/db/backends/base/base.py` | Defines the base DatabaseWrapper class, responsible for connection management and transaction handling. |
| 10 | `django/core/management/commands/loaddata.py` | The loaddata command itself, which is failing in the described scenario. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `tests/sessions_tests/tests.py::SessionTestsMixin.test_pop_no_default_keyerror_raised`

- **Q1 Role.** This is a unit test to ensure that calling pop() on a session object for a nonexistent key without a default value raises a KeyError.
- **Q2 Connection to symptom.** No path. Although the observed symptoms include a `KeyError`, it originates from `instance._state.fields_cache` within the model field descriptor logic, which is completely unrelated to Django's session handling framework being tested here.
- **Q3 Counterfactual.** `no` — This is a test function and is not part of the `loaddata` execution path. Modifying it would have no impact on the bug.
- **Q4 Alternatives considered.**
  - `django/db/models/fields/mixins.py::get_cached_value` — This is where the `KeyError` actually originates in the traceback, making it directly relevant.
  - `django/db/models/fields/related_descriptors.py::__get__` — This is the caller of `get_cached_value` and part of the causal path for the lazy loading that fails.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a test for the session framework and is unrelated to model deserialization or database routing, despite mentioning `KeyError`.

#### ✗ REJECTED — `tests/queryset_pickle/tests.py::PickleabilityTestCase.test_reverse_one_to_one_relatedobjectdoesnotexist_class`

- **Q1 Role.** This is a unit test that verifies the dynamically generated `RelatedObjectDoesNotExist` exception class can be successfully pickled and unpickled.
- **Q2 Connection to symptom.** No path. The symptom is an `Author.DoesNotExist` exception, which is a standard model `DoesNotExist` exception. The exception class being tested here, `RelatedObjectDoesNotExist`, is specific to reverse one-to-one relationships, whereas the bug involves a forward many-to-one (`ForeignKey`) relationship. This code is not executed.
- **Q3 Counterfactual.** `no` — This is a test for pickling an exception class and is not executed during `loaddata`. Modifying it would have no effect on the bug.
- **Q4 Alternatives considered.**
  - `django/db/models/query.py::QuerySet.get` — This is the function that actually raises the `DoesNotExist` exception seen in the traceback.
  - `django/db/models/fields/related_descriptors.py::get_object` — This function calls `QuerySet.get` and is a direct step in the causal chain leading to the exception.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This test concerns pickling and a different type of relationship (reverse one-to-one) than the one implicated in the bug.

#### ✗ REJECTED — `django/db/models/fields/related_descriptors.py::ReverseOneToOneDescriptor.RelatedObjectDoesNotExist`

- **Q1 Role.** This is a property that dynamically creates a custom `RelatedObjectDoesNotExist` exception class for a reverse one-to-one relationship.
- **Q2 Connection to symptom.** No path. The bug involves a `ForeignKey` (a forward many-to-one relationship), which uses the `ForwardManyToOneDescriptor`. This function is part of the `ReverseOneToOneDescriptor`, which is used for `OneToOneField` reverse access and is not on the execution path of the failing code.
- **Q3 Counterfactual.** `no` — This function is not called during the execution that produces the symptom, as the relationship in question is not a reverse one-to-one.
- **Q4 Alternatives considered.**
  - `django/db/models/fields/related_descriptors.py::ForwardManyToOneDescriptor.__get__` — This is the correct descriptor for the `book.author` access and is on the actual execution path.
  - `testbug/models.py::Book.natural_key` — The error occurs during a call to this method, specifically when accessing `self.author`.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for reverse one-to-one relations, but the bug occurs with a forward foreign key.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `tests/sessions_tests/tests.py::SessionTestsMixin.test_pop_no_default_keyerror_raised` | high | This is a test for the session framework and is unrelated to model deserialization or database routing, despite mentioning `KeyError`. |  |
| `tests/queryset_pickle/tests.py::PickleabilityTestCase.test_reverse_one_to_one_relatedobjectdoesnotexist_class` | high | This test concerns pickling and a different type of relationship (reverse one-to-one) than the one implicated in the bug. |  |
| `django/db/models/fields/related_descriptors.py::ReverseOneToOneDescriptor.RelatedObjectDoesNotExist` | high | This function is for reverse one-to-one relations, but the bug occurs with a forward foreign key. |  |

**Causal chains (per candidate)**

- `tests/sessions_tests/tests.py::SessionTestsMixin.test_pop_no_default_keyerror_raised`  (score=0.0)  \
  
- `tests/queryset_pickle/tests.py::PickleabilityTestCase.test_reverse_one_to_one_relatedobjectdoesnotexist_class`  (score=0.0)  \
  
- `django/db/models/fields/related_descriptors.py::ReverseOneToOneDescriptor.RelatedObjectDoesNotExist`  (score=0.0)  \
  

**next_to_explore:** `['django/core/serializers/python.py::Deserializer', 'django/db/models/fields/related_descriptors.py::ForwardManyToOneDescriptor.__get__', 'django/core/serializers/base.py::build_instance', 'django/db/models/manager.py::Manager.db_manager', 'django/db/models/query.py::QuerySet.get']`

### Abductive step #2 (iteration=6)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/core/serializers/python.py::Deserializer`

- **Q1 Role.** This function deserializes simple Python objects, typically from a JSON or XML fixture, back into Django ORM instances.
- **Q2 Connection to symptom.** Yes, this function is a key part of the causal chain. When deserializing a `Book` object that has a natural foreign key to an `Author`, this function resolves the author's natural key to an object, but then (based on the resulting error) appears to use only the author's primary key (`author_id`) to populate the data for the new `Book` instance. This data is then passed to `base.build_instance`, which creates a temporary `Book` object. When `natural_key()` is called on this temporary object, it must lazily fetch the `author` relationship. This lazy fetch loses the `--database other` context, queries the `default` database, and fails with `DoesNotExist`, because the `Author` object only exists in the 'other' database.
- **Q3 Counterfactual.** `yes` — If this deserializer were modified to pass the fully resolved `Author` object to `build_instance` instead of just its primary key, the subsequent lazy database lookup would be unnecessary, preventing the error.
- **Q4 Alternatives considered.**
  - `django/core/serializers/base.py::build_instance` — This is a stronger candidate for the root cause, as it creates the temporary object and fails to propagate the database context (`using`) to it. A fix here would be more general.
  - `django/db/models/fields/related_descriptors.py::ForwardManyToOneDescriptor.__get__` — This function raises the final exception, but it's behaving correctly given the incorrect database context it's operating in. It's a symptom, not a cause.
  - `testbug/models.py::Book.natural_key` — The user could work around the bug by changing this method, but the method itself is a valid implementation and the bug lies within Django's deserialization logic.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function's strategy of resolving a natural foreign key to a PK forces a lazy load whose context is then lost, directly causing the failure in a multi-db scenario.

#### ✗ REJECTED — `django/db/models/fields/related_descriptors.py::ForwardManyToOneDescriptor.__get__`

- **Q1 Role.** This descriptor method implements the logic for accessing a related object on a model instance via a foreign key (e.g., `book.author`).
- **Q2 Connection to symptom.** Yes, this function is directly in the execution path and is where the exceptions originate. The `KeyError` happens when it checks the instance's cache for the related object. When the cache is empty, it proceeds to fetch the object from the database by calling `self.get_object(instance)`. This database query is what raises the `DoesNotExist` exception because it is executed against the wrong database (the default one instead of 'other').
- **Q3 Counterfactual.** `no` — Modifying this function would be treating the symptom, not the cause. The function's logic is correct; the problem is that it's being invoked on a model instance that lacks the correct database state (`_state.db`), a problem created upstream.
- **Q4 Alternatives considered.**
  - `django/core/serializers/python.py::Deserializer` — Preferred, as it creates the situation that leads to the problematic lazy load.
  - `django/core/serializers/base.py::build_instance` — Strongly preferred, as it's the function that creates the temporary instance without propagating the database context.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function correctly executes its logic but fails because its inputs (an instance with missing DB context) are flawed by an upstream process.

#### ✗ REJECTED — `django/db/models/manager.py::Manager`

- **Q1 Role.** This is the default manager class that is added to every Django model, providing the standard database query operations.
- **Q2 Connection to symptom.** No path. This file defines the `Manager` class as `class Manager(BaseManager.from_queryset(QuerySet)): pass`. It contains no executable logic itself. While manager methods are used during the deserialization process (e.g., `get_by_natural_key`), the bug is not in this specific class definition.
- **Q3 Counterfactual.** `no` — The class is just a `pass` statement inheriting from a base class. Modifying it would have no effect on the bug, as the relevant logic resides in its parent classes (`BaseManager`, `QuerySet`) or in user-defined subclasses.
- **Q4 Alternatives considered.**
  - `django.db.models.manager.BaseManager` — This would be a relevant file to investigate, as it contains the actual implementation inherited by `Manager`.
  - `testbug/models.py::BookManager` — The user-defined manager is involved, but its `get_by_natural_key` implementation seems correct; the issue is the context in which other methods are called.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is an empty class definition that simply inherits from a base manager; it cannot be the source of the bug.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/core/serializers/python.py::Deserializer` | high | This function's strategy of resolving a natural foreign key to a PK forces a lazy load whose context is then lost, directly causing the failure in a multi-db scenario. | Instead of resolving the natural foreign key to a PK, resolve it to the full object and pass that to `build_instance` to avoid the lazy load. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/fields/related_descriptors.py::ForwardManyToOneDescriptor.__get__` | high | This function correctly executes its logic but fails because its inputs (an instance with missing DB context) are flawed by an upstream process. |  |
| `django/db/models/manager.py::Manager` | high | This is an empty class definition that simply inherits from a base manager; it cannot be the source of the bug. |  |

**next_to_explore:** `['django/core/serializers/base.py::build_instance', 'django/core/serializers/base.py::Deserializer.handle_fk_values', 'django/db/models/base.py::Model.__init__', 'django/db/models/fields/related_descriptors.py::ForwardManyToOneDescriptor.get_object', 'django/core/management/commands/loaddata.py::Command.handle']`

## Stage 5 — Listwise rerank decisions

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/core/serializers/python.py::Deserializer` | 0.367 | high | 1/1 | (88, 175) |
| 2 | `django/db/models/base.py::Model._check_model_name_db_lookup_clashes` | 0.302 | high | 1/1 | (1721, 1742) |
| 3 | `django/db/models/fields/related.py::ForeignKey.get_default` | 0.264 | high | 1/1 | (1126, 1131) |
| 4 | `django/db/models/fields/related.py::ForeignKey.db_type` | 0.260 | high | 1/1 | (1176, 1177) |
| 5 | `django/db/models/base.py::Model.from_db` | 0.256 | high | 1/1 | (592, 602) |
| 6 | `django/db/models/fields/related_descriptors.py::ForwardManyToOneDescriptor.__get__` | 0.251 | high | 1/1 | (170, 219) |
| 7 | `django/db/models/fields/related.py::ForeignKey.get_db_converters` | 0.236 | high | 1/1 | (1187, 1191) |
| 8 | `django/db/models/base.py::Model._check_default_pk` | 0.229 | high | 1/1 | (1496, 1525) |
| 9 | `django/core/serializers/base.py::Serializer.handle_fk_field` | 0.216 | high | 1/1 | (210, 216) |
| 10 | `django/db/models/manager.py::Manager` | 0.187 | high | 1/1 | (176, 177) |
