"""Primitivas comuns aos algoritmos de busca simbólica."""

from __future__ import annotations

from time import perf_counter
from typing import Mapping

from .maze import Maze
from .metrics import elapsed_milliseconds
from .models import Position, SearchResult, State


def manhattan_distance(position: Position, goal: Position) -> int:
    """Heurística exigida para A*: distância Manhattan sem bônus artificiais."""
    return abs(position[0] - goal[0]) + abs(position[1] - goal[1])


def reconstruct_states(
    parents: Mapping[State, State | None], final_state: State
) -> tuple[State, ...]:
    """Reconstrói a sequência de estados desde a entrada até o estado final."""
    states = [final_state]
    current = final_state
    while (parent := parents[current]) is not None:
        current = parent
        states.append(current)
    states.reverse()
    return tuple(states)


def consumed_recharges(maze: Maze, recharge_mask: int) -> tuple[Position, ...]:
    """Converte a máscara final em posições de recarga, em ordem estável."""
    return tuple(
        position
        for index, position in enumerate(maze.recharge_positions)
        if recharge_mask & (1 << index)
    )


def build_result(
    *,
    algorithm: str,
    maze: Maze,
    final_state: State | None,
    parents: Mapping[State, State | None],
    explored_states: int,
    explored_sequence: tuple[State, ...],
    started_at: float,
    explored_costs: tuple[int, ...] = (),
) -> SearchResult:
    """Cria um resultado uniforme para sucesso ou ausência de solução."""
    execution_time_ms = elapsed_milliseconds(started_at)
    if final_state is None:
        return SearchResult(
            algorithm=algorithm,
            found=False,
            moves=None,
            explored_states=explored_states,
            remaining_energy=None,
            path=(),
            recharges_consumed=(),
            execution_time_ms=execution_time_ms,
            state_sequence=(),
            explored_sequence=explored_sequence,
            explored_costs=explored_costs,
        )

    states = reconstruct_states(parents, final_state)
    path = tuple(state.position for state in states)
    return SearchResult(
        algorithm=algorithm,
        found=True,
        moves=len(states) - 1,
        explored_states=explored_states,
        remaining_energy=final_state.energy,
        path=path,
        recharges_consumed=consumed_recharges(maze, final_state.recharge_mask),
        execution_time_ms=execution_time_ms,
        state_sequence=states,
        explored_sequence=explored_sequence,
        explored_costs=explored_costs,
    )


def start_timer() -> float:
    """Inicia o cronômetro usado pelos algoritmos."""
    return perf_counter()
