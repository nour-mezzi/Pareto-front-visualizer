"""Methods that generate feasible candidate solutions."""

import numpy as np
from .problem import evaluate_solution


def random_repair(problem, number_of_solutions=300, seed=42):
    """
    Build random solutions without exceeding capacity.

    Items are considered in random order and added whenever they fit.
    This is a simple baseline, not an advanced optimizer.
    """
    rng = np.random.default_rng(seed)
    solutions = []
    n = problem.number_of_items

    for _ in range(number_of_solutions):
        selection = [0] * n
        current_weight = 0
        order = rng.permutation(n)

        for index in order:
            item_weight = problem.items[int(index)]["weight"]
            # Vary inclusion probability so candidates cover both sparse and
            # dense selections instead of filling the knapsack every time.
            if (
                rng.random() < 0.65
                and current_weight + item_weight <= problem.capacity
            ):
                selection[int(index)] = 1
                current_weight += item_weight

        solutions.append(evaluate_solution(selection, problem))

    return solutions


def weighted_greedy(problem, lambdas=None):
    """
    Build solutions using a weighted combination of the two profits.

    lambda=1 focuses on profit 1; lambda=0 focuses on profit 2.
    Values between 0 and 1 balance the objectives.
    """
    if lambdas is None:
        lambdas = np.linspace(0.0, 1.0, 21)

    max_p1 = max(item["profit_1"] for item in problem.items) or 1
    max_p2 = max(item["profit_2"] for item in problem.items) or 1
    solutions = []

    for weight_1 in lambdas:
        weight_2 = 1.0 - float(weight_1)

        ranked_items = sorted(
            problem.items,
            key=lambda item: (
                weight_1 * item["profit_1"] / max_p1
                + weight_2 * item["profit_2"] / max_p2
            ) / item["weight"],
            reverse=True,
        )

        selection = [0] * problem.number_of_items
        current_weight = 0

        for item in ranked_items:
            if current_weight + item["weight"] <= problem.capacity:
                selection[item["item_id"] - 1] = 1
                current_weight += item["weight"]

        solutions.append(evaluate_solution(selection, problem))

    return solutions


def brute_force(problem, max_items=20):
    """
    Enumerate every possible subset and keep feasible solutions.

    This requires 2**n evaluations, so we deliberately limit n.
    """
    n = problem.number_of_items
    if n > max_items:
        raise ValueError(
            f"Brute force is limited to {max_items} items; this problem has {n}."
        )

    solutions = []
    for mask in range(1 << n):
        selection = [(mask >> bit) & 1 for bit in range(n)]
        result = evaluate_solution(selection, problem)
        if result["feasible"]:
            solutions.append(result)

    return solutions


def remove_duplicate_selections(solutions):
    """Keep only one copy of each exact item selection."""
    unique = {}
    for solution in solutions:
        key = tuple(solution["selection"])
        unique[key] = solution
    return list(unique.values())
