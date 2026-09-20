# Instance: `django__django-13964`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
Saving parent object after setting on child leads to data loss for parents with non-numeric primary key.
Description
	 
		(last modified by Charlie DeTar)
	 
Given a model with a foreign key relation to another model that has a non-auto CharField as its primary key:
class Product(models.Model):
	sku = models.CharField(primary_key=True, max_length=50)
class Order(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
If the relation is initialized on the parent with an empty instance that does not yet specify its primary key, and the primary key is subsequently defined, the parent does not "see" the primary key's change:
with transaction.atomic():
	order = Order()
	order.product = Product()
	order.product.sku = "foo"
	order.product.save()
	order.save()
	assert Order.objects.filter(product_id="").exists() # Succeeds, but shouldn't
	assert Order.objects.filter(product=order.product).exists() # Fails
Instead of product_id being populated with product.sku, it is set to emptystring. The foreign key constraint which would enforce the existence of a product with sku="" is deferred until the transaction commits. The transaction does correctly fail on commit with a Fo
```

## Stage 3 — Symptoms extracted

- exception types: `['ForeignKeyViolation']`
- error messages: `['ForeignKeyViolation', 'product_id being populated with product.sku, it is set to emptystring']`
- behaviors: `['data loss for parents with non-numeric primary key', 'foreign key constraint deferred', 'transaction fails on commit', "parent does not see the primary key's change", 'product_id is set to emptystring']`
- named APIs: `['models.Model', 'models.CharField', 'models.ForeignKey', 'on_delete.CASCADE', 'transaction.atomic', 'Product.save', 'Order.save', 'Order.objects.filter', 'Product']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/db/models/fields/related.py` | Handles ForeignKey relations and their interaction with primary keys, including setting and saving related objects. |
| 2 | `django/db/models/base.py` | Contains Model class and its save() method, which is central to persisting data and handling relationships. |
| 3 | `django/db/models/sql/query.py` | Deals with constructing and executing SQL queries, including those involving foreign key relationships. |
| 4 | `django/db/backends/base/operations.py` | Abstracts database-specific operations, including those related to data types and query construction for foreign keys. |
| 5 | `django/db/backends/base/schema.py` | Manages database schema changes, including creating and altering tables and columns related to foreign keys. |
| 6 | `django/db/models/fields/__init__.py` | Defines the base Field class and various field types, including ForeignKey, and their behavior. |
| 7 | `django/db/models/fields/related_descriptors.py` | Manages access to related objects, including setting and retrieving values for foreign keys. |
| 8 | `django/db/models/query_utils.py` | Provides utilities for constructing database queries, including Q objects and related lookups. |
| 9 | `django/db/models/lookups.py` | Defines lookups used in filtering queries, including those related to foreign key relationships. |
| 10 | `django/db/backends/sqlite3/base.py` | SQLite backend is mentioned in the issue, so this file is relevant. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/test/testcases.py::TestCase.captureOnCommitCallbacks`

- **Q1 Role.** This is a context manager used in Django's test suite to capture and optionally execute functions registered with `transaction.on_commit()`.
- **Q2 Connection to symptom.** The symptom involves a `ForeignKeyViolation` which occurs when the transaction commits. This function interacts with `on_commit` callbacks, so it could be used in a test to observe this failure. However, it only captures the callbacks; it does not influence the underlying ORM behavior that leads to the incorrect data being saved, which is the root cause of the commit-time failure. The incorrect `product_id` is set during `order.save()`, before this function's context would be relevant.
- **Q3 Counterfactual.** `no` — This is a test utility. Modifying it would not change the core ORM logic that incorrectly determines the foreign key value before the transaction attempts to commit.
- **Q4 Alternatives considered.**
  - `django.db.models.base.Model.save()` — This is a more likely candidate, as it's responsible for preparing and saving the model's state, including the incorrect foreign key value.
  - `django.db.models.fields.related_descriptors.ForwardManyToOneDescriptor.__set__` — This is called on `order.product = ...` and is a prime suspect for where the incorrect state is initially cached.
  - `django.db.transaction.commit` — The actual commit function where the error is raised, but the cause is upstream.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a test utility for observing commit-time behavior, not a part of the ORM logic that causes the incorrect foreign key value to be saved.

#### ✗ REJECTED — `tests/constraints/models.py::UniqueConstraintProduct`

- **Q1 Role.** This is a Django model definition used within the Django test suite specifically for testing `UniqueConstraint` functionality.
- **Q2 Connection to symptom.** No path exists. This model is unrelated to the bug report. The bug involves a `ForeignKey` to a model with a `CharField` primary key. This `UniqueConstraintProduct` model does not have a `ForeignKey` and is used in a different context (testing unique constraints). The name 'Product' is purely coincidental.
- **Q3 Counterfactual.** `no` — Modifying this test model would have no effect on the Django ORM's core handling of foreign key relationships described in the issue.
- **Q4 Alternatives considered.**
  - `The actual Product model from the bug report` — The model definition is central to the problem setup, specifically the `CharField` primary key.
  - `django.db.models.fields.related.ForeignKey` — The field class itself contains the logic for handling the relation, which is where the bug likely lies.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is an unrelated model from the test suite with a coincidental name; it has no connection to the bug's logic.

#### ✗ REJECTED — `tests/model_forms/models.py::Product.__str__`

- **Q1 Role.** This function defines the string representation for a `Product` model instance used in the `model_forms` tests, returning its `slug`.
- **Q2 Connection to symptom.** No path exists. The `__str__` method is used for human-readable representations of an object, not for determining the value of a primary key for a database relationship. The bug is about how the `product_id` column value is determined during `order.save()`, a process that does not involve calling `product.__str__()`.
- **Q3 Counterfactual.** `no` — Changing the string representation of the `Product` model will not affect the internal ORM logic that saves the foreign key value to the database.
- **Q4 Alternatives considered.**
  - `django.db.models.fields.related.ForeignKey.get_attname_column` — This seems highly relevant as it's responsible for getting the column name and value for the foreign key.
  - `django.db.models.fields.related_descriptors.ForwardManyToOneDescriptor.__get__` — This is responsible for retrieving the related object and could be involved in caching stale state.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a string representation method on a test model and is not involved in the ORM's logic for saving foreign key values.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/test/testcases.py::TestCase.captureOnCommitCallbacks` | high | This is a test utility for observing commit-time behavior, not a part of the ORM logic that causes the incorrect foreign key value to be saved. |  |
| `tests/constraints/models.py::UniqueConstraintProduct` | high | This is an unrelated model from the test suite with a coincidental name; it has no connection to the bug's logic. |  |
| `tests/model_forms/models.py::Product.__str__` | high | This is a string representation method on a test model and is not involved in the ORM's logic for saving foreign key values. |  |

**Causal chains (per candidate)**

- `django/test/testcases.py::TestCase.captureOnCommitCallbacks`  (score=0.0)  \
  
- `tests/constraints/models.py::UniqueConstraintProduct`  (score=0.0)  \
  
- `tests/model_forms/models.py::Product.__str__`  (score=0.0)  \
  

**next_to_explore:** `['django.db.models.fields.related_descriptors.ForwardManyToOneDescriptor.__set__', 'django.db.models.fields.related_descriptors.ForwardManyToOneDescriptor.__get__', 'django.db.models.base.Model.save', 'django.db.models.fields.related.ForeignKey.get_prep_value', 'django.db.models.base.Model.save_base']`

### Abductive step #2 (iteration=6)

- leading: 1, considering: 1, rejected: 1

**Per-candidate deliberation traces**

#### … CONSIDERING — `django/db/models/base.py::Model.save`

- **Q1 Role.** This is the main public method for saving a model instance to the database, handling validation, routing, and calling the underlying save implementation.
- **Q2 Connection to symptom.** This function is called when `order.save()` is executed. By this point, the `order` instance's `product_id` field has already been incorrectly set to an empty string by a prior assignment. The `save` method, specifically its helper `_prepare_related_fields_for_save`, fails to detect and correct this stale value before proceeding to call `save_base`, which attempts to persist the incorrect data, ultimately leading to a `ForeignKeyViolation` upon transaction commit.
- **Q3 Counterfactual.** `partially` — A modification here, likely in `_prepare_related_fields_for_save`, to re-synchronize the foreign key ID from the related object before saving would fix the symptom. However, this would be treating the symptom, as the root cause is the initial incorrect state being set during assignment.
- **Q4 Alternatives considered.**
  - `related_descriptors.py::ForwardManyToOneDescriptor.__set__` — Preferred, as it's the function that creates the incorrect, stale state in the first place.
  - `base.py::Model.save_base` — Not preferred, as it's a lower-level utility that operates on data already prepared by `save`.
  - `base.py::Model._prepare_related_fields_for_save` — This is a strong candidate within `save` that is more specific to the problem.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function executes the save with the wrong data and could be patched, but it doesn't create the wrong data itself.

#### ✓ LEADING — `django/db/models/fields/related_descriptors.py::ForwardManyToOneDescriptor.__set__`

- **Q1 Role.** This function is the descriptor's setter, executed when a value is assigned to a foreign key or one-to-one field on a model instance.
- **Q2 Connection to symptom.** Yes, this is the origin of the bug. The execution path is:
1. `order.product = Product()` is executed.
2. `__set__` is called with `instance=order` and `value=Product()`, an unsaved object whose primary key (`sku`) is empty.
3. The descriptor reads the primary key value from the `Product` instance (which is `''`) and sets the `order.product_id` attribute to this empty string.
4. Later, `order.product.sku = "foo"` modifies the `Product` instance, but this does not re-trigger `__set__` on the `order` instance.
5. When `order.save()` is called, it uses the stale `product_id=''` value, causing the observed data loss and subsequent `ForeignKeyViolation`.
- **Q3 Counterfactual.** `yes` — If this function were changed to not cache the PK value from an unsaved object at assignment time, but instead fetched the PK value at save time, the correct value ("foo") would be used.
- **Q4 Alternatives considered.**
  - `base.py::Model.save` — Not preferred; `save` acts on the incorrect state created by `__set__`, so fixing it there is downstream of the cause.
  - `models.py::Product.save` — Not relevant; saving the `Product` works correctly, the issue is how the `Order` object references it.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function is where the stale foreign key value is set, directly causing the parent object to miss the later update to the child's primary key.

#### ✗ REJECTED — `django/db/models/base.py::Model.save_base`

- **Q1 Role.** This function handles the low-level, backend-agnostic parts of saving a model, including signal dispatching, transaction management, and calling the database insertion/update method.
- **Q2 Connection to symptom.** No path. By the time `save_base` is called by `Model.save`, the model instance it receives already has its `product_id` field incorrectly set to an empty string. This function's role is to orchestrate the database write, not to determine or validate the values of the model's fields. It correctly attempts to save the data it is given, which then fails at the database level.
- **Q3 Counterfactual.** `no` — Modifying this low-level function would be incorrect; the logic for resolving foreign key relationships belongs at a higher level in the ORM, not in this generic save handler.
- **Q4 Alternatives considered.**
  - `base.py::Model.save` — Preferred, as it's the caller of `save_base` and contains higher-level logic.
  - `related_descriptors.py::ForwardManyToOneDescriptor.__set__` — Preferred, as it's the source of the incorrect data that `save_base` is eventually asked to persist.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is too low-level; it's a generic part of the save machinery and is not responsible for the ORM-specific logic that caused the bug.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/fields/related_descriptors.py::ForwardManyToOneDescriptor.__set__` | high | This function is where the stale foreign key value is set, directly causing the parent object to miss the later update to the child's primary key. | When an unsaved instance is assigned, the descriptor should fetch the primary key value at save-time, not at assignment-time. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/base.py::Model.save` | medium | This function executes the save with the wrong data and could be patched, but it doesn't create the wrong data itself. | In `_prepare_related_fields_for_save`, re-sync the FK field (`product_id`) from the related object (`product.pk`) if the related object exists. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/models/base.py::Model.save_base` | high | This function is too low-level; it's a generic part of the save machinery and is not responsible for the ORM-specific logic that caused the bug. |  |

**Causal chains (per candidate)**

- `django/db/models/base.py::Model.save`  (score=5.0)  \
  The `order` object's `product_id` is already incorrectly set to `''`. → `order.save()` is called. → The `_prepare_related_fields_for_save` helper is called but fails to correct the stale `product_id`. → `save` calls `save_base` with the `order` instance containing `product_id=''`. → The database operation is queued and fails on transaction commit with a `ForeignKeyViolation`.
- `django/db/models/fields/related_descriptors.py::ForwardManyToOneDescriptor.__set__`  (score=9.0)  \
  `order.product = Product()` triggers the `__set__` method. → The `value` (the new `Product` instance) has an empty primary key (`sku`). → The descriptor sets the underlying `order.product_id` to the value of the product's primary key, which is `''`. → The `order` object now holds a stale `product_id` value. → A later `order.save()` persists this incorrect value, leading to a `ForeignKeyViolation`.
- `django/db/models/base.py::Model.save_base`  (score=1.0)  \
  `save_base` is called with an `Order` instance that already has `product_id` incorrectly set to `''`. → It calls `_save_table` to generate and execute the SQL INSERT. → The database operation is deferred inside the transaction. → The transaction fails to commit due to the foreign key constraint violation.

**next_to_explore:** `['django/db/models/base.py::Model._prepare_related_fields_for_save', 'django/db/models/fields/related.py::ForeignObject.get_related_value', 'django/db/models/fields/related.py::ForeignKey.get_db_prep_value', 'django/db/models/fields/related.py::ForeignKey.get_attname']`

## Stage 5 — Listwise rerank decisions

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/db/models/base.py::Model.save_base` | 0.476 | high | 1/1 | (730, 777) |
| 2 | `django/db/models/fields/related_descriptors.py::ForwardManyToOneDescriptor.__set__` | 0.409 | high | 1/1 | (203, 267) |
| 3 | `django/db/models/base.py::Model.save` | 0.391 | high | 1/1 | (672, 727) |
| 4 | `django/db/models/base.py::Model._prepare_related_fields_for_save` | 0.376 | high | 1/1 | (911, 943) |
| 5 | `django/db/models/base.py::Model._set_pk_val` | 0.314 | high | 1/1 | (577, 581) |
| 6 | `django/db/models/fields/related.py::ForeignKey.get_db_prep_save` | 0.312 | high | 1/1 | (965, 971) |
| 7 | `django/db/models/base.py::Model._save_parents` | 0.293 | high | 1/1 | (781, 807) |
| 8 | `django/db/models/fields/related.py::lazy_related_operation` | 0.279 | high | 1/1 | (62, 80) |
| 9 | `django/db/models/fields/related.py::ForeignKey._check_on_delete` | 0.230 | high | 1/1 | (841, 862) |
| 10 | `django/db/models/sql/query.py::Query.add_select_related` | 0.180 | high | 1/1 | (2035, 2049) |
