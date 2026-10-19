"""Testes da Busca A*."""

from src.astar import a_star_search
from src.bfs import breadth_first_search
from src.maze import Maze
from src.search import manhattan_distance


def test_astar_uses_manhattan_and_matches_bfs_shortest_length() -> None:
    maze = Maze(
        rows=4,
        cols=4,
        start=(0, 0),
        goal=(3, 3),
        obstacles=frozenset({(1, 1), (2, 1)}),
    )

    bfs_result = breadth_first_search(maze, initial_energy=6)
    astar_result = a_star_search(maze, initial_energy=6)

    assert manhattan_distance(maze.start, maze.goal) == 6
    assert astar_result.algorithm == "A*"
    assert astar_result.found
    assert bfs_result.found
    assert astar_result.moves == bfs_result.moves == 6
    assert astar_result.remaining_energy == 0
    assert astar_result.path[0] == maze.start
    assert astar_result.path[-1] == maze.goal
    assert len(astar_result.state_sequence) == astar_result.moves + 1


def test_astar_applies_the_shared_recharge_transition() -> None:
    maze = Maze(rows=1, cols=5, start=(0, 0), goal=(0, 4), recharges={(0, 1): 5})

    result = a_star_search(maze, initial_energy=2)

    assert result.found
    assert result.moves == 4
    assert result.remaining_energy == 3
    assert result.recharges_consumed == ((0, 1),)


def test_astar_reports_null_arrival_metrics_without_solution() -> None:
    maze = Maze(
        rows=3,
        cols=3,
        start=(0, 0),
        goal=(2, 2),
        obstacles=frozenset({(0, 1), (1, 0)}),
    )

    result = a_star_search(maze)

    assert not result.found
    assert result.moves is None
    assert result.remaining_energy is None
    assert result.path == ()
    assert result.state_sequence == ()
