"""Testes das exportações de resultados e gráficos."""

from matplotlib import pyplot as plt

from src.analysis import comparison_summary
from src.export import (
    dataframe_to_csv_bytes,
    figure_to_png_bytes,
    records_to_csv_bytes,
    save_experiment_csv,
    save_figure_png,
)
from src.experiments import records_to_dataframe, run_experiments
from src.visualization import render_maze
from src.maze import Maze


def test_csv_and_png_exports_contain_real_data(tmp_path) -> None:
    records = run_experiments(10, seed_start=1700)
    dataframe = records_to_dataframe(records)
    figure = render_maze(Maze.generate(seed=1700))

    csv_bytes = records_to_csv_bytes(records)
    summary_bytes = dataframe_to_csv_bytes(comparison_summary(dataframe))
    png_bytes = figure_to_png_bytes(figure)
    csv_path = save_experiment_csv(records, output_dir=tmp_path)
    png_path = save_figure_png(figure, output_dir=tmp_path)

    assert b"scenario_id" in csv_bytes
    assert b"encontrou_solucao" in csv_bytes
    assert b"algoritmo" in summary_bytes
    assert png_bytes.startswith(b"\x89PNG")
    assert csv_path.read_bytes() == csv_bytes
    assert png_path.read_bytes() == png_bytes
    plt.close(figure)
