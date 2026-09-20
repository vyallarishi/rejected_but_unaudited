# Instance: `pydata__xarray-6938`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
`.swap_dims()` can modify original object
### What happened?

This is kind of a convoluted example, but something I ran into. It appears that in certain cases `.swap_dims()` can modify the original object, here the `.dims` of a data variable that was swapped into being a dimension coordinate variable.

### What did you expect to happen?

I expected it not to modify the original object.

### Minimal Complete Verifiable Example

```Python
import numpy as np
import xarray as xr

nz = 11
ds = xr.Dataset(
    data_vars={
        "y": ("z", np.random.rand(nz)),
        "lev": ("z", np.arange(nz) * 10),
        # ^ We want this to be a dimension coordinate
    },
)
print(f"ds\n{ds}")
print(f"\nds, 'lev' -> dim coord\n{ds.swap_dims(z='lev')}")

ds2 = (
    ds.swap_dims(z="lev")
    .rename_dims(lev="z")
    .reset_index("lev")
    .reset_coords()
)
print(f"\nds2\n{ds2}")
# ^ This Dataset appears same as the original

print(f"\nds2, 'lev' -> dim coord\n{ds2.swap_dims(z='lev')}")
# ^ Produces a Dataset with dimension coordinate 'lev'
print(f"\nds2 after .swap_dims() applied\n{ds2}")
# ^ `ds2['lev']` now has dimension 'lev' although otherwise same
```
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['modifies original object', 'modifies .dims of a data variable', 'dimension coordinate variable modified']`
- named APIs: `['xr.Dataset', 'xr.Dataset.swap_dims', 'xr.Dataset.rename_dims', 'xr.Dataset.reset_index', 'xr.Dataset.reset_coords']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `xarray/core/dataset.py` | Likely location for `swap_dims` implementation and related logic. |
| 2 | `xarray/core/dataarray.py` | Likely location for `swap_dims` implementation and related logic. |
| 3 | `xarray/core/coordinates.py` | Related to dimension coordinate variables and their management. |
| 4 | `xarray/core/variable.py` | Deals with core data storage and manipulation, including dimensions. |
| 5 | `xarray/core/alignment.py` | Related to aligning and reindexing data, potentially involved in the bug. |
| 6 | `xarray/tests/test_dataset.py` | Tests for Dataset functionality, including `swap_dims`. |
| 7 | `xarray/tests/test_dataarray.py` | Tests for DataArray functionality, including `swap_dims`. |
| 8 | `xarray/core/concat.py` | May be involved if concatenation is related to the issue. |
| 9 | `xarray/core/merge.py` | May be involved if merging is related to the issue. |
| 10 | `xarray/core/indexing.py` | May be involved if indexing is related to the issue. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✓ LEADING — `xarray/core/dataset.py::Dataset.swap_dims`

- **Q1 Role.** Returns a new Dataset with swapped dimensions, promoting data variables to dimension coordinates if their name is used as a new dimension.
- **Q2 Connection to symptom.** Yes, a plausible execution path exists. The symptom is that the original `Dataset` object `ds2` is modified by `ds2.swap_dims(z='lev')`. Specifically, `ds2['lev'].dims` changes. This indicates a failure of immutability within `swap_dims`.
1. `swap_dims` is called with `dims_dict={'z': 'lev'}`.
2. The code iterates through the variables of `ds2`. When it processes the variable `lev`, `k='lev'` and `v` is the `Variable` object for `lev` with `dims=('z',)`. 
3. The calculated `new_dims` for this variable is `('lev',)`. 
4. The condition `if k in dims_dict.values() and new_dims != (k,)` evaluates to `True and False`, which is `False`.
5. The `else` block is executed: `var = v.copy(deep=False)`, followed by `var.dims = new_dims`. 
6. If `v.copy(deep=False)` returns `v` itself (the original `Variable` object) instead of a new shallow copy, then `var` becomes an alias for `v`.
7. Consequently, `var.dims = new_dims` would be equivalent to `v.dims = new_dims`, which modifies the `Variable` object within the original `ds2` dataset in-place, causing the observed symptom.
- **Q3 Counterfactual.** `yes` — If `swap_dims` were modified to guarantee that it does not mutate its input variables, the symptom would be eliminated. This would involve fixing the logic that causes the in-place modification, for example by ensuring a true copy is made before dimensions are changed.
- **Q4 Alternatives considered.**
  - `xarray.core.variable.Variable.copy` — This is a strong candidate for the root cause if it can return `self` on a shallow copy, but the primary misbehavior is in `swap_dims`'s logic, making it the better place to attribute the fault.
  - `xarray.core.dataset.py::Dataset.rename_dims` — Considered as part of the setup that could create a problematic state in `ds2`, but the bug manifests in `swap_dims`, making it the more direct cause.
  - `xarray.core.dataarray.py::DataArray.swap_dims` — Rejected because the minimal example uses a `Dataset`, not a `DataArray`, so this function is not on the execution path.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function is directly called and exhibits the mutation symptom, and a plausible (though subtle) path for in-place modification exists in its logic for promoting a variable to a coordinate.

#### ✗ REJECTED — `xarray/core/dataarray.py::DataArray.swap_dims`

- **Q1 Role.** This function returns a new DataArray with swapped dimensions by converting the DataArray to a temporary Dataset and calling `Dataset.swap_dims`.
- **Q2 Connection to symptom.** No path. The minimal reproducible example operates on an `xarray.Dataset` object, so `Dataset.swap_dims` is called directly, not this `DataArray` method.
- **Q3 Counterfactual.** `no` — Modifying this function would have no effect on the reported bug, as it is not executed in the provided example.
- **Q4 Alternatives considered.**
  - `xarray.core.dataset.py::Dataset.swap_dims` — This is the function that is actually called on the `Dataset` object and is the source of the bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is not on the execution path for the provided minimal example, which uses a Dataset.

#### ✗ REJECTED — `xarray/core/dataset.py::Dataset.rename_dims`

- **Q1 Role.** This function returns a new Dataset with renamed dimensions.
- **Q2 Connection to symptom.** No path. This function is used in the setup of the `ds2` object. While part of the sequence that leads to the bug, the bug itself (in-place modification) is triggered by a subsequent call to `swap_dims`. `rename_dims` itself does not cause the mutation.
- **Q3 Counterfactual.** `no` — The bug is in `swap_dims`. Modifying `rename_dims` would not fix the mutation that occurs within `swap_dims`.
- **Q4 Alternatives considered.**
  - `xarray.core.dataset.py::Dataset.swap_dims` — This is the function that is called after the setup and directly produces the symptom of in-place modification.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is part of the problem's setup but is not the function that performs the incorrect mutation; `swap_dims` is.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `xarray/core/dataset.py::Dataset.swap_dims` | high | This function is directly called and exhibits the mutation symptom, and a plausible (though subtle) path for in-place modification exists in its logic for promoting a variable to a coordinate. | The code path for promoting a variable to a dimension coordinate should not modify the variable in-place. Ensure a new `Variable` object is always created befor |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `xarray/core/dataarray.py::DataArray.swap_dims` | high | This function is not on the execution path for the provided minimal example, which uses a Dataset. |  |
| `xarray/core/dataset.py::Dataset.rename_dims` | high | This function is part of the problem's setup but is not the function that performs the incorrect mutation; `swap_dims` is. |  |

**Causal chains (per candidate)**

- `xarray/core/dataset.py::Dataset.swap_dims`  (score=8.0)  \
  In `Dataset.swap_dims`, the code iterates through variables to prepare for the new dataset. → For the variable `lev`, which is being promoted to a dimension coordinate, the code enters a branch to handle its transformation. → This branch attempts to create a shallow copy of the `lev` variable using `v.copy(deep=False)`. → Hypothesis: The copy operation fails to create a new object and instead returns the original `Variable` object `v`. → The next line, `var.dims = new_dims`, then modifies the `dims` attribute on the original `Variable` object from `ds2`. → This in-place modification violates xarray's immutability contract and is the direct cause of the observed symptom.
- `xarray/core/dataarray.py::DataArray.swap_dims`  (score=0.0)  \
  
- `xarray/core/dataset.py::Dataset.rename_dims`  (score=0.0)  \
  

**next_to_explore:** `['xarray/core/variable.py::Variable.copy', 'xarray/core/dataset.py::Dataset._replace_vars_and_dims', 'xarray/core/dataset.py::Dataset.__init__', 'xarray/core/dataset.py::Dataset.reset_index', 'xarray/core/dataset.py::Dataset.reset_coords']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 2, rejected: 1

**Per-candidate deliberation traces**

#### ✗ REJECTED — `xarray/core/dataset.py::Dataset._replace_vars_and_dims`

- **Q1 Role.** This is a deprecated helper function to create a new Dataset instance by replacing its variables, coordinate names, dimensions, and attributes.
- **Q2 Connection to symptom.** No plausible path. This function is likely called by `swap_dims` to construct the new dataset that `swap_dims` returns. The mutation of the original object (`ds2`) happens because `swap_dims` modifies a `Variable` object from `ds2` in-place. This modification occurs before `_replace_vars_and_dims` is ever called. Therefore, this function is downstream of the defect and does not cause the mutation.
- **Q3 Counterfactual.** `no` — The mutation of the original object's variable has already occurred within the caller (`swap_dims`) before this function is invoked. Modifying this function would not prevent that mutation.
- **Q4 Alternatives considered.**
  - `xarray/core/dataset.py::Dataset.swap_dims` — Preferred, as it is the function that directly performs the unexpected mutation.
  - `xarray/core/dataset.py::Dataset._replace` — Not preferred, as it is called by this function and is even further downstream from the mutation.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a factory helper called after the in-place mutation has already happened in its caller, `swap_dims`.

#### … CONSIDERING — `xarray/core/dataset.py::Dataset.reset_coords`

- **Q1 Role.** This function moves specified non-index coordinates to be data variables, returning a new Dataset.
- **Q2 Connection to symptom.** This function is the final step in the chain of operations that creates the `ds2` object. It calls `obj = self.copy()`, which, for `deep=False` (the default), creates a new `Dataset` that shares the same `Variable` objects as the input dataset. This sharing of `Variable` objects is what makes `ds2` vulnerable to the mutation caused by the bug in `swap_dims`. When `swap_dims` incorrectly modifies a `Variable` in-place, the change is visible on `ds2` because `ds2` holds a reference to that same `Variable` object.
- **Q3 Counterfactual.** `yes` — If this function were modified to perform a deep copy (e.g., `self.copy(deep=True)`), `ds2` would have its own copies of all `Variable` objects. The subsequent buggy `swap_dims` call would then mutate a temporary variable, not one inside `ds2`, and the symptom would disappear.
- **Q4 Alternatives considered.**
  - `xarray/core/dataset.py::Dataset.swap_dims` — Preferred as the root cause, since it performs the mutation. The setup functions only create the conditions for the bug to manifest.
  - `xarray/core/dataset.py::Dataset.reset_index` — Also a valid candidate for the same reason as `reset_coords`; it's another link in the chain that propagates shared variables.
  - `xarray/core/dataset.py::Dataset.copy` — This is the underlying function that implements the variable sharing, but changing its default behavior would be a major breaking change.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function contributes to the bug by creating an object with shared variables, which are then mutated by `swap_dims`. Fixing the sharing here would fix the symptom.

#### … CONSIDERING — `xarray/core/dataset.py::Dataset.reset_index`

- **Q1 Role.** This function resets one or more dimension indexes or multi-index levels, turning them into data variables or coordinates.
- **Q2 Connection to symptom.** This function is part of the chain creating `ds2`. Its implementation uses `new_vars = self._variables.copy()`, which creates a shallow copy of the variables dictionary, meaning the `Variable` objects themselves are shared with the input dataset. This sharing is propagated through the subsequent `.reset_coords()` call to the final `ds2` object, making it susceptible to the mutation bug in `swap_dims`.
- **Q3 Counterfactual.** `yes` — If this function were modified to deep copy the variables it places in the new dataset, the chain of sharing would be broken. The final `ds2` object would not share variables with intermediate objects, and the symptom would be eliminated.
- **Q4 Alternatives considered.**
  - `xarray/core/dataset.py::Dataset.swap_dims` — Preferred as the root cause, as it's the function that improperly mutates state.
  - `xarray/core/dataset.py::Dataset.reset_coords` — Also a valid candidate; it's the final step in the chain that solidifies the shared state in `ds2`.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function is part of the causal chain that creates an object with shared variables, which are then improperly mutated by `swap_dims`.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `xarray/core/dataset.py::Dataset.reset_coords` | medium | This function contributes to the bug by creating an object with shared variables, which are then mutated by `swap_dims`. Fixing the sharing here would fix the symptom. | In the first line, change `obj = self.copy()` to `obj = self.copy(deep=True)` to prevent sharing of `Variable` objects. |
| `xarray/core/dataset.py::Dataset.reset_index` | medium | This function is part of the causal chain that creates an object with shared variables, which are then improperly mutated by `swap_dims`. | Change `new_vars = self._variables.copy()` to a deep copy, e.g., `new_vars = {k: v.copy(deep=True) for k, v in self._variables.items()}`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `xarray/core/dataset.py::Dataset._replace_vars_and_dims` | high | This function is a factory helper called after the in-place mutation has already happened in its caller, `swap_dims`. |  |

**next_to_explore:** `['xarray/core/dataset.py::Dataset.swap_dims', 'xarray/core/dataset.py::Dataset.copy', 'xarray/core/variable.py::Variable.copy', 'xarray/core/dataset.py::Dataset._replace']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `xarray/core/dataset.py::Dataset.swap_dims` | 0.95 |
| 2 | `xarray/core/dataset.py::_replace_vars_and_dims` | 0.2 |
| 3 | `xarray/core/dataset.py::_replace_with_new_dims` | 0.15 |
| 4 | `xarray/core/dataarray.py::DataArray.swap_dims` | 0.1 |
| 5 | `xarray/core/dataset.py::Dataset.reset_index` | 0.05 |
| 6 | `xarray/core/dataset.py::Dataset.rename_dims` | 0.05 |
| 7 | `xarray/core/dataset.py::_rename_dims` | 0.02 |
| 8 | `xarray/core/coordinates.py::DatasetCoordinates.dims` | 0.01 |
| 9 | `xarray/core/coordinates.py::DataArrayCoordinates.dims` | 0.01 |
| 10 | `xarray/core/dataset.py::Dataset.drop_dims` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `xarray/core/dataset.py::Dataset.swap_dims` | 0.950 | high | 1/1 | (3688, 3790) |
| 2 | `xarray/core/dataset.py::Dataset._rename_dims` | 0.507 | high | 1/1 | (3520, 3521) |
| 3 | `xarray/core/dataset.py::Dataset._replace_with_new_dims` | 0.447 | high | 1/1 | (1017, 1029) |
| 4 | `xarray/core/dataset.py::Dataset._replace_vars_and_dims` | 0.415 | high | 1/1 | (1031, 1048) |
| 5 | `xarray/core/coordinates.py::DataArrayCoordinates.variables` | 0.316 | high | 1/1 | (398, 399) |
| 6 | `xarray/core/dataset.py::Dataset.reset_coords` | 0.297 | high | 1/1 | (1698, 1736) |
| 7 | `xarray/core/alignment.py::reindex` | 0.287 | high | 1/1 | (851, 887) |
| 8 | `xarray/core/alignment.py::reindex_variables` | 0.279 | high | 1/1 | (39, 91) |
| 9 | `xarray/core/alignment.py::Aligner.assert_unindexed_dim_sizes_equal` | 0.248 | high | 1/1 | (440, 455) |
| 10 | `xarray/core/dataarray.py::DataArray.swap_dims` | 0.100 | high | 1/1 | (2044, 2101) |
