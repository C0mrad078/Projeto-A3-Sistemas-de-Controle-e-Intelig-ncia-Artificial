"""Modelos de domínio compartilhados pelo simulador."""

from __future__ import annotations

from dataclasses import dataclass

Position = tuple[int, int]


@dataclass(frozen=True, slots=True)
class State:
    """Estado completo do robô em um ponto da busca.

    As coordenadas usam índice zero internamente. O estado inclui energia e a
    máscara de recargas consumidas porque duas visitas à mesma posição podem
    ter possibilidades futuras diferentes.
    """

    row: int
    col: int
    energy: int
    recharge_mask: int = 0

    def __post_init__(self) -> None:
        if self.row < 0 or self.col < 0:
            raise ValueError("As coordenadas do estado não podem ser negativas.")
        if self.energy < 0:
            raise ValueError("A energia do estado não pode ser negativa.")
        if self.recharge_mask < 0:
            raise ValueError("A máscara de recargas não pode ser negativa.")

    @property
    def position(self) -> Position:
        """Retorna a posição como tupla (linha, coluna)."""
        return self.row, self.col


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Resultado padronizado de uma execução de busca."""

    algorithm: str
    found: bool
    moves: int | None
    explored_states: int
    remaining_energy: int | None
    path: tuple[Position, ...]
    recharges_consumed: tuple[Position, ...]
    execution_time_ms: float
    state_sequence: tuple[State, ...]
    explored_sequence: tuple[State, ...] = ()
    explored_costs: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.explored_states < 0:
            raise ValueError("A quantidade de estados explorados não pode ser negativa.")
        if self.execution_time_ms < 0:
            raise ValueError("O tempo de execução não pode ser negativo.")
        if self.explored_costs and len(self.explored_costs) != len(self.explored_sequence):
            raise ValueError("Cada estado explorado precisa ter seu custo g(n) registrado.")
        if any(cost < 0 for cost in self.explored_costs):
            raise ValueError("Os custos de exploração não podem ser negativos.")
        if self.found:
            if self.moves is None or self.remaining_energy is None:
                raise ValueError("Resultados com solução precisam de movimentos e energia.")
            if not self.path or not self.state_sequence:
                raise ValueError("Resultados com solução precisam reconstruir o percurso.")
        elif any(value is not None for value in (self.moves, self.remaining_energy)):
            raise ValueError("Resultados sem solução usam métricas de chegada nulas.")
