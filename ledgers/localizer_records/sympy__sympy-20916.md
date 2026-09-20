# Instance: `sympy__sympy-20916`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
pprint unicode does not format subscripts on Greek letters
Good:

[ -t₀⋅w₀   -t₁⋅w₀   -t₂⋅w₀]


Bad:

[ -t₀⋅ω0   -t₁⋅ω0   -t₂⋅ω0]
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['incorrect formatting of subscripts on Greek letters', 'pprint unicode formatting issue']`
- named APIs: `[]`
- stack frames: `[]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `sympy/__init__.py` | This file imports and exposes the pprint function, making it a central point for addressing printing issues. |
| 2 | `sympy/printing/pretty/pretty_symbology.py` | This file likely contains the mappings for unicode characters, including Greek letters and subscripts, used in pretty printing. |
| 3 | `sympy/printing/pretty/pretty_utf8.py` | This file likely handles the actual UTF-8 encoding and formatting of the output, including subscripts. |
| 4 | `sympy/printing/pretty/pretty_unicode.py` | This file likely handles the actual Unicode formatting of the output, including subscripts. |
| 5 | `sympy/printing/pretty/pretty.py` | This file contains the core logic for pretty printing, including handling of unicode and subscripts. |
| 6 | `examples/beginner/print_pretty.py` | This example demonstrates the use of pprint and might need adjustments to showcase the fix. |
| 7 | `conftest.py` | This file configures the test environment and might contain settings related to pretty printing. |
| 8 | `sympy/abc.py` | This file defines common symbols, including Greek letters, which are relevant to the issue. |
| 9 | `sympy/printing/__init__.py` | This file imports and exposes the printing functions, making it a central point for addressing printing issues. |
| 10 | `sympy/assumptions/tests/test_assumptions_2.py` | This test file tests the pretty printing of assumptions and might need adjustments to showcase the fix. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✗ REJECTED — `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Subs`

- **Q1 Role.** This function provides the pretty-printing implementation for `Subs` objects, which represent expressions with substituted variables.
- **Q2 Connection to symptom.** No plausible path exists. The observed symptom is the incorrect formatting of a `Symbol` object's name (e.g., `omega0`), not a `Subs` object which represents a substitution in an expression (e.g., `f(x)|_{x=0}`).
- **Q3 Counterfactual.** `no` — Modifying this function would not affect how `Symbol` objects are printed, as it is not involved in their formatting logic.
- **Q4 Alternatives considered.**
  - `PrettyPrinter._print_Symbol` — Preferred, as it is the specific method for printing symbols.
  - `split_super_sub` — Preferred, as it is responsible for parsing symbol names into base and subscript parts.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function handles printing for `Subs` objects and is unrelated to the rendering of `Symbol` names.

#### ✗ REJECTED — `sympy/printing/pretty/pretty.py::PrettyPrinter._print_uppergamma`

- **Q1 Role.** This function provides the pretty-printing implementation for the `uppergamma` function, using the Greek letter Gamma (`Γ`) in unicode mode.
- **Q2 Connection to symptom.** No plausible path exists. The symptom concerns the subscripting of the Greek letter omega (`ω`), which is unrelated to the specific logic for printing the `uppergamma` function.
- **Q3 Counterfactual.** `no` — Changing how `uppergamma` is printed will have no effect on how other symbols with subscripts, like `omega0`, are rendered.
- **Q4 Alternatives considered.**
  - `PrettyPrinter._print_Symbol` — Preferred, as it is the method responsible for printing general symbols.
  - `split_super_sub` — Preferred, as it parses symbol names, which is a key step in formatting them.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is for printing a specific mathematical function and is not part of the general symbol-rendering logic.

#### ✓ LEADING — `sympy/printing/conventions.py::split_super_sub`

- **Q1 Role.** This function parses a symbol's name string into a base name, a list of superscripts, and a list of subscripts.
- **Q2 Connection to symptom.** Yes, a plausible path exists. The symbol `Symbol('omega0')` is passed to the pretty printer. Its `_print_Symbol` method calls `split_super_sub('omega0')`. This function correctly parses it into a base name `'omega'` and a subscript `['0']`. The caller then converts `'omega'` to `ω` but fails to convert `'0'` to `₀`, resulting in the incorrect output `ω0`.
- **Q3 Counterfactual.** `yes` — A modification to this function that pre-emptively converts numeric subscripts to unicode characters when the base name is a known Greek letter would cause the caller to render the correct output, fixing the symptom.
- **Q4 Alternatives considered.**
  - `PrettyPrinter._print_Symbol` — This is likely the correct place for the fix, as it is the caller that seems to contain the faulty rendering logic.
- **Q5 Verdict.** `leading` (confidence: `medium`) — This function is on the direct causal path and a modification here would fix the symptom, though the root cause is likely in the caller's handling of this function's output.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sympy/printing/conventions.py::split_super_sub` | medium | This function is on the direct causal path and a modification here would fix the symptom, though the root cause is likely in the caller's handling of this function's output. | When splitting trailing digits that form a subscript, check if the base name is a Greek letter; if so, convert the subscript digits to their unicode subscript c |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Subs` | high | This function handles printing for `Subs` objects and is unrelated to the rendering of `Symbol` names. |  |
| `sympy/printing/pretty/pretty.py::PrettyPrinter._print_uppergamma` | high | This function is for printing a specific mathematical function and is not part of the general symbol-rendering logic. |  |

**Causal chains (per candidate)**

- `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Subs`  (score=0.0)  \
  
- `sympy/printing/pretty/pretty.py::PrettyPrinter._print_uppergamma`  (score=0.0)  \
  
- `sympy/printing/conventions.py::split_super_sub`  (score=8.0)  \
  An expression containing `Symbol('omega0')` is pretty-printed. → The printer calls `_print_Symbol` for this symbol. → `_print_Symbol` calls `split_super_sub` with the name 'omega0'. → `split_super_sub` uses a regex to identify trailing digits, returning `('omega', [], ['0'])`. → The caller, `_print_Symbol`, looks up 'omega' to get the unicode character `ω`. → The caller's logic then fails to convert the subscript '0' to its unicode form `₀` for the Greek letter, appending a literal '0' instead.

**next_to_explore:** `['sympy/printing/pretty/pretty.py::PrettyPrinter._print_Symbol']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 1, rejected: 2

**Per-candidate deliberation traces**

#### … CONSIDERING — `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Symbol`

- **Q1 Role.** This function is responsible for pretty-printing a SymPy `Symbol` object by converting its name into a `prettyForm` object.
- **Q2 Connection to symptom.** Yes, this function is on the direct execution path. When pretty-printing an expression containing `Symbol('omega_0')`, the pretty-printer dispatches to this method. This method then calls `pretty_symbol('omega_0')`, which is presumed to incorrectly return the string 'ω0' instead of 'ω₀'. This incorrect string is then returned by `_print_Symbol`, leading to the observed symptom.
- **Q3 Counterfactual.** `yes` — This function could be modified to correctly parse symbol names with Greek letters and subscripts itself, bypassing the faulty logic in its callee `pretty_symbol`.
- **Q4 Alternatives considered.**
  - `sympy.printing.pretty.pretty_symbology.pretty_symbol` — Preferred, as it is the callee that likely contains the actual symbol-to-string conversion logic and thus the bug.
  - `sympy.printing.conventions.split_super_sub` — Also preferred, as its name suggests it's responsible for parsing subscripts from symbol names, which is failing for Greek letters.
  - `sympy.printing.pretty.pretty.PrettyPrinter._print_Subs` — Not preferred, as it handles explicit `Subs` objects, not the implicit subscripts in `Symbol` names which are at issue here.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function is a direct caller for symbol printing, but the core formatting logic and the likely bug reside in its callee, `pretty_symbol`.

#### ✗ REJECTED — `sympy/printing/pretty/pretty_symbology.py::line_width`

- **Q1 Role.** This function calculates the display width of a unicode string, ignoring non-spacing combining characters for layout purposes.
- **Q2 Connection to symptom.** No path exists. This function is used for calculating the width of an already-generated string for alignment and layout. The bug is in the generation of the string itself (a '0' instead of '₀'), which happens before this function would be called.
- **Q3 Counterfactual.** `no` — Modifying this function would only affect layout calculations. It would not change the characters generated for the symbol, so the incorrect '0' would still be present.
- **Q4 Alternatives considered.**
  - `sympy.printing.pretty.pretty.PrettyPrinter._print_Symbol` — Preferred, as it is responsible for initiating the printing of a symbol.
  - `sympy.printing.pretty.pretty_symbology.pretty_symbol` — Preferred, as it is responsible for converting the symbol's name to a unicode string.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a layout utility function that measures string width and is not involved in generating the incorrect symbol string.

#### ✗ REJECTED — `sympy/printing/pretty/pretty.py::PrettyPrinter._print_EulerGamma`

- **Q1 Role.** This function provides the pretty-printing representation for the specific mathematical constant `EulerGamma`.
- **Q2 Connection to symptom.** No path exists. This function is called only for the `EulerGamma` object. The observed symptom involves a generic `Symbol` with a Greek name and a subscript (`omega_0`), which is handled by `_print_Symbol`, not this function.
- **Q3 Counterfactual.** `no` — Modifying this function would have no effect on the printing of `Symbol('omega_0')` as it is never called for that object.
- **Q4 Alternatives considered.**
  - `sympy.printing.pretty.pretty.PrettyPrinter._print_Symbol` — Preferred, as this is the correct printer method for generic `Symbol` objects.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function handles a specific constant (`EulerGamma`) and is not on the code path for printing a generic symbol with a subscript.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Symbol` | medium | This function is a direct caller for symbol printing, but the core formatting logic and the likely bug reside in its callee, `pretty_symbol`. | A workaround could be implemented here by manually parsing `e.name`, but the proper fix belongs in `pretty_symbol` or one of its helpers. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `sympy/printing/pretty/pretty_symbology.py::line_width` | high | This is a layout utility function that measures string width and is not involved in generating the incorrect symbol string. |  |
| `sympy/printing/pretty/pretty.py::PrettyPrinter._print_EulerGamma` | high | This function handles a specific constant (`EulerGamma`) and is not on the code path for printing a generic symbol with a subscript. |  |

**Causal chains (per candidate)**

- `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Symbol`  (score=7.0)  \
  A call is made to pretty-print an object containing `Symbol('omega_0')`. → The pretty-printer's dispatch mechanism calls `PrettyPrinter._print_Symbol` for this symbol. → Inside `_print_Symbol`, `pretty_symbol('omega_0')` is called. → The `pretty_symbol` function incorrectly processes the name, returning the string 'ω0'. → `_print_Symbol` wraps this incorrect string in a `prettyForm` object and returns it, causing the symptom.
- `sympy/printing/pretty/pretty_symbology.py::line_width`  (score=0.0)  \
  
- `sympy/printing/pretty/pretty.py::PrettyPrinter._print_EulerGamma`  (score=0.0)  \
  

**next_to_explore:** `['sympy.printing.pretty.pretty_symbology.pretty_symbol', 'sympy.printing.conventions.split_super_sub', 'sympy.printing.pretty.pretty.PrettyPrinter._print_Subs']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Symbol` | 0.95 |
| 2 | `sympy/printing/conventions.py::split_super_sub` | 0.85 |
| 3 | `sympy/printing/pretty/pretty_symbology.py::pretty_symbol` | 0.7 |
| 4 | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Subs` | 0.1 |
| 5 | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_EulerGamma` | 0.05 |
| 6 | `sympy/printing/pretty/pretty_symbology.py::pretty_use_unicode` | 0.02 |
| 7 | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_uppergamma` | 0.01 |
| 8 | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_subfactorial` | 0.01 |
| 9 | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_lerchphi` | 0.01 |
| 10 | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_lowergamma` | 0.01 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Symbol` | 0.950 | high | 1/1 | (79, 81) |
| 2 | `sympy/printing/conventions.py::split_super_sub` | 0.850 | high | 1/1 | (13, 70) |
| 3 | `sympy/printing/pretty/pretty_symbology.py::pretty_symbol` | 0.700 | high | 1/1 | (509, 567) |
| 4 | `sympy/printing/pretty/pretty_symbology.py::line_width` | 0.186 | high | 1/1 | (635, 639) |
| 5 | `sympy/printing/pretty/pretty_symbology.py::annotated` | 0.155 | high | 1/1 | (570, 595) |
| 6 | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Subs` | 0.100 | high | 1/1 | (2469, 2484) |
| 7 | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_EulerGamma` | 0.050 | high | 1/1 | (1749, 1752) |
| 8 | `sympy/printing/pretty/pretty_symbology.py::pretty_use_unicode` | 0.020 | high | 1/1 | (41, 55) |
| 9 | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_uppergamma` | 0.010 | high | 1/1 | (1656, 1658) |
| 10 | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_subfactorial` | 0.010 | high | 1/1 | (178, 185) |
