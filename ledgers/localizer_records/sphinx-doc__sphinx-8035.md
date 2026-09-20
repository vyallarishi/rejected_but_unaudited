# Instance: `sphinx-doc__sphinx-8035`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
Support defining specific `:private-members:` for autodoc
**Is your feature request related to a problem? Please describe.**
Currently, if I'm using autodoc, the `:private-members:` option does not allow specification of which private members to document. The current behavior is to document all private members, but what if I would only like to document 1 or 2?

**Describe the solution you'd like**
For `:private-members:` to take arguments, similarly to how `:members:` currently works

**Describe alternatives you've considered**
The current best way to do this is to explicitly list each class in a module and use `:autoattribute:`

- Some prior discussion: https://github.com/sphinx-doc/sphinx/issues/8009
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['autodoc behavior', 'private member documentation']`
- named APIs: `[]`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `sphinx/ext/autodoc/__init__.py` | Core logic for autodoc extension, including handling of members and private members. |
| 2 | `sphinx/ext/autodoc/directive.py` | Handles autodoc directives and options, including processing of documenter options. |
| 3 | `sphinx/domains/python.py` | Python domain-specific logic, potentially involved in handling private members. |
| 4 | `sphinx/domains/__init__.py` | Base classes for domains, including object type handling. |
| 5 | `sphinx/directives/__init__.py` | Base classes for directives, including object descriptions. |
| 6 | `sphinx/application.py` | Core application class for Sphinx, manages extensions and configuration. |
| 7 | `sphinx/config.py` | Configuration file abstraction, where options like private members are handled. |
| 8 | `sphinx/ext/autodoc/importer.py` | Handles importing objects for autodoc, might be relevant for member filtering. |
| 9 | `sphinx/writers/html.py` | HTML writer, might need adjustments for rendering private members. |
| 10 | `sphinx/writers/latex.py` | LaTeX writer, might need adjustments for rendering private members. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 0, considering: 1, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `sphinx/ext/autodoc/__init__.py::inherited_members_option`

- **Q1 Role.** This function is a converter for the `:inherited-members:` option, processing its argument for use in auto directives.
- **Q2 Connection to symptom.** No path exists. This function handles the `:inherited-members:` option, while the observed symptom is related to the `:private-members:` option. Its execution does not influence the handling of private members.
- **Q3 Counterfactual.** `no` — Modifying this function would only affect the behavior of `:inherited-members:`. The issue with `:private-members:` being an all-or-nothing flag would persist.
- **Q4 Alternatives considered.**
  - `sphinx/ext/autodoc/__init__.py::members_option` — This function provides a model for the desired behavior but is not part of the problem.
  - `sphinx/ext/autodoc/__init__.py::Documenter.document_members` — This is a more likely candidate as it orchestrates member documentation.
  - `The option spec for autodoc directives` — The root cause is likely where `:private-members:` is defined as a flag, not in this converter for another option.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for a different option (`:inherited-members:`) and is not on the causal path for the `:private-members:` symptom.

#### ✗ REJECTED — `sphinx/ext/autodoc/__init__.py::members_option`

- **Q1 Role.** This function is a converter for the `:members:` option, parsing its argument into a list of member names to document, or a special value `ALL` if no argument is given.
- **Q2 Connection to symptom.** No path exists. This function implements the behavior that is *desired* for `:private-members:`, as stated in the feature request. It does not cause the current, incorrect behavior of `:private-members:`; rather, its absence for `:private-members:` is the problem.
- **Q3 Counterfactual.** `no` — Modifying this function would alter how `:members:` works, but it would have no effect on `:private-members:`, which is the subject of the issue.
- **Q4 Alternatives considered.**
  - `A hypothetical `private_members_option` function` — The problem is that such a function doesn't exist and isn't used for the `:private-members:` option.
  - `sphinx/ext/autodoc/__init__.py::Documenter.document_members` — This is where the option's value is consumed, making it a more relevant location to investigate.
  - `sphinx.ext.autodoc.directive.AutodocDirective.option_spec` — The root cause is likely the definition of the option itself, which probably specifies it as a flag.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function serves as a template for the desired fix, but it is not causally related to the existing problem with `:private-members:`.

#### … CONSIDERING — `sphinx/ext/autodoc/__init__.py::Documenter.document_members`

- **Q1 Role.** This method generates the documentation for the members of an object, filtering and sorting them based on various options.
- **Q2 Connection to symptom.** Yes, a plausible path exists. This function calls `self.filter_members` to decide which members to document. The `filter_members` method (not shown) is where `self.options.private_members` is likely checked. Because `:private-members:` is currently a boolean flag, `filter_members` can only implement an all-or-nothing logic for private members, which is the observed symptom.
- **Q3 Counterfactual.** `partially` — Modifying this function and its callee `filter_members` is necessary to handle a list of private members. However, the option definition itself must also be changed elsewhere from a flag to one that accepts arguments.
- **Q4 Alternatives considered.**
  - `sphinx.ext.autodoc.Documenter.filter_members` — Preferred as the next step, as it likely contains the specific filtering logic that needs to be changed.
  - `sphinx.ext.autodoc.directive.AutodocDirective.option_spec` — This is the likely root cause, where `:private-members:` is defined as a flag.
  - `sphinx.ext.autodoc.Documenter.get_object_members` — Less likely, as this function's role is to gather members before filtering, not to apply the option-based filtering itself.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function orchestrates member documentation and is on the causal path to the symptom, as it calls the code that filters members based on the problematic option.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sphinx/ext/autodoc/__init__.py::Documenter.document_members` | high | This function orchestrates member documentation and is on the causal path to the symptom, as it calls the code that filters members based on the problematic option. | The logic that calls `filter_members` may need to be updated to handle `self.options.private_members` being a list, not just a boolean. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sphinx/ext/autodoc/__init__.py::inherited_members_option` | high | This function is for a different option (`:inherited-members:`) and is not on the causal path for the `:private-members:` symptom. |  |
| `sphinx/ext/autodoc/__init__.py::members_option` | high | This function serves as a template for the desired fix, but it is not causally related to the existing problem with `:private-members:`. |  |

**Causal chains (per candidate)**

- `sphinx/ext/autodoc/__init__.py::inherited_members_option`  (score=0.0)  \
  
- `sphinx/ext/autodoc/__init__.py::members_option`  (score=0.0)  \
  
- `sphinx/ext/autodoc/__init__.py::Documenter.document_members`  (score=6.0)  \
  An autodoc directive with the `:private-members:` flag is processed. → The `Documenter.document_members` method is called to generate documentation for the object's members. → Inside this method, `self.filter_members` is called to select which members to document. → The `filter_members` method (unseen) reads `self.options.private_members`, which is a boolean value. → Based on this boolean, `filter_members` includes all private members, as it has no information about which specific ones to include. → This results in the observed symptom: all private members are documented, with no way to specify a subset.

**next_to_explore:** `['sphinx.ext.autodoc.Documenter.filter_members', 'sphinx.ext.autodoc.directive.AutodocDirective.option_spec', 'sphinx.ext.autodoc.directive.AutodocDirective.run', 'sphinx.ext.autodoc.Documenter.get_object_members']`

### Abductive step #2 (iteration=6)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✓ LEADING — `sphinx/ext/autodoc/__init__.py::Documenter.filter_members`

- **Q1 Role.** Filters a list of object members, deciding which ones to skip based on options like `private-members`, `special-members`, and `undoc-members`.
- **Q2 Connection to symptom.** Yes. The docstring states that members are skipped if "they are private (except if given explicitly or the private-members option is set)". This logic is implemented here. Currently, it treats `private-members` as a boolean flag. When the option is present, `self.options.private_members` is `True`, and this function's logic proceeds to include all private members, causing the observed symptom of not being able to specify which private members to include.
- **Q3 Counterfactual.** `yes` — Modifying this function to check if `self.options.private_members` is a list of names (and not just `True`), and then using that list to decide which private members to keep, would directly implement the desired feature and eliminate the symptom.
- **Q4 Alternatives considered.**
  - `Documenter.option_spec` — This class attribute is where `private-members` is likely defined as a `flag`; changing it is the other half of the fix, but this function is where the behavior is enacted.
  - `sphinx.ext.autodoc.directive.process_documenter_options` — This function reads `option_spec` to parse the directive options; it's the mechanism that needs to be targeted by changing `option_spec`.
  - `Documenter.get_object_members` — This function implements list-based filtering for `:members:`, serving as a good example, but is not on the causal path for `:private-members:`.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function contains the filtering logic that directly produces the symptom, and modifying it is essential to implementing the requested behavior.

#### ✗ REJECTED — `sphinx/ext/autodoc/__init__.py::Documenter.get_object_members`

- **Q1 Role.** Retrieves members of the object being documented and, if the `:members:` option is a list, filters the members to only those specified.
- **Q2 Connection to symptom.** No path. This function's logic is concerned with the `:members:` and `:inherited-members:` options. It does not read or act upon the `:private-members:` option, so it cannot be the cause of the symptom related to how private members are handled.
- **Q3 Counterfactual.** `no` — The filtering of private members happens in `Documenter.filter_members`. Modifying this function would have no effect on the symptom, as it's not involved in that part of the logic.
- **Q4 Alternatives considered.**
  - `Documenter.filter_members` — Preferred, as this is where private member filtering actually occurs.
  - `Documenter.document_members` — This is the caller of both `get_object_members` and `filter_members`, so it's a level too high.
  - `sphinx.ext.autodoc.members_option` — This utility function is used to parse the `:members:` list, but it's not called for `:private-members:`, which is the root of the problem.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function handles a similar, but separate, option (`:members:`) and is not on the causal path for the `:private-members:` bug.

#### ✗ REJECTED — `sphinx/ext/autodoc/directive.py::AutodocDirective.run`

- **Q1 Role.** Serves as the main entry point for an autodoc directive, responsible for parsing options, creating a documenter instance, and triggering the documentation generation process.
- **Q2 Connection to symptom.** No direct path. While this function initiates the process, it delegates the option parsing to `process_documenter_options` and the member filtering logic to the `Documenter` subclass. The specific logic that causes the symptom (treating `:private-members:` as a boolean) is located in those downstream functions, not here.
- **Q3 Counterfactual.** `no` — The logic is delegated to helper functions and classes. A fix would need to be applied in `process_documenter_options` (by way of `Documenter.option_spec`) and `Documenter.filter_members`, not in this high-level dispatcher.
- **Q4 Alternatives considered.**
  - `sphinx.ext.autodoc.directive.process_documenter_options` — Preferred, as this is where options are parsed based on their defined types.
  - `Documenter.filter_members` — Preferred, as this is where the parsed option is used to filter members.
  - `Documenter.generate` — This is the method called by `run`, but it's still a high-level orchestrator; the detailed logic is deeper.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is a high-level entry point that delegates the faulty logic to other components, making it the wrong place to fix the issue.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sphinx/ext/autodoc/__init__.py::Documenter.filter_members` | high | This function contains the filtering logic that directly produces the symptom, and modifying it is essential to implementing the requested behavior. | Modify the logic to handle `self.options.private_members` as a list of strings, not just a boolean, to selectively include private members. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sphinx/ext/autodoc/__init__.py::Documenter.get_object_members` | high | This function handles a similar, but separate, option (`:members:`) and is not on the causal path for the `:private-members:` bug. |  |
| `sphinx/ext/autodoc/directive.py::AutodocDirective.run` | high | This function is a high-level entry point that delegates the faulty logic to other components, making it the wrong place to fix the issue. |  |

**Causal chains (per candidate)**

- `sphinx/ext/autodoc/__init__.py::Documenter.filter_members`  (score=9.0)  \
  An autodoc directive with `:private-members:` is processed. → Upstream, `process_documenter_options` (using `Documenter.option_spec`) parses this as a boolean flag, setting `options.private_members` to `True`. → `Documenter.document_members` calls `filter_members`. → Inside `filter_members`, a check for private members (e.g., `if membername.startswith('_')`) is performed. → The condition to skip a private member is effectively `if is_private and not self.options.private_members`. → Since `self.options.private_members` is `True`, the condition is false, and the private member is *not* skipped.
- `sphinx/ext/autodoc/__init__.py::Documenter.get_object_members`  (score=0.0)  \
  
- `sphinx/ext/autodoc/directive.py::AutodocDirective.run`  (score=0.0)  \
  

**next_to_explore:** `['sphinx.ext.autodoc.directive.process_documenter_options', 'sphinx.ext.autodoc.Documenter.document_members', 'sphinx.ext.autodoc.members_option', 'sphinx.util.docutils.option.flag']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `sphinx/ext/autodoc/__init__.py::Documenter.filter_members` | 0.9 |
| 2 | `sphinx/ext/autodoc/directive.py::AutodocDirective.run` | 0.8 |
| 3 | `sphinx/ext/autodoc/__init__.py::Documenter.document_members` | 0.6 |
| 4 | `sphinx/ext/autodoc/__init__.py::members_option` | 0.3 |
| 5 | `sphinx/ext/autodoc/__init__.py::Documenter.get_object_members` | 0.1 |
| 6 | `sphinx/ext/autodoc/directive.py::process_documenter_options` | 0.0 |
| 7 | `sphinx/ext/autodoc/__init__.py::inherited_members_option` | 0.0 |
| 8 | `sphinx/ext/autodoc/__init__.py::merge_special_members_option` | 0.0 |
| 9 | `sphinx/ext/autodoc/__init__.py::AttributeDocumenter.document_members` | 0.0 |
| 10 | `sphinx/ext/autodoc/__init__.py::ClassDocumenter.document_members` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `sphinx/ext/autodoc/__init__.py::Documenter.filter_members` | 0.900 | high | 1/1 | (559, 687) |
| 2 | `sphinx/ext/autodoc/directive.py::AutodocDirective.run` | 0.800 | high | 1/1 | (121, 158) |
| 3 | `sphinx/ext/autodoc/__init__.py::Documenter.document_members` | 0.600 | high | 1/1 | (689, 732) |
| 4 | `sphinx/ext/autodoc/__init__.py::members_option` | 0.300 | high | 1/1 | (76, 80) |
| 5 | `sphinx/ext/autodoc/importer.py::get_module_members` | 0.241 | high | 1/1 | (135, 153) |
| 6 | `sphinx/ext/autodoc/directive.py::DummyOptionSpec.__bool__` | 0.216 | high | 1/1 | (44, 46) |
| 7 | `sphinx/ext/autodoc/importer.py::get_object_members` | 0.207 | high | 1/1 | (161, 215) |
| 8 | `sphinx/ext/autodoc/directive.py::DocumenterBridge.__init__` | 0.186 | high | 1/1 | (55, 72) |
| 9 | `sphinx/ext/autodoc/__init__.py::Documenter.get_object_members` | 0.100 | high | 1/1 | (533, 557) |
| 10 | `sphinx/ext/autodoc/importer.py::mangle` | 0.078 | high | 1/1 | (24, 32) |
