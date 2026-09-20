# Instance: `scikit-learn__scikit-learn-12585`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
clone fails for parameters that are estimator types
#### Description

`clone` fails when one or more instance parameters are estimator types (i.e. not instances, but classes). 

I know this is a somewhat unusual use case, but I'm working on a project that provides wrappers for sklearn estimators (https://github.com/phausamann/sklearn-xarray) and I'd like to store the wrapped estimators as their classes - not their instances - as a parameter inside of a wrapper that behaves like an estimator itself. 

#### Steps/Code to Reproduce

    from sklearn.preprocessing import StandardScaler
    from sklearn.base import clone
    clone(StandardScaler(with_mean=StandardScaler))

#### Expected Results

No error.

#### Actual Results
```
Traceback (most recent call last):
...
  File "...\lib\site-packages\sklearn\base.py", line 62, in clone
    new_object_params[name] = clone(param, safe=False)
  File "...\lib\site-packages\sklearn\base.py", line 60, in clone
    new_object_params = estimator.get_params(deep=False)
TypeError: get_params() missing 1 required positional argument: 'self'
```

#### Possible fix

Change `base.py`, line 51 to: 

    elif not hasattr(est
```

## Stage 3 — Symptoms extracted

- exception types: `['TypeError']`
- error messages: `["get_params() missing 1 required positional argument: 'self'"]`
- behaviors: `['clone fails', 'parameter is estimator type']`
- named APIs: `['sklearn.preprocessing.StandardScaler', 'sklearn.base.clone', 'estimator.get_params']`
- stack frames: `[{'file': '...\\lib\\site-packages\\sklearn\\base.py', 'func': 'clone', 'line': 62}, {'file': '...\\lib\\site-packages\\sklearn\\base.py', 'func': 'clone', 'line': 60}]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `sklearn/base.py` | The issue is a TypeError in `clone` due to `get_params` being called on a class, and the proposed fix is in `base.py`. |
| 2 | `sklearn/utils/fixes.py` | Related to fixes in the utils package. |
| 3 | `sklearn/base.py` | The issue is a TypeError in `clone` due to `get_params` being called on a class, and the proposed fix is in `base.py`. |
| 4 | `sklearn/utils/fixes.py` | Related to fixes in the utils package. |
| 5 | `sklearn/utils/__init__.py` | Related to utilities. |
| 6 | `sklearn/utils/validation.py` | Related to validation. |
| 7 | `sklearn/linear_model/base.py` | Base class for linear models, which are estimator types. |
| 8 | `sklearn/svm/base.py` | Base class for SVM models, which are estimator types. |
| 9 | `sklearn/tree/base.py` | Base class for tree models, which are estimator types. |
| 10 | `sklearn/ensemble/base.py` | Base class for ensemble models, which are estimator types. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `sklearn/base.py::BaseEstimator.get_params`

- **Q1 Role.** This instance method retrieves the parameters of an estimator as a dictionary.
- **Q2 Connection to symptom.** No path. The symptom is a `TypeError` that occurs when this function is *called* on a class instead of an instance, meaning the call site is incorrect. The body of this function is never executed, as the error happens during the attempt to bind the `self` argument.
- **Q3 Counterfactual.** `no` — The function's signature `def get_params(self, ...)` is correct for an instance method. The fault lies with the caller (`clone`) which attempts to call it without an instance.
- **Q4 Alternatives considered.**
  - `sklearn.base.py::clone` — Preferred, as it is the function that makes the incorrect call to `get_params`.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is the subject of the erroneous call from `clone`, but it is not the source of the error.

#### ✓ LEADING — `sklearn/base.py::clone`

- **Q1 Role.** This function constructs a new, unfitted estimator by deep-copying the parameters of an existing estimator.
- **Q2 Connection to symptom.** Yes, a direct path exists. 
1. `clone` is called on an estimator whose parameter (`with_mean`) is a class (`StandardScaler`).
2. `clone` iterates through parameters and calls itself recursively on the class: `clone(StandardScaler, safe=False)`.
3. In the recursive call, `hasattr(StandardScaler, 'get_params')` evaluates to `True` because `get_params` is a method on the class.
4. The code then incorrectly assumes `StandardScaler` is an estimator instance and attempts to call `StandardScaler.get_params()`, which fails with a `TypeError` because the `self` argument is missing.
- **Q3 Counterfactual.** `yes` — Adding a check like `isinstance(estimator, type)` would allow the function to identify class objects and treat them as simple values to be copied, rather than estimators to be cloned, preventing the erroneous call.
- **Q4 Alternatives considered.**
  - `sklearn.base.py::BaseEstimator.get_params` — Not preferred; `get_params` is behaving correctly as an instance method, the error is in how it's called.
  - `StandardScaler.__init__` — Not preferred; this function correctly allows a class to be passed as a parameter. The issue is not in object creation, but in cloning.
- **Q5 Verdict.** `leading` (confidence: `high`) — The function contains flawed logic that misidentifies a class as an estimator instance, leading directly to the TypeError; a local fix here resolves the issue.

#### ✗ REJECTED — `sklearn/utils/sparsefuncs.py::_raise_typeerror`

- **Q1 Role.** This is a helper function that raises a TypeError if an input is not a CSR or CSC sparse matrix.
- **Q2 Connection to symptom.** No path. The observed symptom is a `TypeError` related to a missing `self` argument in `get_params`. This function raises a completely different `TypeError` with a different message ("Expected a CSR or CSC sparse matrix...") and is not in the call stack.
- **Q3 Counterfactual.** `no` — This function is entirely unrelated to the execution path of the bug, so modifying it would have no effect.
- **Q4 Alternatives considered.**
  - `sklearn.base.py::clone` — Preferred, as it is the clear source of the bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is functionally and contextually unrelated to the observed bug.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sklearn/base.py::clone` | high | The function contains flawed logic that misidentifies a class as an estimator instance, leading directly to the TypeError; a local fix here resolves the issue. | In the condition that checks for non-estimators, add a check for `isinstance(estimator, type)` to prevent trying to clone class objects. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sklearn/base.py::BaseEstimator.get_params` | high | This function is the subject of the erroneous call from `clone`, but it is not the source of the error. |  |
| `sklearn/utils/sparsefuncs.py::_raise_typeerror` | high | This function is functionally and contextually unrelated to the observed bug. |  |

**Causal chains (per candidate)**

- `sklearn/base.py::BaseEstimator.get_params`  (score=0.0)  \
  The `clone` function calls `StandardScaler.get_params`. → This is an instance method, but it is called on the class itself. → Python's method binding mechanism fails, raising a `TypeError` before the function body is ever entered.
- `sklearn/base.py::clone`  (score=10.0)  \
  A `StandardScaler` instance is created with one of its parameters, `with_mean`, set to the `StandardScaler` class. → The top-level `clone` call gets the parameters, including `('with_mean', <class 'StandardScaler'>)`. → A recursive call `clone(<class 'StandardScaler'>, safe=False)` is made. → Inside this call, `hasattr(<class 'StandardScaler'>, 'get_params')` is `True`. → The function incorrectly proceeds as if it has an estimator instance. → The line `new_object_params = estimator.get_params(deep=False)` is executed, which is `StandardScaler.get_params(deep=False)`.
- `sklearn/utils/sparsefuncs.py::_raise_typeerror`  (score=0.0)  \
  

### Abductive step #2 (iteration=6)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `sklearn/base.py::BaseEstimator._get_param_names`

- **Q1 Role.** This class method introspects an estimator's `__init__` method to retrieve its parameter names.
- **Q2 Connection to symptom.** No path exists. This function is called by `BaseEstimator.get_params`. The traceback shows that the call to `get_params` itself fails with a `TypeError` because it's an instance method being called on a class (`StandardScaler`). The body of `get_params` is never entered, and therefore `_get_param_names` is never called.
- **Q3 Counterfactual.** `no` — Modifying this function would have no effect because it is not on the execution path that leads to the error.
- **Q4 Alternatives considered.**
  - `sklearn.base.clone` — Preferred, as it is the function making the incorrect call to `get_params` on a class type.
  - `sklearn.base.BaseEstimator.get_params` — Considered, as it's the method being called, but the fault lies with the caller's logic, not the method signature.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is not on the causal path; the error occurs before it can be called.

#### ✗ REJECTED — `sklearn/base.py::BaseEstimator.set_params`

- **Q1 Role.** This method sets the parameters of an estimator instance, including for nested objects.
- **Q2 Connection to symptom.** No path exists. The `clone` function fails while trying to get the parameters of the object to be cloned. Parameter setting on the new object would happen after successfully getting the parameters. Since the getting step fails, the execution path that would call `set_params` (or equivalent `__init__` logic) is never reached.
- **Q3 Counterfactual.** `no` — Modifying this function would not fix the symptom, as the error occurs before this function is ever called in the `clone` process.
- **Q4 Alternatives considered.**
  - `sklearn.base.clone` — Preferred, as this is where the logic for handling different parameter types resides and where the error-inducing call is made.
  - `sklearn.base.BaseEstimator.get_params` — Considered, but the issue is not with `get_params` itself but how it's being called by `clone`.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is related to setting parameters, while the error occurs during the process of getting them; it is not on the causal path.

#### ✗ REJECTED — `sklearn/pipeline.py::Pipeline.get_params`

- **Q1 Role.** This method gets the parameters for a `Pipeline` estimator and its contained sub-objects.
- **Q2 Connection to symptom.** No path exists. The code example that reproduces the bug involves `sklearn.preprocessing.StandardScaler`, not `sklearn.pipeline.Pipeline`. Therefore, this specific implementation of `get_params` is never called.
- **Q3 Counterfactual.** `no` — Modifying the `get_params` method for `Pipeline` would not affect the behavior of `clone` when used with a `StandardScaler` instance.
- **Q4 Alternatives considered.**
  - `sklearn.base.BaseEstimator.get_params` — This is the relevant `get_params` implementation (via inheritance) for `StandardScaler`, not the one for `Pipeline`.
  - `sklearn.base.clone` — Preferred, as it is the function that calls `get_params` and is agnostic to the specific estimator type.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is specific to the `Pipeline` class, which is not used in the code that demonstrates the bug.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sklearn/base.py::BaseEstimator._get_param_names` | high | This function is not on the causal path; the error occurs before it can be called. |  |
| `sklearn/base.py::BaseEstimator.set_params` | high | This function is related to setting parameters, while the error occurs during the process of getting them; it is not on the causal path. |  |
| `sklearn/pipeline.py::Pipeline.get_params` | high | This function is specific to the `Pipeline` class, which is not used in the code that demonstrates the bug. |  |

**Causal chains (per candidate)**

- `sklearn/base.py::BaseEstimator._get_param_names`  (score=0.0)  \
  A recursive call to `clone` is made with an estimator class (`StandardScaler`) as its argument. → `clone` attempts to call `get_params` on this class: `StandardScaler.get_params()`. → This call raises a `TypeError` because `get_params` is an instance method that requires a `self` argument. → `_get_param_names` is called from within `get_params`, so it is never reached.
- `sklearn/base.py::BaseEstimator.set_params`  (score=0.0)  \
  `clone` is called on an estimator whose parameter is a class. → A recursive `clone` call on the class parameter fails when trying to get its parameters via `get_params`. → `set_params` is used to configure a new object after its parameters have been determined from the old one. → Since the parameter-getting step fails, the logic for setting parameters on a new object is never reached.
- `sklearn/pipeline.py::Pipeline.get_params`  (score=0.0)  \
  The user's code calls `clone` on a `StandardScaler` instance. → The `get_params` method relevant to the failure is the one inherited by `StandardScaler` from `BaseEstimator`. → `Pipeline.get_params` is a method specific to the `Pipeline` class. → As no `Pipeline` object is involved, this function is not on the execution path.

**next_to_explore:** `['sklearn.base.clone', 'copy.deepcopy', 'sklearn.base.BaseEstimator.get_params', 'sklearn.preprocessing.StandardScaler.__init__']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `sklearn/base.py::clone` | 1.0 |
| 2 | `sklearn/base.py::BaseEstimator.get_params` | 0.8 |
| 3 | `sklearn/base.py::BaseEstimator._get_param_names` | 0.1 |
| 4 | `sklearn/base.py::BaseEstimator.set_params` | 0.1 |
| 5 | `sklearn/pipeline.py::Pipeline.get_params` | 0.0 |
| 6 | `sklearn/base.py::BaseEstimator.__setstate__` | 0.0 |
| 7 | `sklearn/base.py::BaseEstimator.__repr__` | 0.0 |
| 8 | `sklearn/base.py::BaseEstimator.__getstate__` | 0.0 |
| 9 | `sklearn/ensemble/base.py::_set_random_states` | 0.0 |
| 10 | `sklearn/ensemble/base.py::BaseEnsemble.__len__` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `sklearn/base.py::clone` | 1.000 | high | 1/1 | (30, 74) |
| 2 | `sklearn/base.py::BaseEstimator.get_params` | 0.800 | high | 1/1 | (166, 187) |
| 3 | `sklearn/ensemble/base.py::BaseEnsemble._make_estimator` | 0.227 | high | 1/1 | (120, 136) |
| 4 | `sklearn/utils/sparsefuncs.py::_raise_typeerror` | 0.227 | high | 1/1 | (15, 19) |
| 5 | `sklearn/base.py::BaseEstimator._get_param_names` | 0.100 | high | 1/1 | (140, 164) |
| 6 | `sklearn/base.py::BaseEstimator.set_params` | 0.100 | high | 1/1 | (189, 224) |
| 7 | `sklearn/utils/fixes.py::parallel_helper` | 0.086 | high | 1/1 | (203, 214) |
| 8 | `sklearn/utils/fixes.py::_joblib_parallel_args` | 0.067 | high | 1/1 | (334, 379) |
| 9 | `sklearn/pipeline.py::Pipeline.get_params` | 0.000 | high | 1/1 | (123, 137) |
| 10 | `sklearn/base.py::BaseEstimator.__setstate__` | 0.000 | high | 1/1 | (242, 255) |
