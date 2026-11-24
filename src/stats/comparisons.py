import numpy as np
import pandas as pd
from scipy.stats import (
    mannwhitneyu, 
    kruskal, 
    chi2_contingency, 
    spearmanr
)


def _magnitude(value: float, thresholds: tuple) -> str:
    """Label an effect size by conventional cutoffs."""
    small, medium, large = thresholds
    size = abs(value)
    if size < small:
        return "negligible"
    if size < medium:
        return "small"
    if size < large:
        return "medium"
    return "large"


def compare_two_groups(
    a: pd.Series,
    b: pd.Series,
    label_a: str = "Group A",
    label_b: str = "Group B",
) -> dict:
    """
    Mann-Whitney U test between two independent samples.
    """
    a, b = pd.Series(a).dropna(), pd.Series(b).dropna()
    stat, p = mannwhitneyu(a, b, alternative="two-sided")

    # Positive means group a tends to rank higher than group b.
    effect = 2 * stat / (len(a) * len(b)) - 1

    return {
        "test": "Mann-Whitney U",
        "label_a": label_a,
        "label_b": label_b,
        "median_a": a.median(),
        "median_b": b.median(),
        "mean_a": a.mean(),
        "mean_b": b.mean(),
        "n_a": len(a),
        "n_b": len(b),
        "stat": stat,
        "p_value": p,
        "significant": p < 0.05,
        "effect_name": "rank-biserial r",
        "effect": effect,
        "effect_size": _magnitude(effect, (0.1, 0.3, 0.5)),
    }


def compare_groups_kruskal(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    min_n: int = 200,
) -> dict:
    """
    Kruskal-Wallis test for value_col across groups of group_col with at least min_n observations.
    """
    groups = [
        g[value_col].dropna()
        for _, g in df.groupby(group_col, observed=True)
        if g[value_col].notna().sum() >= min_n
    ]
    stat, p = kruskal(*groups)

    n_total = sum(len(g) for g in groups)
    effect = (stat - len(groups) + 1) / (n_total - len(groups))

    return {
        "test": "Kruskal-Wallis",
        "n_groups": len(groups),
        "n": n_total,
        "stat": stat,
        "p_value": p,
        "significant": p < 0.05,
        "effect_name": "eta-squared",
        "effect": effect,
        "effect_size": _magnitude(effect, (0.01, 0.06, 0.14)),
    }


def chi_square_test(
    df: pd.DataFrame,
    col_a: str,
    col_b: str,
) -> dict:
    """
    Chi-square test of independence between two categorical columns.
    """
    table = pd.crosstab(df[col_a], df[col_b])
    stat, p, dof, _ = chi2_contingency(table)

    # Cramer's V: chi-square rescaled to 0-1 
    n_total = table.values.sum()
    effect = np.sqrt(stat / (n_total * (min(table.shape) - 1)))

    return {
        "test": "Chi-square",
        "stat": stat,
        "p_value": p,
        "dof": dof,
        "n": n_total,
        "significant": p < 0.05,
        "effect_name": "Cramer's V",
        "effect": effect,
        "effect_size": _magnitude(effect, (0.1, 0.3, 0.5)),
        "table": table,
    }


def spearman_summary(
    x: pd.Series,
    y: pd.Series,
    label: str = "",
) -> dict:
    """
    Spearman rank correlation between two continuous variables.
    """
    paired = pd.DataFrame({"x": x, "y": y}).dropna()
    rho, p = spearmanr(paired["x"], paired["y"])
    return {
        "test": "Spearman",
        "label": label,
        "rho": rho,
        "p_value": p,
        "n": len(paired),
        "significant": p < 0.05,
        "effect_name": "rho",
        "effect": rho,
        "effect_size": _magnitude(rho, (0.1, 0.3, 0.5)),
    }


def format_test_result(
    result: dict,
    unit: str = "",
) -> str:
    """
    Render a test result dict as a single plain-English sentence.
    """
    p = result["p_value"]
    p_str = "p < 0.001" if p < 0.001 else f"p = {p:.3f}"
    sig = "a statistically significant" if result["significant"] else "not a statistically significant"
    effect = f"{result['effect_name']} = {result['effect']:.3f} ({result['effect_size']})"

    if result["test"] == "Mann-Whitney U":
        return (
            f"{result['label_a']} (median {result['median_a']:.2f}{unit}, n={result['n_a']:,}) vs. "
            f"{result['label_b']} (median {result['median_b']:.2f}{unit}, n={result['n_b']:,}): "
            f"{sig} difference (Mann-Whitney U = {result['stat']:,.0f}, {p_str})\n"
            f"    effect size: {effect}"
        )

    if result["test"] == "Kruskal-Wallis":
        return (
            f"Across {result['n_groups']} groups: {sig} difference "
            f"(Kruskal-Wallis H = {result['stat']:.1f}, {p_str})\n"
            f"    effect size: {effect}"
        )

    if result["test"] == "Chi-square":
        return (
            f"{sig} association "
            f"(chi-square = {result['stat']:.1f}, dof = {result['dof']}, {p_str})\n"
            f"    effect size: {effect}"
        )

    if result["test"] == "Spearman":
        prefix = f"{result['label']}: " if result["label"] else ""
        return (
            f"{prefix}{sig} correlation "
            f"(Spearman rho = {result['rho']:.2f}, n={result['n']:,}, {p_str}, {result['effect_size']})"
        )

    raise ValueError(f"Unknown test type: {result['test']}")
