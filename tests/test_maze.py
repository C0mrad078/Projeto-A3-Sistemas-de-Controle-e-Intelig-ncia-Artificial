"""Testes do gerador e das consultas do labirinto."""

import pytest

from src.maze import GOAL, START, Maze, validate_maze


def test_generated_maze_obeys_official_constraints() -> None:
    maze = Maze.generate(seed=42)

    assert (maze.rows, maze.cols) == (10, 10)
    assert maze.start == START == (0, 0)
    assert maze.goal == GOAL == (9, 9)
    assert 10 <= len(maze.obstacles) <= 25
    assert len(maze.recharges) == 8
    assert sum(value == 5 for value in maze.recharges.values()) == 5
    assert sum(value == 10 for value in maze.recharges.values()) == 3
    assert not maze.obstacles & set(maze.recharges)
    assert not {maze.start, maze.goal} & maze.obstacles
    assert not {maze.start, maze.goal} & set(maze.recharges)


def test_same_seed_reconstructs_exact_scenario() -> None:
    assert Maze.generate(seed=7) == Maze.generate(seed=7)


def test_invalid_obstacle_count_is_rejected() -> None:
    with pytest.raises(ValueError):
        Maze.generate(seed=1, obstacle_count=9)

    with pytest.raises(ValueError):
        Maze.generate(seed=1, obstacle_count=26)


def test_neighbors_are_orthogonal_and_skip_obstacles() -> None:
    maze = Maze(
        rows=3,
        cols=3,
        start=(0, 0),
        goal=(2, 2),
        obstacles=frozenset({(0, 1), (1, 0)}),
    )

    assert maze.neighbors((0, 0)) == ()
    assert maze.neighbors((1, 1)) == ((2, 1), (1, 2))
    assert all(abs(row - 1) + abs(col - 1) == 1 for row, col in maze.neighbors((1, 1)))


def test_validate_maze_accepts_structurally_valid_controlled_map() -> None:
    maze = Maze(rows=2, cols=2, start=(0, 0), goal=(1, 1))

    validate_maze(maze)
