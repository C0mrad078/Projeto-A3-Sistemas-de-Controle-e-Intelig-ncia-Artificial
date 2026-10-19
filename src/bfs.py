"""Busca em Largura para navegação no labirinto."""

from __future__ import annotations

from collections import deque

from .energy import INITIAL_ENERGY, initial_state, transition
from .maze import Maze
from .models import SearchResult, State
from .search import build_result, start_timer


def breadth_first_search(
    maze: Maze, *, initial_energy: int = INITIAL_ENERGY
) -> SearchResult:
    """Encontra o percurso viável com menor quantidade de movimentos.

    Cada item da fila é um estado completo. Assim, a posição sozinha nunca é
    usada como chave de visitados: energia e máscara de recargas fazem parte do
    espaço de estados explorado.
    """
    started_at = start_timer()
    initial = initial_state(maze, initial_energy)
    frontier: deque[State] = deque([initial])
    visited = {initial}
    parents: dict[State, State | None] = {initial: None}
    depths: dict[State, int] = {initial: 0}
    explored_states = 0
    explored_sequence: list[State] = []
    explored_costs: list[int] = []
    final_state: State | None = None

    while frontier:
        current = frontier.popleft()
        explored_states += 1
        explored_sequence.append(current)
        explored_costs.append(depths[current])

        if current.position == maze.goal:
            final_state = current
            break

        for destination in maze.neighbors(current.position):
            successor = transition(maze, current, destination)
            if successor is None or successor in visited:
                continue
            visited.add(successor)
            parents[successor] = current
            depths[successor] = depths[current] + 1
            frontier.append(successor)

    return build_result(
        algorithm="BFS",
        maze=maze,
        final_state=final_state,
        parents=parents,
        explored_states=explored_states,
        explored_sequence=tuple(explored_sequence),
        explored_costs=tuple(explored_costs),
        started_at=started_at,
    )
