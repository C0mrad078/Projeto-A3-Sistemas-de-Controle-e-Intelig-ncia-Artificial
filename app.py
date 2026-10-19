"""Ponto de entrada programático e CLI do Robot Maze AI."""

from __future__ import annotations

import argparse

from src.astar import a_star_search
from src.bfs import breadth_first_search
from src.maze import MAX_OBSTACLES, MIN_OBSTACLES, Maze
from src.models import SearchResult


def run_algorithms(
    *, seed: int = 42, obstacle_count: int | None = None
) -> tuple[Maze, tuple[SearchResult, SearchResult]]:
    """Gera um cenário e executa BFS e A* com as mesmas regras."""
    maze = Maze.generate(seed=seed, obstacle_count=obstacle_count)
    results = (
        breadth_first_search(maze),
        a_star_search(maze),
    )
    return maze, results


def main() -> None:
    """Executa uma comparação textual para validação rápida do núcleo."""
    parser = argparse.ArgumentParser(description="Executa BFS e A* no mesmo labirinto.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--obstacles",
        type=int,
        choices=range(MIN_OBSTACLES, MAX_OBSTACLES + 1),
        default=None,
        help="Quantidade de obstáculos entre 10 e 25; por padrão, aleatória pela semente.",
    )
    args = parser.parse_args()

    maze, results = run_algorithms(seed=args.seed, obstacle_count=args.obstacles)
    print(
        f"Labirinto {maze.rows}x{maze.cols} | obstáculos={len(maze.obstacles)} "
        f"| recargas={len(maze.recharges)}"
    )
    for result in results:
        status = "solução" if result.found else "sem solução"
        print(
            f"{result.algorithm}: {status} | movimentos={result.moves} "
            f"| estados={result.explored_states} "
            f"| energia={result.remaining_energy} "
            f"| tempo_ms={result.execution_time_ms:.3f}"
        )


def dashboard_main() -> None:
    """Inicia o dashboard quando o arquivo é executado pelo Streamlit."""
    from src.dashboard import render_dashboard

    render_dashboard()


if __name__ == "__main__":
    dashboard_main()
