"""Testes dos snapshots de exploração e percurso físico."""

from src.astar import a_star_search
from src.bfs import breadth_first_search
from src.maze import Maze
from src.replay import (
    EXPLORATION_PHASE,
    PHYSICAL_PHASE,
    build_replay,
    next_index,
    previous_index,
)


def test_astar_replay_contains_real_g_h_and_f_values() -> None:
    maze = Maze.generate(seed=44, obstacle_count=10)
    result = a_star_search(maze)
    replay = build_replay(maze, result)

    exploration = [event for event in replay.events if event.phase == EXPLORATION_PHASE]
    assert exploration
    assert len(exploration) == len(result.explored_sequence)
    assert all(event.g is not None and event.h is not None for event in exploration)
    assert all(event.f == event.g + event.h for event in exploration)


def test_physical_replay_preserves_energy_and_recharge_events() -> None:
    maze = Maze.generate(seed=44, obstacle_count=10)
    result = breadth_first_search(maze)
    replay = build_replay(maze, result)

    physical = [event for event in replay.events if event.phase == PHYSICAL_PHASE]
    assert result.found
    assert len(physical) == len(result.state_sequence)
    assert physical[0].physical_move == 0
    for previous, current in zip(physical, physical[1:]):
        assert current.energy_before == previous.energy
        assert current.movement_cost == 1
        assert current.energy_after == current.energy
    assert physical[-1].is_goal


def test_replay_navigation_is_bounded_and_unsolved_has_no_physical_path() -> None:
    maze = Maze(rows=2, cols=2, start=(0, 0), goal=(1, 1), obstacles={(0, 1), (1, 0)})
    result = breadth_first_search(maze)
    replay = build_replay(maze, result)

    assert all(event.phase == EXPLORATION_PHASE for event in replay.events)
    assert next_index(replay.last_index, replay) == replay.last_index
    assert previous_index(0, replay) == 0
