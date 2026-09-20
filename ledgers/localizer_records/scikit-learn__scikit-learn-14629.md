# Instance: `scikit-learn__scikit-learn-14629`

- runs: 1   termination: `ledger_informed`   think-high calls: 3

## Issue (truncated to 1200 chars)

```
AttributeError with cross_val_predict(method='predict_proba') when using MultiOuputClassifier
#### Description
I believe there is a bug when using `cross_val_predict(method='predict_proba')` with a `MultiOutputClassifer`. 

I think the problem is in the use of `estimator.classes_` here:
https://github.com/scikit-learn/scikit-learn/blob/3be7110d2650bbe78eda673001a7adeba62575b0/sklearn/model_selection/_validation.py#L857-L866

To obtain the `classes_` attribute of a `MultiOutputClassifier`, you need `mo_clf.estimators_[i].classes_` instead.

If core team members have any idea of how to address this, I am happy to submit a patch. 

#### Steps/Code to Reproduce

```python
from sklearn.datasets import make_multilabel_classification
from sklearn.multioutput import MultiOutputClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import cross_val_predict

X, Y = make_multilabel_classification()

mo_lda = MultiOutputClassifier(LinearDiscriminantAnalysis())
pred = cross_val_predict(mo_lda, X, Y, cv=5) # Works fine
pred_proba =  cross_val_predict(mo_lda, X, Y, cv=5, method='predict_proba') # Returns error

```
```

## Stage 3 — Symptoms extracted

- exception types: `['AttributeError']`
- error messages: `["'MultiOutputClassifier' object has no attribute 'classes_'"]`
- behaviors: `['prediction probabilities', 'cross-validation prediction']`
- named APIs: `['MultiOutputClassifier', 'LinearDiscriminantAnalysis', 'cross_val_predict', 'make_multilabel_classification']`
- stack frames: `[{'file': 'sklearn/model_selection/_validation.py', 'func': '<unknown>', 'line': 857}, {'file': 'sklearn/model_selection/_validation.py', 'func': '<unknown>', 'line': 866}]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `sklearn/model_selection/_validation.py` | The error occurs in `cross_val_predict` which is implemented in this file. |
| 2 | `sklearn/multioutput.py` | The issue is specific to `MultiOutputClassifier`, so this file is relevant. |
| 3 | `sklearn/base.py` | The fix might involve modifying the base estimator class to handle the `classes_` attribute correctly. |
| 4 | `examples/model_selection/plot_cv_predict.py` | Example uses cross_val_predict, might need adjustment after the fix. |
| 5 | `sklearn/ensemble/_hist_gradient_boosting/gradient_boosting.py` | HistGradientBoostingClassifier also uses predict_proba and might be affected. |
| 6 | `sklearn/calibration.py` | CalibratedClassifierCV uses predict_proba and might be affected. |
| 7 | `sklearn/model_selection/_search.py` | GridSearchCV and RandomizedSearchCV use cross-validation and might be affected. |
| 8 | `sklearn/ensemble/voting.py` | VotingClassifier uses predict_proba and might be affected. |
| 9 | `sklearn/multiclass.py` | OneVsRestClassifier and other multiclass strategies might be affected. |
| 10 | `sklearn/linear_model/logistic.py` | LogisticRegression uses predict_proba and might be affected. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `sklearn/model_selection/tests/test_validation.py::check_cross_val_predict_with_method_multiclass`

- **Q1 Role.** This function is a test helper that checks `cross_val_predict` for various prediction methods on a given multiclass estimator.
- **Q2 Connection to symptom.** No path exists. This function tests `cross_val_predict` with single-output multiclass estimators (using the Iris dataset where `y` is 1D). The bug occurs in the code path for multi-output classification (where `y` is 2D), which is not executed by this test.
- **Q3 Counterfactual.** `no` — This is a test function. Modifying it cannot fix a bug in the `cross_val_predict` implementation itself.
- **Q4 Alternatives considered.**
  - `sklearn.model_selection._validation.cross_val_predict` — This is the implementation function where the error occurs and the fix is needed.
  - `sklearn.multioutput.MultiOutputClassifier` — This is the class that does not meet the interface expectations of `cross_val_predict`.
  - `A new test for MultiOutputClassifier with cross_val_predict` — Adding a failing test case would be the first step to fixing the bug, but that's different from fixing the bug itself.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a test for single-output multiclass problems and does not execute the multi-output code path where the bug occurs.

#### ✗ REJECTED — `sklearn/model_selection/tests/test_validation.py::check_cross_val_predict_multiclass`

- **Q1 Role.** This is a lower-level test helper that computes and verifies the expected output of `cross_val_predict` for a given method and multiclass estimator.
- **Q2 Connection to symptom.** No path exists. This function is specifically designed for single-output multiclass classification where the target `y` is 1-dimensional. The `AttributeError` is triggered by logic that handles multi-output targets (`y.ndim > 1`), so this function's execution path will never encounter the bug.
- **Q3 Counterfactual.** `no` — This is a test helper function; modifying it will not change the behavior of the library code it is testing.
- **Q4 Alternatives considered.**
  - `sklearn.model_selection._validation.cross_val_predict` — This is the function containing the faulty logic that needs to be fixed.
  - `sklearn.multioutput.MultiOutputClassifier` — The fix could involve changing this class to expose the expected attributes.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a test helper for single-output multiclass problems and is not involved in the multi-output code path where the bug lies.

#### ✗ REJECTED — `sklearn/model_selection/tests/test_validation.py::test_cross_val_predict_with_method_multilabel_ovr`

- **Q1 Role.** This function tests `cross_val_predict` with `OneVsRestClassifier` on a multilabel classification problem.
- **Q2 Connection to symptom.** No path exists. Although this function tests a multi-output scenario similar to the user's report, it uses `OneVsRestClassifier`. Unlike `MultiOutputClassifier`, `OneVsRestClassifier` has a `classes_` attribute. Therefore, it satisfies the assumption made by `cross_val_predict` and does not trigger the `AttributeError`, successfully avoiding the buggy code path.
- **Q3 Counterfactual.** `no` — This is a test function. Modifying it to use `MultiOutputClassifier` would reproduce the bug, but not fix it.
- **Q4 Alternatives considered.**
  - `sklearn.model_selection._validation.cross_val_predict` — Preferred, as it's the site of the error and where the logic needs to be more robust.
  - `sklearn.multioutput.MultiOutputClassifier` — A possible but less likely fix location; it would involve changing the estimator to fit `cross_val_predict`'s assumption.
  - `sklearn.multioutput.OneVsRestClassifier` — Not a candidate for a fix, but useful for comparison to understand why it works.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This test uses a multi-output classifier (`OneVsRestClassifier`) that has the `classes_` attribute, thus avoiding the bug.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sklearn/model_selection/tests/test_validation.py::check_cross_val_predict_with_method_multiclass` | high | This is a test for single-output multiclass problems and does not execute the multi-output code path where the bug occurs. |  |
| `sklearn/model_selection/tests/test_validation.py::check_cross_val_predict_multiclass` | high | This is a test helper for single-output multiclass problems and is not involved in the multi-output code path where the bug lies. |  |
| `sklearn/model_selection/tests/test_validation.py::test_cross_val_predict_with_method_multilabel_ovr` | high | This test uses a multi-output classifier (`OneVsRestClassifier`) that has the `classes_` attribute, thus avoiding the bug. |  |

**Causal chains (per candidate)**

- `sklearn/model_selection/tests/test_validation.py::check_cross_val_predict_with_method_multiclass`  (score=0.0)  \
  
- `sklearn/model_selection/tests/test_validation.py::check_cross_val_predict_multiclass`  (score=0.0)  \
  
- `sklearn/model_selection/tests/test_validation.py::test_cross_val_predict_with_method_multilabel_ovr`  (score=0.0)  \
  

**next_to_explore:** `['sklearn.model_selection._validation.cross_val_predict', 'sklearn.multioutput.MultiOutputClassifier', 'sklearn.multioutput.OneVsRestClassifier']`

### Abductive step #2 (iteration=6)

- leading: 1, considering: 0, rejected: 0

**Per-candidate deliberation traces**

#### ✓ LEADING — `sklearn/model_selection/_validation.py::cross_val_predict`

- **Q1 Role.** Generates cross-validated estimates for each input data point by fitting an estimator on training folds and predicting on the corresponding test fold.
- **Q2 Connection to symptom.** Yes, the path is direct. When `cross_val_predict` is called with `method='predict_proba'`, it enters a specific code path to handle probability predictions. According to the user's report and the provided code link, this path contains logic that unconditionally accesses `estimator.classes_`. When the `estimator` is a `MultiOutputClassifier`, which does not have a top-level `classes_` attribute, this access fails and raises the observed `AttributeError`.
- **Q3 Counterfactual.** `yes` — The `AttributeError` is raised directly within this function. Modifying the function to handle estimators without a top-level `classes_` attribute (e.g., by adding a `hasattr` check before the access) would prevent the crash.
- **Q4 Alternatives considered.**
  - `sklearn.multioutput.MultiOutputClassifier` — Considered that `MultiOutputClassifier` should expose a `classes_` attribute for interface consistency, but modifying `cross_val_predict` is a more direct and less disruptive fix for the bug.
  - `sklearn.base._is_classifier` — This function identifies `MultiOutputClassifier` as a classifier, which is correct. The fault lies in the subsequent assumption made by the caller, not in the type check itself.
- **Q5 Verdict.** `leading` (confidence: `high`) — The stack trace points directly to this function, and its internal logic makes an assumption (`estimator.classes_` exists) that is invalid for `MultiOutputClassifier`, directly causing the `AttributeError`.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sklearn/model_selection/_validation.py::cross_val_predict` | high | The stack trace points directly to this function, and its internal logic makes an assumption (`estimator.classes_` exists) that is invalid for `MultiOutputClassifier`, directly causing the `AttributeE | Guard the access to `estimator.classes_` with `hasattr(estimator, 'classes_')` to avoid the error for meta-estimators like `MultiOutputClassifier`. |

**Causal chains (per candidate)**

- `sklearn/model_selection/_validation.py::cross_val_predict`  (score=10.0)  \
  User calls `cross_val_predict` with a `MultiOutputClassifier` and `method='predict_proba'`. → The function identifies `method` as `'predict_proba'` and enters a conditional block. → Inside this block, the code attempts to access `estimator.classes_` to perform a check on the class labels. → The `estimator` object is an instance of `MultiOutputClassifier`, which does not have a `classes_` attribute at the top level. → The attribute access `estimator.classes_` fails, raising an `AttributeError`.

**next_to_explore:** `['sklearn.multioutput.MultiOutputClassifier', 'sklearn.model_selection._validation._fit_and_predict', 'sklearn.base._is_classifier']`

### Abductive step #3 (iteration=9)

- leading: 1, considering: 0, rejected: 1

**Per-candidate deliberation traces**

#### ✓ LEADING — `sklearn/model_selection/_validation.py::_fit_and_predict`

- **Q1 Role.** This function fits an estimator on a training split and generates predictions on a test split for a single fold of cross-validation.
- **Q2 Connection to symptom.** Yes, a direct path exists. 1. `cross_val_predict` calls `_fit_and_predict` with `method='predict_proba'` and a `MultiOutputClassifier` estimator. 2. Inside `_fit_and_predict`, `estimator.predict_proba(X_test)` is called, returning a list of probability arrays. 3. The code enters the `if method == 'predict_proba'` and `if isinstance(predictions, list)` blocks. 4. It then attempts to execute a list comprehension that accesses `estimator.classes_[i_label]`. 5. The `estimator` is a `MultiOutputClassifier` instance, which does not have a `classes_` attribute, leading to the `AttributeError` reported in the stack trace.
- **Q3 Counterfactual.** `yes` — Modifying this function to correctly access the classes for each output from `estimator.estimators_[i].classes_` when dealing with a `MultiOutputClassifier` would resolve the `AttributeError`.
- **Q4 Alternatives considered.**
  - `sklearn.model_selection._validation.py::cross_val_predict` — This is the public API and caller, but the faulty logic is not in this function, it's in the helper `_fit_and_predict`.
  - `sklearn.multioutput.MultiOutputClassifier` — The issue is not with this class's implementation, but how `_fit_and_predict` incorrectly assumes an interface (`.classes_`) that it doesn't provide.
  - `sklearn.model_selection._validation.py::_enforce_prediction_order` — The error occurs when preparing the arguments for this function call, not within the function itself.
- **Q5 Verdict.** `leading` (confidence: `high`) — The traceback points directly to this function, the logic path clearly explains the AttributeError, and a local modification would fix the issue.

#### ✗ REJECTED — `sklearn/model_selection/tests/test_validation.py::check_cross_val_predict_multilabel`

- **Q1 Role.** This is a helper function for testing `cross_val_predict` on multilabel classification problems, specifically for estimators that return predictions as a list of arrays.
- **Q2 Connection to symptom.** No path exists. This is a test function. It calls the buggy `cross_val_predict` function and would therefore fail, but it is not the cause of the bug in the library's application code.
- **Q3 Counterfactual.** `no` — Modifying this test function would not change the behavior of `cross_val_predict` for end-users; it would only change how the library is tested.
- **Q4 Alternatives considered.**
  - `sklearn/model_selection/_validation.py::_fit_and_predict` — This is the actual location of the bug, which this test function helps to expose.
  - `sklearn/model_selection/_validation.py::cross_val_predict` — This test calls `cross_val_predict`, which is the user-facing function that has the bug in its implementation.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a test function that reveals the bug but does not cause it; modifying it would not fix the user's issue.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sklearn/model_selection/_validation.py::_fit_and_predict` | high | The traceback points directly to this function, the logic path clearly explains the AttributeError, and a local modification would fix the issue. | Before accessing `estimator.classes_`, check if the estimator has an `estimators_` attribute. If so, use `estimator.estimators_[i_label].classes_` instead of `e |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sklearn/model_selection/tests/test_validation.py::check_cross_val_predict_multilabel` | high | This is a test function that reveals the bug but does not cause it; modifying it would not fix the user's issue. |  |

**Causal chains (per candidate)**

- `sklearn/model_selection/_validation.py::_fit_and_predict`  (score=10.0)  \
  `cross_val_predict` is called with `method='predict_proba'` and a `MultiOutputClassifier` estimator. → `cross_val_predict` invokes `_fit_and_predict` for each CV fold. → Inside `_fit_and_predict`, `estimator.predict_proba(X_test)` is called, which correctly returns a list of arrays. → The code path enters a block for `method='predict_proba'` and `isinstance(predictions, list)`. → A list comprehension attempts to access `estimator.classes_` to process the list of predictions. → The `estimator` (`MultiOutputClassifier`) has no `classes_` attribute, which raises the `AttributeError`.
- `sklearn/model_selection/tests/test_validation.py::check_cross_val_predict_multilabel`  (score=0.0)  \
  

**next_to_explore:** `['sklearn.multioutput.MultiOutputClassifier', 'sklearn.model_selection._validation.py::_enforce_prediction_order', 'sklearn.model_selection._validation.py::cross_val_predict', 'sklearn.base.is_classifier']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `sklearn/model_selection/_validation.py::cross_val_predict` | 1.0 |
| 2 | `sklearn/model_selection/_validation.py::_fit_and_predict` | 0.7 |
| 3 | `sklearn/multioutput.py::MultiOutputClassifier.predict_proba` | 0.4 |
| 4 | `sklearn/model_selection/tests/test_validation.py::test_cross_val_predict_with_method_multilabel_ovr` | 0.0 |
| 5 | `sklearn/model_selection/tests/test_validation.py::check_cross_val_predict_multilabel` | 0.0 |
| 6 | `sklearn/model_selection/tests/test_validation.py::check_cross_val_predict_multiclass` | 0.0 |
| 7 | `sklearn/model_selection/tests/test_validation.py::check_cross_val_predict_with_method_multiclass` | 0.0 |
| 8 | `sklearn/multiclass.py::OutputCodeClassifier.predict` | 0.0 |
| 9 | `sklearn/multioutput.py::MultiOutputClassifier.__init__` | 0.0 |
| 10 | `sklearn/multioutput.py::MultiOutputEstimator.predict` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `sklearn/model_selection/_validation.py::cross_val_predict` | 1.000 | high | 1/1 | (625, 798) |
| 2 | `sklearn/model_selection/_validation.py::_fit_and_predict` | 0.700 | high | 1/1 | (801, 867) |
| 3 | `sklearn/multiclass.py::OneVsRestClassifier.predict` | 0.406 | high | 1/1 | (275, 314) |
| 4 | `sklearn/multioutput.py::MultiOutputClassifier.predict_proba` | 0.400 | high | 1/1 | (328, 355) |
| 5 | `sklearn/multiclass.py::OneVsRestClassifier.predict_proba` | 0.397 | high | 1/1 | (317, 353) |
| 6 | `sklearn/model_selection/_validation.py::cross_val_score` | 0.313 | high | 1/1 | (254, 382) |
| 7 | `sklearn/model_selection/_validation.py::cross_validate` | 0.273 | high | 1/1 | (37, 251) |
| 8 | `sklearn/model_selection/_validation.py::_fit_and_score` | 0.252 | high | 1/1 | (385, 567) |
| 9 | `sklearn/model_selection/tests/test_validation.py::test_cross_val_predict_with_method_multilabel_ovr` | 0.000 | high | 1/1 | (1438, 1450) |
| 10 | `sklearn/model_selection/tests/test_validation.py::check_cross_val_predict_multilabel` | 0.000 | high | 1/1 | (1345, 1389) |
