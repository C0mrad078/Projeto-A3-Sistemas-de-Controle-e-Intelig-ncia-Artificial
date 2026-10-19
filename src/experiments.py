"""Execução reproduzível de lotes comparativos de BFS e A*."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable, Iterable

from .astar import a_star_search
from .bfs import breadth_first_search
from .maze import Maze
from .models import Position, SearchResult

ProgressCallback = Callable[[int, int], None]
ALLOWED_BATCH_SIZES = (10, 30, 50)


@dataclass(frozen=True, slots=True)
class ExperimentRecord:
    """Linha persistível de um algoritmo em um cenário específico."""

    scenario_id: int
    seed: int
    obstacle_count: int
    algorithm: str
    found: bool
    moves: int | None
    explored_states: int
    remaining_energy: int | None
    recharges_used: int
    recharge_positions: tuple[Position, ...]
    execution_time_ms: float

    def to_row(self) -> dict[str, object]:
        """Converte o registro para exportação tabular em português."""
        row = asdict(self)
        row["encontrou_solucao"] = row.pop("found")
        row["movimentos"] = row.pop("moves")
        row["estados_explorados"] = row.pop("explored_states")
        row["energia_restante"] = row.pop("remaining_energy")
        row["recargas_utilizadas"] = row.pop("recharges_used")
        positions = row.pop("recharge_positions")
        row["posicoes_recarga"] = "; ".join(
            f"({position[0] + 1},{position[1] + 1})" for position in positions
        )
        row["tempo_execucao_ms"] = row.pop("execution_time_ms")
        return row


def _record_from_result(
    *, scenario_id: int, seed: int, maze: Maze, result: SearchResult
) -> ExperimentRecord:
    return ExperimentRecord(
        scenario_id=scenario_id,
        seed=seed,
        obstacle_count=len(maze.obstacles),
        algorithm=result.algorithm,
        found=result.found,
        moves=result.moves,
        explored_states=result.explored_states,
        remaining_energy=result.remaining_energy,
        recharges_used=len(result.recharges_consumed),
        recharge_positions=result.recharges_consumed,
        execution_time_ms=result.execution_time_ms,
    )


def run_experiments(
    batch_size: int,
    *,
    seed_start: int = 10_000,
    progress_callback: ProgressCallback | None = None,
) -> tuple[ExperimentRecord, ...]:
    """Executa um lote com os mesmos cenários para BFS e A*.

    As sementes são ``seed_start + índice``. Cada chamada dos algoritmos recebe
    o mesmo objeto imutável de labirinto, mas cria seu próprio estado inicial,
    energia e máscara de recargas.
    """
    if batch_size not in ALLOWED_BATCH_SIZES:
        raise ValueError("O lote deve conter 10, 30 ou 50 labirintos.")

    total = batch_size * 2
    completed = 0
    records: list[ExperimentRecord] = []
    for index in range(batch_size):
        scenario_id = index + 1
        seed = seed_start + index
        maze = Maze.generate(seed=seed)
        results = (
            breadth_first_search(maze),
            a_star_search(maze),
        )
        for result in results:
            records.append(
                _record_from_result(
                    scenario_id=scenario_id,
                    seed=seed,
                    maze=maze,
                    result=result,
                )
            )
            completed += 1
            if progress_callback is not None:
                progress_callback(completed, total)

    return tuple(records)


def records_to_rows(records: Iterable[ExperimentRecord]) -> list[dict[str, object]]:
    """Converte registros sem mutar os objetos de domínio."""
    return [record.to_row() for record in records]


def records_to_dataframe(records: Iterable[ExperimentRecord]):
    """Retorna um DataFrame para tabelas e gráficos da interface."""
    import pandas as pd

    return pd.DataFrame(records_to_rows(records))
