# Instance: `matplotlib__matplotlib-20826`

- runs: 1   termination: `ledger_informed`   think-high calls: 4

## Issue (truncated to 1200 chars)

```
ax.clear() adds extra ticks, un-hides shared-axis tick labels
### Bug report

**Bug summary**

When using shared axes (e.g. from `plt.subplots(2, 2, sharex=True, sharey=True)`), calling `ax.clear()` causes ticks and tick labels to be shown that should be hidden. The axes are still linked, though (e.g. adjusting the plotting range on one subplot adjusts the others as well). This is a behavior change between matplotlib 3.4.1 and 3.4.2.

**Code for reproduction**

This code produces different results with matplotlib 3.4.1 and 3.4.2:

```python
import numpy as np
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, sharex=True, sharey=True)

x = np.arange(0.0, 2*np.pi, 0.01)
y = np.sin(x)

for ax in axes.flatten():
    ax.clear()
    ax.plot(x, y)
```

This example is of course silly, but I use the general pattern when making animations with FuncAnimation, where my plotting function is a complex module which doesn't facilitate blitting, so I clear and re-use the axes for each frame of the animation.

**Actual outcome**

This is the plot produced with matplotlib 3.4.2:

![matplotlib-3 4 2](https://user-images.githubusercontent.com/23462789/126717
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['adds extra ticks', 'un-hides shared-axis tick labels', 'ticks and tick labels are shown that should be hidden', 'adjusting the plotting range on one subplot adjusts the others', 'tick labels that should be hidden by virtue of the shared axes', 'ticks that appear along the top and right side of each subplot']`
- named APIs: `['plt.subplots', 'ax.clear()', 'ax.plot']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `lib/matplotlib/axes/_base.py` | Likely involved in managing shared axes and tick visibility. |
| 2 | `lib/matplotlib/axis.py` | Manages tick and tick label properties, including visibility. |
| 3 | `lib/matplotlib/pyplot.py` | Provides the `clear()` function used in the example code. |
| 4 | `lib/matplotlib/axes/_axes.py` | Handles axes clearing and plotting, potentially affecting tick visibility. |
| 5 | `lib/matplotlib/figure.py` | Manages axes within a figure, including adding and removing them. |
| 6 | `lib/matplotlib/projections/polar.py` | Potentially related if the issue is specific to polar plots. |
| 7 | `lib/matplotlib/backends/backend_agg.py` | Handles rendering, which could affect how ticks are drawn. |
| 8 | `lib/matplotlib/testing/test_axes.py` | Contains tests for axes functionality, including tick and label behavior. |
| 9 | `lib/matplotlib/tests/test_figure.py` | Contains tests for figure functionality, including axes management. |
| 10 | `lib/matplotlib/tests/test_ticks.py` | Contains tests for tick-related functionality. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `lib/matplotlib/axes/_base.py::_AxesBase.clear`

- **Q1 Role.** This function is a method on the _AxesBase class that clears the axes by calling self.cla().
- **Q2 Connection to symptom.** The user's code calls `ax.clear()`. Since `ax` is an `Axes` object inheriting from `_AxesBase`, this method is the entry point for the call chain. It immediately delegates to `self.cla()`, so it is on the causal path but contains no logic itself.
- **Q3 Counterfactual.** `no` — This function is a simple one-line wrapper around `self.cla()`. The logic that causes the bug is in `cla()` or its callees, so modifying this function would not be the correct fix.
- **Q4 Alternatives considered.**
  - `matplotlib.axes._base._AxesBase.cla` — This is the callee and contains the actual orchestration logic for clearing an Axes, making it a much more likely location for the bug's origin.
  - `matplotlib.axis.Axis.clear` — This is called by `_AxesBase.cla` and is responsible for clearing individual axes, where tick and label properties are managed.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a trivial wrapper and contains no logic related to the symptoms.

#### ✓ LEADING — `lib/matplotlib/axis.py::Axis.clear`

- **Q1 Role.** This function resets the properties of a single Axis object (e.g., xaxis or yaxis) to their default values.
- **Q2 Connection to symptom.** The `ax.clear()` call eventually triggers `self.xaxis.clear()` and `self.yaxis.clear()`. This function resets locators, formatters, and ticks (`self.reset_ticks()`). For shared axes, tick labels are hidden by setting a specific formatter (e.g., `NullFormatter`). This function's aggressive reset to defaults would remove that custom formatter, causing the hidden labels to reappear, which directly matches the primary symptom.
- **Q3 Counterfactual.** `yes` — If this function were modified to not reset formatters/locators when an axis is shared, the symptom of reappearing tick labels would be eliminated. The fix would involve checking the shared status before resetting certain properties.
- **Q4 Alternatives considered.**
  - `matplotlib.axes._base._AxesBase.cla` — This is the caller, but it's more likely the specific `Axis` clearing logic is at fault, rather than the orchestration.
  - `matplotlib.axis.Axis.reset_ticks` — This is a callee and could be where the reset specifically happens, but the decision to reset everything is made here in `clear`.
  - `matplotlib.pyplot.subplots` — This function sets up the sharing, but the bug is triggered by `clear`, indicating a change in the clearing logic, not the setup.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function's purpose is to reset axis properties, and its implementation appears to ignore the special state of shared axes, directly causing the symptoms.

#### ✗ REJECTED — `lib/matplotlib/axis.py::Axis.cla`

- **Q1 Role.** This function is an alias for Axis.clear(), providing a `cla` method on Axis objects.
- **Q2 Connection to symptom.** The `Axes.cla()` method calls `self.xaxis.cla()` and `self.yaxis.cla()`. This function is therefore on the causal path, but it immediately delegates to `self.clear()`, which contains the actual logic.
- **Q3 Counterfactual.** `no` — This is a one-line alias for `self.clear()`. Any fix would need to be in `self.clear()` itself, not in this wrapper.
- **Q4 Alternatives considered.**
  - `matplotlib.axis.Axis.clear` — Preferred, as it is the callee that contains the actual implementation logic.
  - `matplotlib.axes._base._AxesBase.cla` — This is the caller that invokes `Axis.cla`, but the issue lies downstream.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a trivial alias and contains no logic relevant to the bug.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `lib/matplotlib/axis.py::Axis.clear` | high | This function's purpose is to reset axis properties, and its implementation appears to ignore the special state of shared axes, directly causing the symptoms. | The function should check if the axis is part of a shared-axis group and, if so, avoid resetting formatters that are used to hide tick labels. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `lib/matplotlib/axes/_base.py::_AxesBase.clear` | high | This function is a trivial wrapper and contains no logic related to the symptoms. |  |
| `lib/matplotlib/axis.py::Axis.cla` | high | This function is a trivial alias and contains no logic relevant to the bug. |  |

**Causal chains (per candidate)**

- `lib/matplotlib/axes/_base.py::_AxesBase.clear`  (score=1.0)  \
  ax.clear() is called in user code. → _AxesBase.clear() is invoked. → _AxesBase.clear() calls self.cla().
- `lib/matplotlib/axis.py::Axis.clear`  (score=9.0)  \
  ax.clear() is called, which calls ax.cla(). → ax.cla() calls self.xaxis.clear() and self.yaxis.clear(). → Axis.clear() resets axis properties to defaults, including formatters and ticks. → For shared axes, this reset removes the NullFormatter that was hiding tick labels on interior axes. → The removal of the formatter causes the tick labels to become visible again, producing the symptom.
- `lib/matplotlib/axis.py::Axis.cla`  (score=1.0)  \
  ax.clear() is called, which calls ax.cla(). → ax.cla() calls self.xaxis.cla(). → Axis.cla() calls self.clear().

**next_to_explore:** `['matplotlib.axes._base._AxesBase.cla', 'matplotlib.axis.Axis.reset_ticks', 'matplotlib.axis.Axis._reset_major_tick_kw', 'matplotlib.ticker.Formatter', 'matplotlib.figure.Figure.subplots']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 0, rejected: 0

### Abductive step #3 (iteration=9)

- leading: 0, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `lib/matplotlib/figure.py::FigureBase.subplots`

- **Q1 Role.** This function is a factory method on a Figure object that creates a grid of subplots, handling the logic for sharing axes between them.
- **Q2 Connection to symptom.** Yes, this function is responsible for setting up the shared axes as requested by `sharex=True` and `sharey=True`. This setup includes hiding tick labels on the inner axes. The symptom is that these tick labels reappear after `ax.clear()` is called. Therefore, `subplots` correctly establishes a state that is later corrupted by `ax.clear()`. The execution path is: `plt.subplots(...)` is called -> `FigureBase.subplots` creates axes -> it configures axis sharing and tick label visibility -> `ax.clear()` is called later, which undoes the tick label configuration.
- **Q3 Counterfactual.** `no` — The bug report states that if `ax.clear()` is removed, the plot is correct. This indicates that `subplots` is functioning as expected, and the fault lies with `ax.clear()` resetting properties it shouldn't.
- **Q4 Alternatives considered.**
  - `matplotlib.axes._base._AxesBase.clear` — This is the function directly called in the user's code that triggers the symptom, making it the primary suspect for the root cause.
  - `matplotlib.axis.Axis.clear` — This is likely called by `_AxesBase.clear` and is a strong candidate for where the incorrect state reset happens.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function correctly sets up the initial plot state, which is later corrupted by `ax.clear()`; it is part of the context, not the cause of the bug.

#### ✗ REJECTED — `lib/matplotlib/pyplot.py::cla`

- **Q1 Role.** This function is a convenience wrapper in the `pyplot` state-machine interface that gets the current `Axes` object (`gca()`) and calls its `cla()` method to clear it.
- **Q2 Connection to symptom.** No path exists. The user's code for reproduction uses the object-oriented interface, calling `ax.clear()` on specific axes instances returned by `plt.subplots`. It does not use the state-based `plt.cla()` function.
- **Q3 Counterfactual.** `no` — Modifying this function would have no effect on the provided code because it is never called.
- **Q4 Alternatives considered.**
  - `matplotlib.axes._base._AxesBase.clear` — This is the method actually invoked by `ax.clear()` in the user's code and is the correct entry point to investigate.
  - `matplotlib.axes._base._AxesBase.cla` — This is an alias for `_AxesBase.clear` and is what `plt.cla()` would eventually call, but `_AxesBase.clear` is the canonical name to trace from the user's code.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is not on the execution path of the bug-reproducing code.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `lib/matplotlib/figure.py::FigureBase.subplots` | high | This function correctly sets up the initial plot state, which is later corrupted by `ax.clear()`; it is part of the context, not the cause of the bug. |  |
| `lib/matplotlib/pyplot.py::cla` | high | This function is not on the execution path of the bug-reproducing code. |  |

**Causal chains (per candidate)**

- `lib/matplotlib/figure.py::FigureBase.subplots`  (score=2.0)  \
  The user calls `plt.subplots(sharex=True, sharey=True)`. → This function correctly configures the axes, including hiding tick labels for inner subplots. → A subsequent call to `ax.clear()` incorrectly resets these configurations, causing the symptoms. → Therefore, this function only provides the initial state upon which the bug manifests, but does not cause it.
- `lib/matplotlib/pyplot.py::cla`  (score=0.0)  \
  The user's code calls `ax.clear()` on an `Axes` object. → `plt.cla()` is part of the state-based pyplot API and is not called. → Therefore, this function is not in the execution path.

**next_to_explore:** `['lib/matplotlib/axes/_base.py::_AxesBase.clear', 'lib/matplotlib/axes/_base.py::_AxesBase.cla', 'lib/matplotlib/axis.py::Axis.clear', 'lib/matplotlib/axis.py::Axis.reset_ticks', 'lib/matplotlib/axis.py::Axis._reset_major_tick_kw']`

### Abductive step #4 (iteration=12)

- leading: 0, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `lib/matplotlib/figure.py::FigureBase.delaxes`

- **Q1 Role.** This function removes a specified Axes object from the figure and correctly handles breaking any shared-axis links.
- **Q2 Connection to symptom.** No path. The user's code calls `ax.clear()`, which in turn calls `ax.cla()`. Neither of these methods calls `delaxes`. Therefore, this function is not on the execution path of the code that demonstrates the bug.
- **Q3 Counterfactual.** `no` — Since this function is not executed when running the user's code, modifying it would have no effect on the observed symptoms.
- **Q4 Alternatives considered.**
  - `matplotlib.axis.Axis.cla` — Preferred, as it is called by `ax.clear()` and appears to unconditionally reset tick label visibility, which directly explains a key symptom.
  - `matplotlib.axes._base._AxesBase.cla` — Considered, as it is the primary implementation for `ax.clear()` and orchestrates the state-resetting that is causing the issue.
  - `matplotlib.figure.FigureBase.subplots` — Considered, as it sets up the shared-axis properties that are being incorrectly cleared. The bug lies in the interaction between this setup and the clearing logic.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is not on the execution path of the bug-triggering code and therefore cannot be the cause.

#### ✗ REJECTED — `lib/matplotlib/axes/_base.py::_AxesBase.minorticks_off`

- **Q1 Role.** This function disables the drawing of minor ticks on both the x and y axes by setting their minor locators to `NullLocator`.
- **Q2 Connection to symptom.** No path. This function is called via `ax.clear()` -> `ax.cla()` -> `ax.minorticks_off()`. However, the symptom is the *addition* of extra ticks and the un-hiding of tick labels. This function does the opposite of adding ticks (it removes minor ones) and has no effect on major ticks or tick labels. Therefore, it cannot cause the observed symptoms.
- **Q3 Counterfactual.** `no` — The symptoms are related to major ticks and tick labels on shared axes. This function only affects minor ticks, so disabling it would not fix the problem.
- **Q4 Alternatives considered.**
  - `matplotlib.axis.Axis.cla` — Preferred, as it resets tick parameters, which likely causes the reappearance of tick labels.
  - `matplotlib.axis.Axis.reset_ticks` — Considered, as it is called by `Axis.cla` and could be related to the symptom of extra ticks appearing.
  - `matplotlib.axes._base._AxesBase.cla` — Considered, as it is the caller of this function and is responsible for the overall 'clearing' logic that is faulty.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function's action (removing minor ticks) is contrary to the observed symptom of adding ticks and is unrelated to tick label visibility.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `lib/matplotlib/figure.py::FigureBase.delaxes` | high | This function is not on the execution path of the bug-triggering code and therefore cannot be the cause. |  |
| `lib/matplotlib/axes/_base.py::_AxesBase.minorticks_off` | high | This function's action (removing minor ticks) is contrary to the observed symptom of adding ticks and is unrelated to tick label visibility. |  |

**Causal chains (per candidate)**

- `lib/matplotlib/figure.py::FigureBase.delaxes`  (score=0.0)  \
  
- `lib/matplotlib/axes/_base.py::_AxesBase.minorticks_off`  (score=0.0)  \
  

**next_to_explore:** `['lib/matplotlib/axis.py::Axis.cla', 'lib/matplotlib/axes/_base.py::_AxesBase.cla', 'lib/matplotlib/axis.py::Axis.reset_ticks', 'lib/matplotlib/figure.py::FigureBase.subplots']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `lib/matplotlib/axis.py::Axis.clear` | 0.9 |
| 2 | `lib/matplotlib/axes/_base.py::_AxesBase.cla` | 0.8 |
| 3 | `lib/matplotlib/axes/_base.py::_AxesBase.clear` | 0.4 |
| 4 | `lib/matplotlib/axis.py::Axis.cla` | 0.3 |
| 5 | `lib/matplotlib/axis.py::Axis.reset_ticks` | 0.2 |
| 6 | `lib/matplotlib/figure.py::FigureBase.subplots` | 0.1 |
| 7 | `lib/matplotlib/figure.py::FigureBase.delaxes` | 0.0 |
| 8 | `lib/matplotlib/axes/_base.py::_AxesBase.minorticks_off` | 0.0 |
| 9 | `lib/matplotlib/figure.py::Figure.clf` | 0.0 |
| 10 | `lib/matplotlib/figure.py::FigureBase.add_subplot` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `lib/matplotlib/axis.py::Axis.clear` | 0.900 | high | 1/1 | (788, 816) |
| 2 | `lib/matplotlib/axes/_base.py::_AxesBase.cla` | 0.800 | high | 1/1 | (1182, 1312) |
| 3 | `lib/matplotlib/axis.py::YAxis.tick_left` | 0.420 | high | 1/1 | (2468, 2479) |
| 4 | `lib/matplotlib/axis.py::YAxis.tick_right` | 0.410 | high | 1/1 | (2455, 2466) |
| 5 | `lib/matplotlib/axes/_base.py::_AxesBase.set_axis_off` | 0.406 | high | 1/1 | (3428, 3435) |
| 6 | `lib/matplotlib/pyplot.py::cla` | 0.406 | high | 1/1 | (1070, 1073) |
| 7 | `lib/matplotlib/axis.py::Axis.set_tick_params` | 0.405 | high | 1/1 | (843, 880) |
| 8 | `lib/matplotlib/figure.py::Figure.clear` | 0.404 | high | 1/1 | (2728, 2730) |
| 9 | `lib/matplotlib/axes/_base.py::_AxesBase.clear` | 0.400 | high | 1/1 | (1473, 1475) |
| 10 | `lib/matplotlib/axes/_base.py::_AxesBase.tick_params` | 0.386 | high | 1/1 | (3349, 3426) |
