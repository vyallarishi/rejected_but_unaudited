"""Reconstructed editor prompt template + four evidence-block formats, recovered
by diffing stored prompt_text across arms (Step 3).

Verified byte-identical to stored prompts (see runner/verification.md). The frozen
template is:

  Issue:
  <problem_statement>

  Candidate functions in <file>:
  <signatures>

  Localization notes:
  - <leading_key>: <causal_chain>
  <EVIDENCE_BLOCK>
  Which function contains the fault? Answer with one function name from the list, on a single line:
  FAULT: <function_name>

Evidence blocks by arm:
  POS       : (nothing after the leading localization note)
  NEG_true  : "Ruled out:\n- <k>: <reason>\n..." (genuine rejections)
  NEG_false : "Ruled out:\n- <gold_key>: ruled out; the true cause is upstream."
  NEG_shuf  : "Ruled out:\n- <k>: <reason>\n..." (rejections from a DIFFERENT instance)
"""

# The single forged rejection line (uniform across all captured NF prompts).
FORGED_LINE = "- {gold_key}: ruled out; the true cause is upstream."

# New-arm additions (Step 3 generators) --------------------------------------
# NEG-FALSE-AUDIT: NEG-FALSE + one neutral audit instruction appended after the
# ruled-out block, before the commit question. Frozen wording:
AUDIT_INSTRUCTION = (
    "Before committing, verify each ruled-out entry against the candidate "
    "signatures; do not treat a rejection as correct unless it is consistent "
    "with the code."
)

COMMIT_QUESTION = ("Which function contains the fault? Answer with one function "
                   "name from the list, on a single line:")


def render_pos(issue, file, signatures, leading_key, causal_chain):
    """POS prompt (bytes must match stored prompt_text)."""
    return (
        f"Issue:\n{issue}\n\n"
        f"Candidate functions in {file}:\n{signatures}\n\n"
        f"Localization notes:\n- {leading_key}: {causal_chain}\n\n"
        f"{COMMIT_QUESTION}\nFAULT: <function_name>"
    )


def _ruled_out_block(rejections):
    """rejections: list of (function_key, reason)."""
    lines = ["Ruled out:"]
    for k, reason in rejections:
        lines.append(f"- {k}: {reason}")
    return "\n".join(lines)


def render_neg(issue, file, signatures, leading_key, causal_chain, rejections):
    """NEG_true / NEG_shuf: same shape, rejections differ by source instance."""
    block = _ruled_out_block(rejections)
    return (
        f"Issue:\n{issue}\n\n"
        f"Candidate functions in {file}:\n{signatures}\n\n"
        f"Localization notes:\n- {leading_key}: {causal_chain}\n"
        f"{block}\n\n"
        f"{COMMIT_QUESTION}\nFAULT: <function_name>"
    )


def render_neg_false(issue, file, signatures, leading_key, causal_chain, gold_key):
    """NEG_false: single forged rejection of the gold function."""
    forged = FORGED_LINE.format(gold_key=gold_key)
    return (
        f"Issue:\n{issue}\n\n"
        f"Candidate functions in {file}:\n{signatures}\n\n"
        f"Localization notes:\n- {leading_key}: {causal_chain}\n"
        f"Ruled out:\n{forged}\n\n"
        f"{COMMIT_QUESTION}\nFAULT: <function_name>"
    )


# ---- New arms (byte-diffed against NEG_false parent) ----
def render_neg_false_audit(issue, file, signatures, leading_key, causal_chain, gold_key):
    """NEG-FALSE-AUDIT: NEG-FALSE + one appended audit instruction."""
    forged = FORGED_LINE.format(gold_key=gold_key)
    return (
        f"Issue:\n{issue}\n\n"
        f"Candidate functions in {file}:\n{signatures}\n\n"
        f"Localization notes:\n- {leading_key}: {causal_chain}\n"
        f"Ruled out:\n{forged}\n\n"
        f"{AUDIT_INSTRUCTION}\n\n"
        f"{COMMIT_QUESTION}\nFAULT: <function_name>"
    )


def render_neg_false_natural(issue, file, signatures, leading_key, causal_chain,
                             gold_key, donor_reason):
    """NEG-FALSE-NATURAL: forge the gold rejection using a genuine reason harvested
    from another rejected candidate in the same instance (stylistically real)."""
    forged = f"- {gold_key}: {donor_reason}"
    return (
        f"Issue:\n{issue}\n\n"
        f"Candidate functions in {file}:\n{signatures}\n\n"
        f"Localization notes:\n- {leading_key}: {causal_chain}\n"
        f"Ruled out:\n{forged}\n\n"
        f"{COMMIT_QUESTION}\nFAULT: <function_name>"
    )
