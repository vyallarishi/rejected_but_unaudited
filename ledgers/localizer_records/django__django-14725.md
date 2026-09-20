# Instance: `django__django-14725`

- runs: 1   termination: `ledger_informed`   think-high calls: 3

## Issue (truncated to 1200 chars)

```
Provide a way for model formsets to disallow new object creation
Description
	
Model formsets don't provide a way to create an "edit only" view of objects. We see users trying to use extra=0 to accomplish this, but that's not reliable as extra is merely meant for the extra number of forms to display. You can add more forms with Javascript (or just send additional post data).
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['new object creation', 'edit only view of objects']`
- named APIs: `[]`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/contrib/admin/options.py` | This file contains the ModelAdmin and InlineModelAdmin classes, which are central to defining the admin interface and formsets. |
| 2 | `django/forms/models.py` | This file contains the modelformset_factory and inlineformset_factory functions, which are used to create formsets for models. |
| 3 | `django/contrib/admin/helpers.py` | This file defines the InlineAdminFormSet class, which is a wrapper around an inline formset for use in the admin system. |
| 4 | `django/contrib/admin/checks.py` | This file contains checks related to ModelAdmin and InlineModelAdmin, including checks for form and formset classes. |
| 5 | `django/forms/formsets.py` | This file defines the BaseModelFormSet class, which is the base class for all formsets. |
| 6 | `django/contrib/contenttypes/admin.py` | This file defines GenericInlineModelAdmin, which is used for generic inline formsets. |
| 7 | `django/contrib/contenttypes/forms.py` | This file defines BaseGenericInlineFormSet and generic_inlineformset_factory, which are used to create formsets for generic inline objects. |
| 8 | `django/contrib/admin/templates/admin/includes/fieldset.html` | This template is used to render fieldsets in the admin interface, including inline formsets. |
| 9 | `django/contrib/admin/widgets.py` | This file contains widgets used in the admin interface, which might need adjustments for the new feature. |
| 10 | `django/contrib/admin/static/admin/js/inlines.js` | This file contains javascript code for handling inlines in the admin interface, which might need adjustments for the new feature. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 2, rejected: 0

**Per-candidate deliberation traces**

#### … CONSIDERING — `django/forms/formsets.py::BaseFormSet.extra_forms`

- **Q1 Role.** This function returns a list of forms that are considered "extra", i.e., those beyond the initial set of forms meant for editing existing instances.
- **Q2 Connection to symptom.** An execution path through this function contributes to the symptom. `save_new_objects` iterates over the list returned by this function to create new objects. If a user submits additional forms, this function will include them in its return value, which are then passed to `save_new_objects` for creation, causing the unwanted "new object creation".
- **Q3 Counterfactual.** `yes` — If this function were modified to return an empty list when new object creation is disallowed (e.g., based on a new `can_add` flag), `save_new_objects` would have no forms to process, and no new objects would be created.
- **Q4 Alternatives considered.**
  - `models.py::BaseModelFormSet.save_new_objects` — Preferred, as it's more direct to control the saving action itself rather than the data it consumes.
  - `models.py::BaseModelFormSet.initial_form_count` — Not preferred, as modifying it would be a hack that violates the function's semantic meaning.
  - `models.py::BaseModelFormSet.is_valid` — A good alternative; raising a validation error would prevent saving and provide user feedback.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This is a key part of the causal chain for creating new objects, and modifying it would work, but the fix is more semantically appropriate in `save_new_objects`.

#### … CONSIDERING — `django/forms/models.py::BaseModelFormSet.initial_form_count`

- **Q1 Role.** This function returns the number of forms that are required in this FormSet, which for a model formset corresponds to the number of existing instances being edited.
- **Q2 Connection to symptom.** This function's return value is used by `extra_forms` to determine which forms are "extra". These extra forms are then saved as new objects by `save_new_objects`. Therefore, it is an upstream contributor to the new object creation symptom.
- **Q3 Counterfactual.** `yes` — If this function were modified to return the total number of forms when adding is disallowed, `extra_forms` would return an empty list, thus preventing `save_new_objects` from creating new objects.
- **Q4 Alternatives considered.**
  - `models.py::BaseModelFormSet.save_new_objects` — Strongly preferred, as it is the function directly performing the action that needs to be controlled.
  - `formsets.py::BaseFormSet.extra_forms` — Preferred over this function, as it is one step closer to the action being performed.
- **Q5 Verdict.** `considering` (confidence: `low`) — While a modification here could technically prevent the symptom, it would be a confusing hack that breaks the function's semantic contract; the fix belongs elsewhere.

#### ✓ LEADING — `django/forms/models.py::BaseModelFormSet.save_new_objects`

- **Q1 Role.** This function iterates over the extra forms in a model formset and saves them as new model instances.
- **Q2 Connection to symptom.** This function is directly responsible for the "new object creation" symptom. It iterates through `self.extra_forms` and explicitly calls `self.save_new()` for each valid additional form, which creates a new object in the database.
- **Q3 Counterfactual.** `yes` — Adding a guard clause at the beginning of this function to check a new `can_add` flag would directly and cleanly prevent any new objects from being saved, thus providing the requested "edit only" mode.
- **Q4 Alternatives considered.**
  - `formsets.py::BaseFormSet.extra_forms` — Not preferred; it's better to control the action (saving) rather than the data (the list of forms).
  - `models.py::BaseModelFormSet.is_valid` — A reasonable alternative would be to add a validation check, but modifying the save method is a more direct implementation of 'disallowing creation'.
  - `models.py::BaseModelFormSet.__init__` — This is not an alternative but a necessary addition to accept and set the new `can_add` option.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function is the direct cause of the symptom, and modifying it is the most direct and appropriate way to fix the issue.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/models.py::BaseModelFormSet.save_new_objects` | high | This function is the direct cause of the symptom, and modifying it is the most direct and appropriate way to fix the issue. | Add a guard at the start of the function to return early if a new `can_add` attribute on the formset is False. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/formsets.py::BaseFormSet.extra_forms` | medium | This is a key part of the causal chain for creating new objects, and modifying it would work, but the fix is more semantically appropriate in `save_new_objects`. | Conditionally return an empty list if a new `can_add` attribute on the formset is False. |
| `django/forms/models.py::BaseModelFormSet.initial_form_count` | low | While a modification here could technically prevent the symptom, it would be a confusing hack that breaks the function's semantic contract; the fix belongs elsewhere. | If `can_add` is false, return `len(self.forms)` to trick `extra_forms` into returning an empty list. |

**Causal chains (per candidate)**

- `django/forms/formsets.py::BaseFormSet.extra_forms`  (score=7.0)  \
  BaseModelFormSet.save_new_objects() is called. → It iterates over `self.extra_forms`. → This calls `BaseFormSet.extra_forms`, which returns forms submitted by the user beyond the initial ones. → For each of these forms, `save_new_objects` creates a new model instance.
- `django/forms/models.py::BaseModelFormSet.initial_form_count`  (score=5.0)  \
  BaseModelFormSet.save_new_objects() is called. → It accesses `self.extra_forms`. → `BaseFormSet.extra_forms` calls `self.initial_form_count()` to determine the slice point between initial and extra forms. → The value from `initial_form_count` thus determines which forms are considered new and are subsequently saved.
- `django/forms/models.py::BaseModelFormSet.save_new_objects`  (score=9.0)  \
  A user submits a formset with extra forms intended to be new objects. → `save_new_objects` is called as part of the formset saving process. → The function iterates `for form in self.extra_forms:`. → Inside the loop, it calls `self.save_new(form, commit=commit)`. → This call creates and saves a new model instance, which is the observed symptom.

**next_to_explore:** `['django/forms/models.py::BaseModelFormSet.__init__', 'django/forms/models.py::modelformset_factory', 'django/forms/models.py::BaseModelFormSet.is_valid', 'django/forms/formsets.py::BaseFormSet.is_valid', 'django/forms/models.py::BaseModelFormSet.save_new']`

### Abductive step #2 (iteration=6)

- leading: 1, considering: 1, rejected: 0

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/forms/models.py::BaseModelFormSet.save_new`

- **Q1 Role.** This function saves a single form from the formset as a new model instance.
- **Q2 Connection to symptom.** Yes, this function is directly responsible for creating a new object in the database. An execution path that exhibits the symptom of unwanted 'new object creation' must pass through this function. The path is typically `formset.save()` -> `self.save_new_objects()` -> `self.save_new(form)` for each form that represents a new object.
- **Q3 Counterfactual.** `yes` — If this function were modified to check a new flag on the formset (e.g., `self.can_create`) and refuse to save the form if that flag is false, the symptom of unwanted object creation would be eliminated.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::BaseModelFormSet.save` — This is a strong alternative; the check could be placed here to avoid calling `save_new_objects` altogether.
  - `django/forms/models.py::BaseModelFormSet.save_new_objects` — This is the direct caller and another excellent candidate for modification, as it could be changed to do nothing if creation is disallowed.
  - `django/forms/models.py::BaseModelFormSet.__init__` — This is where the configuration would be passed, but modifying it alone is insufficient to prevent the save operation.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function is the final gatekeeper for creating new objects, and modifying it to conditionally block creation would directly solve the problem.

#### … CONSIDERING — `django/forms/models.py::BaseModelFormSet.__init__`

- **Q1 Role.** This is the constructor for the model formset, responsible for initializing its configuration based on provided arguments like the queryset.
- **Q2 Connection to symptom.** No, this function does not directly cause the symptom. However, its current implementation lacks a parameter to configure the formset as 'edit-only'. This omission is a root cause, as it provides no way for downstream methods like `save` to know that new object creation should be disallowed.
- **Q3 Counterfactual.** `no` — Modifying only `__init__` to accept a new parameter (e.g., `can_create=False`) would not change any behavior, as no other code would be aware of or act on this new setting.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::BaseModelFormSet.save_new` — Preferred as the location for the fix, as it's where the creation actually happens and can be prevented.
  - `django/forms/models.py::BaseModelFormSet.save` — Also a strong candidate for enforcing the 'no-create' rule, which would be configured via `__init__`.
  - `django/forms/models.py::modelformset_factory` — This factory would also need to be updated to accept and pass the new parameter to `__init__`, making it part of the complete solution.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function is where a new option to control creation would be introduced, but it doesn't enforce it, so modifying it alone is insufficient to fix the bug.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/models.py::BaseModelFormSet.save_new` | high | This function is the final gatekeeper for creating new objects, and modifying it to conditionally block creation would directly solve the problem. | Add a check for a new formset attribute like `self.can_create` and return early or raise an error if creation is disallowed. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/models.py::BaseModelFormSet.__init__` | high | This function is where a new option to control creation would be introduced, but it doesn't enforce it, so modifying it alone is insufficient to fix the bug. | Accept a new kwarg, e.g., `can_create=True`, and store it as an instance attribute `self.can_create`. |

**Causal chains (per candidate)**

- `django/forms/models.py::BaseModelFormSet.save_new`  (score=9.0)  \
  A request is made to save a formset that includes data for a new, extra form. → The view calls `formset.save()`. → Inside `save()`, the logic determines this is a new form and calls `self.save_new_objects()`. → `save_new_objects()` iterates through new forms and calls `self.save_new(form)`. → `save_new` calls `form.save()`, which creates a new object in the database, producing the symptom.
- `django/forms/models.py::BaseModelFormSet.__init__`  (score=4.0)  \
  A model formset is instantiated, `__init__` is called. → The function does not accept or set any flag to disallow creation. → Later, when `formset.save()` is called, there is no configuration available to indicate that new objects should not be created. → The `save` logic proceeds with its default behavior of creating new objects from extra form data.

**next_to_explore:** `['django/forms/models.py::BaseModelFormSet.save_new_objects', 'django/forms/models.py::BaseModelFormSet.save', 'django/forms/models.py::modelformset_factory', 'django/forms/formsets.py::BaseFormSet.is_valid']`

### Abductive step #3 (iteration=18)

- leading: 1, considering: 2, rejected: 3

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/forms/models.py::BaseModelFormSet.save`

- **Q1 Role.** This function saves the data from the formset to the database, handling both existing and new model instances.
- **Q2 Connection to symptom.** Yes, this function directly causes the creation of new objects. The line `return self.save_existing_objects(commit) + self.save_new_objects(commit)` contains an unconditional call to `self.save_new_objects(commit)`. When a user submits extra forms (for new objects), `save_new_objects` is executed, which persists them to the database, causing the "new object creation" symptom.
- **Q3 Counterfactual.** `yes` — If this function were modified to conditionally call `self.save_new_objects` based on a new formset attribute (e.g., `self.can_add`), it would prevent new object creation and thus solve the issue.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::BaseModelFormSet.save_new_objects` — This is also a strong candidate, but `save` is the orchestrator and a better place for the high-level conditional logic.
  - `django/forms/formsets.py::BaseFormSet.is_valid` — Marking extra forms as invalid is an indirect way to solve this; preventing the save action is more direct.
  - `django/forms/models.py::modelformset_factory` — This is where the option would be configured, but `save` is where it would be enforced.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function's unconditional call to `save_new_objects` is the direct cause of the symptom, and a conditional modification here would fix it.

#### … CONSIDERING — `django/forms/models.py::modelformset_factory`

- **Q1 Role.** This is a factory function that creates a `FormSet` class for a given Django model.
- **Q2 Connection to symptom.** Yes, this function is where a user would configure a formset. The lack of a parameter here to disallow additions (e.g., `can_add=False`) is a root cause of the problem, as it provides no way for a user to specify the desired "edit only" behavior. The default behavior then permits new object creation.
- **Q3 Counterfactual.** `partially` — Adding a parameter here (e.g., `can_add`) is a necessary part of the solution, but it's not sufficient. The parameter would also need to be handled by the formset class, likely in `__init__` and `save`.
- **Q4 Alternatives considered.**
  - `django/forms/formsets.py::formset_factory` — This is a more generic factory; the logic for adding model instances is specific to `ModelFormSet`, so the parameter belongs here.
  - `django/forms/models.py::BaseModelFormSet.__init__` — This is where the parameter from the factory would be processed, making it part of the same solution path.
  - `django/forms/models.py::BaseModelFormSet.save` — This is where the parameter would be used for enforcement. Both are needed for a complete fix.
- **Q5 Verdict.** `considering` (confidence: `high`) — This is the main user-facing API for configuration, making it the correct place to introduce an option to disable additions, though it doesn't enforce it.

#### … CONSIDERING — `django/forms/formsets.py::BaseFormSet.is_valid`

- **Q1 Role.** This method validates all the forms within the formset and returns `True` if all of them are valid.
- **Q2 Connection to symptom.** Yes, a plausible path exists. This method is called before `save`. If extra forms for new objects are submitted and their data is valid, this method returns `True`, allowing the process to continue to `save`, where the new objects are created. One could prevent this by making the formset invalid if extra forms are present when they are not allowed.
- **Q3 Counterfactual.** `partially` — Modifying this to add a validation error for extra forms would prevent saving, but it's an indirect solution. The issue isn't invalid data, but a disallowed action.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::BaseModelFormSet.save` — Preferred, as it's more direct to skip the save action than to fail validation.
  - `django/forms/formsets.py::BaseFormSet.clean` — This is another place for validation logic, and it has the same pros and cons as modifying `is_valid`.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function offers a viable, though indirect, path to a solution by using the validation system to block unwanted additions.

#### ✗ REJECTED — `django/forms/formsets.py::BaseFormSet.forms`

- **Q1 Role.** This property constructs and returns a list of all form instances in the formset, both initial and extra.
- **Q2 Connection to symptom.** This function creates the form instances for any extra data submitted by the user. These form instances are then validated and saved, leading to new object creation. The number of forms created is based on `total_form_count()`, which reads from POST data.
- **Q3 Counterfactual.** `no` — Preventing the creation of form objects here would break subsequent processing like validation. The forms need to be created to be processed, even if that processing ultimately rejects them.
- **Q4 Alternatives considered.**
  - `django/forms/formsets.py::BaseFormSet.total_form_count` — This controls the loop in `forms`. Modifying it would be the actual place to change behavior, but it has the same conceptual problems.
  - `django/forms/models.py::BaseModelFormSet.save` — The correct place to intervene is at the point of saving model objects, not creating form objects.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function's role is to instantiate forms based on input; preventing this would break formset processing and is the wrong layer to enforce persistence logic.

#### ✗ REJECTED — `django/forms/formsets.py::BaseFormSet.initial_form_count`

- **Q1 Role.** This method returns the number of forms that correspond to existing data (either from the `initial` kwarg or from the management form in a POST request).
- **Q2 Connection to symptom.** No path exists. This function's purpose is to report how many forms are for existing instances. The problem of creating new objects concerns forms *in addition* to this count. This function correctly provides information used to distinguish existing vs. new, but it does not cause new objects to be created.
- **Q3 Counterfactual.** `no` — Modifying this function would break the formset's core logic for differentiating between existing and new forms, likely causing other errors.
- **Q4 Alternatives considered.**
  - `django/forms/formsets.py::BaseFormSet.total_form_count` — This function, which determines the total number of forms, is more related to the symptom than `initial_form_count`.
  - `django/forms/models.py::BaseModelFormSet.save_new_objects` — This is the function that acts on forms beyond the initial count, making it causally related.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is purely informational and correctly reports the count of initial forms; it is not on a causal path to the symptom.

#### ✗ REJECTED — `django/contrib/admin/options.py::ModelAdmin._create_formsets`

- **Q1 Role.** This is a helper method within the Django admin to create inline formsets for a model's add/change views.
- **Q2 Connection to symptom.** This function instantiates formsets used within the Django admin. If a user adds a new inline form via JavaScript in the admin, this function is part of the setup that eventually leads to that form being processed and a new object being created upon saving. However, it is only a consumer of the formset API.
- **Q3 Counterfactual.** `no` — A fix here would only apply to inline formsets within the admin. The underlying problem exists in `BaseModelFormSet` and affects all its uses, not just in the admin.
- **Q4 Alternatives considered.**
  - `django/forms/models.py::modelformset_factory` — This is the generic factory, and fixing the issue there would solve it for all use cases, including the admin.
  - `django/forms/models.py::BaseModelFormSet.save` — The core logic is in the formset itself, not in this admin-specific consumer.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is an application-specific use of formsets (in the admin) and not the place to fix the core behavior of the formset itself.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/models.py::BaseModelFormSet.save` | high | This function's unconditional call to `save_new_objects` is the direct cause of the symptom, and a conditional modification here would fix it. | Add a check for a new `self.can_add` attribute before calling `self.save_new_objects(commit)`. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/models.py::modelformset_factory` | high | This is the main user-facing API for configuration, making it the correct place to introduce an option to disable additions, though it doesn't enforce it. | Add a new `can_add=True` parameter and arrange for it to be passed to the created formset class. |
| `django/forms/formsets.py::BaseFormSet.is_valid` | medium | This function offers a viable, though indirect, path to a solution by using the validation system to block unwanted additions. | In a subclass, override to add a formset-level error if new forms are present and a `self.can_add=False` flag is set. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/formsets.py::BaseFormSet.forms` | high | This function's role is to instantiate forms based on input; preventing this would break formset processing and is the wrong layer to enforce persistence logic. |  |
| `django/forms/formsets.py::BaseFormSet.initial_form_count` | high | This function is purely informational and correctly reports the count of initial forms; it is not on a causal path to the symptom. |  |
| `django/contrib/admin/options.py::ModelAdmin._create_formsets` | high | This is an application-specific use of formsets (in the admin) and not the place to fix the core behavior of the formset itself. |  |

**Causal chains (per candidate)**

- `django/forms/models.py::BaseModelFormSet.save`  (score=9.0)  \
  A user submits a formset with extra forms intended for new objects. → The view calls `formset.save()`. → `BaseModelFormSet.save` is executed. → It unconditionally calls `self.save_new_objects(commit)`. → `save_new_objects` iterates through the extra forms and saves them, creating new model instances in the database. → This results in the unwanted "new object creation" symptom.
- `django/forms/models.py::modelformset_factory`  (score=7.0)  \
  A developer wants to create an "edit only" formset. → They call `modelformset_factory` to create the formset class. → The factory function has no parameter like `can_add` to disable new object creation. → The returned formset class therefore has no mechanism to prevent additions. → When this formset is used and saved, it will create new objects by default, exhibiting the symptom.
- `django/forms/formsets.py::BaseFormSet.is_valid`  (score=5.0)  \
  A user submits a formset with extra forms for new objects. → Before saving, `formset.is_valid()` is called. → The method iterates through all forms, including the extra ones. → If the data in the extra forms is valid according to the model's rules, `form.is_valid()` returns True for them. → `formset.is_valid()` returns True, signaling that the data is acceptable. → The program proceeds to call `formset.save()`, which then creates the new objects.
- `django/forms/formsets.py::BaseFormSet.forms`  (score=3.0)  \
  A user submits a POST request with data for extra forms. → `total_form_count` is calculated based on the management form data in the POST. → The `forms` property is accessed. → It creates form instances for all forms up to `total_form_count`, including the extra ones. → These form objects are then used by `is_valid` and `save`, eventually leading to new object creation.
- `django/forms/formsets.py::BaseFormSet.initial_form_count`  (score=1.0)  \
  The `save_new_objects` method is called. → It needs to know which forms are new. → It iterates from `self.initial_form_count()` to `self.total_form_count()`. → This function's correct reporting of the initial count is a precondition for `save_new_objects` to work, but it does not cause the save to happen.
- `django/contrib/admin/options.py::ModelAdmin._create_formsets`  (score=2.0)  \
  A user is on a Django admin change page with inlines. → This function is called to create the inline formsets. → It instantiates a `ModelFormSet` class. → If the user adds a new inline form and saves, the formset's `save` method is called, which creates a new object. → This function is a caller, far upstream from the direct cause.

**next_to_explore:** `['django/forms/models.py::BaseModelFormSet.__init__', 'django/forms/models.py::BaseModelFormSet.save_new_objects', 'django/forms/formsets.py::formset_factory', 'django/forms/formsets.py::BaseFormSet.__init__', 'django/forms/formsets.py::BaseFormSet.total_form_count']`

## Stage 5 — Listwise rerank decisions

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/forms/models.py::BaseModelFormSet.save_new_objects` | 0.670 | high | 1/1 | (814, 826) |
| 2 | `django/forms/models.py::BaseModelFormSet.save` | 0.601 | high | 1/1 | (667, 679) |
| 3 | `django/forms/models.py::BaseModelFormSet.save_new` | 0.582 | high | 1/1 | (654, 656) |
| 4 | `django/forms/models.py::BaseModelFormSet.save_existing_objects` | 0.563 | high | 1/1 | (788, 812) |
| 5 | `django/forms/formsets.py::BaseFormSet.extra_forms` | 0.519 | high | 1/1 | (223, 225) |
| 6 | `django/forms/models.py::modelformset_factory` | 0.516 | high | 1/1 | (872, 899) |
| 7 | `django/forms/models.py::BaseModelFormSet.initial_form_count` | 0.494 | high | 1/1 | (581, 585) |
| 8 | `django/contrib/admin/options.py::ModelAdmin._create_formsets` | 0.486 | high | 1/1 | (1991, 2024) |
| 9 | `django/forms/formsets.py::BaseFormSet.forms` | 0.478 | high | 1/1 | (171, 177) |
| 10 | `django/forms/models.py::BaseModelFormSet._existing_object` | 0.477 | high | 1/1 | (587, 590) |
