#!/usr/bin/env python3
"""Sizing and calibration simulation for the review-ablation harness (entity 5b).

Recomputes every number the entity body quotes for sizing:

  * the attainable permutation floor  (2 / C(2N,N))^M, by exact enumeration
  * the worked verification cases for the per-dimension statistic T = mean|D(p)|
  * the A/A false-positive rate of the JOINT max-statistic decision rule
  * the power of the joint rule on the AC-2-shaped effect, at three sizings
  * Wilson score intervals for every rate reported above

Stdlib only, fixed seed, all parameters at the top. Run:

    python3 sizing-simulation.py

Runtime is a few minutes at the default trial counts; pass --quick for a smoke run.

WHAT IS BEING SIMULATED
-----------------------
A "run" is one headless review of one PR under one arm. It produces three things
the comparator measures:

  anchor_set   a set of candidate fingerprint IDs
  severity_mix a normalized histogram over CRITICAL/HIGH/MEDIUM/LOW/NIT
  tokens       one non-negative scalar (uncached total)

The run model is deliberately simple and deliberately optimistic: a per-PR
STABLE CORE of findings present in every run of that PR, plus a NOISE POOL whose
members are included independently per run with probability Q_NOISE. Real runs
are plausibly noisier and more correlated than this (see the caveat in the entity
body). Nothing here is a substitute for AC-1, which measures the real process.

THE DECISION RULE UNDER TEST
----------------------------
Per PR p, arm X, run i: R(p,X,i). For any two runs a similarity s(a,b) in [0,1]
is defined per dimension:

  anchor_set    Jaccard(F(a), F(b));   Jaccard of two empty sets = 1
  severity_mix  1 - TotalVariation(H(a), H(b))
  tokens        (handled directly as arm means, see below)

For the two set//histogram dimensions:

  J_within(p,X) = mean s over the C(N,2) within-arm pairs
  J_between(p)  = mean s over the N^2 cross-arm pairs
  D(p)          = mean(J_within(p,A), J_within(p,B)) - J_between(p)
  T             = mean over the M PRs of |D(p)|

For tokens, D(p) = mean(tokens in A) - mean(tokens in B) and T = mean|D(p)|,
which is the "mean absolute difference of arm means" the entity specifies.

All three T are invariant under swapping the A/B labels within a PR, which is
what collapses the permutation space and sets the floor at (2/C(2N,N))^M.

JOINT RULE. Enumerate every label assignment (C(2N,N)^M of them; permuting run
labels independently within each PR). For each dimension d, standardize T_d by
its own permutation mean and sd -> z_d. The joint statistic is max_d z_d. Then

  p_joint = fraction of assignments whose max_d z_d >= observed max_d z_d
  p_d     = fraction of assignments whose max_e z_e >= observed z_d
  material         iff p_joint <= ALPHA
  flagged_dimensions = { d : p_d <= ALPHA }

This is single-step Westfall-Young max-T. It self-calibrates under whatever
correlation the three statistics actually have, which is why it replaces three
independent alpha-level tests (whose family-wise rate is uncalibrated, bounded
above by ~0.143 under independence).
"""

from __future__ import annotations

import argparse
import itertools
import math
import random
import statistics
from fractions import Fraction

# ---------------------------------------------------------------- parameters

SEED = 20260728  # fixed; every rate below is reproducible from this seed alone

ALPHA = 0.05

CALIBRATION_TRIALS = 200  # A/A trials per sizing (matches the round-1 count)
POWER_TRIALS = 60  # A/B trials per sizing (matches the round-1 count)

# Run model
STABLE_CORE = 6  # findings present in every run of a PR
NOISE_POOL = 6  # findings sampled independently per run
Q_NOISE = 0.5  # inclusion probability for each noise finding

# AC-2-shaped effect: arm B systematically emits this many extra findings per run
EFFECT_EXTRA_FINDINGS = 3

SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "NIT")

# Token model: per-run uncached total, lognormal-ish around a mean, with the
# arm-B effect adding a proportional bump for the extra findings it emits.
TOKENS_MEAN = 141_000.0
TOKENS_CV = 0.08  # coefficient of variation of the per-run token total
TOKENS_PER_FINDING = 1_800.0

SIZINGS = (
    ("N=2 / M=3", 2, 3),
    ("N=2 / M=4", 2, 4),
    ("N=3 / M=3", 3, 3),
)

DIMENSIONS = ("anchor_set", "severity_mix", "tokens")


# ------------------------------------------------------------- run generation


class Run:
    __slots__ = ("anchors", "hist", "tokens")

    def __init__(self, anchors, hist, tokens):
        self.anchors = anchors
        self.hist = hist
        self.tokens = tokens


def make_pr(rng, pr_id, n_extra=None):
    """Fixed per-PR structure: which findings exist, and each one's severity."""
    if n_extra is None:
        n_extra = EFFECT_EXTRA_FINDINGS
    core = [f"{pr_id}:core:{k}" for k in range(STABLE_CORE)]
    noise = [f"{pr_id}:noise:{k}" for k in range(NOISE_POOL)]
    extra = [f"{pr_id}:effect:{k}" for k in range(n_extra)]
    severity = {f: rng.choice(SEVERITIES) for f in core + noise + extra}
    return core, noise, extra, severity


def sample_run(rng, pr, arm_has_effect):
    core, noise, extra, severity = pr
    found = list(core)
    for f in noise:
        if rng.random() < Q_NOISE:
            found.append(f)
    if arm_has_effect:
        found.extend(extra)
    anchors = frozenset(found)

    counts = {s: 0 for s in SEVERITIES}
    for f in found:
        counts[severity[f]] += 1
    total = sum(counts.values())
    if total == 0:
        # Empty run: a dedicated category carries mass 1, so total-variation
        # distance stays total instead of dividing by zero.
        hist = tuple([0.0] * len(SEVERITIES) + [1.0])
    else:
        hist = tuple([counts[s] / total for s in SEVERITIES] + [0.0])

    tokens = rng.gauss(
        TOKENS_MEAN + TOKENS_PER_FINDING * len(found), TOKENS_MEAN * TOKENS_CV
    )
    return Run(anchors, hist, max(tokens, 0.0))


# ------------------------------------------------------------------ distances


def jaccard(a, b):
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def hist_similarity(h1, h2):
    tv = 0.5 * sum(abs(x - y) for x, y in zip(h1, h2))
    return 1.0 - tv


# -------------------------------------------------- permutation machinery


def splits(two_n, n):
    """Every way to label 2N runs as N arm-A and N arm-B, as (A_idx, B_idx)."""
    out = []
    allidx = range(two_n)
    for a in itertools.combinations(allidx, n):
        b = tuple(i for i in allidx if i not in a)
        out.append((a, b))
    return out


def pairwise(runs, simfn):
    k = len(runs)
    m = [[0.0] * k for _ in range(k)]
    for i in range(k):
        for j in range(i + 1, k):
            s = simfn(runs[i], runs[j])
            m[i][j] = m[j][i] = s
    return m


def agreement_D(sim, a_idx, b_idx):
    n = len(a_idx)
    within_a = statistics.fmean(
        [sim[i][j] for i, j in itertools.combinations(a_idx, 2)]
    )
    within_b = statistics.fmean(
        [sim[i][j] for i, j in itertools.combinations(b_idx, 2)]
    )
    between = statistics.fmean([sim[i][j] for i in a_idx for j in b_idx])
    return (within_a + within_b) / 2.0 - between


def scalar_D(values, a_idx, b_idx):
    return statistics.fmean([values[i] for i in a_idx]) - statistics.fmean(
        [values[i] for i in b_idx]
    )


def per_pr_D_tables(pr_runs, split_list):
    """For one PR: D(p) under every split, for each of the three dimensions."""
    anchors_sim = pairwise(pr_runs, lambda x, y: jaccard(x.anchors, y.anchors))
    sev_sim = pairwise(pr_runs, lambda x, y: hist_similarity(x.hist, y.hist))
    toks = [r.tokens for r in pr_runs]

    rows = []
    for a_idx, b_idx in split_list:
        rows.append(
            (
                agreement_D(anchors_sim, a_idx, b_idx),
                agreement_D(sev_sim, a_idx, b_idx),
                scalar_D(toks, a_idx, b_idx),
            )
        )
    return rows


def joint_test(d_tables, alpha=ALPHA):
    """Single-step max-T over the full assignment space.

    d_tables: list over PRs of [ (D_anchor, D_sev, D_tok) per split ].
    Assignment 0 (the identity split, first in `splits` order) is the observed
    labelling. Returns (p_joint, {dim: p_dim}, T_observed_per_dim).
    """
    m = len(d_tables)
    n_splits = len(d_tables[0])
    n_dims = 3

    # T for every assignment: mean over PRs of |D(p)|.
    # Built incrementally so we never materialise 8000 x M tuples.
    totals = [[0.0] * n_dims]
    for pr_rows in d_tables:
        nxt = []
        abs_rows = [tuple(abs(v) for v in row) for row in pr_rows]
        for acc in totals:
            for row in abs_rows:
                nxt.append([acc[d] + row[d] for d in range(n_dims)])
        totals = nxt
    assert len(totals) == n_splits**m

    ts = [[acc[d] / m for d in range(n_dims)] for acc in totals]

    # observed = the assignment that takes split 0 in every PR, which the
    # incremental build places first.
    observed = ts[0]

    means = [statistics.fmean([t[d] for t in ts]) for d in range(n_dims)]
    sds = [statistics.pstdev([t[d] for t in ts]) for d in range(n_dims)]

    def z(t, d):
        if sds[d] == 0.0:
            return 0.0
        return (t[d] - means[d]) / sds[d]

    maxz = [max(z(t, d) for d in range(n_dims)) for t in ts]
    obs_z = [z(observed, d) for d in range(n_dims)]
    obs_maxz = max(obs_z)

    total = len(ts)
    p_joint = sum(1 for v in maxz if v >= obs_maxz - 1e-12) / total
    p_dim = {
        DIMENSIONS[d]: sum(1 for v in maxz if v >= obs_z[d] - 1e-12) / total
        for d in range(n_dims)
    }
    return p_joint, p_dim, observed


def anchor_only_test(d_tables):
    """The round-1 rule: permutation test on the anchor-set statistic alone."""
    m = len(d_tables)
    totals = [0.0]
    for pr_rows in d_tables:
        nxt = []
        abs_rows = [abs(row[0]) for row in pr_rows]
        for acc in totals:
            for v in abs_rows:
                nxt.append(acc + v)
        totals = nxt
    ts = [acc / m for acc in totals]
    observed = ts[0]
    return sum(1 for v in ts if v >= observed - 1e-12) / len(ts)


# ------------------------------------------------------------------ intervals


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


# ----------------------------------------------------------------- experiments


def floor_check():
    print("== Attainable floor, exact ==")
    for label, n, m in SIZINGS:
        c = math.comb(2 * n, n)
        f = Fraction(2, c) ** m
        print(f"  {label}: C(2N,N)={c}  floor=(2/{c})^{m}={f} = {float(f):.6f}")


def worked_cases(split_cache):
    """Cases the per-dimension rule must flag and must not, by exact enumeration."""
    print("\n== Worked verification, anchor-set statistic (exact enumeration) ==")

    def build(n, m, arm_a_sets, arm_b_sets):
        tables = []
        for p in range(m):
            runs = [Run(frozenset(s), (0,) * 6, 0.0) for s in arm_a_sets] + [
                Run(frozenset(s), (0,) * 6, 0.0) for s in arm_b_sets
            ]
            tables.append(per_pr_D_tables(runs, split_cache[n]))
        return tables

    for label, n, m in (("N=2/M=3", 2, 3), ("N=3/M=3", 3, 3)):
        disjoint = build(n, m, [{"x", "y"}] * n, [{"u", "v"}] * n)
        p = anchor_only_test(disjoint)
        print(f"  disjoint, {label}: assignments={math.comb(2*n,n)**m} p_perm={p:.4f}")

    superset = build(2, 3, [{"x", "y"}] * 2, [{"x", "y", "z"}] * 2)
    print(f"  superset,  N=2/M=3: p_perm={anchor_only_test(superset):.4f}")

    identical = build(2, 3, [{"x", "y"}] * 2, [{"x", "y"}] * 2)
    print(f"  identical, N=2/M=3: p_perm={anchor_only_test(identical):.4f}  (must not flag)")


def joint_worked_cases(split_cache):
    """Proof Policy #7 for the JOINT rule: one case it must flag, one it must not."""
    print("\n== Worked verification, JOINT max-statistic (exact enumeration) ==")
    n, m = 3, 3

    def runs_for(anchors, hist, tokens, count):
        return [Run(frozenset(anchors), hist, tokens) for _ in range(count)]

    h1 = (0.0, 1.0, 0.0, 0.0, 0.0, 0.0)  # all HIGH
    h2 = (0.0, 0.0, 0.0, 0.0, 1.0, 0.0)  # all NIT

    # MUST FLAG: all three dimensions moved, perfect within-arm agreement.
    tables = []
    for _ in range(m):
        runs = runs_for({"x", "y"}, h1, 100.0, n) + runs_for({"u", "v"}, h2, 300.0, n)
        tables.append(per_pr_D_tables(runs, split_cache[n]))
    p_joint, p_dim, obs = joint_test(tables)
    flagged = sorted(d for d, v in p_dim.items() if v <= ALPHA)
    print(
        f"  must-flag  : p_joint={p_joint:.4f} flagged={flagged} "
        f"T=(anchor {obs[0]:.3f}, sev {obs[1]:.3f}, tok {obs[2]:.1f})"
    )

    # MUST FLAG, one dimension only: anchors and severity identical, tokens move.
    tables = []
    for _ in range(m):
        runs = runs_for({"x", "y"}, h1, 100.0, n) + runs_for({"x", "y"}, h1, 300.0, n)
        tables.append(per_pr_D_tables(runs, split_cache[n]))
    p_joint, p_dim, obs = joint_test(tables)
    flagged = sorted(d for d, v in p_dim.items() if v <= ALPHA)
    print(f"  tokens-only: p_joint={p_joint:.4f} flagged={flagged}")

    # MUST NOT FLAG: the two arms are literally the same runs.
    tables = []
    for _ in range(m):
        runs = runs_for({"x", "y"}, h1, 100.0, 2 * n)
        tables.append(per_pr_D_tables(runs, split_cache[n]))
    p_joint, p_dim, obs = joint_test(tables)
    flagged = sorted(d for d, v in p_dim.items() if v <= ALPHA)
    print(f"  must-not   : p_joint={p_joint:.4f} flagged={flagged}")

    # MUST NOT FLAG: an empty-findings run on both arms. severity_mix is defined
    # by the dedicated empty category, so this is a similarity of 1, not a
    # division by zero.
    empty_h = (0.0, 0.0, 0.0, 0.0, 0.0, 1.0)
    tables = []
    for _ in range(m):
        runs = runs_for(set(), empty_h, 100.0, 2 * n)
        tables.append(per_pr_D_tables(runs, split_cache[n]))
    p_joint, p_dim, _ = joint_test(tables)
    print(f"  empty-runs : p_joint={p_joint:.4f} (no ZeroDivisionError)")


def trial(rng, n, m, effect, n_extra=None):
    tables = []
    for p in range(m):
        pr = make_pr(rng, p, n_extra)
        runs = [sample_run(rng, pr, False) for _ in range(n)] + [
            sample_run(rng, pr, effect) for _ in range(n)
        ]
        tables.append(per_pr_D_tables(runs, splits(2 * n, n)))
    return tables


def power_curve(trials_pow, sizing_label="N=3 / M=3", effects=(1, 2, 3, 4, 6, 9)):
    """Power of the joint rule as a function of effect size, at one sizing.

    The body's headline power figure is quoted at effect=+3 findings/run, which
    was written for a single-file ablation. A three-file removal is plausibly a
    larger effect, and the residual this design carries is about SMALL effects.
    Both directions are questions about the same curve, so measure the curve
    rather than argue monotonicity in prose.
    """
    n, m = next((n, m) for lbl, n, m in SIZINGS if lbl == sizing_label)
    print(f"\n== Power vs effect size, joint rule, {sizing_label} ==")
    print(
        f"   seed={SEED} trials={trials_pow} alpha={ALPHA} "
        f"stable_core={STABLE_CORE} noise_pool={NOISE_POOL} q_noise={Q_NOISE}"
    )
    for k in effects:
        rng = random.Random(SEED + 1)
        hits = 0
        pvals = []
        for _ in range(trials_pow):
            tables = trial(rng, n, m, effect=True, n_extra=k)
            p = joint_test(tables)[0]
            pvals.append(p)
            if p <= ALPHA:
                hits += 1
        lo, hi = wilson(hits, trials_pow)
        print(
            f"  effect=+{k:>2} findings/run: power={hits}/{trials_pow}="
            f"{hits/trials_pow:.2f} (Wilson {lo:.2f}-{hi:.2f})"
            f"  median p_joint={statistics.median(pvals):.4f}"
        )


def calibration_and_power(trials_cal, trials_pow):
    print("\n== A/A calibration and AC-2 power, Monte-Carlo ==")
    print(
        f"   seed={SEED} stable_core={STABLE_CORE} noise_pool={NOISE_POOL} "
        f"q_noise={Q_NOISE} effect=+{EFFECT_EXTRA_FINDINGS} findings/run"
    )
    for label, n, m in SIZINGS:
        rng = random.Random(SEED)
        fp_joint = fp_anchor = 0
        for _ in range(trials_cal):
            tables = trial(rng, n, m, effect=False)
            if joint_test(tables)[0] <= ALPHA:
                fp_joint += 1
            if anchor_only_test(tables) <= ALPHA:
                fp_anchor += 1
        lo_j, hi_j = wilson(fp_joint, trials_cal)
        lo_a, hi_a = wilson(fp_anchor, trials_cal)

        rng = random.Random(SEED + 1)
        hits = 0
        pvals = []
        for _ in range(trials_pow):
            tables = trial(rng, n, m, effect=True)
            p = joint_test(tables)[0]
            pvals.append(p)
            if p <= ALPHA:
                hits += 1
        lo_p, hi_p = wilson(hits, trials_pow)

        print(
            f"  {label:>10}: A/A fp joint={fp_joint}/{trials_cal}="
            f"{fp_joint/trials_cal:.3f} (Wilson {lo_j:.3f}-{hi_j:.3f})"
            f"  | anchor-only={fp_anchor}/{trials_cal}={fp_anchor/trials_cal:.3f}"
            f" (Wilson {lo_a:.3f}-{hi_a:.3f})"
        )
        print(
            f"  {'':>10}  power joint={hits}/{trials_pow}={hits/trials_pow:.2f}"
            f" (Wilson {lo_p:.2f}-{hi_p:.2f})"
            f"  median p_perm={statistics.median(pvals):.4f}"
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="fewer trials, smoke run")
    args = ap.parse_args()

    split_cache = {n: splits(2 * n, n) for n in (2, 3)}

    floor_check()
    worked_cases(split_cache)
    joint_worked_cases(split_cache)
    calibration_and_power(
        20 if args.quick else CALIBRATION_TRIALS,
        10 if args.quick else POWER_TRIALS,
    )
    power_curve(10 if args.quick else POWER_TRIALS)


if __name__ == "__main__":
    main()
