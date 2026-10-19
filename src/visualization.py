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
from .visual_config import CharacterSpec, ThemeSpec, get_character, get_theme

COLOR_BACKGROUND = "#F8FAFC"
COLOR_EXPLORED = "#BFDBFE"
COLOR_PATH = "#8B5CF6"
COLOR_ROBOT = "#10B981"
COLOR_OBSTACLE = "#1F2937"
COLOR_RECHARGE_5 = "#FDE68A"
COLOR_RECHARGE_10 = "#FDBA74"
COLOR_START = "#2563EB"
COLOR_GOAL = "#DC2626"


def _add_legend(ax: Axes, theme: ThemeSpec) -> None:
    handles = [
        Patch(facecolor=theme.explored_color, edgecolor="none", label="Expansão virtual"),
        Line2D([0], [0], color=theme.path_color, linewidth=3, label="Caminho físico"),
        Patch(facecolor=theme.obstacle_color, label="Obstáculo"),
        Patch(facecolor=theme.recharge_5_color, label="Recarga +5"),
        Patch(facecolor=theme.recharge_10_color, label="Recarga +10"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=theme.start_color, label="Entrada", markersize=9),
        Line2D([0], [0], marker="X", color="w", markerfacecolor=theme.goal_color, label="Saída", markersize=9),
    ]
    ax.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.08),
        ncol=3,
        frameon=False,
        labelcolor=theme.text_color,
    )


def render_maze(
    maze: Maze,
    *,
    explored_positions: Iterable[Position] = (),
    path: Iterable[Position] = (),
    robot_position: Position | None = None,
    title: str | None = None,
    theme: str | ThemeSpec = "classico",
    character: str | CharacterSpec = "classico",
    energy: int | None = None,
    recharge_effect_position: Position | None = None,
    selected_position: Position | None = None,
    state_label: str | None = None,
) -> Figure:
    """Cria uma figura 2D tematizada sem alterar o labirinto lógico.

    Os argumentos visuais são opcionais para manter compatibilidade com a
    renderização acadêmica existente e nunca são consultados pelos algoritmos.
    """
    theme_spec = get_theme(theme) if isinstance(theme, str) else theme
    character_spec = get_character(character) if isinstance(character, str) else character
    explored = set(explored_positions)
    path_positions = tuple(path)
    figure, axis = subplots(figsize=(7, 7))
    axis.set_facecolor(theme_spec.floor_color)

    for row in range(maze.rows):
        for col in range(maze.cols):
            position = (row, col)
            color = (
                theme_spec.floor_color
                if (row + col) % 2 == 0
                else theme_spec.floor_alt_color
            )
            if position in explored:
                color = theme_spec.explored_color
            if position in maze.recharges:
                color = (
                    theme_spec.recharge_5_color
                    if maze.recharges[position] == 5
                    else theme_spec.recharge_10_color
                )
            if position in maze.obstacles:
                color = theme_spec.obstacle_color
            axis.add_patch(
                Rectangle(
                    (col - 0.5, row - 0.5),
                    1,
                    1,
                    facecolor=color,
                    edgecolor=theme_spec.grid_color,
                    linewidth=1.2,
                )
            )
            if position in maze.recharges:
                value = maze.recharges[position]
                axis.text(
                    col,
                    row,
                    f"+{value}",
                    ha="center",
                    va="center",
                    fontsize=8,
                    fontweight="bold",
                    color=theme_spec.text_color,
                    zorder=4,
                )

    if selected_position is not None and maze.in_bounds(selected_position):
        axis.add_patch(
            Rectangle(
                (selected_position[1] - 0.46, selected_position[0] - 0.46),
                0.92,
                0.92,
                fill=False,
                edgecolor="#FACC15",
                linewidth=3,
                zorder=7,
            )
        )

    if len(path_positions) > 1:
        path_columns = [position[1] for position in path_positions]
        path_rows = [position[0] for position in path_positions]
        axis.plot(path_columns, path_rows, color=COLOR_PATH, linewidth=3, zorder=3)

    axis.scatter(
        [maze.start[1]], [maze.start[0]],
        color=theme_spec.start_color, marker="o", s=180, edgecolors=theme_spec.text_color, linewidths=1.5, zorder=5,
    )
    axis.scatter(
        [maze.goal[1]], [maze.goal[0]],
        color=theme_spec.goal_color, marker="X", s=180, edgecolors=theme_spec.text_color, linewidths=1.5, zorder=5,
    )
    axis.text(maze.start[1], maze.start[0], "I", ha="center", va="center", color=theme_spec.text_color, fontweight="bold", zorder=6)
    axis.text(maze.goal[1], maze.goal[0], "S", ha="center", va="center", color=theme_spec.text_color, fontweight="bold", zorder=6)

    if robot_position is not None:
        marker = {"circular": "o", "hexagonal": "D", "square": "s", "friendly": "o"}.get(
            character_spec.style, "o"
        )
        axis.scatter(
            [robot_position[1]], [robot_position[0]],
            color=character_spec.primary_color,
            marker=marker,
            s=250,
            edgecolors=character_spec.accent_color,
            linewidths=2,
            zorder=6,
        )
        axis.text(
            robot_position[1],
            robot_position[0],
            character_spec.glyph,
            ha="center",
            va="center",
            color=character_spec.accent_color,
            fontsize=10,
            fontweight="bold",
            zorder=7,
        )

    if recharge_effect_position is not None and maze.in_bounds(recharge_effect_position):
        axis.scatter(
            [recharge_effect_position[1]],
            [recharge_effect_position[0]],
            s=600,
            facecolors="none",
            edgecolors=theme_spec.recharge_10_color,
            linewidths=2.5,
            zorder=8,
        )

    axis.set_xlim(-0.5, maze.cols - 0.5)
    axis.set_ylim(maze.rows - 0.5, -0.5)
    axis.set_xticks(range(maze.cols), labels=range(1, maze.cols + 1))
    axis.set_yticks(range(maze.rows), labels=range(1, maze.rows + 1))
    axis.set_xlabel("Coluna")
    axis.set_ylabel("Linha")
    axis.set_title(title or "Labirinto Robot Maze AI")
    axis.grid(False)
    axis.tick_params(colors=theme_spec.text_color)
    axis.xaxis.label.set_color(theme_spec.text_color)
    axis.yaxis.label.set_color(theme_spec.text_color)
    if energy is not None:
        axis.text(
            0.01,
            1.03,
            f"⚡ Energia: {energy}",
            transform=axis.transAxes,
            color=theme_spec.text_color,
            fontweight="bold",
        )
    if state_label:
        axis.text(
            0.99,
            1.03,
            state_label,
            transform=axis.transAxes,
            ha="right",
            color=theme_spec.text_color,
        )
    _add_legend(axis, theme_spec)
    figure.tight_layout()
    return figure
