"""Medição das execuções de busca."""

from __future__ import annotations

from time import perf_counter


def elapsed_milliseconds(started_at: float) -> float:
    """Converte o intervalo desde ``started_at`` em milissegundos."""
    return (perf_counter() - started_at) * 1000
