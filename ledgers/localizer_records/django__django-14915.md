# Instance: `django__django-14915`

- runs: 1   termination: `ledger_informed`   think-high calls: 4

## Issue (truncated to 1200 chars)

```
ModelChoiceIteratorValue is not hashable.
Description
	
Recently I migrated from Django 3.0 to Django 3.1. In my code, I add custom data-* attributes to the select widget options. After the upgrade some of those options broke. Error is {TypeError}unhashable type: 'ModelChoiceIteratorValue'.
Example (this one breaks):
	def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
		context = super().create_option(name, value, label, selected, index, subindex, attrs)
		if not value:
			return context
		if value in self.show_fields: # This is a dict {1: ['first_name', 'last_name']}
			context['attrs']['data-fields'] = json.dumps(self.show_fields[value])
However, working with arrays is not an issue:
	def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
		context = super().create_option(name, value, label, selected, index, subindex, attrs)
		if not value:
			return context
		if value in allowed_values: # This is an array [1, 2]
			...
```

## Stage 3 — Symptoms extracted

- exception types: `['TypeError']`
- error messages: `["unhashable type: 'ModelChoiceIteratorValue'"]`
- behaviors: `['select widget options broke', 'options broke']`
- named APIs: `['super().create_option', 'json.dumps']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/forms/models.py` | The issue involves ModelChoiceIteratorValue which is related to model forms and choices. |
| 2 | `django/contrib/admin/options.py` | The issue occurs in the admin, which uses ModelAdmin and create_option. |
| 3 | `django/db/models/fields/related.py` | The issue involves ModelChoiceIteratorValue, which is related to ForeignKey and related fields. |
| 4 | `django/db/models/query.py` | Querysets are used to retrieve data for the select widget options. |
| 5 | `django/forms/fields.py` | The select widget is a form field. |
| 6 | `django/forms/widgets.py` | The select widget is a form widget. |
| 7 | `django/contrib/admin/helpers.py` | The admin uses helpers to render forms. |
| 8 | `django/core/serializers/base.py` | Serialization might be involved if the data is being serialized before being used in the widget. |
| 9 | `django/contrib/staticfiles/finders.py` | Static files might be involved if the widget uses custom CSS or JavaScript. |
| 10 | `django/core/management/commands/collectstatic.py` | Collectstatic is used to collect static files. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/utils/hashable.py::make_hashable`

- **Q1 Role.** This function attempts to convert a given value into a hashable equivalent, raising a TypeError if the value is non-iterable and non-hashable.
- **Q2 Connection to symptom.** No path exists. The symptom is a `TypeError` raised from an implicit call to the built-in `hash()` function on a `ModelChoiceIteratorValue` instance. This utility function is not on the execution path that leads to the error; in fact, the error occurs precisely because a function like this was not used before the dictionary lookup.
- **Q3 Counterfactual.** `no` — The user's code does not call this function, so modifying it would have no effect on the execution path that triggers the `TypeError`.
- **Q4 Alternatives considered.**
  - `django.forms.models.ModelChoiceIteratorValue.__hash__` — The absence of this method is the direct cause of the object being unhashable; defining it would fix the issue.
  - `User's create_option method` — The user could work around the issue by changing `value` to `value.value` or `str(value)` before the dictionary lookup.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a utility to make values hashable; it is not called in the code path that produces the error.

#### ✗ REJECTED — `django/forms/models.py::ModelChoiceIteratorValue.__init__`

- **Q1 Role.** This is the constructor for the `ModelChoiceIteratorValue` class, initializing an instance with a `value` and its corresponding model `instance`.
- **Q2 Connection to symptom.** Yes, an indirect path exists. 1. An instance of `ModelChoiceIteratorValue` is created via `__init__`. 2. This instance is passed as the `value` argument to the user's `create_option` method. 3. The user's code `if value in self.show_fields:` attempts to use this instance as a dictionary key. 4. This implicitly calls `hash(value)`, which fails because the class is unhashable, raising the `TypeError`.
- **Q3 Counterfactual.** `no` — Modifying the constructor would not make instances of the class hashable. Hashability is determined by the class definition (i.e., the presence of a `__hash__` method), not the constructor's logic.
- **Q4 Alternatives considered.**
  - `django.forms.models.ModelChoiceIteratorValue.__hash__` — Defining this method on the class is the most direct way to fix the problem.
  - `django.forms.models.ModelChoiceIteratorValue.__eq__` — The presence of a custom `__eq__` without a `__hash__` makes a class unhashable by default in Python 3; this is a likely reason for the behavior.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This constructor creates the object that later causes the error, but it does not control the object's hashability.

#### ✗ REJECTED — `django/forms/models.py::ModelChoiceIteratorValue.__str__`

- **Q1 Role.** This function defines the string representation of a `ModelChoiceIteratorValue` instance, which is simply the string representation of its `value` attribute.
- **Q2 Connection to symptom.** No path exists. The symptom is a `TypeError` from hashing an object (`hash(obj)`), whereas this function is invoked for string conversion (`str(obj)`). These are distinct operations, and the error-producing code path does not involve string conversion.
- **Q3 Counterfactual.** `no` — Modifying the string representation of the object has no bearing on its hashability, so the `TypeError` would still be raised.
- **Q4 Alternatives considered.**
  - `django.forms.models.ModelChoiceIteratorValue.__hash__` — This is the missing method that would make the object hashable and resolve the `TypeError`.
  - `User's create_option method` — A workaround is possible here by explicitly calling `str(value)` before the lookup, which would use this `__str__` method.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function handles string conversion, which is unrelated to the hashing operation that causes the `TypeError`.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/utils/hashable.py::make_hashable` | high | This function is a utility to make values hashable; it is not called in the code path that produces the error. |  |
| `django/forms/models.py::ModelChoiceIteratorValue.__init__` | high | This constructor creates the object that later causes the error, but it does not control the object's hashability. |  |
| `django/forms/models.py::ModelChoiceIteratorValue.__str__` | high | This function handles string conversion, which is unrelated to the hashing operation that causes the `TypeError`. |  |

**Causal chains (per candidate)**

- `django/utils/hashable.py::make_hashable`  (score=0.0)  \
  
- `django/forms/models.py::ModelChoiceIteratorValue.__init__`  (score=2.0)  \
  ModelChoiceIteratorValue.__init__ is called, creating an unhashable object. → The object is passed to the user's `create_option` method as `value`. → The user's code `if value in self.show_fields:` attempts to hash the object for a dictionary lookup. → A `TypeError` is raised because the object is unhashable.
- `django/forms/models.py::ModelChoiceIteratorValue.__str__`  (score=0.0)  \
  

**next_to_explore:** `['django.forms.models.ModelChoiceIteratorValue.__hash__', 'django.forms.models.ModelChoiceIteratorValue.__eq__', 'django.forms.models.ModelChoiceIterator', 'django.forms.models.ModelChoiceIterator.choices', 'django.forms.widgets.Select.create_option']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 0, rejected: 0

### Abductive step #3 (iteration=9)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/forms/widgets.py::ChoiceWidget.create_option`

- **Q1 Role.** This function constructs a dictionary of context data used to render a single <option> element within a <select> widget.
- **Q2 Connection to symptom.** No path from this function produces the symptom. This function is called by the user's custom `create_option` method via `super()`. The `TypeError` occurs in the user's code when it attempts to use the `value` argument (which is a `ModelChoiceIteratorValue` object) as a key in a dictionary lookup. This function receives the unhashable `value` but does not perform any action that would cause the `TypeError`.
- **Q3 Counterfactual.** `no` — The error occurs in the calling user code, which uses the original `value` argument. Modifying what this superclass method returns in its context dictionary would not affect the `value` variable in the caller's scope.
- **Q4 Alternatives considered.**
  - `django.forms.models.ModelChoiceIteratorValue` — The class of the object that is unhashable; adding a `__hash__` method here would fix the issue.
  - `django.forms.models.ModelChoiceIterator.choice` — This method creates and returns the `ModelChoiceIteratorValue` instance; it's the origin of the problematic object.
  - `User's custom create_option` — The site of the crash; could be fixed by using `value.value` instead of `value`, but the goal is to find the framework cause.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is on the execution path but does not cause the error; the unhashable object is passed to it and the failing operation happens in the subclass.

#### ✗ REJECTED — `django/contrib/auth/models.py::AnonymousUser.__hash__`

- **Q1 Role.** This function provides a constant hash value for `AnonymousUser` instances, allowing them to be used in hash-based collections.
- **Q2 Connection to symptom.** No path exists. The symptom is a `TypeError` for an unhashable `ModelChoiceIteratorValue`. This function is for a completely different type, `AnonymousUser`, and is unrelated to the forms machinery that is causing the bug.
- **Q3 Counterfactual.** `no` — Modifying the hash implementation for `AnonymousUser` would have no effect on the hashability of `ModelChoiceIteratorValue`.
- **Q4 Alternatives considered.**
  - `django.forms.models.ModelChoiceIteratorValue` — The class that is actually unhashable and causing the `TypeError`.
  - `django.forms.models.ModelChoiceIteratorValue.__eq__` — The presence of this method without a `__hash__` method is why `ModelChoiceIteratorValue` is unhashable.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is entirely unrelated to the types (`ModelChoiceIteratorValue`) and components (forms widgets) involved in the bug.

#### ✗ REJECTED — `tests/select_related/tests.py::SelectRelatedTests.test_select_related_after_values`

- **Q1 Role.** This is a test function that verifies that calling `select_related()` after `values()` on a queryset correctly raises a `TypeError`.
- **Q2 Connection to symptom.** No path exists. This is a test case for the ORM, not for form widgets. While it involves a `TypeError`, the context and error message are completely different from the observed symptom.
- **Q3 Counterfactual.** `no` — This is a test function. Modifying or deleting it would have no effect on the runtime behavior of the Django forms framework.
- **Q4 Alternatives considered.**
  - `django.forms.models.ModelChoiceIteratorValue` — The class that is unhashable, which is the core of the problem.
  - `User's custom create_option` — The location where the `TypeError` is raised.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a test for a different part of the framework and is unrelated to the bug.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/widgets.py::ChoiceWidget.create_option` | high | This function is on the execution path but does not cause the error; the unhashable object is passed to it and the failing operation happens in the subclass. |  |
| `django/contrib/auth/models.py::AnonymousUser.__hash__` | high | This function is entirely unrelated to the types (`ModelChoiceIteratorValue`) and components (forms widgets) involved in the bug. |  |
| `tests/select_related/tests.py::SelectRelatedTests.test_select_related_after_values` | high | This is a test for a different part of the framework and is unrelated to the bug. |  |

**Causal chains (per candidate)**

- `django/forms/widgets.py::ChoiceWidget.create_option`  (score=0.0)  \
  
- `django/contrib/auth/models.py::AnonymousUser.__hash__`  (score=0.0)  \
  
- `tests/select_related/tests.py::SelectRelatedTests.test_select_related_after_values`  (score=0.0)  \
  

**next_to_explore:** `['django.forms.models.ModelChoiceIteratorValue.__eq__', 'django.forms.models.ModelChoiceIteratorValue.__init__', 'django.forms.models.ModelChoiceIterator.choice', 'django.forms.models.ModelChoiceIterator.__iter__', 'django.forms.widgets.Select.render_options']`

### Abductive step #4 (iteration=12)

- leading: 1, considering: 1, rejected: 1

**Per-candidate deliberation traces**

#### … CONSIDERING — `django/forms/models.py::ModelChoiceIterator.__iter__`

- **Q1 Role.** This function is an iterator that yields the choices for a ModelChoiceField, including an optional empty label.
- **Q2 Connection to symptom.** Yes, a path exists. 
1. This iterator is consumed to render a select widget.
2. For each model object in the queryset, it calls `self.choice(obj)`.
3. `self.choice(obj)` returns a choice tuple where the value is a `ModelChoiceIteratorValue` instance.
4. This iterator yields that tuple.
5. The `value` (`ModelChoiceIteratorValue` instance) is passed to the user's `create_option` method.
6. The user's code `if value in self.show_fields:` attempts to hash this value for a dictionary lookup, which fails because `ModelChoiceIteratorValue` is not hashable, raising a `TypeError`.
- **Q3 Counterfactual.** `yes` — If this function were modified to yield the prepared value directly, e.g., `yield (self.field.prepare_value(obj), self.field.label_from_instance(obj))`, the `value` would be a simple hashable type, and the user's code would not fail.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::ModelChoiceIterator.choice` — Preferred, as it's the function that actually creates the problematic `ModelChoiceIteratorValue` object.
  - `django/forms/models.py::ModelChoiceIteratorValue.__hash__` — Preferred as a more direct fix; making the value object hashable would solve the problem without changing the iteration logic.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function is on the direct causal path, yielding the unhashable object that causes the TypeError, but it doesn't create the object itself.

#### ✓ LEADING — `django/forms/models.py::ModelChoiceIterator.choice`

- **Q1 Role.** This method creates a single choice tuple `(value, label)` for a model object, wrapping the value in a `ModelChoiceIteratorValue` object.
- **Q2 Connection to symptom.** Yes, this is a direct cause.
1. This function is called by `ModelChoiceIterator.__iter__`.
2. It instantiates `ModelChoiceIteratorValue` for the choice's value.
3. This object is eventually passed as the `value` parameter to the user's `create_option` method.
4. The user's code attempts to use this `value` as a dictionary key.
5. Because `ModelChoiceIteratorValue` is not hashable, this operation raises the observed `TypeError`.
- **Q3 Counterfactual.** `yes` — If this function returned the prepared value `self.field.prepare_value(obj)` directly instead of wrapping it in `ModelChoiceIteratorValue`, the value would be hashable and the symptom would disappear.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::ModelChoiceIteratorValue.__hash__` — This is the ideal fix; making `ModelChoiceIteratorValue` hashable would solve the issue while preserving the new object structure.
  - `User's custom create_option method` — The user could change their code to access `value.value`, but this is a workaround for a regression in the framework.
  - `django/forms/models.py::ModelChoiceIterator.__iter__` — Less preferred because it's the caller; modifying the function that creates the problematic object is more direct.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function is directly responsible for creating the unhashable `ModelChoiceIteratorValue` object that was introduced in Django 3.1 and causes the user's code to break.

#### ✗ REJECTED — `tests/select_related/tests.py::SelectRelatedTests.test_select_related_after_values_list`

- **Q1 Role.** This is a unit test to ensure that calling `select_related()` on a queryset after `values_list()` raises a `TypeError`.
- **Q2 Connection to symptom.** No path exists. This is a test for ORM behavior, which is unrelated to the form choice rendering that is causing the user's issue. The `TypeError` it tests for is different from the 'unhashable type' error observed.
- **Q3 Counterfactual.** `no` — This is a test function. Modifying, adding, or removing it would have no effect on the runtime behavior of the Django forms framework.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::ModelChoiceIterator.choice` — Any function within the forms subsystem is infinitely more relevant than this test case.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a test for an unrelated feature and has no causal connection to the observed symptom.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/models.py::ModelChoiceIterator.choice` | high | This function is directly responsible for creating the unhashable `ModelChoiceIteratorValue` object that was introduced in Django 3.1 and causes the user's code to break. | Implement `__hash__` on `ModelChoiceIteratorValue` to hash its underlying value. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/models.py::ModelChoiceIterator.__iter__` | high | This function is on the direct causal path, yielding the unhashable object that causes the TypeError, but it doesn't create the object itself. | Change `yield self.choice(obj)` to yield a simple value instead of the `ModelChoiceIteratorValue` wrapper. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `tests/select_related/tests.py::SelectRelatedTests.test_select_related_after_values_list` | high | This function is a test for an unrelated feature and has no causal connection to the observed symptom. |  |

**Causal chains (per candidate)**

- `django/forms/models.py::ModelChoiceIterator.__iter__`  (score=8.0)  \
  A `ModelChoiceField`'s choices are generated by iterating over `ModelChoiceIterator`. → This `__iter__` method calls `self.choice(obj)` for each item in the queryset. → `self.choice(obj)` returns a tuple whose first element is a `ModelChoiceIteratorValue` instance. → This instance is passed as the `value` argument to the widget's `create_option` method. → The user's code attempts a dictionary lookup `value in self.show_fields`, which tries to hash the `ModelChoiceIteratorValue` instance. → A `TypeError: unhashable type` is raised.
- `django/forms/models.py::ModelChoiceIterator.choice`  (score=9.0)  \
  This function is called to generate a choice tuple. → It explicitly creates a `ModelChoiceIteratorValue` instance to wrap the choice's value. → This instance is passed up the call stack through the iterator protocol. → It ends up as the `value` argument in the user's `create_option` method. → The attempt to use this object as a dictionary key (`value in self.show_fields`) fails because it is unhashable. → This raises the `TypeError`.
- `tests/select_related/tests.py::SelectRelatedTests.test_select_related_after_values_list`  (score=0.0)  \
  

**next_to_explore:** `['django/forms/models.py::ModelChoiceIteratorValue.__eq__', 'django/forms/models.py::ModelChoiceIteratorValue.__init__', 'django/forms/models.py::ModelChoiceIteratorValue', 'django/forms/widgets.py::ChoiceWidget.create_option', 'django/forms/fields.py::ModelChoiceField.choices']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/forms/models.py::ModelChoiceIterator.choice` | 0.95 |
| 2 | `django/forms/models.py::ModelChoiceIteratorValue.__init__` | 0.9 |
| 3 | `django/forms/models.py::ModelChoiceIterator.__iter__` | 0.85 |
| 4 | `django/forms/models.py::ModelChoiceIteratorValue.__eq__` | 0.6 |
| 5 | `django/forms/models.py::ModelChoiceField.prepare_value` | 0.1 |
| 6 | `django/forms/models.py::ModelChoiceIteratorValue.__str__` | 0.0 |
| 7 | `django/forms/models.py::ModelChoiceIterator.__init__` | 0.0 |
| 8 | `django/forms/fields.py::CallableChoiceIterator.__init__` | 0.0 |
| 9 | `django/forms/fields.py::CallableChoiceIterator.__iter__` | 0.0 |
| 10 | `django/forms/models.py::ModelChoiceIterator.__bool__` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/forms/models.py::ModelChoiceIterator.choice` | 0.950 | high | 1/1 | (1199, 1203) |
| 2 | `django/forms/models.py::ModelChoiceIteratorValue.__init__` | 0.900 | high | 1/1 | (1162, 1164) |
| 3 | `django/forms/models.py::ModelChoiceIterator.__iter__` | 0.850 | high | 1/1 | (1180, 1188) |
| 4 | `django/forms/models.py::ModelChoiceIteratorValue.__eq__` | 0.600 | high | 1/1 | (1169, 1172) |
| 5 | `django/forms/widgets.py::ChoiceWidget.create_option` | 0.429 | high | 1/1 | (621, 638) |
| 6 | `django/forms/widgets.py::ChoiceWidget.options` | 0.415 | high | 1/1 | (582, 585) |
| 7 | `django/forms/widgets.py::ChoiceWidget.value_from_datadict` | 0.414 | high | 1/1 | (654, 661) |
| 8 | `django/forms/fields.py::TypedMultipleChoiceField._coerce` | 0.407 | high | 1/1 | (912, 929) |
| 9 | `django/utils/hashable.py::make_hashable` | 0.358 | high | 1/1 | (4, 24) |
| 10 | `django/forms/widgets.py::ChoiceWidget.format_value` | 0.333 | high | 1/1 | (663, 669) |
