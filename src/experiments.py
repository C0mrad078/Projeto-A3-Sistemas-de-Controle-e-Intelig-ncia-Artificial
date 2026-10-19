"""Execução reproduzível de lotes comparativos de BFS e A*."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable, Iterable

from .astar import a_star_search
from .bfs import breadth_first_search
from .maze import Maze
from .models import Position, SearchResult
from .scenarios import Scenario, custom_scenario, generate_scenario, validate_mode

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
    mode: str = "Aleatório"

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
        row["modalidade"] = row.pop("mode")
        return row


def _record_from_result(
    *, scenario_id: int, scenario: Scenario, result: SearchResult
) -> ExperimentRecord:
    return ExperimentRecord(
        scenario_id=scenario_id,
        seed=scenario.seed if scenario.seed is not None else -1,
        obstacle_count=scenario.obstacle_count,
        algorithm=result.algorithm,
        found=result.found,
        moves=result.moves,
        explored_states=result.explored_states,
        remaining_energy=result.remaining_energy,
        recharges_used=len(result.recharges_consumed),
        recharge_positions=result.recharges_consumed,
        execution_time_ms=result.execution_time_ms,
        mode=scenario.mode,
    )


def run_experiments(
    batch_size: int,
    *,
    seed_start: int = 10_000,
    mode: str = "Aleatório",
    obstacle_count: int | None = None,
    custom_maze: Maze | None = None,
    custom_batch: bool = False,
    progress_callback: ProgressCallback | None = None,
) -> tuple[ExperimentRecord, ...]:
    """Executa um lote com os mesmos cenários para BFS e A*.

    As sementes são ``seed_start + índice``. Cada chamada dos algoritmos recebe
    o mesmo objeto imutável de labirinto, mas cria seu próprio estado inicial,
    energia e máscara de recargas.
    """
    if batch_size not in ALLOWED_BATCH_SIZES and not custom_batch:
        raise ValueError("O lote deve conter 10, 30 ou 50 labirintos.")
    if custom_batch and not 1 <= batch_size <= 100:
        raise ValueError("A quantidade personalizada deve estar entre 1 e 100 cenários.")
    validate_mode(mode)
    if mode == "Personalizado" and custom_maze is None and obstacle_count is None:
        raise ValueError("O modo Personalizado precisa de um mapa ou de uma quantidade de obstáculos.")

    total = batch_size * 2
    completed = 0
    records: list[ExperimentRecord] = []
    for index in range(batch_size):
        scenario_id = index + 1
        seed = seed_start + index
        if custom_maze is not None:
            scenario = custom_scenario(
                custom_maze,
                seed=custom_maze.seed,
                scenario_id=custom_maze.scenario_id or f"personalizado-{scenario_id}",
            )
        elif mode == "Personalizado":
            generated = generate_scenario(
                "Aleatório", seed=seed, obstacle_count=obstacle_count
            )
            scenario = custom_scenario(generated.maze, seed=seed, scenario_id=f"personalizado-{seed}")
        else:
            scenario = generate_scenario(
                mode, seed=seed, obstacle_count=obstacle_count
            )
        maze = scenario.maze
        results = (
            breadth_first_search(maze),
            a_star_search(maze),
        )
        for result in results:
            records.append(
                _record_from_result(
                    scenario_id=scenario_id,
                    scenario=scenario,
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
