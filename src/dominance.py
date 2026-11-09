"""Pareto dominance and non-dominated sorting for two maximization objectives."""


def dominates(a, b):
    """
    Return True if a is at least as good as b in both profits
    and strictly better in at least one.
    """
    no_worse = (
        a["profit_1"] >= b["profit_1"]
        and a["profit_2"] >= b["profit_2"]
    )
    strictly_better = (
        a["profit_1"] > b["profit_1"]
        or a["profit_2"] > b["profit_2"]
    )
    return no_worse and strictly_better


def pareto_front_slow(solutions):
    """Simple pairwise method. Easy to understand, but O(N squared)."""
    front = []
    for i, candidate in enumerate(solutions):
        is_dominated = False
        for j, other in enumerate(solutions):
            if i != j and dominates(other, candidate):
                is_dominated = True
                break
        if not is_dominated:
            front.append(candidate)
    return front


def pareto_front_fast(solutions):
    """
    Faster two-objective sweep: O(N log N) for sorting plus a linear scan.

    Solutions with identical objective values are all retained, matching
    the strict definition of dominance used above.
    """
    if not solutions:
        return []

    indexed = list(enumerate(solutions))
    indexed.sort(
        key=lambda pair: (
            -pair[1]["profit_1"],
            -pair[1]["profit_2"],
            pair[0],
        )
    )

    front = []
    best_profit_2_from_higher_profit_1 = float("-inf")
    i = 0

    while i < len(indexed):
        current_profit_1 = indexed[i][1]["profit_1"]
        group = []

        while (
            i < len(indexed)
            and indexed[i][1]["profit_1"] == current_profit_1
        ):
            group.append(indexed[i][1])
            i += 1

        group_best_profit_2 = max(s["profit_2"] for s in group)

        # A point is dominated by a point with a strictly larger profit_1
        # if that earlier point has at least as much profit_2.
        if group_best_profit_2 > best_profit_2_from_higher_profit_1:
            for solution in group:
                if solution["profit_2"] == group_best_profit_2:
                    front.append(solution)

        best_profit_2_from_higher_profit_1 = max(
            best_profit_2_from_higher_profit_1,
            group_best_profit_2,
        )

    return front


def get_pareto_front(solutions, method="fast"):
    if method == "slow":
        return pareto_front_slow(solutions)
    return pareto_front_fast(solutions)
