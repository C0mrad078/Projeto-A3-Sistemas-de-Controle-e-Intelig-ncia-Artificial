"""Agregações e gráficos comparativos dos experimentos reais."""

from __future__ import annotations

from collections.abc import Iterable

import matplotlib

matplotlib.use("Agg", force=True)

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from .experiments import ExperimentRecord, records_to_dataframe

ALGORITHM_ORDER = ("BFS", "A*")


def ensure_dataframe(data: pd.DataFrame | Iterable[ExperimentRecord]) -> pd.DataFrame:
    """Normaliza registros ou DataFrame sem alterar a entrada original."""
    if isinstance(data, pd.DataFrame):
        return data.copy()
    return records_to_dataframe(data)


def solved_records(data: pd.DataFrame | Iterable[ExperimentRecord]) -> pd.DataFrame:
    """Filtra métricas que dependem de uma chegada ao objetivo."""
    frame = ensure_dataframe(data)
    return frame[frame["encontrou_solucao"]].copy()


def jointly_solved_scenario_ids(
    data: pd.DataFrame | Iterable[ExperimentRecord],
) -> frozenset[int]:
    """Retorna cenários nos quais BFS e A* encontraram solução."""
    frame = ensure_dataframe(data)
    successful = frame[frame["encontrou_solucao"]]
    counts = successful.groupby("scenario_id")["algorithm"].nunique()
    return frozenset(int(identifier) for identifier in counts[counts == 2].index)


def jointly_solved_records(
    data: pd.DataFrame | Iterable[ExperimentRecord],
) -> pd.DataFrame:
    """Filtra ambos os algoritmos nos cenários de sucesso conjunto."""
    frame = ensure_dataframe(data)
    scenario_ids = jointly_solved_scenario_ids(frame)
    return frame[frame["scenario_id"].isin(scenario_ids)].copy()


def comparison_summary(data: pd.DataFrame | Iterable[ExperimentRecord]) -> pd.DataFrame:
    """Calcula médias e taxa de sucesso por algoritmo."""
    frame = ensure_dataframe(data)
    solved = solved_records(frame)
    rows: list[dict[str, object]] = []
    scenario_total = frame["scenario_id"].nunique()
    for algorithm in ALGORITHM_ORDER:
        algorithm_rows = frame[frame["algorithm"] == algorithm]
        algorithm_solved = solved[solved["algorithm"] == algorithm]
        rows.append(
            {
                "algoritmo": algorithm,
                "cenarios": scenario_total,
                "sucessos": int(algorithm_rows["encontrou_solucao"].sum()),
                "taxa_sucesso_pct": (
                    float(algorithm_rows["encontrou_solucao"].mean() * 100)
                    if not algorithm_rows.empty
                    else 0.0
                ),
                "media_estados_explorados": float(
                    algorithm_rows["estados_explorados"].mean()
                )
                if not algorithm_rows.empty
                else float("nan"),
                "media_tempo_execucao_ms": float(
                    algorithm_rows["tempo_execucao_ms"].mean()
                )
                if not algorithm_rows.empty
                else float("nan"),
                "media_movimentos_sucesso": float(algorithm_solved["movimentos"].mean())
                if not algorithm_solved.empty
                else float("nan"),
                "media_energia_sucesso": float(
                    algorithm_solved["energia_restante"].mean()
                )
                if not algorithm_solved.empty
                else float("nan"),
            }
        )
    return pd.DataFrame(rows)


def build_comparison_figure(
    data: pd.DataFrame | Iterable[ExperimentRecord],
) -> Figure:
    """Gera cinco gráficos de médias com filtros explícitos no título."""
    frame = ensure_dataframe(data)
    jointly_solved = jointly_solved_records(frame)
    chart_specs = (
        ("estados_explorados", "Média de estados explorados", frame),
        ("tempo_execucao_ms", "Média de tempo (ms)", frame),
        (
            "movimentos",
            "Média de movimentos — sucesso conjunto",
            jointly_solved,
        ),
        (
            "taxa_sucesso_pct",
            "Taxa de sucesso (%)",
            comparison_summary(frame),
        ),
        (
            "energia_restante",
            "Média de energia final — sucesso conjunto",
            jointly_solved,
        ),
    )
    figure, axes = plt.subplots(3, 2, figsize=(13, 13))
    for axis, (metric, title, source) in zip(axes.flat, chart_specs):
        if metric == "taxa_sucesso_pct":
            values = [
                float(source.loc[source["algoritmo"] == algorithm, metric].iloc[0])
                for algorithm in ALGORITHM_ORDER
            ]
        else:
            values = [
                float(source.loc[source["algorithm"] == algorithm, metric].mean())
                if not source.loc[source["algorithm"] == algorithm, metric].dropna().empty
                else float("nan")
                for algorithm in ALGORITHM_ORDER
            ]
        axis.bar(ALGORITHM_ORDER, values, color=("#2563EB", "#7C3AED"))
        axis.set_title(title)
        axis.set_ylabel("Valor")
        axis.grid(axis="y", alpha=0.25)
        if all(pd.isna(value) for value in values):
            axis.text(0.5, 0.5, "Nenhum dado solucionado", ha="center", va="center", transform=axis.transAxes)

    axes.flat[-1].axis("off")
    figure.suptitle("Comparação experimental: BFS × A*", fontsize=16)
    figure.tight_layout()
    return figure
