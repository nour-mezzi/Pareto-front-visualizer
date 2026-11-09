"""Matplotlib charts used by the Streamlit interface."""

import matplotlib.pyplot as plt


def plot_front(all_solutions, front, title="Knapsack Pareto Front"):
    fig, ax = plt.subplots(figsize=(9, 5.5))

    if all_solutions:
        ax.scatter(
            [s["profit_1"] for s in all_solutions],
            [s["profit_2"] for s in all_solutions],
            label="Candidate solutions",
            alpha=0.35,
            s=28,
        )

    if front:
        ordered = sorted(front, key=lambda s: s["profit_1"])
        x = [s["profit_1"] for s in ordered]
        y = [s["profit_2"] for s in ordered]
        ax.scatter(x, y, label="Pareto front", s=65, zorder=3)
        ax.plot(x, y, alpha=0.7, zorder=2)

    ax.set_title(title)
    ax.set_xlabel("Total profit 1")
    ax.set_ylabel("Total profit 2")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    return fig
