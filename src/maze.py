"""Geração e consultas de labirintos independentes da interface gráfica."""

from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from types import MappingProxyType
from typing import Mapping

from .models import Position

GRID_SIZE = 10
START: Position = (0, 0)
GOAL: Position = (GRID_SIZE - 1, GRID_SIZE - 1)
MIN_OBSTACLES = 10
MAX_OBSTACLES = 25
RECHARGE_VALUES = (5, 10)
RECHARGE_COUNT = 8


@dataclass(frozen=True, slots=True)
class Maze:
    """Representação imutável de um labirinto.

    A classe aceita dimensões menores para cenários controlados dos testes. A
    função :func:`generate` é a responsável por produzir o cenário acadêmico
    obrigatório de 10 x 10 com oito recargas.
    """

    rows: int
    cols: int
    start: Position
    goal: Position
    obstacles: frozenset[Position] = field(default_factory=frozenset)
    recharges: Mapping[Position, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "obstacles", frozenset(self.obstacles))
        object.__setattr__(self, "recharges", MappingProxyType(dict(self.recharges)))
        self._validate_structure()

    def _validate_structure(self) -> None:
        if self.rows <= 0 or self.cols <= 0:
            raise ValueError("O labirinto precisa ter dimensões positivas.")

        for name, position in (("entrada", self.start), ("saída", self.goal)):
            if not self.in_bounds(position):
                raise ValueError(f"A {name} precisa estar dentro do labirinto.")

        all_positions = self.obstacles | set(self.recharges)
        if not all(self.in_bounds(position) for position in all_positions):
            raise ValueError("Obstáculos e recargas precisam estar dentro do labirinto.")
        if self.start in self.obstacles or self.goal in self.obstacles:
            raise ValueError("Entrada e saída não podem ser obstáculos.")
        if self.start in self.recharges or self.goal in self.recharges:
            raise ValueError("Entrada e saída não podem ser recargas.")
        if self.obstacles & set(self.recharges):
            raise ValueError("Obstáculos e recargas não podem ocupar a mesma célula.")
        if any(value not in RECHARGE_VALUES for value in self.recharges.values()):
            raise ValueError("Recargas devem recuperar exatamente 5 ou 10 pontos.")

    def validate_generated_scenario(self) -> None:
        """Valida as regras adicionais do cenário oficial 10 x 10."""
        if (self.rows, self.cols) != (GRID_SIZE, GRID_SIZE):
            raise ValueError("O cenário oficial precisa ser uma matriz 10 x 10.")
        if self.start != START or self.goal != GOAL:
            raise ValueError("O cenário oficial usa entrada (1,1) e saída (10,10).")
        if not MIN_OBSTACLES <= len(self.obstacles) <= MAX_OBSTACLES:
            raise ValueError("A quantidade de obstáculos deve estar entre 10 e 25.")
        if len(self.recharges) != RECHARGE_COUNT:
            raise ValueError("O cenário oficial precisa de oito recargas.")
        if sum(value == 5 for value in self.recharges.values()) != 5:
            raise ValueError("O cenário oficial precisa de cinco recargas de 5 pontos.")
        if sum(value == 10 for value in self.recharges.values()) != 3:
            raise ValueError("O cenário oficial precisa de três recargas de 10 pontos.")

    def in_bounds(self, position: Position) -> bool:
        """Informa se uma posição pertence à matriz."""
        row, col = position
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_open(self, position: Position) -> bool:
        """Informa se uma célula está dentro da matriz e livre de obstáculo."""
        return self.in_bounds(position) and position not in self.obstacles

    def neighbors(self, position: Position) -> tuple[Position, ...]:
        """Retorna apenas vizinhos ortogonais e livres da posição informada.

        A ordem fixa cima, baixo, esquerda e direita torna a expansão
        determinística, sem pré-calcular um caminho completo.
        """
        row, col = position
        candidates = (
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        )
        return tuple(candidate for candidate in candidates if self.is_open(candidate))

    @property
    def recharge_positions(self) -> tuple[Position, ...]:
        """Recargas em ordem estável para indexação da máscara de bits."""
        return tuple(sorted(self.recharges))

    def recharge_index(self, position: Position) -> int:
        """Retorna o índice estável de uma recarga para a máscara de bits."""
        try:
            return self.recharge_positions.index(position)
        except ValueError as error:
            raise ValueError(f"A posição {position} não é uma recarga.") from error

    @classmethod
    def generate(cls, seed: int, obstacle_count: int | None = None) -> "Maze":
        """Gera um cenário reproduzível pelas mesmas semente e configuração."""
        rng = Random(seed)
        if obstacle_count is None:
            obstacle_count = rng.randint(MIN_OBSTACLES, MAX_OBSTACLES)
        if not MIN_OBSTACLES <= obstacle_count <= MAX_OBSTACLES:
            raise ValueError("A quantidade de obstáculos deve estar entre 10 e 25.")

        positions = [(row, col) for row in range(GRID_SIZE) for col in range(GRID_SIZE)]
        obstacle_candidates = [position for position in positions if position not in {START, GOAL}]
        obstacles = frozenset(rng.sample(obstacle_candidates, obstacle_count))
        free_positions = [
            position
            for position in positions
            if position not in obstacles and position not in {START, GOAL}
        ]
        recharge_positions = rng.sample(free_positions, RECHARGE_COUNT)
        recharges = {
            position: 5 if index < 5 else 10
            for index, position in enumerate(recharge_positions)
        }

        maze = cls(
            rows=GRID_SIZE,
            cols=GRID_SIZE,
            start=START,
            goal=GOAL,
            obstacles=obstacles,
            recharges=recharges,
        )
        maze.validate_generated_scenario()
        return maze


def validate_maze(maze: Maze) -> None:
    """Executa a validação estrutural de um mapa já construído."""
    maze._validate_structure()
