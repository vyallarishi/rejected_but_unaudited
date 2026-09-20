# Instance: `pytest-dev__pytest-10081`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
unittest.TestCase.tearDown executed for classes marked with `unittest.skip` when running --pdb
<!--
Thanks for submitting an issue!

Quick check-list while reporting bugs:
-->

- [x] a detailed description of the bug or problem you are having
- [x] output of `pip list` from the virtual environment you are using
- [x] pytest and operating system versions
- [x] minimal example if possible

Running `pytest --pdb` will run the `tearDown()` of `unittest.TestCase` classes that are decorated with `unittest.skip` on the class level.

Identical to #7215 , but with the `skip()` on the class level rather than on the function level.

Minimal test (adapted from #7215), `test_repro_skip_class.py`:
```python
import unittest

@unittest.skip("hello")
class MyTestCase(unittest.TestCase):
    def setUp(self):
        xxx
    def test_one(self):
        pass
    def tearDown(self):
        xxx
```
Some versions (full below):
```
$ python --version
Python 3.10.5
$ pytest --version
pytest 7.1.2
$ cat /etc/issue
Ubuntu 20.04.4 LTS \n \l
```
Test is properly skipped normally:
```
$ pytest test_repro_skip_class.py
===================================== test session st
```

## Stage 3 — Symptoms extracted

- exception types: `['NameError']`
- error messages: `["name 'xxx' is not defined"]`
- behaviors: `['tearDown executed for skipped classes', 'test teardown executed unexpectedly', 'pdb triggers teardown execution']`
- named APIs: `['unittest.skip', 'unittest.TestCase.setUp', 'unittest.TestCase.tearDown']`
- stack frames: `[{'file': 'test_repro_skip_class.py', 'func': 'tearDown', 'line': 10}]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `src/_pytest/runner.py` | Contains the runtestprotocol function which executes the setup, call, and teardown phases of a test item, and needs to be modified to prevent teardown execution |
| 2 | `src/_pytest/unittest.py` | Handles unittest.TestCase classes, and needs to be modified to prevent tearDown execution for skipped classes when running with --pdb. |
| 3 | `src/_pytest/debugging.py` | Deals with pdb interaction, and needs to be modified to handle skipped tests correctly when pdb is enabled. |
| 4 | `testing/test_unittest.py` | Tests related to unittest integration, and needs to be updated to test the fix for the issue. |
| 5 | `testing/test_debugging.py` | Tests related to pdb integration, and needs to be updated to test the fix for the issue. |
| 6 | `src/_pytest/skipping.py` | May need changes to ensure skip marks are handled correctly during pdb sessions. |
| 7 | `src/_pytest/config/__init__.py` | May need changes to configure pdb behavior. |
| 8 | `src/_pytest/hookspec.py` | May need changes to define new hooks for pdb interaction. |
| 9 | `src/_pytest/hookimpl.py` | May need changes to implement new hooks for pdb interaction. |
| 10 | `testing/test_skipping.py` | Tests related to skipping, and needs to be updated to test the fix for the issue. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `src/_pytest/unittest.py::_is_skipped`

- **Q1 Role.** This function is a helper that checks if a given object has been marked with the `__unittest_skip__` attribute, which is how `unittest` signals a skipped test.
- **Q2 Connection to symptom.** No path. The symptom is that a test's `tearDown` method is run despite the test being skipped. The test output `sE` indicates that the test was correctly identified as skipped (`s`) before an error occurred in teardown (`E`). This implies that this function is working correctly to detect the skip, but the calling logic fails to prevent the teardown from running.
- **Q3 Counterfactual.** `no` — The test is already correctly identified as skipped. The bug is in the execution logic that follows, not in the detection of the skip itself.
- **Q4 Alternatives considered.**
  - `_pytest.unittest.py::TestCaseFunction.setup` — Preferred, as it's likely where the decision to schedule teardown is incorrectly made.
  - `_pytest.runner.py::runtestprotocol` — Considered, as it orchestrates setup/call/teardown, but the bug is specific to unittest handling.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function correctly detects skips; the bug lies in the caller's handling of a detected skip, not in the detection itself.

#### ✗ REJECTED — `src/_pytest/debugging.py::pytestPDB._get_pdb_wrapper_class`

- **Q1 Role.** This class method dynamically creates a wrapper around a PDB (Python Debugger) class to integrate it with pytest's systems like I/O capture and hooks.
- **Q2 Connection to symptom.** No path. The symptom (running `tearDown` for a skipped test) occurs only with `--pdb`, which activates the debugging plugin. However, this specific function only defines the behavior of the interactive PDB session itself. The decision to run `tearDown` is made by the test execution protocol *before* the debugger is ever entered. Therefore, this function is irrelevant to the cause of the symptom.
- **Q3 Counterfactual.** `no` — Modifying the PDB wrapper would not change the test execution logic that incorrectly decides to run the teardown for a skipped test.
- **Q4 Alternatives considered.**
  - `_pytest.debugging.py::pytest_runtest_protocol` — Preferred, as this hook is the entry point for the debugging plugin's influence on test execution.
  - `_pytest.unittest.py::pytest_runtest_protocol` — Preferred, as the interaction between the debugging and unittest plugins' protocols is likely where the bug originates.
- **Q5 Verdict.** `rejected` (confidence: `medium`) — This function defines the debugger's interactive behavior, but the bug stems from the test protocol logic that runs before any debugging session starts.

#### ✓ LEADING — `src/_pytest/unittest.py::TestCaseFunction.teardown`

- **Q1 Role.** This function is the teardown method for a pytest item representing a `unittest` test case, responsible for executing the user-defined `tearDown` method.
- **Q2 Connection to symptom.** This function is the direct cause of the observed `NameError`. The `pytest` runner calls this function as part of the test protocol. Inside this function, it calls `self._explicit_tearDown()`, which is a reference to the user's `tearDown` method. Because `TestCaseFunction.setup` incorrectly ran for the skipped test class, `_explicit_tearDown` was set, leading this function to execute the user's `tearDown` and trigger the error.
- **Q3 Counterfactual.** `yes` — If this function were modified to check if the test's parent class was skipped before calling `_explicit_tearDown`, the user's `tearDown` method would not be executed, and the `NameError` would be avoided.
- **Q4 Alternatives considered.**
  - `_pytest.unittest.py::TestCaseFunction.setup` — Preferred as the root cause; it incorrectly sets `_explicit_tearDown` for a skipped class.
  - `_pytest.unittest.py::pytest_runtest_protocol` — Preferred as a higher-level fix; its logic for `--pdb` leads to using a buggy execution path.
- **Q5 Verdict.** `leading` (confidence: `medium`) — This function directly executes the code that raises the error, and modifying it would fix the symptom, although the root cause is upstream.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `src/_pytest/unittest.py::TestCaseFunction.teardown` | medium | This function directly executes the code that raises the error, and modifying it would fix the symptom, although the root cause is upstream. | Add a check, like `if _is_skipped(self.parent.obj): return`, to prevent execution for class-skipped tests, though the ideal fix is in `TestCaseFunction.setup`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `src/_pytest/unittest.py::_is_skipped` | high | This function correctly detects skips; the bug lies in the caller's handling of a detected skip, not in the detection itself. |  |
| `src/_pytest/debugging.py::pytestPDB._get_pdb_wrapper_class` | medium | This function defines the debugger's interactive behavior, but the bug stems from the test protocol logic that runs before any debugging session starts. |  |

**Causal chains (per candidate)**

- `src/_pytest/unittest.py::_is_skipped`  (score=0.0)  \
  
- `src/_pytest/debugging.py::pytestPDB._get_pdb_wrapper_class`  (score=0.0)  \
  
- `src/_pytest/unittest.py::TestCaseFunction.teardown`  (score=9.0)  \
  When run with `--pdb`, the `unittest` plugin's `pytest_runtest_protocol` cedes control to the default pytest runner. → The default runner calls `item.setup()`, which is `TestCaseFunction.setup`. → `TestCaseFunction.setup` in this version fails to check for class-level skips and incorrectly runs `setUp` and, crucially, sets `self._explicit_tearDown`. → The runner then executes the 'call' phase, where `TestCaseFunction.runtest` correctly identifies the class skip and raises `pytest.skip.Exception`, resulting in a 'skipped' report (`s`). → The runner then proceeds to the 'teardown' phase, calling `TestCaseFunction.teardown`. → Because `self._explicit_tearDown` was set, this function calls the user's `tearDown` method.

**next_to_explore:** `['src/_pytest/unittest.py::TestCaseFunction.setup', 'src/_pytest/unittest.py::pytest_runtest_protocol', 'src/_pytest/runner.py::runtestprotocol', 'src/_pytest/debugging.py::pytest_runtest_protocol']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 1, rejected: 2

**Per-candidate deliberation traces**

#### … CONSIDERING — `src/_pytest/unittest.py::TestCaseFunction.setup`

- **Q1 Role.** This function initializes an instance of the `unittest.TestCase` subclass for a given test method before it runs.
- **Q2 Connection to symptom.** Yes, this function is plausibly on the causal path. For the `tearDown` method of the test class to be called, an instance of that class must exist. This `setup` function is responsible for creating that instance (`self._testcase = self.parent.obj(self.name)`). Even though the test is marked for skipping, this setup hook is still executed, creating the instance that is later incorrectly used during the teardown phase, which is triggered due to the `--pdb` flag's interaction with the test protocol.
- **Q3 Counterfactual.** `yes` — If this function were modified to check if the item is skipped and avoid creating the `_testcase` instance, the subsequent call to `tearDown` on that instance would not occur, thus eliminating the `NameError`.
- **Q4 Alternatives considered.**
  - `src/_pytest/unittest.py::TestCaseFunction.teardown` — Considered as the symmetric counterpart to setup, but its implementation appears safe and does not call the user's teardown method.
  - `src/_pytest/debugging.py` — The root cause is very likely within the debugging plugin, as the bug is specific to `--pdb`, but modifying this `setup` function is a direct way to prevent the symptom.
  - `src/_pytest/runner.py::runtestprotocol` — The logic that calls teardown even after a skipped setup could be at fault, but changing it might have broader consequences.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function creates the test instance which is a prerequisite for the bug; preventing instance creation for skipped tests would fix the symptom, though the root cause is likely elsewhere.

#### ✗ REJECTED — `src/_pytest/unittest.py::pytest_runtest_protocol`

- **Q1 Role.** This function is a hook implementation that patches `twisted.python.failure.Failure` to better integrate `twisted.trial.unittest` tests with pytest's reporting.
- **Q2 Connection to symptom.** No path exists. The function's logic is guarded by a check for `"twisted.trial.unittest" in sys.modules`. The provided environment does not include Twisted, so the `else: yield` path is taken, which simply passes control to the next hook and has no effect on test execution flow.
- **Q3 Counterfactual.** `no` — Modifying this function would have no effect as it is effectively a no-op for any test that is not using the `twisted.trial` framework.
- **Q4 Alternatives considered.**
  - `src/_pytest/runner.py::pytest_runtest_protocol` — This is the hook in the runner that orchestrates the entire test execution and is a much more likely place for relevant logic.
  - `src/_pytest/debugging.py::pytest_runtest_protocol` — The debugging plugin's implementation of this hook is a prime suspect for altering the test flow, given the bug is `--pdb` specific.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function's logic is specific to Twisted integration and is not executed in the provided test scenario.

#### ✗ REJECTED — `src/_pytest/warnings.py::pytest_runtest_protocol`

- **Q1 Role.** This function is a hook implementation that wraps the test execution in a context manager to catch and record any warnings issued during the test run.
- **Q2 Connection to symptom.** No path exists. This function acts as a simple wrapper around the test execution (`yield`) to capture warnings. It does not influence the decision to run or skip setup, call, or teardown phases of the test.
- **Q3 Counterfactual.** `no` — Modifying this function would only affect how warnings are handled and would not prevent the `tearDown` method from being called on a skipped test.
- **Q4 Alternatives considered.**
  - `src/_pytest/skipping.py::pytest_runtest_protocol` — The skipping plugin's hook is responsible for implementing the skip logic, which is what is being interfered with.
  - `src/_pytest/runner.py::runtestprotocol` — This function controls the sequence of setup, call, and teardown, making it central to the execution flow.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is only a wrapper for capturing warnings and has no control over the test execution flow.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `src/_pytest/unittest.py::TestCaseFunction.setup` | high | This function creates the test instance which is a prerequisite for the bug; preventing instance creation for skipped tests would fix the symptom, though the root cause is likely elsewhere. | Add a check at the beginning of the function to see if the item is marked as skipped, and if so, return early without creating the `_testcase` instance. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `src/_pytest/unittest.py::pytest_runtest_protocol` | high | This function's logic is specific to Twisted integration and is not executed in the provided test scenario. |  |
| `src/_pytest/warnings.py::pytest_runtest_protocol` | high | This function is only a wrapper for capturing warnings and has no control over the test execution flow. |  |

**Causal chains (per candidate)**

- `src/_pytest/unittest.py::TestCaseFunction.setup`  (score=6.0)  \
  A `unittest.TestCase` class is marked with `@unittest.skip`. → pytest's collector creates a `TestCaseFunction` item and marks it with `skipif`. → The `pytest_runtest_setup` hook from the `skipping` plugin raises a `pytest.skip` exception. → The `runner` catches this, reports the setup as skipped, and skips the `call` phase. → The `runner` proceeds to the `teardown` phase. → Due to the `--pdb` flag, a logic path is taken that incorrectly results in the user's `MyTestCase.tearDown` method being called.
- `src/_pytest/unittest.py::pytest_runtest_protocol`  (score=0.0)  \
  
- `src/_pytest/warnings.py::pytest_runtest_protocol`  (score=0.0)  \
  

**next_to_explore:** `['src/_pytest/runner.py::runtestprotocol', 'src/_pytest/debugging.py::pytest_exception_interact', 'src/_pytest/unittest.py::TestCaseFunction.teardown', 'src/_pytest/debugging.py::pytest_runtest_protocol', 'src/_pytest/skipping.py::pytest_runtest_setup']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `src/_pytest/unittest.py::TestCaseFunction.setup` | 0.9 |
| 2 | `src/_pytest/unittest.py::TestCaseFunction.teardown` | 0.85 |
| 3 | `src/_pytest/unittest.py::pytest_runtest_protocol` | 0.5 |
| 4 | `src/_pytest/unittest.py::_is_skipped` | 0.2 |
| 5 | `src/_pytest/debugging.py::pytestPDB._get_pdb_wrapper_class` | 0.1 |
| 6 | `src/_pytest/debugging.py::pytestPDB._import_pdb_cls` | 0.05 |
| 7 | `src/_pytest/debugging.py::pytestPDB._init_pdb` | 0.05 |
| 8 | `src/_pytest/debugging.py::pytestPDB.set_trace` | 0.05 |
| 9 | `src/_pytest/unittest.py::UnitTestCase._inject_setup_teardown_fixtures` | 0.02 |
| 10 | `src/_pytest/unittest.py::TestCaseFunction.stopTest` | 0.01 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `src/_pytest/unittest.py::TestCaseFunction.setup` | 0.900 | high | 1/1 | (197, 204) |
| 2 | `src/_pytest/unittest.py::TestCaseFunction.teardown` | 0.850 | high | 1/1 | (206, 211) |
| 3 | `src/_pytest/unittest.py::pytest_runtest_protocol` | 0.500 | high | 1/1 | (373, 399) |
| 4 | `src/_pytest/skipping.py::pytest_runtest_makereport` | 0.217 | high | 1/1 | (263, 287) |
| 5 | `src/_pytest/skipping.py::pytest_runtest_setup` | 0.206 | high | 1/1 | (235, 242) |
| 6 | `src/_pytest/skipping.py::pytest_runtest_call` | 0.204 | high | 1/1 | (246, 259) |
| 7 | `src/_pytest/unittest.py::TestCaseFunction.addSkip` | 0.201 | high | 1/1 | (264, 268) |
| 8 | `src/_pytest/unittest.py::_is_skipped` | 0.200 | high | 1/1 | (412, 414) |
| 9 | `src/_pytest/warnings.py::pytest_runtest_protocol` | 0.173 | high | 1/1 | (105, 109) |
| 10 | `src/_pytest/debugging.py::pytestPDB._get_pdb_wrapper_class` | 0.100 | high | 1/1 | (151, 235) |
