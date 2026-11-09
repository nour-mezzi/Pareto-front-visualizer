# Pareto front visualizer

A small Streamlit app for exploring the **multi-objective 0/1 knapsack problem**.
It generates a knapsack instance, finds feasible selections, and plots the
trade-off between two profit measures.

## What it does

Each item has a weight, profit 1, and profit 2. The app chooses subsets of
items whose total weight stays within the capacity, then compares their two
profit totals.

The chart highlights the **Pareto front**: selections for which no other
candidate has at least as much of both profits and more of one.

## Solution methods

- **Random + Repair** builds varied feasible selections by adding items in random
  order with randomized inclusion.
- **Weighted Greedy** ranks items using a weighted combination of both profits per
  unit of weight.
- **Exact Brute Force** checks every subset. It is limited to 20 items because
  the number of subsets is `2^n`.

The first two methods are heuristics and can miss Pareto-optimal selections.
Brute force gives an exact reference for small instances.

## Quality indicators

- **Hypervolume ratio** compares the area covered by an approximate front with
  the exact front.
- **Recall** is the fraction of exact objective points found by the method.

These indicators are shown only when there are at most 20 items.

## Installation

Python 3.10 or newer is recommended.

### Windows PowerShell

```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\\Scripts\\activate.bat
```

## Start the app

From the project folder:

```bash
streamlit run app.py
```

Open the local address printed by Streamlit, usually `http://localhost:8501`.

## Run the tests

```bash
pytest -q
```

## Project layout

```text
pareto_front_visualizer/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── problem.py
│   ├── generate_solutions.py
│   ├── dominance.py
│   ├── metrics.py
│   └── visualization.py
├── tests/
│   └── test_dominance.py
```

## Notes

- Exact search is practical only for small instances.
- Pareto sorting currently supports two objectives.
- Random + Repair and Weighted Greedy do not guarantee the full front.
- The preference slider uses a normalized weighted score to help browse the front.
- The **conflicting** instance type is useful for demonstrations because its two
  profit measures favor different item profiles.
