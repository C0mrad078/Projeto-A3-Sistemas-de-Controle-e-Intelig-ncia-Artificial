"""Gera os artefatos finais a partir de experimentos reais e reproduzíveis."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from matplotlib import pyplot as plt

from src.analysis import build_comparison_figure, comparison_summary
from src.experiments import records_to_dataframe, run_experiments
from src.export import figure_to_png_bytes

OUTPUT_DIR = Path("results")
BATCHES = ((10, 10_000), (30, 20_000), (50, 30_000))


def _summary_with_medians(frame: pd.DataFrame, batch_size: int) -> pd.DataFrame:
    summary = comparison_summary(frame.drop(columns=["lote", "semente_inicial"]))
    summary.insert(0, "lote", batch_size)
    medians: list[dict[str, object]] = []
    for algorithm in ("BFS", "A*"):
        algorithm_rows = frame[frame["algorithm"] == algorithm]
        solved_rows = algorithm_rows[algorithm_rows["encontrou_solucao"]]
        medians.append(
            {
                "algoritmo": algorithm,
                "mediana_estados_explorados": algorithm_rows["estados_explorados"].median(),
                "mediana_tempo_execucao_ms": algorithm_rows["tempo_execucao_ms"].median(),
                "mediana_movimentos_sucesso": solved_rows["movimentos"].median(),
                "mediana_energia_sucesso": solved_rows["energia_restante"].median(),
            }
        )
    return summary.merge(pd.DataFrame(medians), on="algoritmo", how="left")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    frames: list[pd.DataFrame] = []
    summaries: list[pd.DataFrame] = []

    for batch_size, seed_start in BATCHES:
        records = run_experiments(batch_size, seed_start=seed_start)
        frame = records_to_dataframe(records)
        frame.insert(0, "lote", batch_size)
        frame.insert(1, "semente_inicial", seed_start)
        frames.append(frame)

        summary = _summary_with_medians(frame, batch_size)
        summaries.append(summary)
        figure = build_comparison_figure(records)
        path = OUTPUT_DIR / f"comparacao_lote_{batch_size}.png"
        path.write_bytes(figure_to_png_bytes(figure))
        plt.close(figure)

        print(f"Lote {batch_size}: sementes {seed_start}–{seed_start + batch_size - 1}")
        for row in summary.to_dict(orient="records"):
            print(
                f"  {row['algoritmo']}: sucesso={row['taxa_sucesso_pct']:.2f}% | "
                f"movimentos_medio={row['media_movimentos_sucesso']} | "
                f"estados_medio={row['media_estados_explorados']:.2f} | "
                f"tempo_medio_ms={row['media_tempo_execucao_ms']:.4f}"
            )

    all_frames = pd.concat(frames, ignore_index=True)
    all_summaries = pd.concat(summaries, ignore_index=True)
    all_frames.to_csv(OUTPUT_DIR / "experimentos_finais.csv", index=False, encoding="utf-8-sig")
    all_summaries.to_csv(OUTPUT_DIR / "resumo_finais.csv", index=False, encoding="utf-8-sig")
    print(f"Registros salvos: {len(all_frames)}")
    print(f"Resumo salvo: {len(all_summaries)} linhas")


if __name__ == "__main__":
    main()
