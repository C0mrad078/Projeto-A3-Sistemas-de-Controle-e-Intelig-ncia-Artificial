"""Testes do renderer visual do labirinto."""

from matplotlib import pyplot as plt

from src.maze import Maze
from src.visualization import render_maze


def test_renderer_preserves_academic_one_based_coordinates() -> None:
    maze = Maze(rows=10, cols=10, start=(0, 0), goal=(9, 9))

    figure = render_maze(maze, explored_positions=((0, 0),), path=((0, 0), (0, 1)))
    axis = figure.axes[0]

    assert list(axis.get_xticks()) == list(range(10))
    assert list(axis.get_yticks()) == list(range(10))
    assert [label.get_text() for label in axis.get_xticklabels()] == [str(value) for value in range(1, 11)]
    assert [label.get_text() for label in axis.get_yticklabels()] == [str(value) for value in range(1, 11)]
    plt.close(figure)


def test_renderer_contains_virtual_expansion_and_physical_path_layers() -> None:
    maze = Maze(rows=3, cols=3, start=(0, 0), goal=(2, 2))

    figure = render_maze(
        maze,
        explored_positions=((0, 0), (1, 0)),
        path=((0, 0), (1, 0), (2, 0), (2, 1), (2, 2)),
        robot_position=(1, 0),
    )

    axis = figure.axes[0]
    assert len(axis.patches) == 9
    assert len(axis.lines) == 1
    assert len(axis.collections) >= 3
    plt.close(figure)


def test_renderer_accepts_all_themes_and_characters_without_changing_grid_size() -> None:
    from src.visual_config import CHARACTERS, THEMES

    maze = Maze(rows=10, cols=10, start=(0, 0), goal=(9, 9))
    for theme in THEMES:
        for character in CHARACTERS:
            figure = render_maze(
                maze,
                theme=theme,
                character=character,
                robot_position=(0, 0),
                energy=30,
                recharge_effect_position=(0, 0),
                selected_position=(1, 1),
            )
            assert len(figure.axes[0].patches) == 101
            plt.close(figure)
