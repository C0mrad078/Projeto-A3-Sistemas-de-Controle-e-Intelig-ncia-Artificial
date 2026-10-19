"""Renderer SVG local para o tema Labirinto Clássico.

O desenho é exclusivamente visual. A matriz, os obstáculos, as recargas e os
estados recebidos são fornecidos pelo núcleo do simulador e não são alterados
por este módulo.
"""

from __future__ import annotations

from collections.abc import Iterable
from html import escape

from .maze import Maze
from .models import Position

BOARD_SIZE = 10
CELL_SIZE = 54
BOARD_X = 32
BOARD_Y = 104
PANEL_X = BOARD_X + BOARD_SIZE * CELL_SIZE + 46
SVG_WIDTH = PANEL_X + 300
SVG_HEIGHT = BOARD_Y + BOARD_SIZE * CELL_SIZE + 70


def _cell_x(col: int) -> int:
    return BOARD_X + col * CELL_SIZE


def _cell_y(row: int) -> int:
    return BOARD_Y + row * CELL_SIZE


def _cell_center(position: Position) -> tuple[int, int]:
    row, col = position
    return _cell_x(col) + CELL_SIZE // 2, _cell_y(row) + CELL_SIZE // 2


def _svg_robot(position: Position) -> str:
    center_x, center_y = _cell_center(position)
    return f"""
    <g data-layer=\"robot\" transform=\"translate({center_x - 22} {center_y - 25})\">
      <ellipse cx=\"22\" cy=\"48\" rx=\"15\" ry=\"4\" fill=\"#6caa25\" opacity=\".45\"/>
      <rect x=\"8\" y=\"24\" width=\"28\" height=\"20\" rx=\"7\" fill=\"#75c9d4\" stroke=\"#263c47\" stroke-width=\"2\"/>
      <rect x=\"11\" y=\"6\" width=\"22\" height=\"24\" rx=\"9\" fill=\"#b7e4dc\" stroke=\"#263c47\" stroke-width=\"2\"/>
      <path d=\"M16 6V2M28 6V2\" stroke=\"#263c47\" stroke-width=\"2\" stroke-linecap=\"round\"/>
      <circle cx=\"16\" cy=\"2\" r=\"2\" fill=\"#f0c33c\"/>
      <circle cx=\"28\" cy=\"2\" r=\"2\" fill=\"#f0c33c\"/>
      <circle cx=\"17\" cy=\"16\" r=\"3\" fill=\"#536c75\" stroke=\"#e5fbf4\" stroke-width=\"1\"/>
      <circle cx=\"27\" cy=\"16\" r=\"3\" fill=\"#536c75\" stroke=\"#e5fbf4\" stroke-width=\"1\"/>
      <path d=\"M18 36h8M13 44v5M31 44v5\" stroke=\"#263c47\" stroke-width=\"3\" stroke-linecap=\"round\"/>
      <path d=\"M8 29H3M36 29h5\" stroke=\"#263c47\" stroke-width=\"3\" stroke-linecap=\"round\"/>
    </g>
    """


def _svg_recharge(position: Position, value: int, consumed: bool) -> str:
    center_x, center_y = _cell_center(position)
    opacity = ".28" if consumed else "1"
    return f"""
    <g data-layer=\"recharge\" data-value=\"{value}\" data-consumed=\"{str(consumed).lower()}\" opacity=\"{opacity}\">
      <circle cx=\"{center_x}\" cy=\"{center_y}\" r=\"17\" fill=\"#f2c94c\" stroke=\"#c18d1f\" stroke-width=\"2\"/>
      <circle cx=\"{center_x - 5}\" cy=\"{center_y - 5}\" r=\"4\" fill=\"#ffe98b\" opacity=\".7\"/>
      <text x=\"{center_x}\" y=\"{center_y + 4}\" text-anchor=\"middle\" class=\"coin-label\">+{value}</text>
    </g>
    """


def _svg_obstacle(row: int, col: int) -> str:
    x, y = _cell_x(col), _cell_y(row)
    return f"""
    <g data-layer=\"obstacle\" data-cell=\"{row + 1},{col + 1}\">
      <rect x=\"{x + 1}\" y=\"{y + 1}\" width=\"{CELL_SIZE - 2}\" height=\"{CELL_SIZE - 2}\" fill=\"url(#brick-pattern)\" stroke=\"#bf756c\" stroke-width=\"1.5\"/>
    </g>
    """


def _svg_battery_icon(x: int, y: int) -> str:
    return f"""
    <g data-layer=\"energy-indicator\">
      <rect x=\"{x}\" y=\"{y}\" width=\"53\" height=\"24\" rx=\"3\" fill=\"#e9f2e8\" stroke=\"#4c5c57\" stroke-width=\"2\"/>
      <rect x=\"{x + 53}\" y=\"{y + 7}\" width=\"5\" height=\"10\" rx=\"1\" fill=\"#4c5c57\"/>
      <rect x=\"{x + 5}\" y=\"{y + 5}\" width=\"11\" height=\"14\" fill=\"#63b45b\"/>
      <rect x=\"{x + 18}\" y=\"{y + 5}\" width=\"11\" height=\"14\" fill=\"#63b45b\"/>
      <rect x=\"{x + 31}\" y=\"{y + 5}\" width=\"11\" height=\"14\" fill=\"#63b45b\"/>
    </g>
    """


def render_classic_maze(
    maze: Maze,
    *,
    explored_positions: Iterable[Position] = (),
    path: Iterable[Position] = (),
    robot_position: Position | None = None,
    energy: int = 30,
    title: str = "Robot Maze AI",
    algorithm: str = "Aguardando execução",
    moves: int | None = None,
    explored_states: int | None = None,
    recharge_effect_position: Position | None = None,
) -> str:
    """Retorna um SVG autocontido para a matriz acadêmica 10×10."""
    if (maze.rows, maze.cols) != (BOARD_SIZE, BOARD_SIZE):
        raise ValueError("O renderer clássico exige uma matriz 10x10.")

    explored = set(explored_positions)
    path_positions = tuple(path)
    path_set = set(path_positions)
    robot = robot_position if robot_position is not None else maze.start
    consumed_positions = set(maze.recharges) - set(maze.recharges)
    # O renderer não deduz consumo: a camada de apresentação recebe apenas a
    # posição do efeito. Recargas continuam visíveis para manter o mapa legível.
    del consumed_positions

    escaped_title = escape(title)
    escaped_algorithm = escape(algorithm)
    path_points = " ".join(
        f"{_cell_center(position)[0]},{_cell_center(position)[1]}"
        for position in path_positions
    )
    path_layer = (
        f'<polyline data-layer="physical-path" points="{path_points}" '
        'fill="none" stroke="#4d63c7" stroke-width="5" '
        'stroke-linecap="round" stroke-linejoin="round" opacity=".82"/>'
        if len(path_positions) > 1
        else ""
    )

    cells: list[str] = []
    overlays: list[str] = []
    recharges: list[str] = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            position = (row, col)
            x, y = _cell_x(col), _cell_y(row)
            floor = "#f4f4f4" if (row + col) % 2 else "#ffffff"
            cells.append(
                f'<rect data-cell="{row + 1},{col + 1}" data-layer="floor" '
                f'x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
                f'fill="{floor}" stroke="#202020" stroke-width="1.2"/>'
            )
            if position in explored:
                overlays.append(
                    f'<rect data-layer="virtual-exploration" x="{x + 3}" y="{y + 3}" '
                    f'width="{CELL_SIZE - 6}" height="{CELL_SIZE - 6}" '
                    'rx="4" fill="#89b9ef" opacity=".34"/>'
                )
            if position in path_set:
                overlays.append(
                    f'<rect data-layer="path-cell" x="{x + 5}" y="{y + 5}" '
                    f'width="{CELL_SIZE - 10}" height="{CELL_SIZE - 10}" '
                    'rx="5" fill="#788be0" opacity=".18"/>'
                )
            if position in maze.obstacles:
                cells.append(_svg_obstacle(row, col))
            if position in maze.recharges:
                recharges.append(
                    _svg_recharge(
                        position,
                        maze.recharges[position],
                        position == recharge_effect_position,
                    )
                )

    start_x, start_y = _cell_x(maze.start[1]), _cell_y(maze.start[0])
    goal_x, goal_y = _cell_x(maze.goal[1]), _cell_y(maze.goal[0])
    start_goal = f"""
      <g data-layer=\"start\">
        <rect x=\"{start_x + 2}\" y=\"{start_y + 2}\" width=\"{CELL_SIZE - 4}\" height=\"{CELL_SIZE - 4}\" fill=\"#6ed51c\" stroke=\"#3b8c18\" stroke-width=\"2\"/>
        <text x=\"{start_x + CELL_SIZE / 2}\" y=\"{start_y + 17}\" text-anchor=\"middle\" class=\"cell-label\">IN</text>
      </g>
      <g data-layer=\"goal\">
        <rect x=\"{goal_x + 2}\" y=\"{goal_y + 2}\" width=\"{CELL_SIZE - 4}\" height=\"{CELL_SIZE - 4}\" fill=\"#a7e94c\" stroke=\"#3b8c18\" stroke-width=\"2\"/>
        <circle cx=\"{goal_x + CELL_SIZE / 2}\" cy=\"{goal_y + CELL_SIZE / 2 + 4}\" r=\"13\" fill=\"none\" stroke=\"#426d1d\" stroke-width=\"3\"/>
        <text x=\"{goal_x + CELL_SIZE / 2}\" y=\"{goal_y + 16}\" text-anchor=\"middle\" class=\"cell-label\">OUT</text>
      </g>
    """

    side_stats = f"""
      <text x=\"{PANEL_X}\" y=\"{BOARD_Y + 60}\" class=\"panel-heading\">Execução atual</text>
      <text x=\"{PANEL_X}\" y=\"{BOARD_Y + 88}\" class=\"panel-text\">Algoritmo: {escaped_algorithm}</text>
      <text x=\"{PANEL_X}\" y=\"{BOARD_Y + 114}\" class=\"panel-text\">Movimentos: {moves if moves is not None else '—'}</text>
      <text x=\"{PANEL_X}\" y=\"{BOARD_Y + 140}\" class=\"panel-text\">Estados: {explored_states if explored_states is not None else '—'}</text>
      <text x=\"{PANEL_X}\" y=\"{BOARD_Y + 166}\" class=\"panel-text\">Energia: {energy}</text>
      <rect x=\"{PANEL_X}\" y=\"{BOARD_Y + 186}\" width=\"220\" height=\"10\" rx=\"5\" fill=\"#e5e7eb\"/>
      <rect x=\"{PANEL_X}\" y=\"{BOARD_Y + 186}\" width=\"{max(0, min(220, energy * 220 // 30))}\" height=\"10\" rx=\"5\" fill=\"#69b957\"/>
      <text x=\"{PANEL_X}\" y=\"{BOARD_Y + 240}\" class=\"panel-heading\">Legenda</text>
      <rect x=\"{PANEL_X}\" y=\"{BOARD_Y + 258}\" width=\"18\" height=\"18\" fill=\"#89b9ef\" opacity=\".55\"/>
      <text x=\"{PANEL_X + 28}\" y=\"{BOARD_Y + 272}\" class=\"panel-text\">Expansão virtual</text>
      <line x1=\"{PANEL_X}\" y1=\"{BOARD_Y + 292}\" x2=\"{PANEL_X + 18}\" y2=\"{BOARD_Y + 292}\" stroke=\"#4d63c7\" stroke-width=\"4\"/>
      <text x=\"{PANEL_X + 28}\" y=\"{BOARD_Y + 298}\" class=\"panel-text\">Caminho físico</text>
      <rect x=\"{PANEL_X}\" y=\"{BOARD_Y + 316}\" width=\"18\" height=\"18\" fill=\"url(#brick-pattern)\" stroke=\"#bf756c\"/>
      <text x=\"{PANEL_X + 28}\" y=\"{BOARD_Y + 330}\" class=\"panel-text\">Obstáculo</text>
      <circle cx=\"{PANEL_X + 9}\" cy=\"{BOARD_Y + 358}\" r=\"8\" fill=\"#f2c94c\" stroke=\"#c18d1f\"/>
      <text x=\"{PANEL_X + 28}\" y=\"{BOARD_Y + 364}\" class=\"panel-text\">Recarga +5 / +10</text>
    """

    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{SVG_WIDTH}\" height=\"{SVG_HEIGHT}\" viewBox=\"0 0 {SVG_WIDTH} {SVG_HEIGHT}\" role=\"img\" aria-label=\"{escaped_title}\" data-renderer=\"classic-10x10\">
  <defs>
    <pattern id=\"brick-pattern\" width=\"27\" height=\"18\" patternUnits=\"userSpaceOnUse\">
      <rect width=\"27\" height=\"18\" fill=\"#e7a198\"/>
      <path d=\"M0 1H27M0 17H27M13.5 1V9M0 9H27M0 9V17M27 9V17\" stroke=\"#c77b73\" stroke-width=\"1\" opacity=\".9\"/>
    </pattern>
  </defs>
  <style>
    .title {{ font: 800 29px Arial, sans-serif; fill: #111827; }}
    .subtitle {{ font: 500 15px Arial, sans-serif; fill: #6b7280; }}
    .panel-heading {{ font: 800 17px Arial, sans-serif; fill: #111827; }}
    .panel-text {{ font: 500 14px Arial, sans-serif; fill: #374151; }}
    .cell-label {{ font: 800 10px Arial, sans-serif; fill: #18310f; }}
    .coin-label {{ font: 800 10px Arial, sans-serif; fill: #634913; }}
  </style>
  <rect width=\"100%\" height=\"100%\" fill=\"#ffffff\"/>
  <text x=\"32\" y=\"40\" class=\"title\">{escaped_title}</text>
  <text x=\"32\" y=\"66\" class=\"subtitle\">Labirinto clássico · matriz 10 × 10 · entrada (1,1) · saída (10,10)</text>
  <text x=\"{PANEL_X}\" y=\"49\" class=\"panel-heading\">Energia</text>
  <text x=\"{PANEL_X + 78}\" y=\"49\" class=\"panel-text\">{energy}/30</text>
  {_svg_battery_icon(PANEL_X + 135, 27)}
  <rect x=\"{BOARD_X - 7}\" y=\"{BOARD_Y - 7}\" width=\"{BOARD_SIZE * CELL_SIZE + 14}\" height=\"{BOARD_SIZE * CELL_SIZE + 14}\" fill=\"#f8fafc\" stroke=\"#d1d5db\" stroke-width=\"2\"/>
  <g data-layer=\"grid\">{''.join(cells)}</g>
  <g data-layer=\"overlays\">{''.join(overlays)}</g>
  {path_layer}
  {start_goal}
  <g data-layer=\"recharges\">{''.join(recharges)}</g>
  {_svg_robot(robot)}
  {side_stats}
</svg>"""
