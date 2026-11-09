import pandas as pd
import streamlit as st

from src.problem import generate_problem, selection_to_items
from src.generate_solutions import (
    random_repair,
    weighted_greedy,
    brute_force,
    remove_duplicate_selections,
)
from src.dominance import get_pareto_front
from src.metrics import compare_fronts
from src.visualization import plot_front


st.set_page_config(
    page_title="Pareto Front Visualizer",
    page_icon="PF",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }
    [data-testid="stSidebar"] {
        border-right: 1px solid #e5e7eb;
    }
    [data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #111827;
    }
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricLabel"],
    [data-testid="stMetric"] [data-testid="stMetricValue"],
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #111827 !important;
    }
    [data-testid="stMetric"] svg {
        fill: #111827;
    }
    .app-kicker {
        color: #64748b;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="app-kicker">Multi-objective knapsack</div>', unsafe_allow_html=True)
st.title("Pareto front visualizer")
st.write(
    "Compare feasible item selections when two profit measures compete for the same capacity."
)

with st.sidebar:
    st.header("Problem")
    n_items = st.slider("Number of items", 5, 100, 20)
    instance_type = st.selectbox(
        "Instance type",
        ["conflicting", "uncorrelated", "correlated"],
        help="Uncorrelated profits are generated independently. "
             "Correlated profits tend to increase with item weight. "
             "Conflicting profits create a more visible trade-off curve.",
    )
    tightness = st.slider(
        "Capacity tightness",
        min_value=0.1,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Capacity as a fraction of the sum of all item weights.",
    )
    seed = st.number_input("Random seed", min_value=0, value=42, step=1)

    st.divider()
    st.header("Solutions")
    method = st.selectbox(
        "Method",
        ["Random + Repair", "Weighted Greedy", "Exact Brute Force"],
    )
    random_count = st.select_slider(
        "Number of random candidates",
        options=[50, 100, 300, 500, 1000, 3000],
        value=300,
    )
    run_button = st.button("Generate and analyze", type="primary", use_container_width=True)

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if run_button:
    problem = generate_problem(
        n_items=int(n_items),
        instance_type=instance_type,
        tightness=float(tightness),
        seed=int(seed),
    )

    if method == "Random + Repair":
        candidates = random_repair(
            problem, number_of_solutions=int(random_count), seed=int(seed)
        )
    elif method == "Weighted Greedy":
        candidates = weighted_greedy(problem)
    else:
        if n_items > 20:
            st.error(
                "Exact Brute Force is limited to 20 items because it checks "
                "every possible subset. Reduce the number of items to 20 or fewer."
            )
            st.stop()
        candidates = brute_force(problem)

    candidates = remove_duplicate_selections(candidates)
    front = get_pareto_front(candidates)

    # For small instances, calculate the exact front as a reference for metrics.
    exact_front = None
    if n_items <= 20 and method != "Exact Brute Force":
        exact_candidates = brute_force(problem)
        exact_front = get_pareto_front(exact_candidates)

    st.session_state.analysis = {
        "problem": problem,
        "method": method,
        "candidates": candidates,
        "front": front,
        "exact_front": exact_front,
    }

analysis = st.session_state.analysis

if analysis is None:
    st.info(
        "Set the problem and solution method in the sidebar, then run an analysis."
    )
    st.subheader("About the chart")
    st.write(
        "Each dot is a feasible selection. The highlighted points are not "
        "dominated by another candidate in both profit measures."
    )
else:
    problem = analysis["problem"]
    candidates = analysis["candidates"]
    front = analysis["front"]
    exact_front = analysis["exact_front"]

    st.subheader("Problem overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Number of items", problem.number_of_items)
    c2.metric("Capacity", f'{problem.capacity:,}')
    c3.metric("Candidate solutions", f"{len(candidates):,}")
    c4.metric("Pareto solutions", f"{len(front):,}")

    with st.expander("See the generated items"):
        st.dataframe(pd.DataFrame(problem.items), use_container_width=True)

    st.subheader("Pareto front")
    fig = plot_front(
        candidates,
        front,
        title=f"Knapsack Pareto front — {analysis['method']}",
    )
    st.pyplot(fig, use_container_width=True)

    st.caption(
        "Points farther right and higher up have larger values for both profits. "
        "The front shows the available trade-offs rather than one universal winner."
    )

    if exact_front is not None:
        metrics = compare_fronts(front, exact_front)
        st.subheader("Quality compared with the exact front")
        m1, m2, m3 = st.columns(3)
        m1.metric("Hypervolume ratio", f"{metrics['hypervolume_ratio']:.3f}")
        m2.metric("Recall", f"{metrics['recall']:.1%}")
        m3.metric("Exact front points", len(exact_front))
        st.caption(
            "The hypervolume ratio compares the area covered by this method with "
            "the exact front. Recall is the share of exact objective points found."
        )
    elif problem.number_of_items > 20:
        st.info(
            "No exact reference front is shown above 20 items because exhaustive "
            "search grows exponentially."
        )

    st.subheader("Explore a solution")
    if front:
        front_sorted = sorted(front, key=lambda s: (s["profit_1"], s["profit_2"]))
        selected_index = st.slider(
            "Choose a Pareto solution",
            min_value=0,
            max_value=len(front_sorted) - 1,
            value=0,
        )
        chosen = front_sorted[selected_index]
        a, b, c, d = st.columns(4)
        a.metric("Profit 1", chosen["profit_1"])
        b.metric("Profit 2", chosen["profit_2"])
        c.metric("Total weight", chosen["weight"])
        d.metric("Capacity used", f"{chosen['weight'] / problem.capacity:.1%}")

        selected_items = selection_to_items(chosen["selection"], problem)
        st.write("**Selected items**")
        if selected_items:
            st.dataframe(pd.DataFrame(selected_items), use_container_width=True)
        else:
            st.write("This solution selects no items.")

    st.subheader("Choose your preferred balance")
    preference = st.slider(
        "Importance of profit 1",
        min_value=0,
        max_value=100,
        value=50,
        help="0 means focus on profit 2; 100 means focus on profit 1.",
    )
    if front:
        max_p1 = max(s["profit_1"] for s in front) or 1
        max_p2 = max(s["profit_2"] for s in front) or 1
        w1 = preference / 100
        w2 = 1 - w1
        recommended = max(
            front,
            key=lambda s: (
                w1 * s["profit_1"] / max_p1
                + w2 * s["profit_2"] / max_p2
            ),
        )
        st.write(
            f"With this preference, a balanced choice has profit 1 = "
            f"**{recommended['profit_1']}**, profit 2 = "
            f"**{recommended['profit_2']}**, and weight = **{recommended['weight']}**."
        )
        st.caption(
            "This score is a way to browse the trade-offs; it is not an objective "
            "ranking of the solutions."
        )

    st.subheader("Download results")
    front_df = pd.DataFrame(front)
    st.download_button(
        "Download Pareto front as CSV",
        data=front_df.to_csv(index=False).encode("utf-8"),
        file_name="pareto_front.csv",
        mime="text/csv",
    )
