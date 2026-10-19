"""Testes da amostragem de frames para animação."""

import pytest

from src.animation import sample_states
from src.models import State


def test_sample_states_preserves_order_and_endpoints() -> None:
    states = tuple(State(0, index, 30) for index in range(100))

    sampled = sample_states(states, max_frames=10)

    assert len(sampled) == 10
    assert sampled[0] == states[0]
    assert sampled[-1] == states[-1]
    assert all(first.col < second.col for first, second in zip(sampled, sampled[1:]))


def test_sample_states_rejects_zero_frame_budget() -> None:
    with pytest.raises(ValueError):
        sample_states((State(0, 0, 30),), max_frames=0)
