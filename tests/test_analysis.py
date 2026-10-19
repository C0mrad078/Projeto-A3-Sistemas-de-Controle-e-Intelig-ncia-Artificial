"""Testes das agregações e gráficos experimentais."""

from matplotlib import pyplot as plt

from src.analysis import (
    build_comparison_figure,
    comparison_summary,
    jointly_solved_scenario_ids,
)
from src.experiments import records_to_dataframe, run_experiments


def test_summary_and_joint_success_filter_use_real_experiment_records() -> None:
    records = run_experiments(10, seed_start=1400)
    frame = records_to_dataframe(records)

    summary = comparison_summary(frame)

    assert list(summary["algoritmo"]) == ["BFS", "A*"]
    assert all(summary["cenarios"] == 10)
    assert all(summary["sucessos"] <= summary["cenarios"])
    assert jointly_solved_scenario_ids(frame).issubset(set(range(1, 11)))


def test_comparison_figure_has_five_requested_metrics() -> None:
    records = run_experiments(10, seed_start=1500)
    frame = records_to_dataframe(records)

    figure = build_comparison_figure(frame)

    assert len(figure.axes) == 6
    assert figure.axes[-1].axison is False
    plt.close(figure)
