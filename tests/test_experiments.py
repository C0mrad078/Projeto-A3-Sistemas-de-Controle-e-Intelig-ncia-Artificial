"""Testes do laboratório de experimentos."""

import pytest

from src.experiments import records_to_rows, run_experiments


def test_experiments_are_reproducible_by_seed() -> None:
    first = run_experiments(10, seed_start=500)
    second = run_experiments(10, seed_start=500)

    first_rows = records_to_rows(first)
    second_rows = records_to_rows(second)
    for first_row, second_row in zip(first_rows, second_rows):
        assert {
            key: value for key, value in first_row.items() if key != "tempo_execucao_ms"
        } == {
            key: value for key, value in second_row.items() if key != "tempo_execucao_ms"
        }


def test_each_scenario_uses_the_same_maze_for_bfs_and_astar() -> None:
    records = run_experiments(10, seed_start=700)

    for scenario_id in range(1, 11):
        pair = [record for record in records if record.scenario_id == scenario_id]
        assert {record.algorithm for record in pair} == {"BFS", "A*"}
        assert len({record.seed for record in pair}) == 1
        assert len({record.obstacle_count for record in pair}) == 1


def test_experiment_metrics_are_consistent_and_progress_is_reported() -> None:
    progress: list[tuple[int, int]] = []
    records = run_experiments(
        10,
        seed_start=900,
        progress_callback=lambda completed, total: progress.append((completed, total)),
    )

    assert len(records) == 20
    assert progress[0] == (1, 20)
    assert progress[-1] == (20, 20)
    for record in records:
        assert record.explored_states >= 1
        assert record.execution_time_ms >= 0
        assert 0 <= record.recharges_used <= 8
        if record.found:
            assert record.moves is not None
            assert record.remaining_energy is not None
        else:
            assert record.moves is None
            assert record.remaining_energy is None


def test_only_official_batch_sizes_are_allowed() -> None:
    with pytest.raises(ValueError):
        run_experiments(5)
