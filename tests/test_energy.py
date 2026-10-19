"""Testes das transições compartilhadas de energia."""

from src.energy import initial_state, transition
from src.maze import Maze


def test_movement_cost_is_applied_before_recharge_without_energy_cap() -> None:
    maze = Maze(rows=1, cols=3, start=(0, 0), goal=(0, 2), recharges={(0, 1): 5})

    state = transition(maze, initial_state(maze, energy=30), (0, 1))

    assert state is not None
    assert state.energy == 34
    assert state.recharge_mask == 1


def test_recharge_is_consumed_only_once() -> None:
    maze = Maze(rows=1, cols=4, start=(0, 0), goal=(0, 3), recharges={(0, 1): 5})
    initial = initial_state(maze, energy=2)

    first = transition(maze, initial, (0, 1))
    second = transition(maze, first, (0, 2)) if first else None
    back = transition(maze, second, (0, 1)) if second else None

    assert first is not None and first.energy == 6
    assert second is not None and second.energy == 5
    assert back is not None and back.energy == 4
    assert back.recharge_mask == first.recharge_mask


def test_arrival_at_goal_with_zero_energy_is_legal() -> None:
    maze = Maze(rows=1, cols=2, start=(0, 0), goal=(0, 1))

    state = transition(maze, initial_state(maze, energy=1), maze.goal)

    assert state is not None
    assert state.position == maze.goal
    assert state.energy == 0


def test_exhausted_robot_cannot_start_another_move() -> None:
    maze = Maze(rows=1, cols=2, start=(0, 0), goal=(0, 1))

    assert transition(maze, initial_state(maze, energy=0), maze.goal) is None


def test_diagonal_move_is_rejected() -> None:
    maze = Maze(rows=2, cols=2, start=(0, 0), goal=(1, 1))

    assert transition(maze, initial_state(maze), maze.goal) is None
