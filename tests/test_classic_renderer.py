"""Testes do renderer visual clássico baseado em SVG local."""

from src.classic_renderer import render_classic_maze
from src.maze import Maze


def test_classic_renderer_produces_a_10x10_game_board() -> None:
    maze = Maze.generate(seed=42, obstacle_count=15)

    svg = render_classic_maze(
        maze,
        explored_positions=((0, 0), (1, 0)),
        path=((0, 0), (1, 0), (2, 0)),
        robot_position=(1, 0),
        energy=29,
        algorithm="BFS",
        moves=2,
        explored_states=3,
    )

    assert 'data-renderer="classic-10x10"' in svg
    assert svg.count('data-layer="floor"') == 100
    assert svg.count('data-layer="obstacle"') == 15
    assert svg.count('data-layer="recharge"') == 8
    assert 'data-layer="virtual-exploration"' in svg
    assert 'data-layer="physical-path"' in svg
    assert 'data-layer="robot"' in svg
    assert "+5" in svg and "+10" in svg


def test_classic_renderer_rejects_non_academic_grid() -> None:
    maze = Maze(rows=3, cols=3, start=(0, 0), goal=(2, 2))

    try:
        render_classic_maze(maze)
    except ValueError as error:
        assert "10x10" in str(error)
    else:
        raise AssertionError("O renderer deveria rejeitar matrizes diferentes de 10x10.")
