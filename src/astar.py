"""Busca A* para navegação no labirinto."""

from __future__ import annotations

import heapq
from itertools import count
from math import inf

from .energy import INITIAL_ENERGY, initial_state, transition
from .maze import Maze
from .models import SearchResult, State
from .search import build_result, manhattan_distance, start_timer


def a_star_search(
    maze: Maze, *, initial_energy: int = INITIAL_ENERGY
) -> SearchResult:
    """Encontra um percurso usando A* e distância Manhattan admissível."""
    started_at = start_timer()
    initial = initial_state(maze, initial_energy)
    sequence = count()
    initial_g = 0
    frontier: list[tuple[int, int, int, State]] = [
        (
            manhattan_distance(initial.position, maze.goal),
            initial_g,
            next(sequence),
            initial,
        )
    ]
    best_g: dict[State, int] = {initial: initial_g}
    parents: dict[State, State | None] = {initial: None}
    explored_states = 0
    explored_sequence: list[State] = []
    final_state: State | None = None

    while frontier:
        _, current_g, _, current = heapq.heappop(frontier)
        if current_g != best_g.get(current, inf):
            continue

        explored_states += 1
        explored_sequence.append(current)
        if current.position == maze.goal:
            final_state = current
            break

        for destination in maze.neighbors(current.position):
            successor = transition(maze, current, destination)
            if successor is None:
                continue

            successor_g = current_g + 1
            if successor_g >= best_g.get(successor, inf):
                continue

            best_g[successor] = successor_g
            parents[successor] = current
            successor_f = successor_g + manhattan_distance(
                successor.position, maze.goal
            )
            heapq.heappush(
                frontier,
                (successor_f, successor_g, next(sequence), successor),
            )

    return build_result(
        algorithm="A*",
        maze=maze,
        final_state=final_state,
        parents=parents,
        explored_states=explored_states,
        explored_sequence=tuple(explored_sequence),
        started_at=started_at,
    )
