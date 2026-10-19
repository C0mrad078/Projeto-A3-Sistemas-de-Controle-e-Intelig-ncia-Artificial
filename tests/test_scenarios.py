"""Testes das modalidades e do formato de cenários personalizados."""

import pytest

from src.maze import GOAL, START, Maze
from src.scenarios import (
    apply_cell_edit,
    apply_tool_edit,
    config_from_json,
    config_to_json,
    custom_scenario,
    custom_validation,
    generate_scenario,
)


@pytest.mark.parametrize(
    ("mode", "lower", "upper"),
    [("Fácil", 10, 14), ("Médio", 15, 19), ("Difícil", 20, 25)],
)
def test_difficulty_modes_respect_obstacle_ranges(mode: str, lower: int, upper: int) -> None:
    scenario = generate_scenario(mode, seed=123)

    assert lower <= scenario.obstacle_count <= upper
    assert scenario.maze.mode == mode
    scenario.maze.validate_generated_scenario()


def test_random_mode_is_reproducible_when_seed_is_provided() -> None:
    first = generate_scenario("Aleatório", seed=321)
    second = generate_scenario("Aleatório", seed=321)

    assert first == second
    assert 10 <= first.obstacle_count <= 25


def test_custom_json_round_trip_preserves_the_complete_map() -> None:
    original = custom_scenario(Maze.generate(seed=8, obstacle_count=12), seed=8)

    restored = config_from_json(config_to_json(original.maze, seed=original.seed))

    assert restored.mode == "Personalizado"
    assert restored.maze == original.maze
    assert restored.maze.start == START
    assert restored.maze.goal == GOAL


def test_cell_editor_prevents_blocking_start_and_limits_obstacles() -> None:
    maze = Maze(rows=10, cols=10, start=START, goal=GOAL)
    with pytest.raises(ValueError):
        apply_cell_edit(maze, START, "Obstáculo")

    filled = maze
    for index, position in enumerate(
        (row, col) for row in range(10) for col in range(10)
        if (row, col) not in {START, GOAL}
    ):
        if index == 25:
            break
        filled = apply_cell_edit(filled, position, "Obstáculo")
    with pytest.raises(ValueError):
        apply_cell_edit(filled, (9, 8), "Obstáculo")


def test_custom_json_rejects_wrong_recharge_counts() -> None:
    scenario = custom_scenario(Maze.generate(seed=11, obstacle_count=10), seed=11)
    payload = config_to_json(scenario.maze)
    payload = payload.replace('"valor": 10', '"valor": 5', 1)

    with pytest.raises(ValueError):
        config_from_json(payload)


def test_editor_tools_preserve_recharges_when_removing_only_an_obstacle() -> None:
    maze = Maze(
        rows=10,
        cols=10,
        start=START,
        goal=GOAL,
        obstacles={(1, 1)},
        recharges={(1, 2): 5},
    )

    edited = apply_tool_edit(maze, (1, 1), "Remover obstáculo")

    assert (1, 1) not in edited.obstacles
    assert edited.recharges[(1, 2)] == 5


def test_custom_validation_reports_all_missing_requirements() -> None:
    valid, errors = custom_validation(Maze(rows=10, cols=10, start=START, goal=GOAL))

    assert not valid
    assert any("mínimo permitido é 10" in error for error in errors)
    assert any("+5" in error for error in errors)
    assert any("+10" in error for error in errors)
