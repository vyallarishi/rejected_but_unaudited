# Instance: `pytest-dev__pytest-7324`

- runs: 1   termination: `ledger_informed`   think-high calls: 3

## Issue (truncated to 1200 chars)

```
Pytest crashes the interpreter on debug build for 3.8+
Short reproducer
```py
>>> Expression.compile("False")
python: Python/compile.c:3559: compiler_nameop: Assertion `!_PyUnicode_EqualToASCIIString(name, "None") && !_PyUnicode_EqualToASCIIString(name, "True") && !_PyUnicode_EqualToASCIIString(name, "False")' failed.
[1]    29440 abort (core dumped)  python
```

Related issue for improvement of this behavior: [bpo-40870](https://bugs.python.org/issue40870)
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `['Assertion `!_PyUnicode_EqualToASCIIString(name, "None") && !_PyUnicode_EqualToASCIIString(name, "True") && !_PyUnicode_EqualToASCIIString(name, "False")\' failed.']`
- behaviors: `['interpreter crash']`
- named APIs: `['Expression.compile']`
- stack frames: `[{'file': 'Python/compile.c', 'func': 'compiler_nameop', 'line': 3559}]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `src/_pytest/_code/source.py` | Contains the `compile` and `compile_` functions which are directly implicated in the traceback. |
| 2 | `src/_pytest/_code/__init__.py` | Exports the `compile` function from `_pytest._code.source`, making it a key point of interaction. |
| 3 | `src/_pytest/assertion/rewrite.py` | Assertion rewriting involves compiling code, so it's a plausible location for the crash. |
| 4 | `src/_pytest/python.py` | Deals with collection and handling of Python test functions, potentially involving code compilation. |
| 5 | `src/_pytest/debugging.py` | Debugging tools might interact with code compilation or execution, making it relevant. |
| 6 | `testing/code/test_source.py` | Tests the `Source` class and its `compile` method, so it's useful for verifying fixes. |
| 7 | `testing/code/test_code.py` | Tests the `Code` class, which wraps code objects and interacts with source code. |
| 8 | `testing/test_assertion.py` | Tests related to assertion rewriting, which might expose issues with code compilation. |
| 9 | `testing/test_assertrewrite.py` | Tests the assertion rewriting hook, which is directly related to the issue. |
| 10 | `src/_pytest/mark/expression.py` | Compiles expressions for mark evaluation, potentially triggering the bug. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✓ LEADING — `src/_pytest/mark/expression.py::Expression.compile`

- **Q1 Role.** This function compiles a string expression into a Python code object for later evaluation, specifically for pytest's marker matching system.
- **Q2 Connection to symptom.** Yes, this is the entry point for the bug. 
1. `Expression.compile` is called with `input="False"`.
2. It calls `astexpr = expression(Scanner(input))`, a custom parser that likely returns an `ast.Name(id='False', ...)` node.
3. This AST node is passed to the Python built-in `compile()`.
4. In Python 3.8+ debug builds, `compile()` calls the C function `compiler_nameop` for the `ast.Name` node.
5. `compiler_nameop` has an assertion that fails if the name is 'False', 'True', or 'None', as these should be constants, causing the interpreter to crash.
- **Q3 Counterfactual.** `yes` — If this function were modified to transform the AST node for 'False' into an `ast.Constant` before passing it to `compile()`, the crash would be prevented.
- **Q4 Alternatives considered.**
  - `_pytest.mark.expression.expression` — This parser is the likely root cause for creating the wrong AST node; fixing it is a better solution.
  - `_pytest.assertion.rewrite.py::AssertionRewriter.visit_Name` — This is unrelated as it's part of assertion rewriting, not marker expression compilation.
  - `Python's built-in compile()` — This is where the crash occurs, but it's behaving correctly by rejecting an invalid AST; the fault is in the caller.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function is the direct entry point in the reproducer and orchestrates the call to `compile` with the problematic AST.

#### ✗ REJECTED — `src/_pytest/assertion/rewrite.py::AssertionRewriter._assert_expr_to_lineno`

- **Q1 Role.** This function retrieves a mapping from line numbers to the string representation of `assert` expressions found in a source file.
- **Q2 Connection to symptom.** No path exists. The reproducer `Expression.compile("False")` does not involve `assert` statements or the assertion rewriting subsystem. This function is part of a different feature and is not on the execution path that leads to the crash.
- **Q3 Counterfactual.** `no` — Since this function is not executed when the bug is reproduced, modifying it would have no effect on the symptom.
- **Q4 Alternatives considered.**
  - `src/_pytest/mark/expression.py::Expression.compile` — This is the actual code path that triggers the bug.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is part of the assertion rewriting module, which is not involved in the marker expression compilation that causes the crash.

#### ✗ REJECTED — `src/_pytest/assertion/rewrite.py::AssertionRewriter.visit_Name`

- **Q1 Role.** This function is part of pytest's assertion rewriting mechanism; it transforms an `ast.Name` node to generate a richer explanation for assertion failures.
- **Q2 Connection to symptom.** No path exists. While this function processes `ast.Name` nodes, it does so only during assertion rewriting. The bug is triggered by compiling a marker expression via `Expression.compile`, which is a separate code path that does not involve assertion rewriting. The similarity in handling `ast.Name` for keywords like 'False' is coincidental to this specific bug report's reproducer.
- **Q3 Counterfactual.** `no` — This function is not on the execution path for the given reproducer, so modifying it would not prevent the crash.
- **Q4 Alternatives considered.**
  - `src/_pytest/mark/expression.py::Expression.compile` — This is the correct entry point for the bug.
  - `_pytest.mark.expression.expression` — This is the parser that likely creates the problematic AST, making it the root cause.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is part of assertion rewriting, which is not the code path triggered by the reproducer.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `src/_pytest/mark/expression.py::Expression.compile` | high | This function is the direct entry point in the reproducer and orchestrates the call to `compile` with the problematic AST. | Post-process the AST from `expression()` to convert `ast.Name` nodes for 'True', 'False', 'None' into `ast.Constant` nodes before calling `compile()`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `src/_pytest/assertion/rewrite.py::AssertionRewriter._assert_expr_to_lineno` | high | This function is part of the assertion rewriting module, which is not involved in the marker expression compilation that causes the crash. |  |
| `src/_pytest/assertion/rewrite.py::AssertionRewriter.visit_Name` | high | This function is part of assertion rewriting, which is not the code path triggered by the reproducer. |  |

**Causal chains (per candidate)**

- `src/_pytest/mark/expression.py::Expression.compile`  (score=9.0)  \
  The function is called with input="False". → It calls the internal parser `expression(Scanner(input))`, which incorrectly produces an `ast.Name(id='False')` node. → This AST is passed to the Python built-in `compile()`. → The CPython compiler's `compiler_nameop` function receives the `ast.Name` node. → An assertion in `compiler_nameop` checks that names for opcodes are not keywords like 'False'. → The assertion fails, causing the interpreter to abort.
- `src/_pytest/assertion/rewrite.py::AssertionRewriter._assert_expr_to_lineno`  (score=0.0)  \
  
- `src/_pytest/assertion/rewrite.py::AssertionRewriter.visit_Name`  (score=0.0)  \
  

**next_to_explore:** `['_pytest.mark.expression.expression', '_pytest.mark.expression.Scanner']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 1, rejected: 1

**Per-candidate deliberation traces**

#### … CONSIDERING — `src/_pytest/mark/expression.py::expression`

- **Q1 Role.** This function parses a string from a scanner into an `ast.Expression` node, handling the special case of an empty string.
- **Q2 Connection to symptom.** The reproducer `Expression.compile("False")` calls this function to parse the string. The `else` branch is taken, which calls `expr(s)`. It is plausible that `expr(s)` incorrectly returns an `ast.Name(id='False')` node for the input string "False". This function then wraps it in an `ast.Expression` and returns it. The caller then passes this AST to Python's `compile()`, which triggers the assertion failure in CPython's `compiler_nameop` because 'False' is a keyword and should not be a name.
- **Q3 Counterfactual.** `yes` — A modification in this function to check the returned AST from `expr(s)` and convert an `ast.Name(id='False')` to `ast.Constant(value=False)` would fix the symptom before the AST is compiled.
- **Q4 Alternatives considered.**
  - `_pytest.mark.expression::expr` — Preferred as the likely root cause, as it's the function that probably creates the incorrect AST node.
  - `_pytest.assertion.rewrite::AssertionRewriter.visit_Name` — Not preferred, as assertion rewriting seems unrelated to marker expression parsing, which is what the reproducer does.
  - `_pytest.mark.expression::Expression.compile` — Considered as the entry point, but the error seems to be in the parsing logic it delegates to, not the compilation call itself.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function is on the causal path and can be patched, but it likely just propagates an incorrect AST from the `expr` function it calls.

#### ✗ REJECTED — `src/_pytest/assertion/rewrite.py::AssertionRewriter.builtin`

- **Q1 Role.** This function creates an AST node for a pytest-internal representation of a Python builtin, such as `@py_builtins.name`.
- **Q2 Connection to symptom.** No path. The reproducer `Expression.compile("False")` triggers marker expression parsing, which is a separate pytest feature from assertion rewriting. This function is part of the assertion rewriter and is not expected to be on the execution path for the given symptom.
- **Q3 Counterfactual.** `no` — Since this function is not on the execution path for the bug, modifying it would have no effect on the symptom.
- **Q4 Alternatives considered.**
  - `_pytest.mark.expression.py::expression` — Preferred, as it is directly involved in parsing the expression from the reproducer.
  - `_pytest.mark.expression.py::expr` — Preferred as the likely root cause of the malformed AST, which `expression` then processes.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is part of assertion rewriting, which is not involved in the execution path of parsing marker expressions.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `src/_pytest/mark/expression.py::expression` | medium | This function is on the causal path and can be patched, but it likely just propagates an incorrect AST from the `expr` function it calls. | Check if the parsed expression is an `ast.Name` for 'True', 'False', or 'None' and convert it to the appropriate `ast.Constant`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `src/_pytest/assertion/rewrite.py::AssertionRewriter.builtin` | high | This function is part of assertion rewriting, which is not involved in the execution path of parsing marker expressions. |  |

**Causal chains (per candidate)**

- `src/_pytest/mark/expression.py::expression`  (score=6.0)  \
  Expression.compile("False") calls this function to parse the string. → The function calls `expr(s)`, which is hypothesized to incorrectly return `ast.Name(id='False')`. → The function wraps this incorrect node in an `ast.Expression` and returns it. → The caller then uses Python's `compile()` on the returned AST. → The CPython compiler's `compiler_nameop` function asserts that a name cannot be 'False', causing the interpreter to crash.
- `src/_pytest/assertion/rewrite.py::AssertionRewriter.builtin`  (score=0.0)  \
  No plausible chain. This function is part of assertion rewriting, while the bug occurs during marker expression parsing.

**next_to_explore:** `['src/_pytest/mark/expression.py::expr', 'src/_pytest/mark/expression.py::Expression.compile', 'src/_pytest/mark/expression.py::Scanner.accept', 'src/_pytest/assertion/rewrite.py::AssertionRewriter.visit_Name']`

### Abductive step #3 (iteration=9)

- leading: 0, considering: 1, rejected: 2

**Per-candidate deliberation traces**

#### … CONSIDERING — `src/_pytest/mark/expression.py::expr`

- **Q1 Role.** This function parses a logical expression string (with 'or') from a token stream into an `ast.BoolOp` node.
- **Q2 Connection to symptom.** Yes, a plausible path exists. `Expression.compile("False")` invokes the parser, which calls this `expr` function. For the input "False", the `while` loop for `OR` is skipped, and the function calls `and_expr(s)`. A function called deeper in the stack (by `and_expr`) incorrectly creates an `ast.Name(id='False')` node instead of an `ast.Constant(value=False)`. This faulty AST node is then returned up through `expr` and is eventually passed to the built-in `compile()`, which crashes on Python 3.8+ due to the invalid AST.
- **Q3 Counterfactual.** `no` — The function's primary logic handles `or` operators, which is not triggered by the input "False". The bug originates in a called function (`and_expr` or one of its callees) that parses the terminal, so modifying only `expr` would not fix the root cause.
- **Q4 Alternatives considered.**
  - `_pytest.mark.expression.py::and_expr` — Preferred, as it's the next function in the parser's call chain and closer to the terminal parsing.
  - `A hypothetical `primary` function` — Strongly preferred, as such a function would be responsible for converting a NAME token into an AST node, which is where the error occurs.
  - `_pytest.mark.expression.py::Expression.compile` — Not preferred, as the error is in AST generation, not its final compilation.
- **Q5 Verdict.** `considering` (confidence: `medium`) — The function is on the causal path but delegates the faulty work to a callee; the fix is not here.

#### ✗ REJECTED — `src/_pytest/mark/expression.py::Scanner.accept`

- **Q1 Role.** This function consumes and returns the current token if it matches the expected type, otherwise it returns `None` and optionally raises an error.
- **Q2 Connection to symptom.** No path exists. This function is a generic utility that operates on token types, not their values, and it does not create AST nodes. The bug is caused by the misinterpretation of the token's *value* ('False') during the higher-level AST construction phase, which merely uses this function as a tool to advance through tokens.
- **Q3 Counterfactual.** `no` — This is a generic scanner utility. Modifying it would not fix the semantic error of how 'False' is represented in the AST; it would just break the parser.
- **Q4 Alternatives considered.**
  - `_pytest.mark.expression.py::expr` — Preferred, as it's a caller that contains the actual parsing logic.
  - `The parser function that creates `ast.Name` nodes` — This is where the actual bug lies, as it makes the wrong semantic choice.
  - `_pytest.mark.expression.py::tokenize` — Considered, as it creates the tokens, but it likely correctly identifies 'False' as a NAME token; the error is in the interpretation.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a generic scanner utility that is not involved in the semantic interpretation causing the bug.

#### ✗ REJECTED — `src/_pytest/assertion/rewrite.py::AssertionRewriter.display`

- **Q1 Role.** This function wraps an AST expression node in a call to the `_saferepr` helper function, which is used for displaying expression values during assertion rewriting.
- **Q2 Connection to symptom.** No path exists. The observed symptom occurs during pytest's mark expression evaluation (`Expression.compile`), which is a feature for test selection. This function is part of pytest's assertion rewriting subsystem, a completely separate feature that is not invoked by the reproducer.
- **Q3 Counterfactual.** `no` — This function is not on the execution path for the bug. Modifying it would have no effect on the symptom.
- **Q4 Alternatives considered.**
  - `_pytest.mark.expression.py::Expression.compile` — Preferred, as this is the actual entry point for the bug.
  - `_pytest.mark.expression.py::expr` — Preferred, as this function is on the actual execution path.
  - `Any function in `_pytest/mark/expression.py`` — The bug is located in the mark expression feature, not assertion rewriting.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function belongs to an unrelated pytest feature (assertion rewriting) and is not in the call stack for the bug.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `src/_pytest/mark/expression.py::expr` | medium | The function is on the causal path but delegates the faulty work to a callee; the fix is not here. | Check downstream parser functions like `and_expr` or a `primary` equivalent for logic that incorrectly creates an `ast.Name` node for 'False' on Python 3.8+ ins |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `src/_pytest/mark/expression.py::Scanner.accept` | high | This is a generic scanner utility that is not involved in the semantic interpretation causing the bug. |  |
| `src/_pytest/assertion/rewrite.py::AssertionRewriter.display` | high | This function belongs to an unrelated pytest feature (assertion rewriting) and is not in the call stack for the bug. |  |

**Causal chains (per candidate)**

- `src/_pytest/mark/expression.py::expr`  (score=4.0)  \
  `Expression.compile('False')` calls the parser, which in turn calls `expr()`. → `expr()` calls `and_expr()` to parse the expression term. → A downstream function called by `and_expr()` incorrectly creates an `ast.Name(id='False')` node. → This invalid AST node for Python 3.8+ is returned up the call stack through `expr()`. → The invalid AST is passed to the built-in `compile()`, causing an assertion failure in CPython.
- `src/_pytest/mark/expression.py::Scanner.accept`  (score=1.0)  \
  The parser, for example in `expr()`, calls `s.accept(TokenType.OR)` to check for an 'or' operator. → This function's execution is incidental to the bug; it's a generic utility and the path that uses it in `expr` is not even taken for the input 'False'.
- `src/_pytest/assertion/rewrite.py::AssertionRewriter.display`  (score=0.0)  \
  

**next_to_explore:** `['src/_pytest/mark/expression.py::and_expr', 'src/_pytest/mark/expression.py::not_expr', 'src/_pytest/mark/expression.py::primary', 'src/_pytest/mark/expression.py::tokenize', 'src/_pytest/mark/expression.py::Expression.compile']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `src/_pytest/mark/expression.py::Expression.compile` | 1.0 |
| 2 | `src/_pytest/mark/expression.py::expression` | 0.9 |
| 3 | `src/_pytest/mark/expression.py::expr` | 0.8 |
| 4 | `src/_pytest/assertion/rewrite.py::AssertionRewriter.builtin` | 0.0 |
| 5 | `src/_pytest/assertion/rewrite.py::AssertionRewriter.visit_Name` | 0.0 |
| 6 | `src/_pytest/assertion/rewrite.py::AssertionRewriter.display` | 0.0 |
| 7 | `src/_pytest/assertion/rewrite.py::AssertionRewriter.assign` | 0.0 |
| 8 | `src/_pytest/assertion/rewrite.py::AssertionRewriter.visit_UnaryOp` | 0.0 |
| 9 | `src/_pytest/assertion/rewrite.py::AssertionRewriter.visit_Call` | 0.0 |
| 10 | `src/_pytest/assertion/rewrite.py::AssertionRewriter._assert_expr_to_lineno` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `src/_pytest/mark/expression.py::Expression.compile` | 1.000 | high | 1/1 | (196, 205) |
| 2 | `src/_pytest/mark/expression.py::expression` | 0.900 | high | 1/1 | (130, 136) |
| 3 | `src/_pytest/mark/expression.py::expr` | 0.800 | high | 1/1 | (139, 144) |
| 4 | `src/_pytest/_code/source.py::compile_` | 0.210 | high | 1/1 | (257, 277) |
| 5 | `src/_pytest/python.py::CallSpec2.copy` | 0.187 | high | 1/1 | (829, 837) |
| 6 | `src/_pytest/python.py::PyCollector.istestclass` | 0.185 | high | 1/1 | (379, 380) |
| 7 | `src/_pytest/_code/source.py::Source.compile` | 0.153 | high | 1/1 | (183, 227) |
| 8 | `src/_pytest/mark/expression.py::Scanner.accept` | 0.141 | high | 1/1 | (111, 119) |
| 9 | `src/_pytest/_code/source.py::get_statement_startend2` | 0.136 | high | 1/1 | (324, 343) |
| 10 | `src/_pytest/python.py::PyobjMixin.reportinfo` | 0.130 | high | 1/1 | (333, 348) |
