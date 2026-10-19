"""Casos extremos e verificações independentes de optimalidade."""

import pytest

from src.astar import a_star_search
from src.bfs import breadth_first_search
from src.energy import initial_state, transition
from src.maze import Maze


def test_obstacles_can_completely_block_the_goal() -> None:
    maze = Maze(
        rows=3,
        cols=3,
        start=(0, 0),
        goal=(2, 2),
        obstacles=frozenset({(0, 1), (1, 0)}),
    )

    bfs_result = breadth_first_search(maze)
    astar_result = a_star_search(maze)

    assert not bfs_result.found
    assert not astar_result.found
    assert bfs_result.moves is None
    assert astar_result.remaining_energy is None


def test_energy_insufficiency_is_not_confused_with_obstacle_failure() -> None:
    maze = Maze(rows=1, cols=3, start=(0, 0), goal=(0, 2))

    result = breadth_first_search(maze, initial_energy=1)

    assert not result.found
    assert result.explored_states >= 1
    assert result.path == ()


def test_returning_to_a_cell_with_different_energy_is_a_new_full_state() -> None:
    maze = Maze(rows=1, cols=3, start=(0, 0), goal=(0, 2), recharges={(0, 1): 5})
    first = transition(maze, initial_state(maze, energy=2), (0, 1))
    second = transition(maze, first, (0, 2)) if first else None
    returned = transition(maze, second, (0, 1)) if second else None

    assert first is not None and second is not None and returned is not None
    assert first.position == returned.position
    assert first.energy != returned.energy
    assert first.recharge_mask == returned.recharge_mask
    assert first != returned


@pytest.mark.parametrize("seed", (101, 202, 303, 404))
def test_bfs_and_astar_match_minimum_length_across_seeds(seed: int) -> None:
    maze = Maze.generate(seed=seed, obstacle_count=10)

    bfs_result = breadth_first_search(maze)
    astar_result = a_star_search(maze)

    assert bfs_result.found == astar_result.found
    if bfs_result.found and astar_result.found:
        assert bfs_result.moves == astar_result.moves


def test_multiple_minimum_paths_can_have_different_recharge_outcomes() -> None:
    maze = Maze(
        rows=3,
        cols=3,
        start=(0, 0),
        goal=(2, 2),
        recharges={(0, 1): 5, (1, 0): 10},
    )

    bfs_result = breadth_first_search(maze, initial_energy=4)
    astar_result = a_star_search(maze, initial_energy=4)

    assert bfs_result.found and astar_result.found
    assert bfs_result.moves == astar_result.moves == 4
    assert bfs_result.remaining_energy is not None
    assert astar_result.remaining_energy is not None
    assert bfs_result.remaining_energy in {5, 10}
    assert astar_result.remaining_energy in {5, 10}
