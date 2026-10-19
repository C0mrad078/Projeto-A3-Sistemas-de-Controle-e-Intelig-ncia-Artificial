"""Testes da Busca em Largura."""

from src.bfs import breadth_first_search
from src.maze import Maze


def test_bfs_finds_shortest_path_and_reconstructs_states() -> None:
    maze = Maze(rows=3, cols=3, start=(0, 0), goal=(2, 2))

    result = breadth_first_search(maze, initial_energy=4)

    assert result.algorithm == "BFS"
    assert result.found
    assert result.moves == 4
    assert result.remaining_energy == 0
    assert result.path[0] == maze.start
    assert result.path[-1] == maze.goal
    assert len(result.state_sequence) == result.moves + 1
    assert tuple(state.position for state in result.state_sequence) == result.path
    assert all(
        abs(first[0] - second[0]) + abs(first[1] - second[1]) == 1
        for first, second in zip(result.path, result.path[1:])
    )


def test_bfs_reports_no_solution_when_energy_is_insufficient() -> None:
    maze = Maze(rows=1, cols=3, start=(0, 0), goal=(0, 2))

    result = breadth_first_search(maze, initial_energy=1)

    assert not result.found
    assert result.moves is None
    assert result.remaining_energy is None
    assert result.path == ()
    assert result.state_sequence == ()
    assert result.recharges_consumed == ()
    assert result.explored_states > 0


def test_bfs_uses_recharge_to_extend_a_route() -> None:
    maze = Maze(rows=1, cols=5, start=(0, 0), goal=(0, 4), recharges={(0, 1): 5})

    result = breadth_first_search(maze, initial_energy=2)

    assert result.found
    assert result.moves == 4
    assert result.remaining_energy == 3
    assert result.recharges_consumed == ((0, 1),)
