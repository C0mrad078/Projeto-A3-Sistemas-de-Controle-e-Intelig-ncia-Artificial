"""Testes dos indicadores e gráficos do painel de análise."""

from src.astar import a_star_search
from src.bfs import breadth_first_search
from src.dashboard_analysis import (
    comparison_table,
    energy_rows,
    geometric_shortest_path,
    interpret_results,
    scenario_indicators,
)
from src.maze import Maze


def test_geometric_indicators_are_separate_from_energy_search() -> None:
    maze = Maze(rows=3, cols=3, start=(0, 0), goal=(2, 2), obstacles={(1, 1)})

    path = geometric_shortest_path(maze)
    indicators = scenario_indicators(maze)

    assert path is not None
    assert len(path) - 1 == 4
    assert indicators["distancia_manhattan"] == 4
    assert indicators["distancia_geometrica_minima"] == 4
    assert indicators["caminho_geometrico_existe"] is True


def test_energy_rows_use_the_actual_search_state_sequence() -> None:
    maze = Maze.generate(seed=73, obstacle_count=10)
    results = {"BFS": breadth_first_search(maze), "A*": a_star_search(maze)}
    solved = next(result for result in results.values() if result.found)

    rows = energy_rows(maze, solved)

    assert len(rows) == solved.moves
    assert rows[0]["energia_antes"] == 30
    assert rows[-1]["energia_depois"] == solved.remaining_energy
    assert all(row["custo_movimento"] == 1 for row in rows)


def test_comparison_table_labels_missing_solution_as_not_applicable() -> None:
    maze = Maze(rows=2, cols=2, start=(0, 0), goal=(1, 1), obstacles={(0, 1), (1, 0)})
    results = {"BFS": breadth_first_search(maze), "A*": a_star_search(maze)}

    table = comparison_table(results)

    assert table.loc[0, "BFS"] == "Não"
    assert table.loc[1, "BFS"] == "Não aplicável"


def test_interpretation_is_deterministic_and_result_dependent() -> None:
    maze = Maze.generate(seed=73, obstacle_count=10)
    results = {"BFS": breadth_first_search(maze), "A*": a_star_search(maze)}

    first = interpret_results(results)
    second = interpret_results(results)

    assert first == second
    assert any("estado" in message.lower() for message in first)
