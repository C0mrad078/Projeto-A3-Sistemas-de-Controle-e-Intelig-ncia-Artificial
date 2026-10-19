"""Renderização do labirinto para o dashboard e exportações PNG."""

from __future__ import annotations

from collections.abc import Iterable

import matplotlib

matplotlib.use("Agg", force=True)

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.pyplot import subplots

from .maze import Maze
from .models import Position

COLOR_BACKGROUND = "#F8FAFC"
COLOR_EXPLORED = "#BFDBFE"
COLOR_PATH = "#8B5CF6"
COLOR_ROBOT = "#10B981"
COLOR_OBSTACLE = "#1F2937"
COLOR_RECHARGE_5 = "#FDE68A"
COLOR_RECHARGE_10 = "#FDBA74"
COLOR_START = "#2563EB"
COLOR_GOAL = "#DC2626"


def _add_legend(ax: Axes) -> None:
    handles = [
        Patch(facecolor=COLOR_EXPLORED, edgecolor="none", label="Expansão virtual"),
        Line2D([0], [0], color=COLOR_PATH, linewidth=3, label="Caminho físico"),
        Patch(facecolor=COLOR_OBSTACLE, label="Obstáculo"),
        Patch(facecolor=COLOR_RECHARGE_5, label="Recarga +5"),
        Patch(facecolor=COLOR_RECHARGE_10, label="Recarga +10"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLOR_START, label="Entrada", markersize=9),
        Line2D([0], [0], marker="X", color="w", markerfacecolor=COLOR_GOAL, label="Saída", markersize=9),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3, frameon=False)


def render_maze(
    maze: Maze,
    *,
    explored_positions: Iterable[Position] = (),
    path: Iterable[Position] = (),
    robot_position: Position | None = None,
    title: str | None = None,
) -> Figure:
    """Cria uma figura com expansão virtual e percurso efetivo separados."""
    explored = set(explored_positions)
    path_positions = tuple(path)
    figure, axis = subplots(figsize=(7, 7))
    axis.set_facecolor(COLOR_BACKGROUND)

    for row in range(maze.rows):
        for col in range(maze.cols):
            position = (row, col)
            color = COLOR_BACKGROUND
            if position in explored:
                color = COLOR_EXPLORED
            if position in maze.recharges:
                color = (
                    COLOR_RECHARGE_5
                    if maze.recharges[position] == 5
                    else COLOR_RECHARGE_10
                )
            if position in maze.obstacles:
                color = COLOR_OBSTACLE
            axis.add_patch(
                Rectangle(
                    (col - 0.5, row - 0.5),
                    1,
                    1,
                    facecolor=color,
                    edgecolor="white",
                    linewidth=1.2,
                )
            )

    if len(path_positions) > 1:
        path_columns = [position[1] for position in path_positions]
        path_rows = [position[0] for position in path_positions]
        axis.plot(path_columns, path_rows, color=COLOR_PATH, linewidth=3, zorder=3)

    axis.scatter(
        [maze.start[1]], [maze.start[0]],
        color=COLOR_START, marker="o", s=180, edgecolors="white", linewidths=1.5, zorder=5,
    )
    axis.scatter(
        [maze.goal[1]], [maze.goal[0]],
        color=COLOR_GOAL, marker="X", s=180, edgecolors="white", linewidths=1.5, zorder=5,
    )

    if robot_position is not None:
        axis.scatter(
            [robot_position[1]], [robot_position[0]],
            color=COLOR_ROBOT, marker="o", s=230, edgecolors="white", linewidths=2, zorder=6,
        )

    axis.set_xlim(-0.5, maze.cols - 0.5)
    axis.set_ylim(maze.rows - 0.5, -0.5)
    axis.set_xticks(range(maze.cols), labels=range(1, maze.cols + 1))
    axis.set_yticks(range(maze.rows), labels=range(1, maze.rows + 1))
    axis.set_xlabel("Coluna")
    axis.set_ylabel("Linha")
    axis.set_title(title or "Labirinto Robot Maze AI")
    axis.grid(False)
    _add_legend(axis)
    figure.tight_layout()
    return figure
