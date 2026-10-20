"""Testes do renderer SVG do laboratório futurista."""

from src.futuristic_renderer import render_futuristic_maze
from src.maze import Maze


def test_futuristic_renderer_preserves_the_academic_grid() -> None:
    maze = Maze.generate(seed=42, obstacle_count=15)

    svg = render_futuristic_maze(
        maze,
        explored_positions=((0, 0),),
        path=((0, 0), (0, 1)),
        robot_position=(0, 1),
        energy=29,
        algorithm="A*",
        moves=1,
        explored_states=2,
    )

    assert 'data-theme="laboratorio"' in svg
    assert 'data-renderer="futuristic-10x10"' in svg
    assert svg.count('data-layer="floor"') == 100
    assert svg.count('data-layer="obstacle"') == 15
    assert svg.count('data-layer="recharge"') == 8
    assert 'data-layer="virtual-exploration"' in svg
    assert 'data-layer="physical-path"' in svg
    assert 'data-layer="robot"' in svg


def test_futuristic_renderer_rejects_non_academic_grid() -> None:
    maze = Maze(rows=3, cols=3, start=(0, 0), goal=(2, 2))

    try:
        render_futuristic_maze(maze)
    except ValueError as error:
        assert "10x10" in str(error)
    else:
        raise AssertionError("O renderer futurista deveria exigir uma matriz 10x10.")
