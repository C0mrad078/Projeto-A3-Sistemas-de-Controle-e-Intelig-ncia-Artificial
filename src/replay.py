"""Snapshots imutáveis para reproduzir buscas sem recalculá-las."""

from __future__ import annotations

from dataclasses import dataclass

from .energy import MOVEMENT_COST
from .maze import Maze
from .models import Position, SearchResult, State
from .search import manhattan_distance

EXPLORATION_PHASE = "exploração virtual"
PHYSICAL_PHASE = "percurso físico"


@dataclass(frozen=True, slots=True)
class ReplayEvent:
    """Um quadro semântico da busca ou do percurso do robô."""

    index: int
    phase: str
    position: Position
    energy: int
    explored_count: int
    physical_move: int | None
    energy_before: int | None
    energy_after: int | None
    movement_cost: int | None
    recharge_value: int
    recharge_position: Position | None
    g: int | None
    h: int | None
    f: int | None
    is_goal: bool


@dataclass(frozen=True, slots=True)
class Replay:
    """Sequência navegável de eventos derivada de um resultado já calculado."""

    algorithm: str
    events: tuple[ReplayEvent, ...]

    @property
    def last_index(self) -> int:
        return max(0, len(self.events) - 1)

    def event(self, index: int) -> ReplayEvent:
        if not self.events:
            raise IndexError("A reprodução não possui eventos.")
        return self.events[clamp_index(index, self.last_index)]


def _recharge_between(maze: Maze, before: State, after: State) -> tuple[int, Position | None]:
    changed = after.recharge_mask ^ before.recharge_mask
    if not changed:
        return 0, None
    recharge_index = changed.bit_length() - 1
    position = maze.recharge_positions[recharge_index]
    return maze.recharges[position], position


def build_replay(maze: Maze, result: SearchResult) -> Replay:
    """Cria eventos de exploração e percurso usando somente dados registrados."""
    events: list[ReplayEvent] = []
    costs = result.explored_costs or tuple(range(len(result.explored_sequence)))
    for index, state in enumerate(result.explored_sequence):
        g = costs[index]
        h = manhattan_distance(state.position, maze.goal)
        events.append(
            ReplayEvent(
                index=len(events),
                phase=EXPLORATION_PHASE,
                position=state.position,
                energy=state.energy,
                explored_count=index + 1,
                physical_move=None,
                energy_before=None,
                energy_after=None,
                movement_cost=None,
                recharge_value=0,
                recharge_position=None,
                g=g,
                h=h,
                f=g + h,
                is_goal=state.position == maze.goal,
            )
        )

    if result.found:
        for move, state in enumerate(result.state_sequence):
            if move == 0:
                before_energy = state.energy
                recharge_value = 0
                recharge_position = None
            else:
                before = result.state_sequence[move - 1]
                before_energy = before.energy
                recharge_value, recharge_position = _recharge_between(maze, before, state)
            events.append(
                ReplayEvent(
                    index=len(events),
                    phase=PHYSICAL_PHASE,
                    position=state.position,
                    energy=state.energy,
                    explored_count=len(result.explored_sequence),
                    physical_move=move,
                    energy_before=before_energy,
                    energy_after=state.energy,
                    movement_cost=None if move == 0 else MOVEMENT_COST,
                    recharge_value=recharge_value,
                    recharge_position=recharge_position,
                    g=move,
                    h=manhattan_distance(state.position, maze.goal),
                    f=move + manhattan_distance(state.position, maze.goal),
                    is_goal=state.position == maze.goal,
                )
            )
    return Replay(result.algorithm, tuple(events))


def clamp_index(index: int, last_index: int) -> int:
    """Mantém controles de reprodução dentro dos eventos disponíveis."""
    if last_index < 0:
        return 0
    return max(0, min(index, last_index))


def next_index(index: int, replay: Replay) -> int:
    return clamp_index(index + 1, replay.last_index)


def previous_index(index: int, replay: Replay) -> int:
    return clamp_index(index - 1, replay.last_index)
