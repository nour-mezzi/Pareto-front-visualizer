"""Create and evaluate Multi-Objective 0/1 Knapsack Problem instances."""

from dataclasses import dataclass
from typing import List, Dict, Any
import numpy as np


@dataclass
class KnapsackProblem:
    items: List[Dict[str, int]]
    capacity: int

    @property
    def number_of_items(self) -> int:
        return len(self.items)


def generate_problem(
    n_items: int = 20,
    instance_type: str = "uncorrelated",
    tightness: float = 0.5,
    seed: int = 42,
) -> KnapsackProblem:
    """
    Generate an instance with one weight and two profits per item.

    tightness controls the capacity as a fraction of the sum of all weights.
    """
    if n_items < 1:
        raise ValueError("n_items must be at least 1.")
    if not 0.1 <= tightness <= 1.0:
        raise ValueError("tightness must be between 0.1 and 1.0.")

    rng = np.random.default_rng(seed)
    weights = rng.integers(10, 101, size=n_items)

    if instance_type == "uncorrelated":
        profit_1 = rng.integers(10, 151, size=n_items)
        profit_2 = rng.integers(10, 151, size=n_items)
    elif instance_type == "correlated":
        # Both profits tend to increase with item weight, with some noise.
        noise_1 = rng.integers(-20, 41, size=n_items)
        noise_2 = rng.integers(-20, 41, size=n_items)
        profit_1 = np.maximum(1, weights + noise_1)
        profit_2 = np.maximum(1, weights + noise_2)
    elif instance_type == "conflicting":
        # Give lighter items an advantage in one objective and heavier items
        # an advantage in the other, producing a wider trade-off curve.
        scale = np.linspace(1.0, 0.35, n_items)
        reverse_scale = scale[::-1]
        profit_1 = np.maximum(
            1,
            np.rint(weights * scale + rng.integers(10, 51, size=n_items)),
        )
        profit_2 = np.maximum(
            1,
            np.rint(weights * reverse_scale + rng.integers(10, 51, size=n_items)),
        )
    else:
        raise ValueError(
            "instance_type must be 'uncorrelated', 'correlated', or 'conflicting'."
        )

    items = [
        {
            "item_id": i + 1,
            "weight": int(weights[i]),
            "profit_1": int(profit_1[i]),
            "profit_2": int(profit_2[i]),
        }
        for i in range(n_items)
    ]

    capacity = max(1, int(round(float(weights.sum()) * tightness)))
    return KnapsackProblem(items=items, capacity=capacity)


def evaluate_solution(selection, problem: KnapsackProblem) -> Dict[str, Any]:
    """Calculate total weight and both profits for a 0/1 selection vector."""
    if len(selection) != problem.number_of_items:
        raise ValueError("The selection vector length must match the item count.")

    selected = [int(bool(value)) for value in selection]
    total_weight = sum(
        item["weight"] * chosen for item, chosen in zip(problem.items, selected)
    )
    total_profit_1 = sum(
        item["profit_1"] * chosen for item, chosen in zip(problem.items, selected)
    )
    total_profit_2 = sum(
        item["profit_2"] * chosen for item, chosen in zip(problem.items, selected)
    )

    return {
        "selection": selected,
        "weight": total_weight,
        "profit_1": total_profit_1,
        "profit_2": total_profit_2,
        "feasible": total_weight <= problem.capacity,
    }


def selection_to_items(selection, problem: KnapsackProblem):
    """Return the actual item records selected by a binary vector."""
    return [
        item for item, chosen in zip(problem.items, selection) if int(chosen) == 1
    ]
