"""Renderer SVG local do tema Floresta."""

from __future__ import annotations

from collections.abc import Iterable
from html import escape

from .maze import Maze
from .models import Position

CELL_SIZE = 68
BOARD_X = 28
BOARD_Y = 72
GRID_SIZE = 10
BOARD_PIXELS = CELL_SIZE * GRID_SIZE
SVG_WIDTH = BOARD_X * 2 + BOARD_PIXELS
SVG_HEIGHT = BOARD_Y + BOARD_PIXELS + 72


def _x(col: int) -> int:
    return BOARD_X + col * CELL_SIZE


def _y(row: int) -> int:
    return BOARD_Y + row * CELL_SIZE


def _center(position: Position) -> tuple[int, int]:
    row, col = position
    return _x(col) + CELL_SIZE // 2, _y(row) + CELL_SIZE // 2


def _tree(row: int, col: int) -> str:
    center_x, center_y = _center((row, col))
    variant = (row * 7 + col * 3) % 3
    scale = (0.82, 0.96, 1.08)[variant]
    return f"""
    <g data-layer=\"obstacle\" data-cell=\"{row + 1},{col + 1}\" transform=\"translate({center_x} {center_y + 5}) scale({scale})\">
      <ellipse cx=\"0\" cy=\"22\" rx=\"25\" ry=\"9\" fill=\"#2d5d3e\" opacity=\".72\"/>
      <path d=\"M-8 23L-5 6H5L8 23Z\" fill=\"#c77745\" stroke=\"#4a3324\" stroke-width=\"2\"/>
      <path d=\"M0 -34L-24 0H-12L-29 18H29L12 0H24Z\" fill=\"#204e3b\" stroke=\"#132f27\" stroke-width=\"3\" stroke-linejoin=\"round\"/>
      <path d=\"M0 -27L-11 -5M-18 10H-4M9 -1l12 14\" stroke=\"#4f8c4c\" stroke-width=\"4\" stroke-linecap=\"round\" opacity=\".9\"/>
      <path d=\"M-5 22l5 -12 5 12\" fill=\"none\" stroke=\"#e59b59\" stroke-width=\"2\"/>
    </g>
    """


def _rock(row: int, col: int) -> str:
    center_x, center_y = _center((row, col))
    return f"""
    <g data-layer=\"obstacle\" data-cell=\"{row + 1},{col + 1}\">
      <ellipse cx=\"{center_x}\" cy=\"{center_y + 17}\" rx=\"25\" ry=\"7\" fill=\"#527b4b\" opacity=\".7\"/>
      <path d=\"M{center_x - 22} {center_y + 11}l8 -25 18 -7 18 16-6 19-25 4z\" fill=\"#9fae93\" stroke=\"#405b45\" stroke-width=\"3\"/>
      <path d=\"M{center_x - 10} {center_y - 15}l12 -4 7 8-20 2z\" fill=\"#c7d2b2\" opacity=\".8\"/>
    </g>
    """


def _recharge(position: Position, value: int, active: bool) -> str:
    center_x, center_y = _center(position)
    opacity = ".34" if active else "1"
    return f"""
    <g data-layer=\"recharge\" data-value=\"{value}\" opacity=\"{opacity}\">
      <ellipse cx=\"{center_x}\" cy=\"{center_y + 16}\" rx=\"20\" ry=\"7\" fill=\"#5c7c42\" opacity=\".7\"/>
      <rect x=\"{center_x - 18}\" y=\"{center_y - 15}\" width=\"36\" height=\"31\" rx=\"7\" fill=\"#8c987f\" stroke=\"#435b3e\" stroke-width=\"2\"/>
      <path d=\"M{center_x - 16} {center_y - 2}h32M{center_x - 4} {center_y - 14}v28M{center_x + 10} {center_y - 13}v27\" stroke=\"#b9c6a1\" stroke-width=\"2\" opacity=\".8\"/>
      <circle cx=\"{center_x}\" cy=\"{center_y}\" r=\"7\" fill=\"#f4d44f\" stroke=\"#fff19a\" stroke-width=\"2\"/>
      <text x=\"{center_x}\" y=\"{center_y + 3}\" text-anchor=\"middle\" class=\"value\">+{value}</text>
    </g>
    """


def _marker(position: Position, label: str, color: str) -> str:
    center_x, center_y = _center(position)
    return f"""
    <g data-layer=\"{label.lower()}\">
      <circle cx=\"{center_x}\" cy=\"{center_y}\" r=\"20\" fill=\"{color}\" stroke=\"#f9f0a5\" stroke-width=\"3\" opacity=\".9\"/>
      <circle cx=\"{center_x}\" cy=\"{center_y}\" r=\"9\" fill=\"#e8f3bd\" stroke=\"#355c36\" stroke-width=\"2\"/>
      <text x=\"{center_x}\" y=\"{center_y + 36}\" text-anchor=\"middle\" class=\"marker-label\">{label}</text>
    </g>
    """


def _robot(position: Position) -> str:
    center_x, center_y = _center(position)
    return f"""
    <g data-layer=\"robot\" transform=\"translate({center_x - 18} {center_y - 24})\">
      <ellipse cx=\"18\" cy=\"47\" rx=\"18\" ry=\"5\" fill=\"#315b3a\" opacity=\".5\"/>
      <rect x=\"2\" y=\"14\" width=\"32\" height=\"28\" rx=\"12\" fill=\"#4d9ed0\" stroke=\"#183e5b\" stroke-width=\"2\"/>
      <rect x=\"7\" y=\"20\" width=\"22\" height=\"13\" rx=\"6\" fill=\"#18364d\"/>
      <circle cx=\"14\" cy=\"26\" r=\"3\" fill=\"#e7f7e7\"/><circle cx=\"23\" cy=\"26\" r=\"3\" fill=\"#e7f7e7\"/>
      <path d=\"M18 14V7\" stroke=\"#1c5b65\" stroke-width=\"3\" stroke-linecap=\"round\"/><circle cx=\"18\" cy=\"6\" r=\"4\" fill=\"#f7d94f\"/>
      <path d=\"M8 43h7M21 43h7\" stroke=\"#183e5b\" stroke-width=\"3\" stroke-linecap=\"round\"/>
      <path d=\"M38 11l4 -5M43 14h6M38 18l4 5\" stroke=\"#f6df3d\" stroke-width=\"2\" stroke-linecap=\"round\"/>
    </g>
    """


def render_forest_maze(
    maze: Maze,
    *,
    explored_positions: Iterable[Position] = (),
    path: Iterable[Position] = (),
    robot_position: Position | None = None,
    energy: int = 30,
    title: str = "Floresta",
    algorithm: str = "Aguardando execução",
    moves: int | None = None,
    explored_states: int | None = None,
    recharge_effect_position: Position | None = None,
) -> str:
    """Retorna o cenário de floresta em SVG autocontido."""
    if (maze.rows, maze.cols) != (GRID_SIZE, GRID_SIZE):
        raise ValueError("O renderer de floresta exige uma matriz 10x10.")

    explored = set(explored_positions)
    path_positions = tuple(path)
    robot = robot_position if robot_position is not None else maze.start
    path_points = " ".join(
        f"{_center(position)[0]},{_center(position)[1]}" for position in path_positions
    )
    path_layer = (
        f'<polyline data-layer="physical-path" points="{path_points}" fill="none" '
        'stroke="#f2d37b" stroke-width="7" stroke-linecap="round" '
        'stroke-linejoin="round" opacity=".86"/>'
        if len(path_positions) > 1
        else ""
    )

    cells: list[str] = []
    overlays: list[str] = []
    obstacles: list[str] = []
    recharges: list[str] = []
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            position = (row, col)
            x, y = _x(col), _y(row)
            floor = "#7f9a32" if (row + col) % 3 else "#91a83d"
            cells.append(
                f'<rect data-layer="floor" data-cell="{row + 1},{col + 1}" '
                f'x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
                f'fill="{floor}" stroke="#657d2f" stroke-width="1.4"/>'
            )
            cells.append(
                f'<path data-layer="grass-detail" d="M{x + 12} {y + 20}l3 -6m-1 7 5 -3M{x + 46} {y + 50}l3 -6m-1 7 5 -3" stroke="#aec45a" stroke-width="2" stroke-linecap="round" opacity=".7"/>'
            )
            if position in explored:
                overlays.append(
                    f'<rect data-layer="virtual-exploration" x="{x + 4}" y="{y + 4}" '
                    f'width="{CELL_SIZE - 8}" height="{CELL_SIZE - 8}" rx="8" '
                    'fill="#f2d56d" opacity=".35"/>'
                )
            if position in maze.obstacles:
                if (row * 5 + col) % 4 == 0:
                    obstacles.append(_rock(row, col))
                else:
                    obstacles.append(_tree(row, col))
            if position in maze.recharges:
                recharges.append(
                    _recharge(
                        position,
                        maze.recharges[position],
                        position == recharge_effect_position,
                    )
                )

    escaped_title = escape(title)
    escaped_algorithm = escape(algorithm)
    start_marker = _marker(maze.start, "IN", "#e3b64e")
    goal_marker = _marker(maze.goal, "OUT", "#e6cb59")
    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{SVG_WIDTH}\" height=\"{SVG_HEIGHT}\" viewBox=\"0 0 {SVG_WIDTH} {SVG_HEIGHT}\" role=\"img\" aria-label=\"{escaped_title}\" data-theme=\"floresta\" data-renderer=\"forest-10x10\">
  <defs>
    <linearGradient id=\"forest-border\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\"><stop offset=\"0\" stop-color=\"#e1b64e\"/><stop offset=\"1\" stop-color=\"#8b742b\"/></linearGradient>
  </defs>
  <style>
    .title {{ font: 800 23px Arial, sans-serif; fill: #f8f0b4; letter-spacing: 1px; }}
    .label {{ font: 600 13px Arial, sans-serif; fill: #f5ecae; letter-spacing: .5px; }}
    .value {{ font: 800 9px Arial, sans-serif; fill: #4e4a1e; }}
    .marker-label {{ font: 800 9px Arial, sans-serif; fill: #29442c; letter-spacing: 1px; }}
  </style>
  <rect width=\"100%\" height=\"100%\" fill=\"#d5ae4b\"/>
  <rect x=\"12\" y=\"12\" width=\"{SVG_WIDTH - 24}\" height=\"{SVG_HEIGHT - 24}\" rx=\"20\" fill=\"url(#forest-border)\" stroke=\"#5f5426\" stroke-width=\"3\"/>
  <text x=\"{BOARD_X}\" y=\"42\" class=\"title\">FLORESTA</text>
  <text x=\"{BOARD_X + 180}\" y=\"42\" class=\"label\">{escaped_algorithm} · energia {energy}/30</text>
  <rect x=\"{BOARD_X + 555}\" y=\"29\" width=\"90\" height=\"10\" rx=\"5\" fill=\"#65752c\"/>
  <rect x=\"{BOARD_X + 555}\" y=\"29\" width=\"{max(0, min(90, energy * 3))}\" height=\"10\" rx=\"5\" fill=\"#f5e27b\"/>
  <rect x=\"{BOARD_X - 4}\" y=\"{BOARD_Y - 4}\" width=\"{BOARD_PIXELS + 8}\" height=\"{BOARD_PIXELS + 8}\" rx=\"10\" fill=\"#365f39\" stroke=\"#d8c461\" stroke-width=\"5\"/>
  <g data-layer=\"grid\">{''.join(cells)}</g>
  <g data-layer=\"overlays\">{''.join(overlays)}</g>
  {path_layer}
  <g data-layer=\"obstacles\">{''.join(obstacles)}</g>
  <g data-layer=\"recharges\">{''.join(recharges)}</g>
  {start_marker}
  {goal_marker}
  {_robot(robot)}
  <text x=\"{BOARD_X}\" y=\"{BOARD_Y + BOARD_PIXELS + 42}\" class=\"label\">MOVIMENTOS {moves if moves is not None else '—'} · ESTADOS {explored_states if explored_states is not None else '—'}</text>
</svg>"""
