# Instance: `django__django-12193`

- runs: 1   termination: `ledger_informed`   think-high calls: 4

## Issue (truncated to 1200 chars)

```
SplitArrayField with BooleanField always has widgets checked after the first True value.
Description
	 
		(last modified by Peter Andersen)
	 
When providing a SplitArrayField BooleanField with preexisting data, the final_attrs dict is updated to include 'checked': True after the for loop has reached the first True value in the initial data array. Once this occurs every widget initialized after that defaults to checked even though the backing data may be False. This is caused by the CheckboxInput widget's get_context() modifying the attrs dict passed into it. This is the only widget that modifies the attrs dict passed into its get_context().
CheckboxInput setting attrs['checked'] to True: ​https://github.com/django/django/blob/master/django/forms/widgets.py#L527
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['widgets checked after the first True value', 'widget defaults to checked', "attrs dict is updated to include 'checked': True", "CheckboxInput widget's get_context() modifying the attrs dict"]`
- named APIs: `['CheckboxInput.get_context']`
- stack frames: `[{'file': 'django/forms/widgets.py', 'func': 'get_context', 'line': 527}]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/forms/fields.py` | Base field definitions are likely to be involved in widget initialization. |
| 2 | `django/forms/widgets.py` | The CheckboxInput widget's get_context() is identified as the source of the issue. |
| 3 | `django/contrib/postgres/forms/fields.py` | SplitArrayField is mentioned in the issue description. |
| 4 | `django/contrib/postgres/forms/widgets.py` | SplitArrayWidget is used by SplitArrayField and likely involved in rendering. |
| 5 | `django/forms/boundfield.py` | BoundField handles rendering of widgets and their attributes. |
| 6 | `django/forms/forms.py` | Forms are responsible for field and widget initialization. |
| 7 | `django/forms/models.py` | ModelForms are used to generate forms from models, potentially involving SplitArrayField. |
| 8 | `django/db/models/fields/__init__.py` | Field definitions are relevant to how widgets are initialized with data. |
| 9 | `django/db/models/fields/related.py` | Related fields might be used within SplitArrayField, so this file is relevant. |
| 10 | `django/core/management/commands/loaddata.py` | If initial data is loaded via fixtures, this file might be relevant. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 0, considering: 0, rejected: 0

### Abductive step #2 (iteration=6)

- leading: 0, considering: 1, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/forms/widgets.py::CheckboxInput.value_from_datadict`

- **Q1 Role.** This function extracts a boolean value for a checkbox from submitted form data, handling the case where an unchecked box's name is absent from the data.
- **Q2 Connection to symptom.** No path exists. The observed symptom occurs during the rendering of a form with pre-existing data, where widgets are incorrectly marked as 'checked'. This function, however, is exclusively on the data processing path for an incoming form submission, not the rendering path.
- **Q3 Counterfactual.** `no` — Modifying this function would affect how submitted form data is interpreted, but it would have no effect on the rendering logic that causes the bug with initial data.
- **Q4 Alternatives considered.**
  - `widgets.py::CheckboxInput.get_context` — Preferred, as the bug report identifies it as the function that mutates the 'attrs' dictionary during rendering.
  - `array.py::SplitArrayWidget.get_context` — Preferred, as it is the likely location of the loop that reuses the mutated 'attrs' dictionary for subsequent widgets.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function handles form submission data, while the bug occurs during form rendering with initial data.

#### ✗ REJECTED — `django/contrib/postgres/forms/array.py::SplitArrayWidget.value_from_datadict`

- **Q1 Role.** This function aggregates values from multiple sub-widgets of an array widget into a single list from submitted form data.
- **Q2 Connection to symptom.** No path exists. This function is called when processing data from a user's form submission. The symptom of incorrectly checked boxes appears during the initial rendering of the form, which is a separate code path.
- **Q3 Counterfactual.** `no` — The bug is in the rendering path, not the data extraction path. Changing this function would not alter how the widgets are displayed with initial data.
- **Q4 Alternatives considered.**
  - `widgets.py::CheckboxInput.get_context` — Preferred, as it is known to mutate the attributes dictionary.
  - `array.py::SplitArrayWidget.get_context` — Preferred, as this is the component that likely iterates over sub-widgets and reuses the shared, mutated attributes dictionary.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for processing submitted form data, whereas the bug manifests during the rendering of the form with initial data.

#### … CONSIDERING — `django/forms/fields.py::Field.widget_attrs`

- **Q1 Role.** This method returns a dictionary of HTML attributes to be added to a widget, based on the properties of its associated field.
- **Q2 Connection to symptom.** Yes, a plausible path exists. A caller, likely `SplitArrayWidget`, would call this method to get a base set of attributes. This dictionary of attributes is then passed into a loop that renders each sub-widget. When a `CheckboxInput` sub-widget for a `True` value is rendered, its `get_context` method mutates this dictionary. The same mutated dictionary is then reused for the next sub-widget in the loop, causing the symptom.
- **Q3 Counterfactual.** `no` — The root cause is not this function providing an attribute dictionary, but rather the caller reusing that dictionary across loop iterations while a callee (`CheckboxInput.get_context`) mutates it. The fix belongs in the caller or the callee.
- **Q4 Alternatives considered.**
  - `widgets.py::CheckboxInput.get_context` — A stronger candidate; fixing the mutation by copying the attrs dict would solve the problem at its source.
  - `array.py::SplitArrayWidget.get_context` — A very strong candidate; fixing the reuse by copying the attrs dict within the loop would also solve the problem.
  - `array.py::SplitArrayField.__init__` — Less likely, but it sets up the field/widget relationship and could be where the shared attribute dictionary originates.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function is on the causal path by providing the dictionary that gets mutated, but the primary fault lies elsewhere.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/fields.py::Field.widget_attrs` | medium | This function is on the causal path by providing the dictionary that gets mutated, but the primary fault lies elsewhere. | The caller of this function, likely in SplitArrayWidget, should copy the returned dictionary before passing it to sub-widgets in a loop. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/widgets.py::CheckboxInput.value_from_datadict` | high | This function handles form submission data, while the bug occurs during form rendering with initial data. |  |
| `django/contrib/postgres/forms/array.py::SplitArrayWidget.value_from_datadict` | high | This function is for processing submitted form data, whereas the bug manifests during the rendering of the form with initial data. |  |

**Causal chains (per candidate)**

- `django/forms/widgets.py::CheckboxInput.value_from_datadict`  (score=0.0)  \
  
- `django/contrib/postgres/forms/array.py::SplitArrayWidget.value_from_datadict`  (score=0.0)  \
  
- `django/forms/fields.py::Field.widget_attrs`  (score=5.0)  \
  A rendering method in `SplitArrayWidget` calls `field.widget_attrs` to get a base attribute dictionary. → This dictionary is then passed into a loop that renders each `CheckboxInput` sub-widget. → `CheckboxInput.get_context` is called for a sub-widget with a `True` value, and it mutates the shared attribute dictionary by adding `'checked': True`. → The loop continues to the next sub-widget, passing the same, now-mutated, dictionary to its `get_context` method. → This causes all subsequent checkboxes to appear checked, regardless of their actual value.

**next_to_explore:** `['django/contrib/postgres/forms/array.py::SplitArrayWidget.get_context', 'django/contrib/postgres/forms/array.py::SplitArrayWidget.render', 'django/contrib/postgres/forms/array.py::SplitArrayField.widget_attrs', 'django/forms/widgets.py::Widget.get_context']`

### Abductive step #3 (iteration=9)

- leading: 1, considering: 0, rejected: 0

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/contrib/postgres/forms/array.py::SplitArrayWidget.get_context`

- **Q1 Role.** This function prepares the rendering context for a SplitArrayWidget, which is composed of multiple sub-widgets, by iterating through the array values and generating a context for each sub-widget.
- **Q2 Connection to symptom.** Yes, a direct path exists. The function iterates through a list of values to create subwidgets. Inside the loop, it calls `self.widget.get_context` (which is `CheckboxInput.get_context` in this case) for each value, but it passes the *exact same* `final_attrs` dictionary object to every call. When the loop encounters the first `True` value, the `CheckboxInput.get_context` call modifies this shared `final_attrs` dictionary to include `'checked': True`. This modification persists, so for all subsequent iterations, `CheckboxInput.get_context` receives a `final_attrs` dictionary that already has `'checked': True`, causing all following checkboxes to be rendered as checked regardless of their backing data.
- **Q3 Counterfactual.** `yes` — If this function were modified to pass a copy of `final_attrs` (e.g., `final_attrs.copy()`) into the sub-widget's `get_context` call, the mutation from one call would not affect subsequent calls, fixing the symptom.
- **Q4 Alternatives considered.**
  - `django/forms/widgets.py::CheckboxInput.get_context` — This is where the mutation occurs; fixing it to not modify its `attrs` argument would also solve the bug, and might be a more correct fix.
  - `django/forms/widgets.py::Widget.build_attrs` — This function creates the initial `attrs` dictionary, but it is not responsible for the mutation that causes the bug.
  - `django/contrib/postgres/forms/array.py::SplitArrayField.__init__` — This function sets up the field and widget, but is too far upstream from the rendering logic where the state corruption happens.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function contains the loop that reuses a mutable dictionary (`final_attrs`) across calls to a mutating function, directly causing state to leak between sub-widget renderings.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/contrib/postgres/forms/array.py::SplitArrayWidget.get_context` | high | This function contains the loop that reuses a mutable dictionary (`final_attrs`) across calls to a mutating function, directly causing state to leak between sub-widget renderings. | Pass a copy of the `final_attrs` dictionary to the sub-widget's `get_context` call, for example by using `final_attrs.copy()`. |

**Causal chains (per candidate)**

- `django/contrib/postgres/forms/array.py::SplitArrayWidget.get_context`  (score=10.0)  \
  SplitArrayWidget.get_context is called to render a list of checkboxes with initial data (e.g., `[False, True, False]`). → It creates a single `final_attrs` dictionary to be used for all subwidgets. → It loops through the data, calling `self.widget.get_context` (which is `CheckboxInput.get_context`) for each item, passing the *same* `final_attrs` dictionary instance each time. → When `CheckboxInput.get_context` receives a `True` value, it modifies the passed-in `final_attrs` dictionary by adding `'checked': True`. → For all subsequent iterations of the loop, `CheckboxInput.get_context` receives the `final_attrs` dictionary which now contains `'checked': True`, causing all following checkboxes to be rendered as checked, regardless of their actual value.

**next_to_explore:** `['django/forms/widgets.py::CheckboxInput.get_context', 'django/forms/widgets.py::Widget.get_context', 'django/forms/widgets.py::Widget.build_attrs']`

### Abductive step #4 (iteration=15)

- leading: 0, considering: 0, rejected: 5

**Per-candidate deliberation traces**

#### ✗ REJECTED — `django/forms/widgets.py::Widget.build_attrs`

- **Q1 Role.** It merges a base attribute dictionary with an extra attribute dictionary to create the final set of HTML attributes for a widget.
- **Q2 Connection to symptom.** No path. This function is called by `Widget.get_context` to create the `attrs` dictionary for the template context. It correctly creates and returns a new dictionary, so it does not contribute to the problem of a mutated dictionary persisting across loop iterations. The problem is that the dictionary passed *to* `get_context` is mutated by a subclass, and this function is downstream of that mutation within a single `get_context` call.
- **Q3 Counterfactual.** `no` — This function behaves correctly by creating a new dictionary. The bug is caused by a caller reusing a dictionary that a subclass of Widget mutates, both of which are outside the scope of this function.
- **Q4 Alternatives considered.**
  - `array.py::SplitArrayWidget.get_context` — Preferred, as it is the likely location of the loop that reuses the mutated dictionary.
  - `widgets.py::CheckboxInput.get_context` — Preferred, as it is the function described as performing the problematic mutation.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a pure helper function that correctly creates a new dictionary and is not the source of the mutation.

#### ✗ REJECTED — `django/forms/widgets.py::Widget.get_context`

- **Q1 Role.** It prepares a context dictionary for rendering a widget in a template, including the widget's name, value, and HTML attributes.
- **Q2 Connection to symptom.** This function is part of the causal path but is not the cause. `CheckboxInput.get_context` (a subclass method) mutates the `attrs` dictionary it receives and then calls this `super` method. This method then operates with the already-mutated dictionary. The problem is that the caller of `CheckboxInput.get_context` (likely `SplitArrayWidget.get_context`) reuses this dictionary in a loop, causing the mutation to leak to subsequent widgets.
- **Q3 Counterfactual.** `no` — The mutation of the `attrs` dictionary happens in the `CheckboxInput.get_context` subclass before this base method is called. Therefore, modifying this function cannot prevent the mutation from affecting the dictionary object held by the original caller.
- **Q4 Alternatives considered.**
  - `widgets.py::CheckboxInput.get_context` — Preferred, as this is where the problematic mutation occurs.
  - `array.py::SplitArrayWidget.get_context` — Preferred, as this is where the mutated dictionary is likely reused across loop iterations.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This base method is not the source of the bug; the issue lies in a subclass's side effect and a caller's loop logic.

#### ✗ REJECTED — `django/contrib/postgres/forms/array.py::SplitArrayField.clean`

- **Q1 Role.** It validates a list of values submitted for a SplitArrayField by cleaning each item with the base field's clean method and handling errors.
- **Q2 Connection to symptom.** No path. This function is involved in data validation after a form is submitted. The observed symptom is a rendering issue that occurs when displaying a form with initial data, which happens before the `clean` method is ever called.
- **Q3 Counterfactual.** `no` — This function operates during form validation, not form rendering. Modifying it would have no effect on the initial appearance of widgets.
- **Q4 Alternatives considered.**
  - `array.py::SplitArrayWidget.get_context` — Preferred, as it handles widget rendering, which is where the bug manifests.
  - `widgets.py::CheckboxInput.get_context` — Preferred, as it is implicated in the rendering bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for data validation, which is unrelated to the described widget rendering symptom.

#### ✗ REJECTED — `django/contrib/postgres/forms/array.py::SplitArrayField.to_python`

- **Q1 Role.** It converts a value (typically from a database or initial data) into a Python list, ensuring each item in the list is also converted to its appropriate Python type by the base field.
- **Q2 Connection to symptom.** No path. This function processes the field's value into a Python-native format. While it handles the initial data, the bug is not in the data itself but in how the widget rendering logic uses that data and shares state (the `attrs` dictionary) incorrectly. This function does not deal with rendering or widget attributes.
- **Q3 Counterfactual.** `no` — The data is likely being converted correctly; the problem is in the rendering logic that consumes this data, not in the data preparation itself.
- **Q4 Alternatives considered.**
  - `array.py::SplitArrayWidget.get_context` — Preferred, as this function is responsible for rendering and is the likely source of the bug.
  - `widgets.py::CheckboxInput.get_context` — Preferred, as this function is reported to cause the mutation.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function handles data type conversion, which is upstream of and unrelated to the widget rendering attribute bug.

#### ✗ REJECTED — `django/forms/widgets.py::CheckboxInput.value_omitted_from_data`

- **Q1 Role.** It determines if a value for this widget was omitted from the submitted form data, always returning `False` for a checkbox because an unchecked box doesn't appear in the POST data.
- **Q2 Connection to symptom.** No path. This function is called during the processing of submitted form data (data binding). The symptom described is a rendering issue when the form is first displayed with initial data, which is a separate phase of the form lifecycle.
- **Q3 Counterfactual.** `no` — This function is not involved in rendering the widget, so changing it would not affect the symptom.
- **Q4 Alternatives considered.**
  - `array.py::SplitArrayWidget.get_context` — Preferred, as it is responsible for rendering the array of widgets.
  - `widgets.py::CheckboxInput.get_context` — Preferred, as it is responsible for rendering the individual checkbox.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for interpreting submitted form data, which is unrelated to the initial rendering bug.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/forms/widgets.py::Widget.build_attrs` | high | This is a pure helper function that correctly creates a new dictionary and is not the source of the mutation. |  |
| `django/forms/widgets.py::Widget.get_context` | high | This base method is not the source of the bug; the issue lies in a subclass's side effect and a caller's loop logic. |  |
| `django/contrib/postgres/forms/array.py::SplitArrayField.clean` | high | This function is for data validation, which is unrelated to the described widget rendering symptom. |  |
| `django/contrib/postgres/forms/array.py::SplitArrayField.to_python` | high | This function handles data type conversion, which is upstream of and unrelated to the widget rendering attribute bug. |  |
| `django/forms/widgets.py::CheckboxInput.value_omitted_from_data` | high | This function is for interpreting submitted form data, which is unrelated to the initial rendering bug. |  |

**Causal chains (per candidate)**

- `django/forms/widgets.py::Widget.build_attrs`  (score=0.0)  \
  
- `django/forms/widgets.py::Widget.get_context`  (score=1.0)  \
  
- `django/contrib/postgres/forms/array.py::SplitArrayField.clean`  (score=0.0)  \
  
- `django/contrib/postgres/forms/array.py::SplitArrayField.to_python`  (score=0.0)  \
  
- `django/forms/widgets.py::CheckboxInput.value_omitted_from_data`  (score=0.0)  \
  

**next_to_explore:** `['django/contrib/postgres/forms/array.py::SplitArrayWidget.get_context', 'django/forms/widgets.py::CheckboxInput.get_context']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/contrib/postgres/forms/array.py::SplitArrayWidget.get_context` | 0.95 |
| 2 | `django/forms/widgets.py::CheckboxInput.get_context` | 0.7 |
| 3 | `django/forms/fields.py::Field.widget_attrs` | 0.15 |
| 4 | `django/forms/widgets.py::Widget.get_context` | 0.05 |
| 5 | `django/forms/widgets.py::Widget.build_attrs` | 0.02 |
| 6 | `django/contrib/postgres/forms/array.py::SplitArrayField.__init__` | 0.01 |
| 7 | `django/contrib/postgres/forms/array.py::SplitArrayWidget.value_from_datadict` | 0.01 |
| 8 | `django/forms/widgets.py::CheckboxInput.__init__` | 0.01 |
| 9 | `django/contrib/postgres/forms/array.py::SplitArrayField.to_python` | 0.01 |
| 10 | `django/contrib/postgres/forms/array.py::SplitArrayField.clean` | 0.01 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/contrib/postgres/forms/array.py::SplitArrayWidget.get_context` | 0.950 | high | 1/1 | (133, 152) |
| 2 | `django/forms/widgets.py::CheckboxInput.get_context` | 0.700 | high | 1/1 | (523, 528) |
| 3 | `django/forms/widgets.py::CheckboxInput.value_from_datadict` | 0.356 | high | 1/1 | (530, 540) |
| 4 | `django/forms/forms.py::BaseForm.get_initial_for_field` | 0.312 | high | 1/1 | (481, 489) |
| 5 | `django/forms/widgets.py::CheckboxSelectMultiple.id_for_label` | 0.301 | high | 1/1 | (781, 788) |
| 6 | `django/forms/boundfield.py::BoundField.build_widget_attrs` | 0.285 | high | 1/1 | (221, 228) |
| 7 | `django/forms/widgets.py::CheckboxInput.value_omitted_from_data` | 0.285 | high | 1/1 | (542, 545) |
| 8 | `django/forms/widgets.py::CheckboxSelectMultiple.value_omitted_from_data` | 0.280 | high | 1/1 | (776, 779) |
| 9 | `django/forms/widgets.py::CheckboxInput.format_value` | 0.272 | high | 1/1 | (517, 521) |
| 10 | `django/forms/boundfield.py::BoundField.as_widget` | 0.261 | high | 1/1 | (79, 97) |
