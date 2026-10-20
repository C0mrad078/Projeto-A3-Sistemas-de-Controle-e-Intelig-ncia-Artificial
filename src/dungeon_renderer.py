"""Renderer SVG local do tema Dungeon Pixel Art."""

from __future__ import annotations

from collections.abc import Iterable
from html import escape

from .maze import Maze
from .models import Position

CELL_SIZE = 64
BOARD_X = 52
BOARD_Y = 76
GRID_SIZE = 10
BOARD_PIXELS = CELL_SIZE * GRID_SIZE
SVG_WIDTH = BOARD_X * 2 + BOARD_PIXELS
SVG_HEIGHT = BOARD_Y + BOARD_PIXELS + 80


def _x(col: int) -> int:
    return BOARD_X + col * CELL_SIZE


def _y(row: int) -> int:
    return BOARD_Y + row * CELL_SIZE


def _center(position: Position) -> tuple[int, int]:
    row, col = position
    return _x(col) + CELL_SIZE // 2, _y(row) + CELL_SIZE // 2


def _stone_block(x: int, y: int, width: int, height: int, layer: str, cell: str = "") -> str:
    return f"""
    <g data-layer=\"{layer}\"{f' data-cell=\"{cell}\"' if cell else ''} shape-rendering=\"crispEdges\">
      <rect x=\"{x}\" y=\"{y}\" width=\"{width}\" height=\"{height}\" fill=\"#363b4d\" stroke=\"#171b2a\" stroke-width=\"3\"/>
      <path d=\"M{x + 4} {y + 6}h{width - 8}M{x + 6} {y + height - 7}h{width - 12}\" stroke=\"#596074\" stroke-width=\"3\" opacity=\".8\"/>
      <path d=\"M{x + width // 3} {y + 9}l-5 12 7 6M{x + width - 17} {y + height - 22}l-8 7 5 6\" stroke=\"#1f2538\" stroke-width=\"2\" fill=\"none\"/>
      <rect x=\"{x + 5}\" y=\"{y + 4}\" width=\"8\" height=\"4\" fill=\"#73798a\" opacity=\".7\"/>
    </g>
    """


def _obstacle(row: int, col: int) -> str:
    return _stone_block(
        _x(col) + 7,
        _y(row) + 7,
        CELL_SIZE - 14,
        CELL_SIZE - 14,
        "obstacle",
        f"{row + 1},{col + 1}",
    )


def _border() -> str:
    tiles: list[str] = []
    for col in range(GRID_SIZE):
        tiles.append(_stone_block(_x(col), _y(0) - 34, CELL_SIZE, 30, "border"))
        tiles.append(_stone_block(_x(col), _y(GRID_SIZE - 1) + CELL_SIZE + 4, CELL_SIZE, 30, "border"))
    for row in range(1, GRID_SIZE - 1):
        tiles.append(_stone_block(_x(0) - 34, _y(row), 30, CELL_SIZE, "border"))
        tiles.append(_stone_block(_x(GRID_SIZE - 1) + CELL_SIZE + 4, _y(row), 30, CELL_SIZE, "border"))
    return "".join(tiles)


def _energy_pad(position: Position, value: int, active: bool) -> str:
    center_x, center_y = _center(position)
    fill = "#b9c0cb" if value == 10 else "#59627c"
    opacity = ".35" if active else "1"
    return f"""
    <g data-layer=\"recharge\" data-value=\"{value}\" opacity=\"{opacity}\" shape-rendering=\"crispEdges\">
      <rect x=\"{center_x - 21}\" y=\"{center_y - 21}\" width=\"42\" height=\"42\" rx=\"3\" fill=\"#20263a\" stroke=\"#797e8e\" stroke-width=\"3\"/>
      <rect x=\"{center_x - 15}\" y=\"{center_y - 15}\" width=\"30\" height=\"30\" rx=\"2\" fill=\"{fill}\" stroke=\"#d8d9d2\" stroke-width=\"2\"/>
      <path d=\"M{center_x + 4} {center_y - 16}l-11 16h8l-5 15 14-19h-8z\" fill=\"#ffe47c\"/>
      <text x=\"{center_x}\" y=\"{center_y + 32}\" text-anchor=\"middle\" class=\"value\">+{value}</text>
    </g>
    """


def _portal(position: Position, color: str, label: str) -> str:
    center_x, center_y = _center(position)
    return f"""
    <g data-layer=\"{label.lower()}\" shape-rendering=\"crispEdges\">
      <path d=\"M{center_x - 23} {center_y}l7 -17h32l7 17-7 17h-32z\" fill=\"#0f1020\" stroke=\"{color}\" stroke-width=\"4\" opacity=\".95\"/>
      <rect x=\"{center_x - 11}\" y=\"{center_y - 11}\" width=\"22\" height=\"22\" fill=\"#04050d\" stroke=\"{color}\" stroke-width=\"3\"/>
      <path d=\"M{center_x - 28} {center_y - 7}h7M{center_x + 21} {center_y + 7}h7\" stroke=\"{color}\" stroke-width=\"3\"/>
      <text x=\"{center_x}\" y=\"{center_y + 34}\" text-anchor=\"middle\" class=\"portal-label\">{label}</text>
    </g>
    """


def _robot(position: Position) -> str:
    center_x, center_y = _center(position)
    return f"""
    <g data-layer=\"robot\" transform=\"translate({center_x - 22} {center_y - 25})\" shape-rendering=\"crispEdges\">
      <rect x=\"5\" y=\"8\" width=\"34\" height=\"36\" rx=\"5\" fill=\"#3d7fd7\" stroke=\"#a6c8ff\" stroke-width=\"3\"/>
      <rect x=\"10\" y=\"17\" width=\"24\" height=\"15\" rx=\"3\" fill=\"#eff9ff\"/>
      <rect x=\"14\" y=\"21\" width=\"5\" height=\"5\" fill=\"#1b355b\"/><rect x=\"25\" y=\"21\" width=\"5\" height=\"5\" fill=\"#1b355b\"/>
      <rect x=\"17\" y=\"3\" width=\"13\" height=\"5\" fill=\"#a6c8ff\"/><rect x=\"20\" y=\"0\" width=\"7\" height=\"4\" fill=\"#ffe277\"/>
      <rect x=\"8\" y=\"44\" width=\"10\" height=\"4\" fill=\"#1c355a\"/><rect x=\"26\" y=\"44\" width=\"10\" height=\"4\" fill=\"#1c355a\"/>
    </g>
    """


def render_dungeon_maze(
    maze: Maze,
    *,
    explored_positions: Iterable[Position] = (),
    path: Iterable[Position] = (),
    robot_position: Position | None = None,
    energy: int = 30,
    title: str = "Dungeon Pixel Art",
    algorithm: str = "Aguardando execução",
    moves: int | None = None,
    explored_states: int | None = None,
    recharge_effect_position: Position | None = None,
) -> str:
    """Retorna o cenário de dungeon pixel-art em SVG autocontido."""
    if (maze.rows, maze.cols) != (GRID_SIZE, GRID_SIZE):
        raise ValueError("O renderer de dungeon exige uma matriz 10x10.")

    explored = set(explored_positions)
    path_positions = tuple(path)
    robot = robot_position if robot_position is not None else maze.start
    path_points = " ".join(
        f"{_center(position)[0]},{_center(position)[1]}" for position in path_positions
    )
    path_layer = (
        f'<polyline data-layer="physical-path" points="{path_points}" fill="none" '
        'stroke="#f6db62" stroke-width="6" stroke-linecap="square" '
        'stroke-linejoin="miter" opacity=".86"/>'
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
                f'fill="url(#dungeon-floor)" stroke="#2d4c55" stroke-width="2"/>'
            )
            if position in explored:
                overlays.append(
                    f'<rect data-layer="virtual-exploration" x="{x + 5}" y="{y + 5}" '
                    f'width="{CELL_SIZE - 10}" height="{CELL_SIZE - 10}" '
                    'fill="#7e6cae" opacity=".28"/>'
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
    start = _portal(maze.start, "#f09a56", "IN")
    goal = _portal(maze.goal, "#38dce6", "OUT")
    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{SVG_WIDTH}\" height=\"{SVG_HEIGHT}\" viewBox=\"0 0 {SVG_WIDTH} {SVG_HEIGHT}\" role=\"img\" aria-label=\"{escaped_title}\" data-theme=\"dungeon\" data-renderer=\"dungeon-10x10\">
  <defs>
    <linearGradient id=\"dungeon-bg\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#373552\"/><stop offset=\"1\" stop-color=\"#19182a\"/></linearGradient>
    <pattern id=\"dungeon-floor\" width=\"32\" height=\"32\" patternUnits=\"userSpaceOnUse\">
      <rect width=\"32\" height=\"32\" fill=\"#4f7777\"/>
      <path d=\"M0 2h32M2 0v32M15 1v7M1 16h8M30 18h-7M18 31v-8\" stroke=\"#84a6a0\" stroke-width=\"1\" opacity=\".4\"/>
    </pattern>
  </defs>
  <style>
    .title {{ font: 800 23px monospace; fill: #f2e7c9; letter-spacing: 1px; }}
    .label {{ font: 700 13px monospace; fill: #c4d6ce; letter-spacing: .5px; }}
    .value {{ font: 800 9px monospace; fill: #fff0a4; }}
    .portal-label {{ font: 800 9px monospace; fill: #e5fbff; letter-spacing: 1px; }}
  </style>
  <rect width=\"100%\" height=\"100%\" fill=\"url(#dungeon-bg)\"/>
  <rect x=\"18\" y=\"18\" width=\"{SVG_WIDTH - 36}\" height=\"{SVG_HEIGHT - 36}\" rx=\"34\" fill=\"none\" stroke=\"#5b5773\" stroke-width=\"3\"/>
  <text x=\"{BOARD_X}\" y=\"34\" class=\"title\">DUNGEON PIXEL ART</text>
  <text x=\"{BOARD_X + 365}\" y=\"34\" class=\"label\">{escaped_algorithm} · ENERGIA {energy}/30</text>
  <rect x=\"{BOARD_X - 35}\" y=\"{BOARD_Y - 35}\" width=\"{BOARD_PIXELS + 70}\" height=\"{BOARD_PIXELS + 70}\" rx=\"14\" fill=\"#20263a\" stroke=\"#63758c\" stroke-width=\"6\"/>
  {_border()}
  <g data-layer=\"grid\">{''.join(cells)}</g>
  <g data-layer=\"overlays\">{''.join(overlays)}</g>
  {path_layer}
  <g data-layer=\"obstacles\">{''.join(obstacles)}</g>
  <g data-layer=\"recharges\">{''.join(recharges)}</g>
  {start}
  {goal}
  {_robot(robot)}
  <text x=\"{BOARD_X}\" y=\"{BOARD_Y + BOARD_PIXELS + 58}\" class=\"label\">MOVIMENTOS {moves if moves is not None else '—'} · ESTADOS {explored_states if explored_states is not None else '—'}</text>
</svg>"""
