# Instance: `matplotlib__matplotlib-23314`

- runs: 1   termination: `ledger_informed`   think-high calls: 3

## Issue (truncated to 1200 chars)

```
[Bug]: set_visible() not working for 3d projection 
### Bug summary

in the subplot projection="3d" the set_visible function doesn't work even if the value is set to False

### Code for reproduction

```python
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

fig, (ax1, ax2) = plt.subplots(1, 2, subplot_kw={'projection': '3d'})
ax1.scatter(1,1,1)
ax2.scatter(1,1,1, c='r')
ax1.set_visible(False)

plt.show()
# Thanks Tim for your help! 
```


### Actual outcome

the subplot remains visible which should not happen if the value is set to False

### Expected outcome

the subplot is not visible if the value is set to False

### Additional information

_No response_

### Operating system

_No response_

### Matplotlib Version

3.4.2

### Matplotlib Backend

Qt5Agg

### Python version

3.8.10

### Jupyter version

_No response_

### Installation

_No response_
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['subplot remains visible', "set_visible function doesn't work"]`
- named APIs: `['plt.subplots', 'ax1.scatter', 'ax2.scatter', 'ax1.set_visible', 'plt.show']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `lib/matplotlib/axes/_axes.py` | Likely location for implementing set_visible for axes, including 3D. |
| 2 | `lib/matplotlib/artist.py` | Base class for artists, including Axes, and handles visibility. |
| 3 | `lib/matplotlib/mplot3d/axes3d.py` | Handles 3D-specific axes properties and rendering. |
| 4 | `lib/matplotlib/axes/__init__.py` | Exports the _axes module. |
| 5 | `lib/matplotlib/backends/backend_bases.py` | Abstract base classes for backends, may be involved in rendering. |
| 6 | `examples/mplot3d/scatter3d.py` | Example using 3d projection. |
| 7 | `examples/mplot3d/lines3d.py` | Example using 3d projection. |
| 8 | `lib/matplotlib/figure.py` | Figure management and layout. |
| 9 | `lib/matplotlib/tests/test_axes.py` | Tests for axes functionality, may need to be updated to reflect the fix. |
| 10 | `lib/matplotlib/tests/test_mplot3d.py` | Tests for 3D axes functionality, may need to be updated to reflect the fix. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `lib/matplotlib/sphinxext/plot_directive.py::split_code_at_show`

- **Q1 Role.** This function is a wrapper that splits a string of Python code at occurrences of 'plt.show()' for use in the Sphinx documentation generator.
- **Q2 Connection to symptom.** No plausible path exists. This function is part of Matplotlib's documentation generation tooling (sphinxext) and is not executed when a user runs a plotting script. The bug is a runtime rendering issue, which is entirely separate from documentation parsing.
- **Q3 Counterfactual.** `no` — Modifying this function would only impact the generation of Matplotlib's documentation and would have no effect on the execution of a user's plotting script.
- **Q4 Alternatives considered.**
  - `mpl_toolkits.mplot3d.axes3d.Axes3D.set_visible` — Preferred, as the bug is 3D-specific, and this is the most direct method to control visibility.
  - `matplotlib.axes._base._AxesBase.set_visible` — Considered, as this is the inherited method that is actually being called in the buggy version.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for documentation generation and is not on the execution path of the user's code.

#### ✗ REJECTED — `lib/matplotlib/sphinxext/plot_directive.py::_split_code_at_show`

- **Q1 Role.** This function implements the logic to split a block of code text into parts based on 'plt.show()' delimiters for the Sphinx plot directive.
- **Q2 Connection to symptom.** No plausible path exists. This function is part of the Sphinx extension for building documentation. It processes text files and is not involved in the runtime logic of creating or displaying plots from a user script.
- **Q3 Counterfactual.** `no` — Changing this function would not affect the user's script, as it's unrelated to the core plotting and rendering engine.
- **Q4 Alternatives considered.**
  - `mpl_toolkits.mplot3d.axes3d.Axes3D.draw` — Considered, as this method is responsible for drawing 3D-specific elements like panes, which remain visible.
  - `matplotlib.artist.Artist.set_visible` — Considered as the ultimate base method, but the issue is specific to the composition of a 3D axes, not the basic property.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a helper for the Sphinx plot directive and is irrelevant to the runtime bug.

#### ✗ REJECTED — `lib/mpl_toolkits/axes_grid1/mpl_axes.py::SimpleAxisArtist.set_visible`

- **Q1 Role.** This function sets the visibility of a `SimpleAxisArtist`, an artist used for drawing axis lines within the `axes_grid1` toolkit.
- **Q2 Connection to symptom.** No plausible path exists. The user's code creates a 3D subplot using `mplot3d`, which is a separate toolkit from `axes_grid1`. The `Axes3D` object and its components do not use `SimpleAxisArtist`, so this function is never called in the execution of the user's code.
- **Q3 Counterfactual.** `no` — Since this function is not on the execution path for a standard 3D subplot, modifying it would have no effect on the observed bug.
- **Q4 Alternatives considered.**
  - `matplotlib.axes._base._AxesBase.set_visible` — Preferred, as this is the method being called on the `Axes3D` object, and its logic doesn't account for 3D-specific panes.
  - `mpl_toolkits.mplot3d.axes3d.Axes3D.draw` — Considered, because it draws the panes that are not being hidden, revealing why the base `set_visible` is insufficient.
  - `mpl_toolkits.mplot3d.axes3d.Axes3D.__init__` — Considered, to confirm that 3D panes are not registered as standard children artists.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is in a different toolkit (`axes_grid1`) and is not used when creating a `mplot3d` axes.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `lib/matplotlib/sphinxext/plot_directive.py::split_code_at_show` | high | This function is for documentation generation and is not on the execution path of the user's code. |  |
| `lib/matplotlib/sphinxext/plot_directive.py::_split_code_at_show` | high | This is a helper for the Sphinx plot directive and is irrelevant to the runtime bug. |  |
| `lib/mpl_toolkits/axes_grid1/mpl_axes.py::SimpleAxisArtist.set_visible` | high | This function is in a different toolkit (`axes_grid1`) and is not used when creating a `mplot3d` axes. |  |

**Causal chains (per candidate)**

- `lib/matplotlib/sphinxext/plot_directive.py::split_code_at_show`  (score=0.0)  \
  
- `lib/matplotlib/sphinxext/plot_directive.py::_split_code_at_show`  (score=0.0)  \
  
- `lib/mpl_toolkits/axes_grid1/mpl_axes.py::SimpleAxisArtist.set_visible`  (score=0.0)  \
  

**next_to_explore:** `['matplotlib.axes._base._AxesBase.set_visible', 'mpl_toolkits.mplot3d.axes3d.Axes3D.draw', 'mpl_toolkits.mplot3d.axes3d.Axes3D.__init__', 'mpl_toolkits.mplot3d.axes3d.Axes3D.set_visible']`

### Abductive step #2 (iteration=6)

- leading: 1, considering: 0, rejected: 1

**Per-candidate deliberation traces**

#### ✗ REJECTED — `lib/matplotlib/artist.py::Artist.set_visible`

- **Q1 Role.** This is a generic method on the base `Artist` class to set the visibility state of any artist object.
- **Q2 Connection to symptom.** The user code calls `ax1.set_visible(False)`. Since `Axes3D` inherits from `Artist`, this method is called, setting the internal `_visible` flag to `False` and marking the artist as `stale`. The symptom (the axes remaining visible) occurs because the drawing code for `Axes3D` later fails to check this `_visible` flag. Therefore, this function works correctly, but its effect is ignored elsewhere.
- **Q3 Counterfactual.** `no` — Modifying this function would not fix the bug, as it correctly sets the visibility state. The problem lies in the consumer of this state (`Axes3D.draw`), which does not check it.
- **Q4 Alternatives considered.**
  - `mpl_toolkits.mplot3d.axes3d.py::Axes3D.draw` — Preferred, as this is where the visibility flag set by `set_visible` should be checked before any drawing occurs.
  - `matplotlib.axes._base._AxesBase.draw` — Considered, as it's the superclass implementation which likely contains the correct visibility check that `Axes3D.draw` is missing.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function correctly sets the `_visible` attribute; the bug is caused by other code failing to read this attribute.

#### ✓ LEADING — `lib/mpl_toolkits/mplot3d/axes3d.py::Axes3D.draw`

- **Q1 Role.** This method handles the complete drawing process for a 3D axes, including its background, panes, grid lines, and all child artists.
- **Q2 Connection to symptom.** An execution path directly produces the symptom. When the figure is rendered via `plt.show()`, this `draw` method is called on the `Axes3D` instance. The code proceeds to draw the background patch (`self.patch.draw(renderer)`) and axes panes without first checking if the axes object itself is visible (i.e., `if not self.get_visible(): return`). This omission is the direct cause of the invisible axes being drawn.
- **Q3 Counterfactual.** `yes` — Adding a check `if not self.get_visible(): return` at the beginning of this function would cause it to do nothing for an invisible axes, fixing the bug.
- **Q4 Alternatives considered.**
  - `matplotlib.artist.py::Artist.set_visible` — Not preferred, as that function correctly sets the state that this `draw` method incorrectly ignores.
  - `matplotlib.axes._base._AxesBase.draw` — This is the 2D equivalent method, which correctly performs the visibility check. The bug exists because `Axes3D.draw` overrides it but fails to replicate this specific check.
  - `matplotlib.figure.py::Figure.draw` — This is the caller, but by convention, visibility checks are the responsibility of the artist's own `draw` method, not the caller.
- **Q5 Verdict.** `leading` (confidence: `high`) — This method lacks the standard visibility check at its entry point, which directly explains why `set_visible(False)` is ignored for 3D axes.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `lib/mpl_toolkits/mplot3d/axes3d.py::Axes3D.draw` | high | This method lacks the standard visibility check at its entry point, which directly explains why `set_visible(False)` is ignored for 3D axes. | Add `if not self.get_visible(): return` at the beginning of the method, similar to `_AxesBase.draw`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `lib/matplotlib/artist.py::Artist.set_visible` | high | This function correctly sets the `_visible` attribute; the bug is caused by other code failing to read this attribute. |  |

**Causal chains (per candidate)**

- `lib/matplotlib/artist.py::Artist.set_visible`  (score=2.0)  \
  User calls `ax1.set_visible(False)`. → `Artist.set_visible` is invoked on the `Axes3D` object. → The instance's `_visible` attribute is set to `False`. → The symptom is that this state change has no effect on the final rendered output, which is a failure in a different part of the code.
- `lib/mpl_toolkits/mplot3d/axes3d.py::Axes3D.draw`  (score=10.0)  \
  User calls `plt.show()`, which triggers the draw pipeline. → The figure calls `draw` on its children, including the `Axes3D` instance `ax1`. → `Axes3D.draw` is executed. → The method does not check `self.get_visible()` at the beginning. → It proceeds to call `self.patch.draw(renderer)` and draw other components. → The supposedly invisible axes is rendered on the canvas, producing the bug.

**next_to_explore:** `['lib/matplotlib/axes/_base.py::_AxesBase.draw', 'lib/matplotlib/figure.py::Figure.draw', 'lib/mpl_toolkits/mplot3d/axes3d.py::Axes3D.__init__', 'lib/matplotlib/axes/_base.py::_AxesBase.set_visible']`

### Abductive step #3 (iteration=12)

- leading: 0, considering: 0, rejected: 4

**Per-candidate deliberation traces**

#### ✗ REJECTED — `lib/matplotlib/axes/_base.py::_AxesBase.draw`

- **Q1 Role.** This is the base class method for drawing an Axes object and all its children artists onto the canvas.
- **Q2 Connection to symptom.** This function contains the correct logic to prevent drawing if an axes is not visible, with the check `if not self.get_visible(): return` at the very beginning. However, the `Axes3D` class provides its own `draw` method, which overrides this one. Therefore, for a 3D projection, this code path is likely not executed, and if the overriding method in `Axes3D` omits this visibility check, the symptom would occur.
- **Q3 Counterfactual.** `no` — Modifying this function would have no effect because it is not called for `Axes3D` instances; the specialized `Axes3D.draw` method is called instead.
- **Q4 Alternatives considered.**
  - `mpl_toolkits.mplot3d.axes3d.py::Axes3D.draw` — Preferred hypothesis: This override is the likely location of the missing visibility check.
  - `matplotlib.artist.py::Artist.set_visible` — Less likely, as this is a fundamental method; a bug here would have broader impact.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function has the correct logic, but it is overridden by `Axes3D.draw` and thus not on the execution path for the bug.

#### ✗ REJECTED — `lib/mpl_toolkits/mplot3d/axes3d.py::Axes3D.__init__`

- **Q1 Role.** This is the constructor for a 3D axes, responsible for initializing 3D-specific properties like viewing angles and projection type.
- **Q2 Connection to symptom.** No path. This function is called during the creation of the subplot, long before `set_visible(False)` is called and the figure is drawn. It does not set or interact with the visibility state, which is handled by the `Artist` base class.
- **Q3 Counterfactual.** `no` — The bug lies in the drawing logic failing to respect the visibility flag, not in the initial state set by the constructor.
- **Q4 Alternatives considered.**
  - `mpl_toolkits.mplot3d.axes3d.py::Axes3D.draw` — The drawing method is the most plausible place for the error.
  - `matplotlib.figure.py::Figure.draw` — The figure's draw method calls the axes' draw method, so the fault is likely in the latter.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for initialization and is not involved in the drawing process where the visibility check fails.

#### ✗ REJECTED — `lib/matplotlib/figure.py::Figure.draw`

- **Q1 Role.** This function orchestrates the drawing of the entire figure, including its background and all contained axes.
- **Q2 Connection to symptom.** This function is on the execution path, as it is responsible for calling the `draw` method of each axes. It checks its own visibility but correctly delegates the responsibility of checking axes-level visibility to the `axes.draw()` method. If the called `axes.draw()` method (in this case, `Axes3D.draw`) is faulty and doesn't check for visibility, this function will unknowingly draw an invisible axes, leading to the symptom.
- **Q3 Counterfactual.** `no` — This function correctly follows the object-oriented design by delegating to the axes' draw method. The bug is in the delegate (`Axes3D.draw`), not the caller.
- **Q4 Alternatives considered.**
  - `mpl_toolkits.mplot3d.axes3d.py::Axes3D.draw` — Preferred hypothesis: This is the delegate method that fails to perform the visibility check.
  - `matplotlib.axes._base.py::_AxesBase.draw` — This is the base class method that `Axes3D.draw` overrides, likely incorrectly.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function correctly delegates drawing to the axes; the fault lies in the axes's own `draw` method.

#### ✗ REJECTED — `lib/matplotlib/figure.py::FigureBase.set_frameon`

- **Q1 Role.** This function sets the visibility of the figure's background patch.
- **Q2 Connection to symptom.** No path. This function controls the visibility of the figure's background, not the visibility of a subplot/axes within the figure. The user code calls `ax.set_visible()`, which is an entirely different method affecting a different object.
- **Q3 Counterfactual.** `no` — This function is unrelated to `Axes` visibility and modifying it would have no effect on the symptom.
- **Q4 Alternatives considered.**
  - `matplotlib.artist.py::Artist.set_visible` — This is the method the user calls, but the problem is likely in how that state is used, not set.
  - `mpl_toolkits.mplot3d.axes3d.py::Axes3D.draw` — This is the most likely place where the visibility state is ignored.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is irrelevant as it controls the figure's frame, not an axes' visibility.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `lib/matplotlib/axes/_base.py::_AxesBase.draw` | high | This function has the correct logic, but it is overridden by `Axes3D.draw` and thus not on the execution path for the bug. |  |
| `lib/mpl_toolkits/mplot3d/axes3d.py::Axes3D.__init__` | high | This function is for initialization and is not involved in the drawing process where the visibility check fails. |  |
| `lib/matplotlib/figure.py::Figure.draw` | high | This function correctly delegates drawing to the axes; the fault lies in the axes's own `draw` method. |  |
| `lib/matplotlib/figure.py::FigureBase.set_frameon` | high | This function is irrelevant as it controls the figure's frame, not an axes' visibility. |  |

**Causal chains (per candidate)**

- `lib/matplotlib/axes/_base.py::_AxesBase.draw`  (score=0.0)  \
  
- `lib/mpl_toolkits/mplot3d/axes3d.py::Axes3D.__init__`  (score=0.0)  \
  
- `lib/matplotlib/figure.py::Figure.draw`  (score=0.0)  \
  
- `lib/matplotlib/figure.py::FigureBase.set_frameon`  (score=0.0)  \
  

**next_to_explore:** `['lib/mpl_toolkits/mplot3d/axes3d.py::Axes3D.draw']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `lib/mpl_toolkits/mplot3d/axes3d.py::Axes3D.draw` | 0.95 |
| 2 | `lib/matplotlib/artist.py::Artist.set_visible` | 0.1 |
| 3 | `lib/matplotlib/axes/_base.py::_AxesBase.draw` | 0.0 |
| 4 | `lib/matplotlib/figure.py::Figure.draw` | 0.0 |
| 5 | `lib/mpl_toolkits/axes_grid1/mpl_axes.py::SimpleAxisArtist.set_visible` | 0.0 |
| 6 | `lib/matplotlib/figure.py::FigureBase.set_frameon` | 0.0 |
| 7 | `lib/mpl_toolkits/mplot3d/axes3d.py::Axes3D.__init__` | 0.0 |
| 8 | `lib/matplotlib/artist.py::Artist.get_visible` | 0.0 |
| 9 | `lib/matplotlib/figure.py::SubFigure.set_dpi` | 0.0 |
| 10 | `lib/matplotlib/gridspec.py::GridSpec.update` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `lib/mpl_toolkits/mplot3d/axes3d.py::Axes3D.draw` | 0.950 | high | 1/1 | (389, 444) |
| 2 | `lib/matplotlib/gridspec.py::SubplotSpec.get_gridspec` | 0.278 | high | 1/1 | (626, 627) |
| 3 | `lib/matplotlib/figure.py::FigureBase._process_projection_requirements` | 0.276 | high | 1/1 | (1558, 1594) |
| 4 | `lib/matplotlib/artist.py::_stale_axes_callback` | 0.251 | high | 1/1 | (81, 83) |
| 5 | `lib/matplotlib/gridspec.py::SubplotSpec.subgridspec` | 0.251 | high | 1/1 | (707, 747) |
| 6 | `lib/matplotlib/figure.py::FigureBase.add_subplot` | 0.248 | high | 1/1 | (624, 751) |
| 7 | `lib/matplotlib/sphinxext/plot_directive.py::split_code_at_show` | 0.216 | high | 1/1 | (331, 333) |
| 8 | `lib/matplotlib/sphinxext/plot_directive.py::_split_code_at_show` | 0.200 | high | 1/1 | (336, 351) |
| 9 | `lib/matplotlib/artist.py::_get_tightbbox_for_layout_only` | 0.184 | high | 1/1 | (1358, 1367) |
| 10 | `lib/matplotlib/artist.py::Artist.set_visible` | 0.100 | high | 1/1 | (1008, 1018) |
