# Instance: `matplotlib__matplotlib-20859`

- runs: 1   termination: `ledger_informed`   think-high calls: 4

## Issue (truncated to 1200 chars)

```
Adding a legend to a `SubFigure` doesn't work
<!--To help us understand and resolve your issue, please fill out the form to the best of your ability.-->
<!--You can feel free to delete the sections that do not apply.-->

### Bug report

**Bug summary**

<!--A short 1-2 sentences that succinctly describes the bug-->

Adding a legend to a `SubFigure` doesn't work

**Code for reproduction**

<!--A minimum code snippet required to reproduce the bug.
Please make sure to minimize the number of dependencies required, and provide
any necessary plotted data.
Avoid using threads, as Matplotlib is (explicitly) not thread-safe.-->

```python
import matplotlib.pyplot as plt

subfig = plt.figure().subfigures()
ax = subfig.subplots()
ax.plot([0, 1, 2], [0, 1, 2], label="test")
subfig.legend()
```

**Actual outcome**

<!--The output produced by the above code, which may be a screenshot, console output, etc.-->

```python-traceback
Traceback (most recent call last):
  File "bug_test.py", line 5, in <module>
    subfig.legend()
  File "/.../matplotlib/lib/matplotlib/figure.py", line 1068, in legend
    l = mlegend.Legend(self, handles, labels, *extra_args,
  File
```

## Stage 3 — Symptoms extracted

- exception types: `['TypeError']`
- error messages: `['Legend needs either Axes or Figure as parent']`
- behaviors: `['adding a legend to a SubFigure']`
- named APIs: `['plt.figure', 'Figure.subfigures', 'SubFigure.subplots', 'Axes.plot', 'SubFigure.legend']`
- stack frames: `[{'file': '/.../matplotlib/lib/matplotlib/figure.py', 'func': 'legend', 'line': 1068}, {'file': '/.../matplotlib/lib/matplotlib/legend.py', 'func': '__init__', 'line': 441}, {'file': 'bug_test.py', 'func': '<module>', 'line': 5}]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `lib/matplotlib/legend.py` | Implements the legend functionality, and the traceback points to this file. |
| 2 | `lib/matplotlib/axes/_axes.py` | Axes objects are the parents of legends, and the issue involves adding a legend to a SubFigure's axes. |
| 3 | `lib/matplotlib/figure.py` | The issue is about adding a legend to a SubFigure, so this file is relevant. |
| 4 | `lib/matplotlib/backend_bases.py` | Defines the base classes for backends, including methods for drawing and rendering. |
| 5 | `lib/matplotlib/artist.py` | Defines the Artist base class, which is inherited by Figure, Axes, and Legend. |
| 6 | `lib/matplotlib/container.py` | Defines container classes like BarContainer, ErrorbarContainer, and StemContainer, which might be relevant to how legends are handled. |
| 7 | `lib/matplotlib/legend_handler.py` | Deals with how different plot types are represented in the legend. |
| 8 | `examples/text_labels_and_annotations/figlegend_demo.py` | Example demonstrating figure legends. |
| 9 | `examples/subplots_axes_and_figures/subfigures.py` | Example demonstrating subfigures. |
| 10 | `lib/matplotlib/tests/test_legend.py` | Tests for the legend functionality. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 0, considering: 0, rejected: 0

### Abductive step #2 (iteration=6)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `lib/matplotlib/axes/_base.py::_process_plot_var_args._makeline`

- **Q1 Role.** This is a helper function within `Axes` that creates a `Line2D` artist object from processed plot arguments.
- **Q2 Connection to symptom.** No path. This function is called during `ax.plot()`, which successfully creates a line artist with a label. The error, a `TypeError`, occurs much later during the `subfig.legend()` call, which is an entirely separate operation. The execution of `_makeline` has already completed without error before the symptomatic code path is entered.
- **Q3 Counterfactual.** `no` — The error is a type check on the `SubFigure` object within the `Legend` constructor. Modifying this function, which only creates `Line2D` objects, would not change the type of `SubFigure` or alter the logic in the `Legend` class.
- **Q4 Alternatives considered.**
  - `matplotlib.legend.Legend.__init__` — Preferred, as this is where the traceback shows the TypeError is explicitly raised.
  - `matplotlib.figure.FigureBase.legend` — Preferred, as this is the method called on the `SubFigure` object that initiates the failing legend creation process.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is involved in creating the plotted line, not the legend, and its execution is complete before the error occurs.

#### ✗ REJECTED — `lib/matplotlib/axes/_base.py::_process_plot_var_args._plot_args`

- **Q1 Role.** This function processes the positional and keyword arguments for `Axes.plot`, handling various call signatures and preparing them for artist creation.
- **Q2 Connection to symptom.** No path. This function is called as part of `ax.plot()` to parse arguments like `label`. While the label is necessary for the legend to be generated, this function's role is limited to argument parsing for the plot artist. It does not participate in the `subfig.legend()` call, where the `TypeError` originates.
- **Q3 Counterfactual.** `no` — The bug is caused by a strict type check in `legend.py`. Modifying this argument-parsing function for `plot` would not affect the type of the `SubFigure` object or the checks performed when its `legend` method is called.
- **Q4 Alternatives considered.**
  - `matplotlib.legend.Legend.__init__` — Preferred, as the traceback points directly to this function as the source of the exception.
  - `matplotlib.figure.FigureBase.legend` — Preferred, as it is the direct caller of the code that fails.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function only parses arguments for `plot` and is not on the execution path of the failing `subfig.legend()` call.

#### ✗ REJECTED — `lib/matplotlib/axes/_axes.py::Axes.legend`

- **Q1 Role.** This method creates and places a legend on an `Axes` object.
- **Q2 Connection to symptom.** No path. The user's code calls `subfig.legend()`, which resolves to `FigureBase.legend`, not `Axes.legend`. While its purpose is similar, this specific function is not executed in the provided failing example. The bug is specific to creating a legend on a `SubFigure`, not an `Axes`.
- **Q3 Counterfactual.** `no` — Modifying `Axes.legend` would have no effect because the failing code calls `SubFigure.legend`, which is a completely different method on a different class.
- **Q4 Alternatives considered.**
  - `matplotlib.figure.FigureBase.legend` — Preferred, as this is the method that is actually called on the `SubFigure` object in the user's code.
  - `matplotlib.legend.Legend.__init__` — Preferred, as it is the ultimate source of the error according to the traceback.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is not in the call stack for the bug; the code calls `SubFigure.legend`, not `Axes.legend`.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `lib/matplotlib/axes/_base.py::_process_plot_var_args._makeline` | high | This function is involved in creating the plotted line, not the legend, and its execution is complete before the error occurs. |  |
| `lib/matplotlib/axes/_base.py::_process_plot_var_args._plot_args` | high | This function only parses arguments for `plot` and is not on the execution path of the failing `subfig.legend()` call. |  |
| `lib/matplotlib/axes/_axes.py::Axes.legend` | high | This function is not in the call stack for the bug; the code calls `SubFigure.legend`, not `Axes.legend`. |  |

**Causal chains (per candidate)**

- `lib/matplotlib/axes/_base.py::_process_plot_var_args._makeline`  (score=0.0)  \
  
- `lib/matplotlib/axes/_base.py::_process_plot_var_args._plot_args`  (score=0.0)  \
  
- `lib/matplotlib/axes/_axes.py::Axes.legend`  (score=0.0)  \
  

**next_to_explore:** `['lib/matplotlib/legend.py::Legend.__init__', 'lib/matplotlib/figure.py::FigureBase.legend', 'lib/matplotlib/figure.py::SubFigure', 'lib/matplotlib/figure.py::Figure']`

### Abductive step #3 (iteration=9)

- leading: 1, considering: 0, rejected: 0

**Per-candidate deliberation traces**

#### ✓ LEADING — `lib/matplotlib/legend.py::Legend.__init__`

- **Q1 Role.** This function is the constructor for the Legend artist, responsible for initializing its properties and attaching it to a parent Axes or Figure.
- **Q2 Connection to symptom.** Yes, this function directly produces the symptom. 
1. `Legend.__init__` is called with the `parent` argument being a `SubFigure` instance. 
2. The function's code includes a check to validate that the `parent` is an instance of `Axes` or `Figure`. 
3. A `SubFigure` object is not an instance of `Axes` or `Figure`, so this check fails. 
4. Consequently, the function raises the `TypeError` with the message "Legend needs either Axes or Figure as parent", which matches the observed traceback.
- **Q3 Counterfactual.** `yes` — Modifying the type check to also accept `matplotlib.figure.FigureBase` (from which `SubFigure` inherits) would allow the `SubFigure` instance to be considered a valid parent, preventing the `TypeError` from being raised.
- **Q4 Alternatives considered.**
  - `matplotlib.figure.FigureBase.legend` — This is the caller. The fix could be here, but it's more logical for the `Legend` class itself to correctly identify its valid parents, rather than having callers adapt.
  - `matplotlib.figure.SubFigure` — Changing `SubFigure` to inherit from `Figure` might work, but this is a major architectural change with unknown side effects, whereas the current issue is a localized type check.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function contains the explicit type check that causes the TypeError, and modifying it as suggested by the user is the direct and correct fix.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `lib/matplotlib/legend.py::Legend.__init__` | high | This function contains the explicit type check that causes the TypeError, and modifying it as suggested by the user is the direct and correct fix. | In the parent type check, allow `FigureBase` in addition to `Axes` and `Figure`. The check should be something like `isinstance(parent, (Axes, FigureBase))`. |

**Causal chains (per candidate)**

- `lib/matplotlib/legend.py::Legend.__init__`  (score=10.0)  \
  `SubFigure.legend()` is called, which in turn calls `FigureBase.legend()`. → `FigureBase.legend()` instantiates `Legend`, passing the `SubFigure` instance as the `parent` argument to `Legend.__init__`. → Inside `Legend.__init__`, a condition checks if `parent` is an instance of `Axes` or `Figure`. → The `SubFigure` instance is not an instance of `Axes` or `Figure`, so the check fails. → The function raises a `TypeError` with the exact message seen in the bug report.

**next_to_explore:** `['lib/matplotlib/figure.py::FigureBase.legend', 'lib/matplotlib/figure.py::FigureBase', 'lib/matplotlib/figure.py::SubFigure', 'lib/matplotlib/figure.py::Figure']`

### Abductive step #4 (iteration=18)

- leading: 0, considering: 0, rejected: 5

**Per-candidate deliberation traces**

#### ✗ REJECTED — `lib/matplotlib/axes/_base.py::_process_plot_var_args.__init__`

- **Q1 Role.** This is the constructor for a helper class that parses and processes arguments for plotting functions like `Axes.plot`.
- **Q2 Connection to symptom.** This function is called as part of `ax.plot(...)`. It helps process the arguments to create a line with a label. The legend later tries to use this label. However, the `TypeError` is about the legend's parent container (`SubFigure`), not about the contents of the legend. The error would occur even if `ax.plot` was not called, so there is no direct causal path to the symptom.
- **Q3 Counterfactual.** `no` — Modifying this function would affect how plot arguments are handled, but it would not change the type of `subfig` or the type check inside `Legend.__init__` that causes the crash.
- **Q4 Alternatives considered.**
  - `matplotlib.legend.Legend.__init__` — This is the function that raises the TypeError, making it the most direct location of the bug's manifestation.
  - `matplotlib.figure.FigureBase.legend` — This method is the caller of `Legend.__init__` and is called on the `SubFigure` object; it's a strong candidate for investigation.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is involved in creating labeled artists for the legend, but is not causally related to the TypeError, which stems from `SubFigure` not being a valid legend parent.

#### ✗ REJECTED — `lib/matplotlib/figure.py::FigureBase.add_subfigure`

- **Q1 Role.** This function adds a `SubFigure` to a figure, typically as part of a grid of subplots.
- **Q2 Connection to symptom.** Yes, a path exists. This function is called by `figure.subfigures()` and creates the `SubFigure` instance (`subfig`). This `subfig` object is later used to call `subfig.legend()`. Inside the `legend()` call, this `subfig` object is passed as the `parent` to `Legend.__init__`, where it fails the `isinstance(parent, Figure)` check, causing the `TypeError`.
- **Q3 Counterfactual.** `no` — This function's job is to create a `SubFigure`. The problem is not that it creates a `SubFigure`, but that `Legend.__init__` does not accept it. Changing this function to not create a `SubFigure` would break intended functionality.
- **Q4 Alternatives considered.**
  - `matplotlib.legend.Legend.__init__` — Preferred, as it contains the faulty type check that needs to be relaxed to include `SubFigure` or `FigureBase`.
  - `matplotlib.figure.SubFigure` — Considered whether `SubFigure` should inherit from `Figure`, but this would likely be a major architectural change and is probably incorrect.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function correctly creates the `SubFigure` object; the fault lies downstream in `Legend.__init__` which improperly rejects this object type.

#### ✗ REJECTED — `lib/matplotlib/axes/_base.py::_process_plot_var_args.__call__`

- **Q1 Role.** This method executes the main logic of the `_process_plot_var_args` helper, parsing `*args` and `**kwargs` for a plotting command to generate plottable data.
- **Q2 Connection to symptom.** This function is called by `ax.plot()` and is responsible for interpreting the data and the `label` keyword argument. This creates the labeled artist that the legend is intended to display. However, the `TypeError` is independent of whether there are any labeled artists. Therefore, this function's execution is coincidental to the bug itself.
- **Q3 Counterfactual.** `no` — Modifying this function would change how plot data is processed, but it has no bearing on the type check performed when `subfig.legend()` is called.
- **Q4 Alternatives considered.**
  - `matplotlib.legend.Legend.__init__` — This is where the error is raised due to a strict type check, making it the root cause.
  - `matplotlib.figure.FigureBase._get_legend_handles_labels` — This function gathers the artists to be included in the legend; while relevant to legend content, it's not related to the parent type error.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function processes plot arguments to create legend entries, but the TypeError is unrelated to legend content and happens before content is placed.

#### ✗ REJECTED — `lib/matplotlib/axes/_base.py::_process_plot_var_args.__getstate__`

- **Q1 Role.** This function defines the serialization (pickling) behavior for `_process_plot_var_args` instances.
- **Q2 Connection to symptom.** No path. Serialization is not used in the provided code snippet, so this function is never called.
- **Q3 Counterfactual.** `no` — The function is not on the execution path of the bug, so modifying it would have no effect.
- **Q4 Alternatives considered.**
  - `N/A` — This function is completely irrelevant to the bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for pickling and is not on the execution path of the bug.

#### ✗ REJECTED — `lib/matplotlib/axes/_base.py::_process_plot_var_args.__setstate__`

- **Q1 Role.** This function defines the deserialization (unpickling) behavior for `_process_plot_var_args` instances.
- **Q2 Connection to symptom.** No path. Deserialization is not used in the provided code snippet, so this function is never called.
- **Q3 Counterfactual.** `no` — The function is not on the execution path of the bug, so modifying it would have no effect.
- **Q4 Alternatives considered.**
  - `N/A` — This function is completely irrelevant to the bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for unpickling and is not on the execution path of the bug.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `lib/matplotlib/axes/_base.py::_process_plot_var_args.__init__` | high | This function is involved in creating labeled artists for the legend, but is not causally related to the TypeError, which stems from `SubFigure` not being a valid legend parent. |  |
| `lib/matplotlib/figure.py::FigureBase.add_subfigure` | high | This function correctly creates the `SubFigure` object; the fault lies downstream in `Legend.__init__` which improperly rejects this object type. |  |
| `lib/matplotlib/axes/_base.py::_process_plot_var_args.__call__` | high | This function processes plot arguments to create legend entries, but the TypeError is unrelated to legend content and happens before content is placed. |  |
| `lib/matplotlib/axes/_base.py::_process_plot_var_args.__getstate__` | high | This function is for pickling and is not on the execution path of the bug. |  |
| `lib/matplotlib/axes/_base.py::_process_plot_var_args.__setstate__` | high | This function is for unpickling and is not on the execution path of the bug. |  |

**Causal chains (per candidate)**

- `lib/matplotlib/axes/_base.py::_process_plot_var_args.__init__`  (score=1.0)  \
  ax.plot([0, 1, 2], [0, 1, 2], label="test") is called. → Internally, an instance of `_process_plot_var_args` is created to handle the arguments. → `_process_plot_var_args.__init__` is called. → This sets up the processing for a line that has a label, which is needed for the user's desired outcome (a legend with an entry). → However, the subsequent `TypeError` in `subfig.legend()` is unrelated to whether a labeled artist exists.
- `lib/matplotlib/figure.py::FigureBase.add_subfigure`  (score=4.0)  \
  plt.figure().subfigures() is called, which internally calls `add_subfigure`. → `add_subfigure` creates and returns a `SubFigure` instance. → This instance is assigned to the `subfig` variable. → `subfig.legend()` is called. → The `subfig` object is passed as the `parent` argument to `matplotlib.legend.Legend.__init__`. → The type check `isinstance(parent, matplotlib.figure.Figure)` fails for the `SubFigure` object, causing a `TypeError`.
- `lib/matplotlib/axes/_base.py::_process_plot_var_args.__call__`  (score=1.0)  \
  ax.plot([0, 1, 2], [0, 1, 2], label="test") is called. → The `__call__` method of the `_process_plot_var_args` instance is invoked. → This method processes the positional and keyword arguments, creating a `Line2D` artist with the label 'test'. → This labeled artist is added to the axes, making it available for the legend. → The subsequent `TypeError` in `subfig.legend()` is unrelated to the existence of this artist.
- `lib/matplotlib/axes/_base.py::_process_plot_var_args.__getstate__`  (score=0.0)  \
  This function is not called in the execution path of the provided code.
- `lib/matplotlib/axes/_base.py::_process_plot_var_args.__setstate__`  (score=0.0)  \
  This function is not called in the execution path of the provided code.

**next_to_explore:** `['matplotlib.legend.Legend.__init__', 'matplotlib.figure.FigureBase.legend', 'matplotlib.figure.SubFigure', 'matplotlib.figure.Figure.legend', 'matplotlib.axes.Axes.legend']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `lib/matplotlib/legend.py::Legend.__init__` | 1.0 |
| 2 | `lib/matplotlib/figure.py::FigureBase.legend` | 0.2 |
| 3 | `lib/matplotlib/figure.py::FigureBase.add_subfigure` | 0.1 |
| 4 | `lib/matplotlib/figure.py::FigureBase.subfigures` | 0.05 |
| 5 | `lib/matplotlib/axes/_axes.py::Axes.legend` | 0.0 |
| 6 | `lib/matplotlib/legend.py::_parse_legend_args` | 0.0 |
| 7 | `lib/matplotlib/axes/_axes.py::Axes._remove_legend` | 0.0 |
| 8 | `lib/matplotlib/figure.py::FigureBase.add_subplot` | 0.0 |
| 9 | `lib/matplotlib/figure.py::SubFigure.axes` | 0.0 |
| 10 | `lib/matplotlib/legend.py::Legend.draw` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `lib/matplotlib/legend.py::Legend.__init__` | 1.000 | high | 1/1 | (294, 553) |
| 2 | `lib/matplotlib/axes/_base.py::_process_plot_var_args._plot_args` | 0.301 | high | 1/1 | (406, 538) |
| 3 | `lib/matplotlib/axes/_axes.py::Axes.plot` | 0.293 | high | 1/1 | (1383, 1630) |
| 4 | `lib/matplotlib/legend.py::Legend.get_children` | 0.287 | high | 1/1 | (858, 860) |
| 5 | `lib/matplotlib/axes/_axes.py::Axes.get_legend_handles_labels` | 0.269 | high | 1/1 | (172, 184) |
| 6 | `lib/matplotlib/axes/_base.py::_process_plot_var_args.__call__` | 0.221 | high | 1/1 | (242, 312) |
| 7 | `lib/matplotlib/figure.py::FigureBase.legend` | 0.200 | high | 1/1 | (941, 1073) |
| 8 | `lib/matplotlib/axes/_base.py::_process_plot_var_args._makeline` | 0.198 | high | 1/1 | (347, 352) |
| 9 | `lib/matplotlib/axes/_base.py::_process_plot_var_args.__getstate__` | 0.198 | high | 1/1 | (228, 230) |
| 10 | `lib/matplotlib/axes/_base.py::_process_plot_var_args._makefill` | 0.197 | high | 1/1 | (354, 404) |
