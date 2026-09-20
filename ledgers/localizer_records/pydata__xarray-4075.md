# Instance: `pydata__xarray-4075`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
[bug] when passing boolean weights to weighted mean
<!-- A short summary of the issue, if appropriate -->


#### MCVE Code Sample
<!-- In order for the maintainers to efficiently understand and prioritize issues, we ask you post a "Minimal, Complete and Verifiable Example" (MCVE): http://matthewrocklin.com/blog/work/2018/02/28/minimal-bug-reports -->

```python
import numpy as np
import xarray as xr

dta = xr.DataArray([1., 1., 1.])
wgt = xr.DataArray(np.array([1, 1, 0], dtype=np.bool))

dta.weighted(wgt).mean()
```
Returns 

```
<xarray.DataArray ()>
array(2.)
```

#### Expected Output
```
<xarray.DataArray ()>
array(1.)
```

#### Problem Description
Passing a boolean array as weights to the weighted mean returns the wrong result because the `weights` are not properly normalized (in this case). Internally the `sum_of_weights` is calculated as

```python
xr.dot(dta.notnull(), wgt)
```
i.e. the dot product of two boolean arrays. This yields:
```
<xarray.DataArray ()>
array(True)
```

We'll need to convert it to int or float:
```python
xr.dot(dta.notnull(), wgt * 1)
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['wrong result', 'weights are not properly normalized']`
- named APIs: `['xr.DataArray.weighted', 'xr.DataArray.mean', 'xr.dot', 'xr.DataArray.notnull']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `xarray/core/computation.py` | Deals with applying functions and ufuncs, including weighted operations. |
| 2 | `xarray/core/weighted.py` | Implements the weighted mean calculation and related operations. |
| 3 | `xarray/core/duck_array_ops.py` | Contains array operations, including mean, that need to handle boolean weights correctly. |
| 4 | `xarray/tests/test_computation.py` | Tests for apply_ufunc, which is used in weighted operations. |
| 5 | `xarray/tests/test_weighted.py` | Tests the weighted mean and sum operations. |
| 6 | `xarray/core/common.py` | Defines the weighted method used by DataArray and Dataset. |
| 7 | `xarray/core/dataarray.py` | Defines the DataArray.weighted method. |
| 8 | `xarray/core/dataset.py` | Defines the Dataset.weighted method. |
| 9 | `xarray/tests/test_duck_array_ops.py` | Tests for array operations, including mean. |
| 10 | `xarray/conventions.py` | May need changes related to data type handling during encoding/decoding. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✓ LEADING — `xarray/core/weighted.py::Weighted._weighted_mean`

- **Q1 Role.** This internal method computes the weighted mean by dividing the weighted sum by the sum of weights.
- **Q2 Connection to symptom.** Yes, this function directly produces the incorrect output. It calls `_sum_of_weights`, which incorrectly returns a boolean `True` when weights are boolean. This function then performs the division `weighted_sum / sum_of_weights`, which evaluates to `2.0 / True` and results in `2.0`, the wrong answer.
- **Q3 Counterfactual.** `yes` — Modifying this function to cast the `sum_of_weights` variable to a numeric type before the division would correct the calculation and make the symptom go away.
- **Q4 Alternatives considered.**
  - `xarray/core/weighted.py::Weighted._sum_of_weights` — This is the root cause, as it returns a boolean. It's a better place to fix, but not in the provided list.
  - `xarray/core/computation.py::dot` — The underlying function whose behavior with boolean arrays causes the issue, but changing it would be too broad.
  - `xarray/core/weighted.py::Weighted.mean` — This is just a public-facing wrapper and contains no calculation logic.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function performs the final, erroneous division using the incorrect boolean sum of weights, and a fix here is both possible and effective.

#### ✗ REJECTED — `xarray/core/weighted.py::Weighted.mean`

- **Q1 Role.** This is the public API method that users call to compute a weighted mean, dispatching the actual computation to an internal implementation.
- **Q2 Connection to symptom.** Yes, an execution path exists. The user calls this function, which in turn calls `_weighted_mean`. `_weighted_mean` returns the incorrect value, and this function passes that incorrect value back to the user. However, it does not perform the faulty calculation itself.
- **Q3 Counterfactual.** `no` — This function is a dispatcher. The faulty logic resides in the callee, `_weighted_mean`. Modifying this function alone would not fix the problem without reimplementing the logic from the callee.
- **Q4 Alternatives considered.**
  - `xarray/core/weighted.py::Weighted._weighted_mean` — Preferred, as it contains the actual calculation logic that leads to the incorrect result.
  - `xarray/core/weighted.py::Weighted._sum_of_weights` — The root cause of the issue is here, making it a much better target for a fix.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a wrapper that correctly dispatches to the implementation; it does not contain the faulty logic.

#### ✗ REJECTED — `xarray/core/weighted.py::Weighted._weighted_sum`

- **Q1 Role.** This internal method computes the weighted sum of a DataArray, which serves as the numerator in a weighted mean calculation.
- **Q2 Connection to symptom.** No path exists. This function calculates the numerator of the weighted mean. In the provided example, the weighted sum is `(1*1 + 1*1 + 1*0) = 2`, which is correct. The final incorrect result of `2.0` is due to an incorrect denominator (`1.0`), not the numerator.
- **Q3 Counterfactual.** `no` — The bug is caused by an incorrect `sum_of_weights` (the denominator), not the `weighted_sum` (the numerator) that this function calculates.
- **Q4 Alternatives considered.**
  - `xarray/core/weighted.py::Weighted._weighted_mean` — Preferred, as it combines the numerator and the faulty denominator.
  - `xarray/core/weighted.py::Weighted._sum_of_weights` — Preferred, as it is responsible for calculating the faulty denominator.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function correctly calculates the numerator for the weighted mean; the error occurs elsewhere.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `xarray/core/weighted.py::Weighted._weighted_mean` | high | This function performs the final, erroneous division using the incorrect boolean sum of weights, and a fix here is both possible and effective. | Cast `sum_of_weights` to a numeric type before division, e.g., `return weighted_sum / sum_of_weights.astype(float)`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `xarray/core/weighted.py::Weighted.mean` | high | This function is a wrapper that correctly dispatches to the implementation; it does not contain the faulty logic. |  |
| `xarray/core/weighted.py::Weighted._weighted_sum` | high | This function correctly calculates the numerator for the weighted mean; the error occurs elsewhere. |  |

**Causal chains (per candidate)**

- `xarray/core/weighted.py::Weighted._weighted_mean`  (score=9.0)  \
  User calls `dta.weighted(wgt).mean()`. → `Weighted.mean` calls `_weighted_mean`. → `_weighted_mean` calls `_sum_of_weights` to get the denominator. → `_sum_of_weights` computes `xr.dot(da.notnull(), weights)` where both arguments are boolean arrays. → `xr.dot` returns a boolean scalar `True`. → `_weighted_mean` receives `sum_of_weights = True`.
- `xarray/core/weighted.py::Weighted.mean`  (score=3.0)  \
  User calls `dta.weighted(wgt).mean()`. → This function calls `_weighted_mean`, which performs the faulty calculation. → `_weighted_mean` returns the incorrect value `2.0`. → This function returns the incorrect value `2.0` to the user.
- `xarray/core/weighted.py::Weighted._weighted_sum`  (score=0.0)  \
  `_weighted_mean` calls `_weighted_sum` to get the numerator. → `_weighted_sum` correctly calculates and returns `2.0`. → This correct value is later used in a faulty division in `_weighted_mean`.

**next_to_explore:** `['xarray/core/weighted.py::Weighted._sum_of_weights', 'xarray/core/computation.py::dot']`

### Abductive step #2 (iteration=9)

- leading: 1, considering: 2, rejected: 2

**Per-candidate deliberation traces**

#### … CONSIDERING — `xarray/core/weighted.py::Weighted._sum_of_weights`

- **Q1 Role.** This function calculates the sum of weights, accounting for missing values in the data array by masking them.
- **Q2 Connection to symptom.** Yes. This function is called to get the `sum_of_weights` for the mean calculation. It creates a boolean `mask` from the data's non-null values and passes it along with the boolean `weights` array to `self._reduce`. This pair of boolean arrays is what triggers the incorrect behavior in the underlying `xr.dot` call, leading to `sum_of_weights` being `True` (which becomes 1.0) instead of `2`.
- **Q3 Counterfactual.** `yes` — If this function cast the boolean `self.weights` to an integer type before calling `_reduce`, the dot product would become numerical, yielding the correct sum of `2` and thus the correct final mean.
- **Q4 Alternatives considered.**
  - `xarray/core/weighted.py::Weighted._reduce` — Preferred, as `_reduce` is where the incorrect optimization `(da * weights).sum() -> dot(da, weights)` is implemented; fixing it there is more fundamental.
  - `xarray/core/computation.py::dot` — Also a strong candidate, as it's the ultimate source of the incorrect boolean arithmetic, but modifying it could have wider, unintended consequences.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function directly sets up the condition for the bug (passing two boolean arrays to _reduce), and a fix here is viable, but the logical error is in a lower-level function.

#### … CONSIDERING — `xarray/core/computation.py::dot`

- **Q1 Role.** This function provides a generalized dot product for xarray objects, analogous to `numpy.einsum`.
- **Q2 Connection to symptom.** Yes, this is the function that, according to the bug report, performs the incorrect computation. When called with two boolean arrays by `_reduce`, it is said to return a single boolean `True` instead of the numerical sum of products (`2`), which directly causes the final result to be wrong.
- **Q3 Counterfactual.** `yes` — If `dot` were modified to treat boolean dtypes as numbers (0 and 1) and perform a numerical sum, it would return `2`, fixing the symptom at its root.
- **Q4 Alternatives considered.**
  - `xarray/core/weighted.py::Weighted._reduce` — Preferred, as `_reduce`'s documented contract is violated. Fixing it there is a more localized and safer change than altering the general-purpose `dot` function.
  - `xarray/core/weighted.py::Weighted._sum_of_weights` — A possible but less ideal location for a fix, as it would be patching the inputs to `_reduce` rather than fixing the faulty component.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function is reported to be the source of the incorrect value, but its code is not visible, and changing its core behavior might be risky.

#### ✗ REJECTED — `xarray/core/weighted.py::Weighted.sum_of_weights`

- **Q1 Role.** This is a public API method that wraps the internal `_sum_of_weights` calculation, handling attribute preservation.
- **Q2 Connection to symptom.** No path. This function is a simple wrapper around `_implementation` and `_sum_of_weights`. It does not contain any computational logic that contributes to the bug.
- **Q3 Counterfactual.** `no` — Modifying this wrapper would not fix the underlying calculation error in `_sum_of_weights` and its callees.
- **Q4 Alternatives considered.**
  - `xarray/core/weighted.py::Weighted._sum_of_weights` — This is the function being wrapped and contains the actual logic, making it a much better candidate.
  - `xarray/core/weighted.py::DataArrayWeighted._implementation` — This is another wrapper in the call stack, also not relevant to the bug's logic.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a high-level wrapper and is not involved in the faulty calculation.

#### ✗ REJECTED — `xarray/core/weighted.py::DataArrayWeighted._implementation`

- **Q1 Role.** This function is a helper that executes a given function on the `DataArray` object and handles attribute preservation.
- **Q2 Connection to symptom.** No path. This is a generic wrapper function that calls the function passed to it (in this case, `_sum_of_weights`). It has no knowledge of the computation being performed and does not influence the numerical result.
- **Q3 Counterfactual.** `no` — This function is a generic helper; modifying it would not fix the specific issue with boolean weights and would likely break other functionalities.
- **Q4 Alternatives considered.**
  - `xarray/core/weighted.py::Weighted._sum_of_weights` — This is the function passed as an argument to `_implementation` and is where the relevant logic resides.
  - `xarray/core/weighted.py::Weighted.sum_of_weights` — The caller of this function, also a wrapper.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a generic implementation helper and is not part of the causal chain for the bug's logic.

#### ✓ LEADING — `xarray/core/weighted.py::Weighted._reduce`

- **Q1 Role.** This function provides a reduction operation using `xr.dot`, intended as an efficient equivalent to `(da * weights).sum(dim, skipna)`.
- **Q2 Connection to symptom.** Yes, this function has a direct causal link. It is called by `_sum_of_weights` with two boolean arrays. It then calls `xr.dot` on these arrays, which incorrectly returns a boolean. The function's documented equivalence to `(da * weights).sum()` does not hold for boolean dtypes, which is the core of the issue.
- **Q3 Counterfactual.** `yes` — If this function checked for boolean `da` and `weights` and cast one to an integer before calling `dot`, it would enforce numerical calculation, correct the result from `dot`, and fix the symptom.
- **Q4 Alternatives considered.**
  - `xarray/core/weighted.py::Weighted._sum_of_weights` — Could fix the issue by preparing arguments, but the fault lies in `_reduce`'s broken optimization.
  - `xarray/core/computation.py::dot` — This is where the wrong value is produced, but `_reduce` is the function that violates its own contract by using `dot` improperly.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function's optimization via `dot` is faulty for boolean dtypes, breaking its documented contract and directly causing the bug.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `xarray/core/weighted.py::Weighted._reduce` | high | This function's optimization via `dot` is faulty for boolean dtypes, breaking its documented contract and directly causing the bug. | Before calling `dot`, check if both `da` and `weights` have boolean dtypes, and if so, cast `weights` to an integer dtype. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `xarray/core/weighted.py::Weighted._sum_of_weights` | high | This function directly sets up the condition for the bug (passing two boolean arrays to _reduce), and a fix here is viable, but the logical error is in a lower-level function. | Before calling `_reduce`, cast `self.weights` to an integer type if its dtype is boolean. |
| `xarray/core/computation.py::dot` | medium | This function is reported to be the source of the incorrect value, but its code is not visible, and changing its core behavior might be risky. | When operating on two boolean arrays, ensure the result is a numerical sum rather than a logical reduction. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `xarray/core/weighted.py::Weighted.sum_of_weights` | high | This function is a high-level wrapper and is not involved in the faulty calculation. |  |
| `xarray/core/weighted.py::DataArrayWeighted._implementation` | high | This is a generic implementation helper and is not part of the causal chain for the bug's logic. |  |

**Causal chains (per candidate)**

- `xarray/core/weighted.py::Weighted._sum_of_weights`  (score=8.0)  \
  Weighted.mean calls this function (via public API wrappers) to get the denominator for the weighted average. → It creates a boolean `mask` array. → It calls `_reduce` with the boolean `mask` and the user-provided boolean `weights`. → This call to `_reduce` returns an incorrect boolean value `True` instead of the integer `2`. → This incorrect value is returned and used in the final division, causing the wrong result.
- `xarray/core/computation.py::dot`  (score=8.0)  \
  This function is called by `_reduce` with two boolean arrays. → As described in the bug report, it performs a logical-like operation and returns a single boolean `True`. → This incorrect value is the direct source of the miscalculation for `sum_of_weights`. → The incorrect `sum_of_weights` propagates up to `mean`, causing the wrong final result.
- `xarray/core/weighted.py::Weighted.sum_of_weights`  (score=0.0)  \
  
- `xarray/core/weighted.py::DataArrayWeighted._implementation`  (score=0.0)  \
  
- `xarray/core/weighted.py::Weighted._reduce`  (score=10.0)  \
  This function is called by `_sum_of_weights` with two boolean arrays (`mask`, `weights`). → Its purpose is to compute `(da * weights).sum()`, but it uses `dot(da, weights)` as an optimization. → This optimization is incorrect for two boolean arrays, as `dot` returns a boolean `True` while `(da * weights).sum()` would correctly return `2`. → The function thus breaks its contract and returns the wrong value to `_sum_of_weights`. → This incorrect value causes the final weighted mean to be miscalculated.

**next_to_explore:** `['xarray/core/weighted.py::Weighted._weighted_sum', 'xarray/core/weighted.py::Weighted.mean', 'xarray/core/weighted.py::Weighted._weighted_mean']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `xarray/core/computation.py::dot` | 0.95 |
| 2 | `xarray/core/weighted.py::Weighted._reduce` | 0.9 |
| 3 | `xarray/core/weighted.py::Weighted._sum_of_weights` | 0.85 |
| 4 | `xarray/core/weighted.py::Weighted._weighted_mean` | 0.7 |
| 5 | `xarray/core/weighted.py::Weighted.mean` | 0.2 |
| 6 | `xarray/core/weighted.py::Weighted._weighted_sum` | 0.1 |
| 7 | `xarray/core/weighted.py::Weighted.__repr__` | 0.0 |
| 8 | `xarray/core/weighted.py::DataArrayWeighted._implementation` | 0.0 |
| 9 | `xarray/core/weighted.py::Weighted.sum` | 0.0 |
| 10 | `xarray/core/weighted.py::Weighted.__init__` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `xarray/core/computation.py::dot` | 0.950 | high | 1/1 | (1072, 1215) |
| 2 | `xarray/core/weighted.py::Weighted._reduce` | 0.900 | high | 1/1 | (113, 135) |
| 3 | `xarray/core/weighted.py::Weighted._sum_of_weights` | 0.850 | high | 1/1 | (137, 150) |
| 4 | `xarray/core/weighted.py::Weighted._weighted_mean` | 0.700 | high | 1/1 | (162, 174) |
| 5 | `xarray/core/common.py::DataWithCoords.weighted` | 0.252 | high | 1/1 | (766, 783) |
| 6 | `xarray/core/weighted.py::Weighted.sum_of_weights` | 0.252 | high | 1/1 | (180, 188) |
| 7 | `xarray/core/weighted.py::Weighted.mean` | 0.200 | high | 1/1 | (201, 210) |
| 8 | `xarray/core/computation.py::apply_dataarray_vfunc` | 0.188 | high | 1/1 | (213, 244) |
| 9 | `xarray/core/computation.py::apply_ufunc` | 0.164 | high | 1/1 | (759, 1069) |
| 10 | `xarray/core/common.py::DataWithCoords.rolling_exp` | 0.156 | high | 1/1 | (865, 903) |
