"""Regras de energia e transições de estados do robô."""

from __future__ import annotations

from .maze import Maze
from .models import State

INITIAL_ENERGY = 30
MOVEMENT_COST = 1


def initial_state(maze: Maze, energy: int = INITIAL_ENERGY) -> State:
    """Cria o estado inicial na entrada, sem recargas consumidas."""
    if energy < 0:
        raise ValueError("A energia inicial não pode ser negativa.")
    return State(maze.start[0], maze.start[1], energy, 0)


def transition(maze: Maze, state: State, destination: tuple[int, int]) -> State | None:
    """Aplica uma transição legal de movimento e energia.

    A ordem é deliberadamente única para BFS e A*:

    1. A posição destino precisa ser um vizinho ortogonal livre do estado atual.
    2. O custo de um movimento é descontado; estados sem pelo menos um ponto
       de energia não podem iniciar outro movimento.
    3. Ao entrar na célula, uma recarga ainda não consumida é coletada e soma
       5 ou 10 pontos, sem limite máximo artificial de energia.
    4. O estado resultante é aceito. Portanto, chegar ao objetivo com energia
       zero é legal quando o último movimento começou com energia 1.

    ``None`` representa uma transição impossível, inclusive por falta de
    energia ou por tentativa de movimento diagonal/obstruído.
    """
    if destination not in maze.neighbors(state.position):
        return None
    if state.energy < MOVEMENT_COST:
        return None

    remaining_energy = state.energy - MOVEMENT_COST
    recharge_mask = state.recharge_mask
    recharge_value = maze.recharges.get(destination)

    if recharge_value is not None:
        recharge_bit = 1 << maze.recharge_index(destination)
        if not recharge_mask & recharge_bit:
            recharge_mask |= recharge_bit
            remaining_energy += recharge_value

    return State(
        row=destination[0],
        col=destination[1],
        energy=remaining_energy,
        recharge_mask=recharge_mask,
    )
