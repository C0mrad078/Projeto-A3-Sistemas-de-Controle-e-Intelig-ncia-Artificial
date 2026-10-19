"""Modalidades de geração e configuração de cenários oficiais."""

from __future__ import annotations

import json
from dataclasses import dataclass
from random import SystemRandom
from typing import Any, Mapping

from .maze import (
    GOAL,
    MAX_OBSTACLES,
    MIN_OBSTACLES,
    START,
    Maze,
)
from .models import Position

DIFFICULTY_MODES = ("Fácil", "Médio", "Difícil")
GENERATION_MODES = DIFFICULTY_MODES + ("Aleatório", "Personalizado")
DIFFICULTY_RANGES: dict[str, tuple[int, int]] = {
    "Fácil": (10, 14),
    "Médio": (15, 19),
    "Difícil": (20, 25),
}
CELL_KINDS = ("Livre", "Obstáculo", "Recarga +5", "Recarga +10")
EDITOR_TOOLS = (
    "Selecionar célula",
    "Adicionar obstáculo",
    "Remover obstáculo",
    "Adicionar recarga +5",
    "Adicionar recarga +10",
    "Remover elemento",
)


@dataclass(frozen=True, slots=True)
class Scenario:
    """Cenário com metadados usados pela interface e pelos experimentos."""

    maze: Maze
    mode: str
    seed: int | None
    obstacle_count: int
    scenario_id: str


def validate_mode(mode: str) -> None:
    if mode not in GENERATION_MODES:
        raise ValueError(f"Modalidade inválida: {mode!r}.")


def obstacle_range(mode: str) -> tuple[int, int]:
    """Retorna os limites de obstáculos da modalidade selecionada."""
    validate_mode(mode)
    return DIFFICULTY_RANGES.get(mode, (MIN_OBSTACLES, MAX_OBSTACLES))


def _resolve_seed(seed: int | None) -> int:
    return seed if seed is not None else SystemRandom().randrange(0, 2**31)


def generate_scenario(
    mode: str,
    *,
    seed: int | None = None,
    obstacle_count: int | None = None,
    scenario_id: str | None = None,
) -> Scenario:
    """Gera um cenário conforme uma das cinco modalidades oficiais.

    ``seed=None`` usa uma semente nova e não previsível a cada geração. Quando
    uma semente é informada, a matriz e a quantidade sorteada são reproduzíveis.
    O modo Personalizado é reservado para um mapa já editado/importado.
    """
    validate_mode(mode)
    if mode == "Personalizado":
        raise ValueError("Use custom_scenario para construir o modo Personalizado.")

    resolved_seed = _resolve_seed(seed)
    lower, upper = obstacle_range(mode)
    if obstacle_count is None:
        from random import Random

        count = Random(resolved_seed).randint(lower, upper)
    else:
        count = obstacle_count
    if not lower <= count <= upper:
        raise ValueError(
            f"A modalidade {mode} aceita entre {lower} e {upper} obstáculos."
        )
    identifier = scenario_id or f"{mode.lower()}-{resolved_seed}-{count}"
    maze = Maze.generate(
        seed=resolved_seed,
        obstacle_count=count,
        mode=mode,
        scenario_id=identifier,
    )
    return Scenario(maze, mode, resolved_seed, count, identifier)


def custom_scenario(
    maze: Maze,
    *,
    seed: int | None = None,
    scenario_id: str | None = None,
) -> Scenario:
    """Valida um mapa oficial e o identifica como Personalizado."""
    maze.validate_generated_scenario()
    identifier = scenario_id or f"personalizado-{seed if seed is not None else 'manual'}"
    custom_maze = Maze(
        rows=maze.rows,
        cols=maze.cols,
        start=maze.start,
        goal=maze.goal,
        obstacles=maze.obstacles,
        recharges=maze.recharges,
        seed=seed,
        mode="Personalizado",
        scenario_id=identifier,
    )
    return Scenario(custom_maze, "Personalizado", seed, len(custom_maze.obstacles), identifier)


def custom_validation(maze: Maze) -> tuple[bool, tuple[str, ...]]:
    """Valida o mapa editável sem lançar exceção na interface."""
    errors: list[str] = []
    if (maze.rows, maze.cols) != (10, 10):
        errors.append("A matriz precisa ser 10x10.")
    if maze.start != START:
        errors.append("A entrada precisa permanecer em (1,1).")
    if maze.goal != GOAL:
        errors.append("A saída precisa permanecer em (10,10).")
    if len(maze.obstacles) < MIN_OBSTACLES:
        errors.append(f"Você adicionou {len(maze.obstacles)} obstáculos. O mínimo permitido é 10.")
    elif len(maze.obstacles) > MAX_OBSTACLES:
        errors.append("O máximo permitido é 25 obstáculos.")
    recharge_5 = sum(value == 5 for value in maze.recharges.values())
    recharge_10 = sum(value == 10 for value in maze.recharges.values())
    if recharge_5 != 5:
        difference = 5 - recharge_5
        errors.append(
            f"É necessário posicionar mais {difference} pontos de energia +5."
            if difference > 0
            else "Há pontos de energia +5 em excesso; o total deve ser 5."
        )
    if recharge_10 != 3:
        difference = 3 - recharge_10
        errors.append(
            f"É necessário posicionar mais {difference} pontos de energia +10."
            if difference > 0
            else "Há pontos de energia +10 em excesso; o total deve ser 3."
        )
    try:
        maze._validate_structure()
    except ValueError as error:
        errors.append(str(error))
    return not errors, tuple(errors)


def apply_cell_edit(maze: Maze, position: Position, kind: str) -> Maze:
    """Aplica uma edição de célula, permitindo estado temporário incompleto."""
    if kind not in CELL_KINDS:
        raise ValueError(f"Tipo de célula inválido: {kind!r}.")
    if not maze.in_bounds(position):
        raise ValueError("A célula editada precisa estar dentro da matriz.")
    if position in {maze.start, maze.goal} and kind != "Livre":
        raise ValueError("Entrada e saída devem permanecer livres.")

    obstacles = set(maze.obstacles)
    recharges = dict(maze.recharges)
    obstacles.discard(position)
    recharges.pop(position, None)
    if kind == "Obstáculo":
        if len(obstacles) >= MAX_OBSTACLES:
            raise ValueError("O cenário não pode ter mais de 25 obstáculos.")
        obstacles.add(position)
    elif kind == "Recarga +5":
        recharges[position] = 5
    elif kind == "Recarga +10":
        recharges[position] = 10
    return Maze(
        rows=maze.rows,
        cols=maze.cols,
        start=maze.start,
        goal=maze.goal,
        obstacles=obstacles,
        recharges=recharges,
        seed=maze.seed,
        mode="Personalizado",
        scenario_id=maze.scenario_id,
    )


def apply_tool_edit(maze: Maze, position: Position, tool: str) -> Maze:
    """Aplica uma ferramenta do editor sem confundir remoção de obstáculo com recarga."""
    if tool not in EDITOR_TOOLS:
        raise ValueError(f"Ferramenta de edição inválida: {tool!r}.")
    if tool == "Selecionar célula":
        return maze
    if tool == "Adicionar obstáculo":
        return apply_cell_edit(maze, position, "Obstáculo")
    if tool == "Adicionar recarga +5":
        return apply_cell_edit(maze, position, "Recarga +5")
    if tool == "Adicionar recarga +10":
        return apply_cell_edit(maze, position, "Recarga +10")
    if tool == "Remover elemento":
        return apply_cell_edit(maze, position, "Livre")
    if position not in maze.obstacles:
        return maze
    obstacles = set(maze.obstacles)
    obstacles.remove(position)
    return Maze(
        rows=maze.rows,
        cols=maze.cols,
        start=maze.start,
        goal=maze.goal,
        obstacles=obstacles,
        recharges=maze.recharges,
        seed=maze.seed,
        mode="Personalizado",
        scenario_id=maze.scenario_id,
    )


def _position_to_json(position: Position) -> dict[str, int]:
    return {"linha": position[0] + 1, "coluna": position[1] + 1}


def maze_to_config(
    maze: Maze, *, mode: str | None = None, seed: int | None = None
) -> dict[str, Any]:
    """Serializa um mapa com coordenadas acadêmicas de 1 a 10."""
    return {
        "versao": 1,
        "modalidade": mode or maze.mode,
        "semente": seed if seed is not None else maze.seed,
        "identificador": maze.scenario_id,
        "dimensoes": {"linhas": maze.rows, "colunas": maze.cols},
        "entrada": _position_to_json(maze.start),
        "saida": _position_to_json(maze.goal),
        "obstaculos": [_position_to_json(position) for position in sorted(maze.obstacles)],
        "recargas": [
            {**_position_to_json(position), "valor": value}
            for position, value in sorted(maze.recharges.items())
        ],
    }


def config_to_json(maze: Maze, *, mode: str | None = None, seed: int | None = None) -> str:
    return json.dumps(maze_to_config(maze, mode=mode, seed=seed), ensure_ascii=False, indent=2)


def _json_position(value: Mapping[str, Any], name: str) -> Position:
    try:
        return int(value["linha"]) - 1, int(value["coluna"]) - 1
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Posição inválida em {name}.") from error


def config_from_mapping(payload: Mapping[str, Any]) -> Scenario:
    """Importa uma configuração JSON e aplica todas as regras acadêmicas."""
    dimensions = payload.get("dimensoes", {})
    if dimensions.get("linhas") != 10 or dimensions.get("colunas") != 10:
        raise ValueError("A configuração precisa ser uma matriz 10 x 10.")
    start = _json_position(payload.get("entrada", {}), "entrada")
    goal = _json_position(payload.get("saida", {}), "saída")
    if start != START or goal != GOAL:
        raise ValueError("A entrada deve ser (1,1) e a saída deve ser (10,10).")
    obstacles = frozenset(
        _json_position(item, "obstáculo") for item in payload.get("obstaculos", [])
    )
    recharges: dict[Position, int] = {}
    for item in payload.get("recargas", []):
        position = _json_position(item, "recarga")
        try:
            value = int(item["valor"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Cada recarga precisa de um valor inteiro.") from error
        if position in recharges:
            raise ValueError("Não pode haver duas recargas na mesma célula.")
        recharges[position] = value
    seed_value = payload.get("semente")
    seed = int(seed_value) if seed_value is not None else None
    maze = Maze(
        rows=10,
        cols=10,
        start=start,
        goal=goal,
        obstacles=obstacles,
        recharges=recharges,
        seed=seed,
        mode="Personalizado",
        scenario_id=str(payload.get("identificador") or f"personalizado-{seed or 'manual'}"),
    )
    return custom_scenario(maze, seed=seed, scenario_id=maze.scenario_id)


def config_from_json(raw: str) -> Scenario:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("O arquivo não contém JSON válido.") from error
    if not isinstance(payload, dict):
        raise ValueError("A configuração JSON precisa ser um objeto.")
    return config_from_mapping(payload)
