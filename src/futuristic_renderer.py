"""Renderer SVG local do tema Laboratório Futurista."""

from __future__ import annotations

from collections.abc import Iterable
from html import escape

from .maze import Maze
from .models import Position

CELL_SIZE = 64
BOARD_X = 42
BOARD_Y = 72
GRID_SIZE = 10
BOARD_PIXELS = CELL_SIZE * GRID_SIZE
SVG_WIDTH = BOARD_X * 2 + BOARD_PIXELS
SVG_HEIGHT = BOARD_Y + BOARD_PIXELS + 78


def _x(col: int) -> int:
    return BOARD_X + col * CELL_SIZE


def _y(row: int) -> int:
    return BOARD_Y + row * CELL_SIZE


def _center(position: Position) -> tuple[int, int]:
    row, col = position
    return _x(col) + CELL_SIZE // 2, _y(row) + CELL_SIZE // 2


def _obstacle(row: int, col: int) -> str:
    x, y = _x(col), _y(row)
    return f"""
    <g data-layer=\"obstacle\" data-cell=\"{row + 1},{col + 1}\">
      <rect x=\"{x + 7}\" y=\"{y + 8}\" width=\"50\" height=\"48\" rx=\"7\" fill=\"#222845\" stroke=\"#50618d\" stroke-width=\"3\"/>
      <path d=\"M{x + 11} {y + 14}h42l-5 7h-37z\" fill=\"#72809a\" opacity=\".72\"/>
      <path d=\"M{x + 12} {y + 51}h39l-6 4h-28z\" fill=\"#11172c\" opacity=\".82\"/>
      <path d=\"M{x + 19} {y + 23}l8 8-5 8M{x + 42} {y + 20}l-5 11 7 6\" fill=\"none\" stroke=\"#39486d\" stroke-width=\"2\" opacity=\".85\"/>
    </g>
    """


def _energy_pad(position: Position, value: int, active: bool) -> str:
    center_x, center_y = _center(position)
    color = "#e0b460" if value == 10 else "#6d87c9"
    opacity = "1" if not active else ".4"
    return f"""
    <g data-layer=\"recharge\" data-value=\"{value}\" opacity=\"{opacity}\">
      <rect x=\"{center_x - 22}\" y=\"{center_y - 20}\" width=\"44\" height=\"40\" rx=\"7\" fill=\"#18213b\" stroke=\"#65739a\" stroke-width=\"2\"/>
      <rect x=\"{center_x - 16}\" y=\"{center_y - 14}\" width=\"32\" height=\"28\" rx=\"4\" fill=\"{color}\" stroke=\"#9ba8d0\" stroke-width=\"1\"/>
      <path d=\"M{center_x + 3} {center_y - 13}l-10 15h8l-4 12 12-17h-8z\" fill=\"#f7f3d2\"/>
      <text x=\"{center_x}\" y=\"{center_y + 28}\" text-anchor=\"middle\" class=\"value\">+{value}</text>
    </g>
    """


def _portal(position: Position, color: str, label: str) -> str:
    center_x, center_y = _center(position)
    return f"""
    <g data-layer=\"{label.lower()}\">
      <circle cx=\"{center_x}\" cy=\"{center_y}\" r=\"23\" fill=\"#090c1d\" stroke=\"{color}\" stroke-width=\"5\" opacity=\".95\"/>
      <circle cx=\"{center_x}\" cy=\"{center_y}\" r=\"15\" fill=\"#05050d\" stroke=\"{color}\" stroke-width=\"2\" opacity=\".9\"/>
      <path d=\"M{center_x - 27} {center_y - 10}q27 -28 54 0M{center_x - 24} {center_y + 18}q24 16 48 0\" fill=\"none\" stroke=\"{color}\" stroke-width=\"2\" opacity=\".6\"/>
      <text x=\"{center_x}\" y=\"{center_y + 39}\" text-anchor=\"middle\" class=\"portal-label\">{label}</text>
    </g>
    """


def _robot(position: Position) -> str:
    center_x, center_y = _center(position)
    return f"""
    <g data-layer=\"robot\" transform=\"translate({center_x - 23} {center_y - 26})\">
      <ellipse cx=\"23\" cy=\"53\" rx=\"17\" ry=\"5\" fill=\"#050714\" opacity=\".7\"/>
      <rect x=\"2\" y=\"9\" width=\"42\" height=\"39\" rx=\"15\" fill=\"#4d83e3\" stroke=\"#9bd1ff\" stroke-width=\"2\"/>
      <rect x=\"8\" y=\"19\" width=\"30\" height=\"18\" rx=\"9\" fill=\"#ebf9ff\"/>
      <circle cx=\"17\" cy=\"28\" r=\"4\" fill=\"#163d75\"/>
      <circle cx=\"29\" cy=\"28\" r=\"4\" fill=\"#163d75\"/>
      <path d=\"M17 6V0M29 6V0\" stroke=\"#94cfff\" stroke-width=\"3\" stroke-linecap=\"round\"/>
      <circle cx=\"17\" cy=\"0\" r=\"2\" fill=\"#ffda6a\"/><circle cx=\"29\" cy=\"0\" r=\"2\" fill=\"#ffda6a\"/>
      <path d=\"M10 45h8M28 45h8\" stroke=\"#b8e1ff\" stroke-width=\"3\" stroke-linecap=\"round\"/>
    </g>
    """


def render_futuristic_maze(
    maze: Maze,
    *,
    explored_positions: Iterable[Position] = (),
    path: Iterable[Position] = (),
    robot_position: Position | None = None,
    energy: int = 30,
    title: str = "Laboratório Futurista",
    algorithm: str = "Aguardando execução",
    moves: int | None = None,
    explored_states: int | None = None,
    recharge_effect_position: Position | None = None,
) -> str:
    """Retorna o cenário futurista em SVG autocontido."""
    if (maze.rows, maze.cols) != (GRID_SIZE, GRID_SIZE):
        raise ValueError("O renderer futurista exige uma matriz 10x10.")

    explored = set(explored_positions)
    path_positions = tuple(path)
    robot = robot_position if robot_position is not None else maze.start
    path_points = " ".join(
        f"{_center(position)[0]},{_center(position)[1]}" for position in path_positions
    )
    path_layer = (
        f'<polyline data-layer="physical-path" points="{path_points}" fill="none" '
        'stroke="#d7f6ff" stroke-width="6" stroke-linecap="round" '
        'stroke-linejoin="round" opacity=".8"/>'
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
            cells.append(
                f'<rect data-layer="floor" data-cell="{row + 1},{col + 1}" '
                f'x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
                'fill="url(#floor-pattern)" stroke="#4f6c82" stroke-width="1"/>'
            )
            if position in explored:
                overlays.append(
                    f'<rect data-layer="virtual-exploration" x="{x + 4}" y="{y + 4}" '
                    f'width="{CELL_SIZE - 8}" height="{CELL_SIZE - 8}" rx="8" '
                    'fill="#a56bf0" opacity=".22"/>'
                )
            if position in maze.obstacles:
                obstacles.append(_obstacle(row, col))
            if position in maze.recharges:
                recharges.append(
                    _energy_pad(
                        position,
                        maze.recharges[position],
                        position == recharge_effect_position,
                    )
                )

    escaped_title = escape(title)
    escaped_algorithm = escape(algorithm)
    bar_width = max(0, min(300, energy * 10))
    start_label = _portal(maze.start, "#ff7a38", "IN")
    goal_label = _portal(maze.goal, "#42e7ef", "OUT")
    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{SVG_WIDTH}\" height=\"{SVG_HEIGHT}\" viewBox=\"0 0 {SVG_WIDTH} {SVG_HEIGHT}\" role=\"img\" aria-label=\"{escaped_title}\" data-theme=\"laboratorio\" data-renderer=\"futuristic-10x10\">
  <defs>
    <linearGradient id=\"background-gradient\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\">
      <stop offset=\"0\" stop-color=\"#20142d\"/><stop offset=\"1\" stop-color=\"#090812\"/>
    </linearGradient>
    <linearGradient id=\"frame-gradient\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\">
      <stop offset=\"0\" stop-color=\"#657f91\"/><stop offset=\"1\" stop-color=\"#30476b\"/>
    </linearGradient>
    <pattern id=\"floor-pattern\" width=\"32\" height=\"32\" patternUnits=\"userSpaceOnUse\">
      <rect width=\"32\" height=\"32\" fill=\"#668692\"/>
      <path d=\"M0 1h32M1 0v32M16 0v7M0 16h7M31 18h-8M18 31v-8\" stroke=\"#87a5aa\" stroke-width=\"1\" opacity=\".22\"/>
    </pattern>
  </defs>
  <style>
    .title {{ font: 800 24px Arial, sans-serif; fill: #e7f7fa; letter-spacing: 1px; }}
    .label {{ font: 600 13px Arial, sans-serif; fill: #a8c8d7; letter-spacing: .8px; }}
    .value {{ font: 800 10px Arial, sans-serif; fill: #faf2b9; }}
    .portal-label {{ font: 800 9px Arial, sans-serif; fill: #d9f9ff; letter-spacing: 1px; }}
  </style>
  <rect width=\"100%\" height=\"100%\" fill=\"url(#background-gradient)\"/>
  <rect x=\"14\" y=\"14\" width=\"{SVG_WIDTH - 28}\" height=\"{SVG_HEIGHT - 28}\" rx=\"30\" fill=\"none\" stroke=\"#46506e\" stroke-width=\"2\" opacity=\".8\"/>
  <text x=\"{BOARD_X}\" y=\"38\" class=\"title\">LABORATÓRIO FUTURISTA</text>
  <text x=\"{BOARD_X + 394}\" y=\"38\" class=\"label\">{escaped_algorithm} · energia {energy}/30</text>
  <rect x=\"{BOARD_X + 560}\" y=\"25\" width=\"100\" height=\"10\" rx=\"5\" fill=\"#1a2741\" stroke=\"#4d668b\"/>
  <rect x=\"{BOARD_X + 560}\" y=\"25\" width=\"{bar_width}\" height=\"10\" rx=\"5\" fill=\"#63dce7\"/>
  <rect x=\"{BOARD_X - 9}\" y=\"{BOARD_Y - 9}\" width=\"{BOARD_PIXELS + 18}\" height=\"{BOARD_PIXELS + 18}\" rx=\"18\" fill=\"url(#frame-gradient)\" stroke=\"#1f3659\" stroke-width=\"7\"/>
  <g data-layer=\"grid\">{''.join(cells)}</g>
  <g data-layer=\"overlays\">{''.join(overlays)}</g>
  {path_layer}
  <g data-layer=\"obstacles\">{''.join(obstacles)}</g>
  <g data-layer=\"recharges\">{''.join(recharges)}</g>
  {start_label}
  {goal_label}
  {_robot(robot)}
  <text x=\"{BOARD_X}\" y=\"{BOARD_Y + BOARD_PIXELS + 45}\" class=\"label\">MOVIMENTOS {moves if moves is not None else '—'} · ESTADOS {explored_states if explored_states is not None else '—'}</text>
</svg>"""
