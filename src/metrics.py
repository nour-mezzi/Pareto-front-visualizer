"""Quality indicators for comparing approximate Pareto fronts."""


def hypervolume_2d(front, reference=(0, 0)):
    """
    Calculate the exact 2D hypervolume for a non-dominated max/max front.

    The reference point should be no better than the solutions, normally (0, 0)
    when both profits are positive.
    """
    ref_x, ref_y = reference
    points = [
        (s["profit_1"], s["profit_2"])
        for s in front
        if s["profit_1"] > ref_x and s["profit_2"] > ref_y
    ]

    if not points:
        return 0.0

    # Keep the best y for each x, then sort from low x to high x.
    best_by_x = {}
    for x, y in points:
        best_by_x[x] = max(best_by_x.get(x, float("-inf")), y)

    ordered = sorted(best_by_x.items())
    area = 0.0
    previous_x = ref_x

    for x, y in ordered:
        area += (x - previous_x) * (y - ref_y)
        previous_x = x

    return float(area)


def recall_against_exact(approximate_front, exact_front):
    """Fraction of exact-front objective points present in the approximate set."""
    exact_points = {
        (s["profit_1"], s["profit_2"]) for s in exact_front
    }
    if not exact_points:
        return 1.0

    approximate_points = {
        (s["profit_1"], s["profit_2"]) for s in approximate_front
    }
    return len(exact_points & approximate_points) / len(exact_points)


def compare_fronts(approximate_front, exact_front):
    exact_hv = hypervolume_2d(exact_front)
    approximate_hv = hypervolume_2d(approximate_front)
    hv_ratio = approximate_hv / exact_hv if exact_hv > 0 else 1.0

    return {
        "approximate_hypervolume": approximate_hv,
        "exact_hypervolume": exact_hv,
        "hypervolume_ratio": min(hv_ratio, 1.0),
        "recall": recall_against_exact(approximate_front, exact_front),
    }
