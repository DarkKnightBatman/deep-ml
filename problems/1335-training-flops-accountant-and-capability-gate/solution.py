import math

def capability_gate(n_params, n_tokens, log10_compute_thresholds,
                    eval_scores, eval_limits):

    C = 6 * n_params * n_tokens
    L = math.log10(C)

    log10_flops = round(L, 4)

    compute_band = sum(
        1 for t in log10_compute_thresholds
        if L >= t
    )

    flagged_evals = sorted(
        name
        for name in eval_scores
        if name in eval_limits
        and eval_scores[name] >= eval_limits[name]
    )

    if flagged_evals or compute_band >= 2:
        decision = "pause"
    elif compute_band == 1:
        decision = "report"
    else:
        decision = "below"

    return {
        "log10_flops": log10_flops,
        "compute_band": compute_band,
        "flagged_evals": flagged_evals,
        "decision": decision
    }