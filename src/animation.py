"""Utilitários puros para animação controlada de sequências de estados."""

from __future__ import annotations

from collections.abc import Sequence

from .models import State


def sample_states(states: Sequence[State], max_frames: int = 80) -> tuple[State, ...]:
    """Seleciona frames uniformes sem alterar a sequência original.

    A busca continua registrando todos os estados. A amostragem reduz apenas
    atualizações visuais para evitar uma animação lenta em BFS.
    """
    if max_frames <= 0:
        raise ValueError("A animação precisa permitir pelo menos um frame.")
    if len(states) <= max_frames:
        return tuple(states)
    indexes = {
        round(index * (len(states) - 1) / (max_frames - 1))
        for index in range(max_frames)
    }
    return tuple(states[index] for index in sorted(indexes))
