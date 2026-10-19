"""Verificações dos artefatos finais versionados."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).parents[1]


def test_final_experiment_artifacts_are_present_and_complete() -> None:
    experiments = pd.read_csv(ROOT / "results" / "experimentos_finais.csv")
    summary = pd.read_csv(ROOT / "results" / "resumo_finais.csv")

    assert len(experiments) == 180
    assert len(summary) == 6
    assert set(experiments["lote"]) == {10, 30, 50}
    assert set(experiments["algorithm"]) == {"BFS", "A*"}
    assert experiments["seed"].nunique() == 90
    assert all(experiments["estados_explorados"] >= 1)


def test_report_and_comparison_images_are_valid_files() -> None:
    report = ROOT / "docs" / "relatorio_robot_maze_ai.pdf"

    assert report.read_bytes().startswith(b"%PDF")
    for batch_size in (10, 30, 50):
        image = ROOT / "results" / f"comparacao_lote_{batch_size}.png"
        assert image.read_bytes().startswith(b"\x89PNG")
