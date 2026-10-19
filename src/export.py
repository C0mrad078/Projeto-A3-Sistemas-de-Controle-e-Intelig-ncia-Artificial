"""Exportação de resultados e figuras produzidos pelo programa."""

from __future__ import annotations

import csv
from io import BytesIO, StringIO
from pathlib import Path
from typing import Iterable

from matplotlib.figure import Figure

from .experiments import ExperimentRecord, records_to_rows

DEFAULT_RESULTS_DIR = Path("results")


def records_to_csv_bytes(records: Iterable[ExperimentRecord]) -> bytes:
    """Serializa registros reais em CSV UTF-8 com cabeçalho em português."""
    rows = records_to_rows(records)
    if not rows:
        return b""
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8-sig")


def dataframe_to_csv_bytes(dataframe) -> bytes:
    """Serializa uma tabela comparativa sem incluir o índice."""
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def figure_to_png_bytes(figure: Figure, *, dpi: int = 150) -> bytes:
    """Serializa uma figura Matplotlib em PNG."""
    output = BytesIO()
    figure.savefig(output, format="png", dpi=dpi, bbox_inches="tight")
    return output.getvalue()


def plotly_figure_to_png_bytes(figure) -> bytes:
    """Serializa um gráfico Plotly em PNG usando Kaleido."""
    return figure.to_image(format="png")


def save_experiment_csv(
    records: Iterable[ExperimentRecord],
    *,
    output_dir: Path = DEFAULT_RESULTS_DIR,
) -> Path:
    """Persiste a exportação de experimentos em ``results/``."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "experimentos.csv"
    path.write_bytes(records_to_csv_bytes(records))
    return path


def save_figure_png(
    figure: Figure,
    *,
    filename: str = "comparacao.png",
    output_dir: Path = DEFAULT_RESULTS_DIR,
) -> Path:
    """Persiste uma figura PNG no diretório de resultados."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    path.write_bytes(figure_to_png_bytes(figure))
    return path
