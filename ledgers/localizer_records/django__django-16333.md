# Instance: `django__django-16333`

- runs: 1   termination: `ledger_informed`   think-high calls: 3

## Issue (truncated to 1200 chars)

```
UserCreationForm should save data from ManyToMany form fields
Description
	
When using contrib.auth.forms.UserCreationForm with a custom User model which has ManyToManyField fields, the data in all related form fields (e.g. a ModelMultipleChoiceField) is not saved. 
This is because unlike its parent class django.forms.ModelForm, UserCreationForm.save(commit=True) omits to call self.save_m2m(). 
This has been discussed on the #django-developers mailing list ​https://groups.google.com/u/1/g/django-developers/c/2jj-ecoBwE4 and I'm ready to work on a PR.
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['data in related form fields is not saved']`
- named APIs: `['UserCreationForm.save', 'django.forms.ModelForm', 'self.save_m2m']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/contrib/auth/forms.py` | Contains UserCreationForm, the form in question, and its save() method needs modification. |
| 2 | `django/db/models/fields/related.py` | ManyToManyField is involved, so this file containing related field definitions is relevant. |
| 3 | `django/forms/models.py` | UserCreationForm inherits from ModelForm, so this file is relevant to how form data is saved. |
| 4 | `django/contrib/auth/admin.py` | UserAdmin uses UserCreationForm, so changes there might be needed. |
| 5 | `django/contrib/admin/options.py` | ModelAdmin.save_formset() and save_related() are involved in saving related objects. |
| 6 | `django/contrib/admin/helpers.py` | AdminForm and InlineAdminFormSet are used to structure the admin form and handle formsets. |
| 7 | `django/core/management/commands/createsuperuser.py` | This command uses UserCreationForm, so changes there might be needed. |
| 8 | `django/db/models/base.py` | Model save() method is relevant to how data is persisted. |
| 9 | `django/db/models/manager.py` | Manager classes are used to interact with the database. |
| 10 | `django/contrib/auth/models.py` | The User model and its related PermissionsMixin are relevant to the issue. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/contrib/auth/forms.py::UserCreationForm.save`

- **Q1 Role.** Saves a new user instance to the database, setting the password before the final commit.
- **Q2 Connection to symptom.** Yes, a path through this function directly causes the symptom. 
1. `UserCreationForm.save(commit=True)` is called.
2. `super().save(commit=False)` is executed, which creates a model instance but does not trigger M2M saving because `commit` is `False`.
3. The user's password is set.
4. `user.save()` is called inside the `if commit:` block, saving the main model instance.
5. The function then returns, but it has *not* called `self.save_m2m()`, which is the method responsible for saving data for `ManyToManyField` fields. This omission is the direct cause of the data loss.
- **Q3 Counterfactual.** `yes` — Adding a call to `self.save_m2m()` inside the `if commit:` block, after `user.save()`, would correctly save the many-to-many data and eliminate the symptom.
- **Q4 Alternatives considered.**
  - `django.forms.models.ModelForm.save` — This is the parent method. It is not the cause; rather, its correct implementation (which calls save_m2m) is what this function fails to replicate.
  - `django.forms.models.BaseModelForm._save_m2m` — This function performs the M2M saving, but the problem is that it's not being called, not that its implementation is faulty.
- **Q5 Verdict.** `leading` (confidence: `high`) — This method overrides its parent's save logic but omits the call to `self.save_m2m()`, directly causing the failure to save ManyToManyField data.

#### ✗ REJECTED — `django/forms/models.py::BaseModelForm._save_m2m`

- **Q1 Role.** Saves the data for many-to-many fields associated with a model form.
- **Q2 Connection to symptom.** No path. This function is what *should* be executed to prevent the symptom. The symptom (data not being saved) occurs precisely because this function is *not called* by `UserCreationForm.save`.
- **Q3 Counterfactual.** `no` — Modifying this function would have no effect, as the root cause of the bug is that it is never invoked in the problematic execution path.
- **Q4 Alternatives considered.**
  - `django.contrib.auth.forms.UserCreationForm.save` — This is the caller function, and its failure to invoke `_save_m2m` (via `save_m2m`) is the actual source of the bug.
  - `django.forms.models.ModelForm.save` — The parent class's save method correctly calls this logic, highlighting the omission in the child class.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is part of the solution, not the problem; the bug is caused by it not being called.

#### ✗ REJECTED — `django/contrib/auth/forms.py::UserCreationForm.__init__`

- **Q1 Role.** Initializes the form instance, primarily to set the autofocus attribute on the username field.
- **Q2 Connection to symptom.** No path. This function is executed during form instantiation and only deals with widget presentation. It has no involvement in the data persistence logic, which occurs much later in the `save` method.
- **Q3 Counterfactual.** `no` — Changes to this function would only affect the form's HTML rendering and have no impact on the database saving process.
- **Q4 Alternatives considered.**
  - `django.contrib.auth.forms.UserCreationForm.save` — Preferred as the location of the bug, as it directly handles the data saving logic where the failure occurs.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function's role is limited to form initialization and is completely unrelated to the data saving mechanism.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/auth/forms.py::UserCreationForm.save` | high | This method overrides its parent's save logic but omits the call to `self.save_m2m()`, directly causing the failure to save ManyToManyField data. | Inside the `if commit:` block, add a call to `self.save_m2m()` after `user.save()`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/models.py::BaseModelForm._save_m2m` | high | This function is part of the solution, not the problem; the bug is caused by it not being called. |  |
| `django/contrib/auth/forms.py::UserCreationForm.__init__` | high | This function's role is limited to form initialization and is completely unrelated to the data saving mechanism. |  |

**Causal chains (per candidate)**

- `django/contrib/auth/forms.py::UserCreationForm.save`  (score=10.0)  \
  UserCreationForm.save(commit=True) is called. → The method overrides the parent ModelForm.save behavior. → It calls user.save() to persist the main user object. → It fails to call self.save_m2m(), which is responsible for persisting ManyToMany relations. → As a result, data from ManyToMany form fields is not saved.
- `django/forms/models.py::BaseModelForm._save_m2m`  (score=0.0)  \
  
- `django/contrib/auth/forms.py::UserCreationForm.__init__`  (score=0.0)  \
  

**next_to_explore:** `['django.forms.models.ModelForm.save', 'django.forms.models.ModelForm.save_m2m']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 0, rejected: 0

### Abductive step #3 (iteration=9)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/contrib/auth/admin.py::UserAdmin.get_form`

- **Q1 Role.** This function determines which form to use for creating or editing a user in the Django admin interface, specifically selecting the `add_form` when a new user is being created.
- **Q2 Connection to symptom.** No path directly causes the symptom. This function is called when creating a user through the admin interface and is responsible for selecting `UserCreationForm`. While this places `UserCreationForm` in the execution path, the failure to save ManyToMany data is due to a bug within the form's `save` method itself, not in how the form is selected.
- **Q3 Counterfactual.** `no` — Modifying this function to use a different form would be a workaround for the admin, but it would not fix the underlying bug in `UserCreationForm.save`.
- **Q4 Alternatives considered.**
  - `django.contrib.auth.forms.UserCreationForm.save` — Preferred, as the bug report explicitly identifies it as the location of the missing `save_m2m` call.
  - `django.contrib.admin.ModelAdmin.save_model` — Not preferred, as the issue is described at the form level, which is typically handled before the admin's `save_model` is called.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function only selects the buggy form in the admin context; it does not contain the bug itself.

#### ✗ REJECTED — `django/contrib/auth/forms.py::UserCreationForm.clean_password2`

- **Q1 Role.** This method validates that the two password fields in the user creation form have identical values.
- **Q2 Connection to symptom.** No path. This function executes during form validation, before the `save` method is ever called. Its purpose is to check for password mismatches and raise a `ValidationError` if they don't match. It has no interaction with saving model fields, especially not ManyToMany fields.
- **Q3 Counterfactual.** `no` — Changing this password validation logic would have no effect on the `save` method's implementation, which is where the ManyToMany data is lost.
- **Q4 Alternatives considered.**
  - `django.contrib.auth.forms.UserCreationForm.save` — Preferred, as this is where saving logic resides and where the bug is reported to be.
  - `django.contrib.auth.forms.UserCreationForm._post_clean` — This is closer to the save process as it finalizes data, but it's still part of validation, not persistence of M2M relations.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a field validation method completely unrelated to the form's model-saving logic.

#### ✗ REJECTED — `django/contrib/auth/forms.py::AuthenticationForm.__init__`

- **Q1 Role.** This is the constructor for the `AuthenticationForm`, which is used to handle user login, not user creation.
- **Q2 Connection to symptom.** No path. This function is part of the user login form (`AuthenticationForm`), whereas the bug occurs in the user creation form (`UserCreationForm`). These are two distinct forms for different purposes and do not share a relevant inheritance chain.
- **Q3 Counterfactual.** `no` — Modifying the constructor of the login form will have no impact on the behavior of the separate user creation form.
- **Q4 Alternatives considered.**
  - `django.contrib.auth.forms.UserCreationForm.__init__` — This is the constructor for the correct form, but the bug is in the `save` method, not initialization.
  - `django.contrib.auth.forms.UserCreationForm.save` — Preferred, as it is the method responsible for saving the form data and is the source of the bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function belongs to the login form, which is entirely separate from the user creation form where the bug exists.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/auth/admin.py::UserAdmin.get_form` | high | This function only selects the buggy form in the admin context; it does not contain the bug itself. |  |
| `django/contrib/auth/forms.py::UserCreationForm.clean_password2` | high | This is a field validation method completely unrelated to the form's model-saving logic. |  |
| `django/contrib/auth/forms.py::AuthenticationForm.__init__` | high | This function belongs to the login form, which is entirely separate from the user creation form where the bug exists. |  |

**Causal chains (per candidate)**

- `django/contrib/auth/admin.py::UserAdmin.get_form`  (score=0.0)  \
  User creates a new user in the Django admin. → The `UserAdmin.add_view` is triggered, which calls `get_form`. → This function returns `self.add_form`, which is `UserCreationForm`. → The user fills out the form, including a ManyToMany field, and submits. → `UserCreationForm.save()` is called. → The `save()` method fails to call `save_m2m()`, causing the symptom.
- `django/contrib/auth/forms.py::UserCreationForm.clean_password2`  (score=0.0)  \
  User submits a `UserCreationForm`. → The form's `is_valid()` method is called, which triggers all `clean_` methods. → `clean_password2` runs, comparing `password1` and `password2` from `cleaned_data`. → Assuming passwords match, the method returns successfully. → Validation finishes, and `form.save()` is called later. → This function's execution is orthogonal to the problem of saving M2M data in the `save` method.
- `django/contrib/auth/forms.py::AuthenticationForm.__init__`  (score=0.0)  \
  A user navigates to the login page. → An `AuthenticationForm` instance is created. → The `__init__` method is called to set up the form fields for username and password. → This execution path is completely separate from the user creation workflow involving `UserCreationForm`.

**next_to_explore:** `['django.contrib.auth.forms.UserCreationForm.save', 'django.forms.models.ModelForm.save', 'django.forms.models.BaseModelForm.save', 'django.forms.models.BaseModelForm._save_m2m']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/contrib/auth/forms.py::UserCreationForm.save` | 1.0 |
| 2 | `django/contrib/auth/admin.py::UserAdmin.get_form` | 0.1 |
| 3 | `django/forms/models.py::BaseModelForm._save_m2m` | 0.0 |
| 4 | `django/db/models/fields/related.py::ManyToManyField.save_form_data` | 0.0 |
| 5 | `django/contrib/auth/forms.py::UserCreationForm.clean_password2` | 0.0 |
| 6 | `django/contrib/auth/forms.py::UserCreationForm._post_clean` | 0.0 |
| 7 | `django/contrib/auth/forms.py::UserCreationForm.__init__` | 0.0 |
| 8 | `django/contrib/auth/forms.py::SetPasswordForm.save` | 0.0 |
| 9 | `django/contrib/auth/forms.py::AuthenticationForm.__init__` | 0.0 |
| 10 | `django/contrib/auth/forms.py::AuthenticationForm.clean` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/contrib/auth/forms.py::UserCreationForm.save` | 1.000 | high | 1/1 | (139, 144) |
| 2 | `django/contrib/auth/forms.py::AuthenticationForm.get_user` | 0.371 | high | 1/1 | (246, 247) |
| 3 | `django/forms/models.py::BaseModelForm.save` | 0.358 | high | 1/1 | (526, 548) |
| 4 | `django/contrib/auth/base_user.py::AbstractBaseUser.save` | 0.350 | high | 1/1 | (74, 78) |
| 5 | `django/forms/models.py::modelform_factory` | 0.345 | high | 1/1 | (557, 642) |
| 6 | `django/contrib/auth/admin.py::GroupAdmin.formfield_for_manytomany` | 0.329 | high | 1/1 | (34, 40) |
| 7 | `django/forms/models.py::modelform_defines_fields` | 0.314 | high | 1/1 | (1657, 1660) |
| 8 | `django/contrib/auth/admin.py::UserAdmin._add_view` | 0.311 | high | 1/1 | (121, 147) |
| 9 | `django/contrib/auth/admin.py::UserAdmin.add_view` | 0.287 | high | 1/1 | (117, 119) |
| 10 | `django/contrib/auth/admin.py::UserAdmin.get_form` | 0.100 | high | 1/1 | (90, 98) |
