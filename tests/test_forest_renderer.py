"""Testes do renderer SVG da floresta."""

from src.forest_renderer import render_forest_maze
from src.maze import Maze


def test_forest_renderer_preserves_academic_elements() -> None:
    maze = Maze.generate(seed=42, obstacle_count=15)

    svg = render_forest_maze(
        maze,
        explored_positions=((0, 0),),
        path=((0, 0), (1, 0)),
        robot_position=(1, 0),
        energy=29,
        algorithm="BFS",
        moves=1,
        explored_states=2,
    )

    assert 'data-theme="floresta"' in svg
    assert 'data-renderer="forest-10x10"' in svg
    assert svg.count('data-layer="floor"') == 100
    assert svg.count('data-layer="obstacle"') == 15
    assert svg.count('data-layer="recharge"') == 8
    assert 'data-layer="grass-detail"' in svg
    assert 'data-layer="virtual-exploration"' in svg
    assert 'data-layer="physical-path"' in svg
    assert 'data-layer="robot"' in svg


def test_forest_renderer_rejects_non_academic_grid() -> None:
    maze = Maze(rows=3, cols=3, start=(0, 0), goal=(2, 2))

    try:
        render_forest_maze(maze)
    except ValueError as error:
        assert "10x10" in str(error)
    else:
        raise AssertionError("O renderer de floresta deveria exigir uma matriz 10x10.")
