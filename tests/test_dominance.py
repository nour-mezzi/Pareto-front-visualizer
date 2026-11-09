from src.dominance import dominates, pareto_front_slow, pareto_front_fast
from src.problem import generate_problem
from src.generate_solutions import random_repair


def point(p1, p2):
    return {"profit_1": p1, "profit_2": p2}


def objective_set(front):
    return {(s["profit_1"], s["profit_2"]) for s in front}


def test_dominance_true():
    assert dominates(point(10, 10), point(8, 10))


def test_dominance_false_for_tradeoff():
    assert not dominates(point(10, 5), point(8, 8))


def test_dominance_false_for_equal_points():
    assert not dominates(point(10, 10), point(10, 10))


def test_front_removes_dominated_points():
    solutions = [point(10, 10), point(8, 8), point(7, 12), point(5, 4)]
    expected = {(10, 10), (7, 12)}
    assert objective_set(pareto_front_slow(solutions)) == expected
    assert objective_set(pareto_front_fast(solutions)) == expected


def test_fast_and_slow_agree_with_duplicates():
    solutions = [
        point(10, 10), point(10, 10), point(9, 10),
        point(8, 12), point(8, 11), point(5, 20),
    ]
    assert objective_set(pareto_front_slow(solutions)) == objective_set(
        pareto_front_fast(solutions)
    )


def test_conflicting_problem_type_generates_feasible_diverse_candidates():
    problem = generate_problem(
        n_items=12,
        instance_type="conflicting",
        seed=7,
    )
    candidates = random_repair(problem, number_of_solutions=100, seed=7)

    assert len(problem.items) == 12
    assert all(candidate["feasible"] for candidate in candidates)
    assert len({tuple(candidate["selection"]) for candidate in candidates}) > 1
