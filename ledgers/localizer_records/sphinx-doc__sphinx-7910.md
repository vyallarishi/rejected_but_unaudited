# Instance: `sphinx-doc__sphinx-7910`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
Decorated __init__ doesn't show up in docs
Subject: Decorated __init__ won't be documented. I'm working on [tensorpack](github.com/ppwwyyxx/tensorpack)

### Problem
- I have `napoleon_include_init_with_doc = True`, so `__init__` will be documented. But if I decorate the `__init__` method, it will not show up in docs.
I decorate it with `functools.wraps`, so the decorated object still has the same `__doc__`.
I've found that the bug is due to this commit: https://github.com/sphinx-doc/sphinx/commit/bbfd0d058aecf85bd3b711a846c83e2fe00fa136
I've printed the relevant variables in that function:
```
qualname='DistributedTrainerReplicated.__init__'
name='__init__'
obj.__doc__ has contents
```
And the root cause of the issue is in this line of code:
```python
cls = obj.__globals__[cls_path]
```
Because `obj` now is not the method itself, but a decorated method, its `__globals__` does not contain the class anymore. This makes sphinx think it's not a method, i.e. `cls_is_owner=False`.


### Environment info
- OS: <Unix/Linux/Mac/Win/other with version>: ArchLinux
- Python version: 3.6
- Sphinx version:1.6.5
```

## Stage 3 — Symptoms extracted

- exception types: `['KeyError']`
- error messages: `['cls = obj.__globals__[cls_path]', 'cls_is_owner=False']`
- behaviors: `['decorated __init__ not documented', "decorated method's __globals__ does not contain the class"]`
- named APIs: `['functools.wraps']`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `sphinx/domains/python.py` | Handles Python object descriptions and signature parsing, including __init__. |
| 2 | `sphinx/ext/autodoc/__init__.py` | Core of autodoc, responsible for documenting objects including methods. |
| 3 | `sphinx/ext/napoleon/__init__.py` | Deals with docstring parsing, which is relevant to documenting __init__. |
| 4 | `sphinx/ext/autodoc/directive.py` | Handles autodoc directives, processing options for documenters. |
| 5 | `sphinx/ext/autodoc/importer.py` | Imports Python objects for documentation, potentially affected by decorators. |
| 6 | `sphinx/domains/__init__.py` | Base classes for domains, including object description directives. |
| 7 | `sphinx/directives/__init__.py` | Handles directives, including object descriptions. |
| 8 | `sphinx/pycode/parser.py` | Parses Python code to extract information, including signatures. |
| 9 | `sphinx/writers/html.py` | HTML writer, potentially needing changes to render decorated __init__. |
| 10 | `sphinx/writers/latex.py` | LaTeX writer, potentially needing changes to render decorated __init__. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 1, rejected: 1

**Per-candidate deliberation traces**

#### ✓ LEADING — `sphinx/ext/autodoc/__init__.py::InstanceAttributeDocumenter.add_content`

- **Q1 Role.** Overrides the parent method to explicitly prevent docstring extraction for objects documented as instance attributes.
- **Q2 Connection to symptom.** Upstream misclassification causes the decorated `__init__` to be handled by `InstanceAttributeDocumenter`. This function is then called, and it invokes its parent with `no_docstring=True`, which directly leads to the `__init__`'s docstring not being included in the documentation.
- **Q3 Counterfactual.** `yes` — Changing `no_docstring=True` to `no_docstring=False` in the call to `super().add_content` would cause the docstring to be processed and included, thus eliminating the symptom.
- **Q4 Alternatives considered.**
  - `sphinx.util.inspect.isdescriptor` — The root cause of the misclassification; fixing it is the correct but more distant solution.
  - `sphinx.ext.autodoc.Documenter.add_content` — Modifying the parent class is a less targeted and potentially riskier fix.
  - `sphinx.ext.autodoc.AutoDoc.get_documenter` — Fixing the documenter selection logic is another alternative, but also upstream of the immediate symptom gatekeeper.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function is the direct gatekeeper preventing the docstring from being processed due to an upstream misclassification, and a simple modification here would fix the symptom.

#### ✗ REJECTED — `sphinx/ext/autodoc/__init__.py::Documenter.get_doc`

- **Q1 Role.** This function decodes and returns the lines of the docstring for the object being documented.
- **Q2 Connection to symptom.** No path. In the failing scenario, this function is never called for the decorated `__init__` method because its caller (`Documenter.add_content`) is explicitly told to skip docstring processing.
- **Q3 Counterfactual.** `no` — Modifying a function that is not executed on the problematic code path cannot resolve the issue.
- **Q4 Alternatives considered.**
  - `sphinx.ext.autodoc.Documenter.add_content` — The caller that contains the logic to skip calling this function.
  - `sphinx.ext.autodoc.InstanceAttributeDocumenter.add_content` — The function that instructs the caller to skip this function.
  - `sphinx.util.inspect.isdescriptor` — The root cause of the entire incorrect execution path.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is not on the failing execution path, as it is skipped by its caller.

#### … CONSIDERING — `sphinx/ext/autodoc/__init__.py::Documenter.add_content`

- **Q1 Role.** This method adds documented content, including docstrings, to the output buffer for a given object.
- **Q2 Connection to symptom.** This function contains the conditional logic (`if not no_docstring:`) that skips calling `get_doc()` when `no_docstring` is `True`. Since the misclassified `__init__` results in this function being called with `no_docstring=True`, this logic is the direct reason the docstring is omitted.
- **Q3 Counterfactual.** `yes` — Removing or altering the `if not no_docstring:` check would cause `get_doc()` to be called, and the docstring would be added, fixing the symptom.
- **Q4 Alternatives considered.**
  - `sphinx.ext.autodoc.InstanceAttributeDocumenter.add_content` — This subclass method is what sets `no_docstring=True`, making it a more specific target for a fix.
  - `sphinx.util.inspect.isdescriptor` — This is the root cause of the misclassification that starts the whole problematic chain of events.
  - `sphinx.ext.autodoc.Documenter.get_doc` — This function is the one being skipped, so it's not the cause.
- **Q5 Verdict.** `considering` (confidence: `high`) — While a modification here would fix the symptom, it's a less targeted change than modifying the subclass that sets the problematic flag.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sphinx/ext/autodoc/__init__.py::InstanceAttributeDocumenter.add_content` | high | This function is the direct gatekeeper preventing the docstring from being processed due to an upstream misclassification, and a simple modification here would fix the symptom. | Change the call to `super().add_content` to pass `no_docstring=False`. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sphinx/ext/autodoc/__init__.py::Documenter.add_content` | high | While a modification here would fix the symptom, it's a less targeted change than modifying the subclass that sets the problematic flag. | Remove the `if not no_docstring:` guard around the `self.get_doc()` call. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sphinx/ext/autodoc/__init__.py::Documenter.get_doc` | high | This function is not on the failing execution path, as it is skipped by its caller. |  |

**Causal chains (per candidate)**

- `sphinx/ext/autodoc/__init__.py::InstanceAttributeDocumenter.add_content`  (score=8.0)  \
  An upstream inspection function (likely `sphinx.util.inspect.isdescriptor`) fails to identify the decorated `__init__` as a method, returning `False`. → The documenter factory (`AutoDoc.get_documenter`) misclassifies the object and selects `InstanceAttributeDocumenter`. → `InstanceAttributeDocumenter.add_content` is called. → This function calls `super().add_content(more_content, no_docstring=True)`. → The parent `Documenter.add_content` receives `no_docstring=True` and skips extracting the docstring. → The `__init__` method's docstring does not appear in the generated documentation.
- `sphinx/ext/autodoc/__init__.py::Documenter.get_doc`  (score=0.0)  \
  
- `sphinx/ext/autodoc/__init__.py::Documenter.add_content`  (score=7.0)  \
  An upstream inspection function misclassifies the decorated `__init__`. → `InstanceAttributeDocumenter` is chosen to document it. → `InstanceAttributeDocumenter.add_content` calls this function (`Documenter.add_content`) with `no_docstring=True`. → The `if not no_docstring:` condition in this function evaluates to false. → The call to `self.get_doc()` is skipped. → The docstring is not added to the documentation.

**next_to_explore:** `['sphinx.util.inspect.isdescriptor', 'sphinx.ext.autodoc.AutoDoc.get_documenter', 'sphinx.ext.autodoc.MethodDocumenter.can_document_member', 'sphinx.ext.autodoc.AttributeDocumenter.can_document_member']`

### Abductive step #2 (iteration=6)

- leading: 1, considering: 1, rejected: 1

**Per-candidate deliberation traces**

#### … CONSIDERING — `sphinx/ext/autosummary/__init__.py::get_documenter`

- **Q1 Role.** This function determines and returns the appropriate `autodoc.Documenter` class (e.g., `ModuleDocumenter`, `MethodDocumenter`) for a given Python object.
- **Q2 Connection to symptom.** This function selects the documenter class. The user's provided causal graph indicates that `InstanceAttributeDocumenter` is being used to process the `__init__` method. This is the wrong documenter. This function makes that incorrect selection, likely because `MethodDocumenter.can_document_member` returns `False` for the decorated `__init__`. This leads to the method being treated as a simple attribute, and its docstring not being included as configured.
- **Q3 Counterfactual.** `partially` — A modification here to forcefully select `MethodDocumenter` for decorated methods would fix the symptom. However, the root of the incorrect decision lies in the callee, `MethodDocumenter.can_document_member`, which is a better place for the fix.
- **Q4 Alternatives considered.**
  - `sphinx/ext/autodoc/__init__.py::MethodDocumenter.can_document_member` — Preferred, as it's the source of the logic that causes this function to make the wrong choice.
  - `sphinx/ext/autodoc/__init__.py::Documenter.filter_members` — Considered based on user's textual report, but this function is likely not reached if the wrong documenter is chosen first.
  - `The user's decorator implementation` — The decorator might be what causes `inspect.isroutine` to fail, but Sphinx should be robust to common decorator patterns.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function makes the incorrect choice of documenter, directly causing the issue, but the faulty logic it relies on is in `can_document_member`.

#### ✗ REJECTED — `sphinx/util/inspect.py::isdescriptor`

- **Q1 Role.** This function checks if a given object is a descriptor by seeing if it has a `__get__`, `__set__`, or `__delete__` method.
- **Q2 Connection to symptom.** No path. A wrapped function object is typically not a descriptor itself, so this function would correctly return `False`. While method-likeness is related to being a descriptor, the specific failure reported by the user (`__globals__` lookup) is unrelated to the logic in this function. The mis-documentation of `__init__` stems from incorrect documenter selection or ownership checks, not from this check.
- **Q3 Counterfactual.** `no` — The function is likely behaving correctly. Forcing it to return `True` for a non-descriptor would be an incorrect change and would not address the root cause of the bug in autodoc's logic.
- **Q4 Alternatives considered.**
  - `sphinx/ext/autodoc/__init__.py::MethodDocumenter.can_document_member` — This is a more likely place for the error, as it directly controls which documenter is chosen.
  - `sphinx/ext/autodoc/__init__.py::Documenter.filter_members` — The user's report of a `KeyError` points here, which is far more specific and plausible than an issue in `isdescriptor`.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function correctly identifies that a wrapped function is not a descriptor; the bug lies in how Sphinx handles such objects, not in this utility function.

#### ✓ LEADING — `sphinx/ext/autodoc/__init__.py::MethodDocumenter.can_document_member`

- **Q1 Role.** This class method determines if a given object (`member`) can be documented by `MethodDocumenter`.
- **Q2 Connection to symptom.** This function is the gatekeeper for selecting `MethodDocumenter`. The user's causal graph shows `InstanceAttributeDocumenter` is used, which strongly implies this function returned `False` for the decorated `__init__`. This happens if `inspect.isroutine(member)` returns `False`. This incorrect classification is the first step that leads to `__init__` not being documented as a method.
- **Q3 Counterfactual.** `yes` — If this function were modified to correctly identify decorated functions as routines (e.g., by checking the `__wrapped__` attribute), it would return `True`, causing the correct documenter to be selected and fixing the issue.
- **Q4 Alternatives considered.**
  - `sphinx/ext/autosummary/__init__.py::get_documenter` — A fix is possible in the caller, but less clean as it separates the decision from the logic.
  - `inspect.isroutine` — The underlying standard library function could be the reason for the `False` return, but modifying it is not appropriate for a Sphinx-specific fix.
  - `sphinx/ext/autodoc/__init__.py::Documenter.filter_members` — This is where the user suspects the error is, but it would only be reached if `can_document_member` returned `True`.
- **Q5 Verdict.** `leading` (confidence: `high`) — Evidence suggests the wrong documenter is chosen, and this function is the gatekeeper; fixing its check for decorated methods would resolve the primary error.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sphinx/ext/autodoc/__init__.py::MethodDocumenter.can_document_member` | high | Evidence suggests the wrong documenter is chosen, and this function is the gatekeeper; fixing its check for decorated methods would resolve the primary error. | Modify the `inspect.isroutine(member)` check to also consider the `__wrapped__` object, e.g., `inspect.isroutine(unwrap(member))`. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sphinx/ext/autosummary/__init__.py::get_documenter` | high | This function makes the incorrect choice of documenter, directly causing the issue, but the faulty logic it relies on is in `can_document_member`. | As a workaround, add a special case to select `MethodDocumenter` if `hasattr(obj, '__wrapped__')`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sphinx/util/inspect.py::isdescriptor` | high | This function correctly identifies that a wrapped function is not a descriptor; the bug lies in how Sphinx handles such objects, not in this utility function. |  |

**Causal chains (per candidate)**

- `sphinx/ext/autosummary/__init__.py::get_documenter`  (score=8.0)  \
  get_documenter is called for the decorated `__init__` method. → It calls `MethodDocumenter.can_document_member`, which incorrectly returns `False`. → It continues searching and selects `InstanceAttributeDocumenter` as a fallback. → The returned `InstanceAttributeDocumenter` treats `__init__` as a simple attribute, not a method whose docstring should be displayed. → The `__init__` documentation does not appear in the output.
- `sphinx/util/inspect.py::isdescriptor`  (score=0.0)  \
  The function is called on a wrapped function object. → The object does not have `__get__`, `__set__`, or `__delete__` methods. → The function correctly returns `False`. → This correct behavior does not contribute to the bug.
- `sphinx/ext/autodoc/__init__.py::MethodDocumenter.can_document_member`  (score=9.0)  \
  `get_documenter` calls this function with the decorated `__init__` method. → The check `inspect.isroutine(member)` returns `False` because the decorator obscures the function's nature. → The function returns `False`. → `get_documenter` then fails to select `MethodDocumenter`. → A fallback documenter (`InstanceAttributeDocumenter`) is chosen, which does not correctly handle documenting `__init__` methods. → The `__init__` method's documentation is omitted from the generated output.

**next_to_explore:** `['sphinx.ext.autodoc.Documenter.filter_members', 'sphinx.ext.autodoc.InstanceAttributeDocumenter.add_content', 'sphinx.ext.autodoc.Documenter.generate', 'inspect.isroutine']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `sphinx/ext/autodoc/__init__.py::MethodDocumenter.can_document_member` | 0.9 |
| 2 | `sphinx/ext/autodoc/__init__.py::InstanceAttributeDocumenter.add_content` | 0.85 |
| 3 | `sphinx/ext/autodoc/__init__.py::Documenter.add_content` | 0.8 |
| 4 | `sphinx/ext/autosummary/__init__.py::get_documenter` | 0.5 |
| 5 | `sphinx/ext/autodoc/__init__.py::Documenter.get_doc` | 0.1 |
| 6 | `sphinx/ext/autodoc/__init__.py::DocstringSignatureMixin.get_doc` | 0.1 |
| 7 | `sphinx/ext/napoleon/__init__.py::_skip_member` | 0.1 |
| 8 | `sphinx/ext/autodoc/__init__.py::DataDeclarationDocumenter.add_content` | 0.05 |
| 9 | `sphinx/ext/autodoc/__init__.py::Documenter.__init__` | 0.05 |
| 10 | `sphinx/util/inspect.py::isdescriptor` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `sphinx/ext/autodoc/__init__.py::MethodDocumenter.can_document_member` | 0.900 | high | 1/1 | (1701, 1704) |
| 2 | `sphinx/ext/autodoc/__init__.py::InstanceAttributeDocumenter.add_content` | 0.850 | high | 1/1 | (1995, 1997) |
| 3 | `sphinx/ext/autodoc/__init__.py::Documenter.add_content` | 0.800 | high | 1/1 | (495, 526) |
| 4 | `sphinx/ext/autosummary/__init__.py::get_documenter` | 0.500 | high | 1/1 | (184, 216) |
| 5 | `sphinx/ext/napoleon/__init__.py::_process_docstring` | 0.181 | high | 1/1 | (331, 378) |
| 6 | `sphinx/domains/__init__.py::Domain.__init__` | 0.179 | high | 1/1 | (202, 229) |
| 7 | `sphinx/ext/napoleon/__init__.py::Config.__init__` | 0.169 | high | 1/1 | (268, 272) |
| 8 | `sphinx/domains/__init__.py::ObjType.__init__` | 0.153 | high | 1/1 | (52, 56) |
| 9 | `sphinx/domains/__init__.py::Index.__init__` | 0.132 | high | 1/1 | (95, 99) |
| 10 | `sphinx/ext/autodoc/__init__.py::Documenter.get_doc` | 0.100 | high | 1/1 | (462, 478) |
