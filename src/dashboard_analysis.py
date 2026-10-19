"""Indicadores, tabelas e gráficos usados pelo Dashboard de Análise."""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd
import plotly.graph_objects as go

from .energy import INITIAL_ENERGY, MOVEMENT_COST
from .maze import Maze
from .models import Position, SearchResult
from .search import manhattan_distance

ALGORITHMS = ("BFS", "A*")
ALGORITHM_COLORS = {"BFS": "#2563EB", "A*": "#7C3AED"}


def geometric_shortest_path(maze: Maze) -> tuple[Position, ...] | None:
    """Encontra o menor caminho considerando apenas obstáculos e vizinhança."""
    frontier: deque[Position] = deque([maze.start])
    parents: dict[Position, Position | None] = {maze.start: None}
    while frontier:
        current = frontier.popleft()
        if current == maze.goal:
            path = [current]
            while parents[path[-1]] is not None:
                path.append(parents[path[-1]])  # type: ignore[arg-type]
            return tuple(reversed(path))
        for neighbor in maze.neighbors(current):
            if neighbor not in parents:
                parents[neighbor] = current
                frontier.append(neighbor)
    return None


def scenario_indicators(maze: Maze, result: SearchResult | None = None) -> dict[str, Any]:
    """Calcula indicadores geométricos e de energia sem misturar os conceitos."""
    geometric_path = geometric_shortest_path(maze)
    indicators: dict[str, Any] = {
        "distancia_manhattan": manhattan_distance(maze.start, maze.goal),
        "caminho_geometrico_existe": geometric_path is not None,
        "distancia_geometrica_minima": (
            len(geometric_path) - 1 if geometric_path is not None else None
        ),
        "energia_adicional_necessaria": None,
    }
    if result is not None and result.found:
        indicators["energia_adicional_necessaria"] = required_initial_energy(result) - INITIAL_ENERGY
    return indicators


def required_initial_energy(result: SearchResult) -> int:
    """Calcula a energia inicial mínima para o caminho registrado."""
    if not result.found:
        raise ValueError("Um resultado sem solução não possui caminho para analisar.")
    recharge_total = 0
    required = 0
    for index, state in enumerate(result.state_sequence[1:], start=1):
        previous = result.state_sequence[index - 1]
        recharge = max(0, state.energy - previous.energy + MOVEMENT_COST)
        required = max(required, index - recharge_total)
        recharge_total += recharge
    return required


def energy_rows(maze: Maze, result: SearchResult) -> list[dict[str, Any]]:
    """Produz o registro real de energia de cada movimento físico."""
    if not result.found:
        return []
    rows: list[dict[str, Any]] = []
    used_mask = 0
    for movement, (before, after) in enumerate(
        zip(result.state_sequence, result.state_sequence[1:]), start=1
    ):
        recharge_value = 0
        recharge_position = after.position
        if after.recharge_mask != before.recharge_mask:
            bit = after.recharge_mask ^ before.recharge_mask
            index = bit.bit_length() - 1
            recharge_position = maze.recharge_positions[index]
            recharge_value = maze.recharges[recharge_position]
            used_mask = after.recharge_mask
        rows.append(
            {
                "movimento": movement,
                "linha": after.row + 1,
                "coluna": after.col + 1,
                "posicao": f"({after.row + 1},{after.col + 1})",
                "energia_antes": before.energy,
                "custo_movimento": MOVEMENT_COST,
                "recarga": recharge_value,
                "recarga_posicao": (
                    f"({recharge_position[0] + 1},{recharge_position[1] + 1})"
                    if recharge_value
                    else "—"
                ),
                "energia_depois": after.energy,
                "recargas_utilizadas": after.recharge_mask.bit_count(),
            }
        )
    return rows


def _difference(left: Any, right: Any) -> Any:
    if left is None or right is None:
        return "Não aplicável"
    if isinstance(left, bool) or isinstance(right, bool):
        return "—"
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return round(right - left, 3)
    return "—"


def comparison_table(results: Mapping[str, SearchResult]) -> pd.DataFrame:
    """Tabela pronta para a aba Visão Geral, com nulos legíveis."""
    bfs = results.get("BFS")
    astar = results.get("A*")
    if bfs is None or astar is None:
        return pd.DataFrame()
    rows = []
    metrics = (
        ("Encontrou solução", "found", lambda result: "Sim" if result.found else "Não"),
        ("Movimentos", "moves", lambda result: result.moves),
        ("Estados explorados", "explored_states", lambda result: result.explored_states),
        ("Energia final", "remaining_energy", lambda result: result.remaining_energy),
        ("Tempo (ms)", "execution_time_ms", lambda result: round(result.execution_time_ms, 3)),
        ("Recargas", "recharges", lambda result: len(result.recharges_consumed) if result.found else None),
    )
    for label, _, getter in metrics:
        left = getter(bfs)
        right = getter(astar)
        rows.append(
            {
                "Métrica": label,
                "BFS": left if left is not None else "Não aplicável",
                "A*": right if right is not None else "Não aplicável",
                "Diferença (A* − BFS)": _difference(left, right),
            }
        )
    return pd.DataFrame(rows)


def performance_figures(results: Mapping[str, SearchResult]) -> dict[str, go.Figure]:
    """Cria gráficos interativos do cenário atual a partir de dados reais."""
    available = [results[name] for name in ALGORITHMS if name in results]
    labels = [result.algorithm for result in available]

    def bar(title: str, y_title: str, values: list[float | None]) -> go.Figure:
        figure = go.Figure(
            go.Bar(
                x=labels,
                y=values,
                marker_color=[ALGORITHM_COLORS[name] for name in labels],
                text=["Não aplicável" if value is None else value for value in values],
                textposition="auto",
                hovertemplate="%{x}: %{y}<extra></extra>",
            )
        )
        figure.update_layout(title=title, yaxis_title=y_title, xaxis_title="Algoritmo")
        return figure

    return {
        "estados": bar("Estados completos expandidos", "Estados", [r.explored_states for r in available]),
        "tempo": bar("Tempo de processamento", "Milissegundos", [round(r.execution_time_ms, 3) for r in available]),
        "movimentos": bar("Tamanho do caminho", "Movimentos", [r.moves for r in available if r.found]),
        "energia": bar("Energia final", "Energia", [r.remaining_energy for r in available if r.found]),
    }


def energy_figure(maze: Maze, results: Mapping[str, SearchResult]) -> go.Figure:
    """Cria a evolução de energia somente para percursos solucionados."""
    figure = go.Figure()
    for algorithm in ALGORITHMS:
        result = results.get(algorithm)
        if result is None or not result.found:
            continue
        states = result.state_sequence
        figure.add_trace(
            go.Scatter(
                x=list(range(len(states))),
                y=[state.energy for state in states],
                mode="lines+markers",
                name=algorithm,
                line={"color": ALGORITHM_COLORS[algorithm]},
                customdata=[state.position for state in states],
                hovertemplate="Movimento %{x}<br>Energia %{y}<br>Célula %{customdata}<extra></extra>",
            )
        )
        for index, state in enumerate(states[1:], start=1):
            previous = states[index - 1]
            if state.energy > previous.energy - MOVEMENT_COST:
                figure.add_annotation(
                    x=index,
                    y=state.energy,
                    text=f"+{state.energy - previous.energy + MOVEMENT_COST}",
                    showarrow=True,
                    arrowhead=2,
                    font={"color": ALGORITHM_COLORS[algorithm]},
                )
    figure.update_layout(
        title="Evolução da energia no percurso físico",
        xaxis_title="Movimentos realizados",
        yaxis_title="Energia disponível",
        hovermode="x unified",
    )
    return figure


def interpret_results(results: Mapping[str, SearchResult]) -> tuple[str, ...]:
    """Gera explicações determinísticas, condicionadas aos resultados reais."""
    bfs = results.get("BFS")
    astar = results.get("A*")
    if bfs is None or astar is None:
        return ("Execute BFS e A* no mesmo cenário para interpretar os resultados.",)
    messages = [
        "Um estado explorado inclui posição, energia disponível e máscara das recargas já consumidas.",
        "O BFS expande estados por níveis de movimentos; por isso, entre percursos viáveis, o primeiro objetivo encontrado tem menor comprimento.",
        "O A* prioriza f(n)=g(n)+h(n), usando a distância Manhattan como orientação sem alterar a regra de energia.",
    ]
    if bfs.found and astar.found:
        if bfs.moves == astar.moves:
            messages.append(
                "Os caminhos têm o mesmo comprimento mínimo neste cenário. Eles ainda podem consumir recargas diferentes."
            )
        else:
            messages.append(
                "Os comprimentos diferem neste resultado; confira se ambos foram executados no mesmo cenário e se a métrica de movimentos é a mesma."
            )
        if astar.explored_states < bfs.explored_states:
            messages.append("Neste cenário, A* expandiu menos estados que BFS, resultado compatível com a orientação da heurística Manhattan.")
        elif astar.explored_states > bfs.explored_states:
            messages.append("Neste cenário, A* expandiu mais estados que BFS; a heurística não garante vantagem em todos os mapas.")
        else:
            messages.append("Neste cenário, os dois algoritmos expandiram a mesma quantidade de estados.")
        if astar.execution_time_ms < bfs.execution_time_ms:
            messages.append("A* foi mais rápido nesta medição; o tempo também depende da máquina e do custo de cada operação.")
        elif astar.execution_time_ms > bfs.execution_time_ms:
            messages.append("BFS foi mais rápido nesta medição; isso não contradiz a optimalidade do A*.")
        else:
            messages.append("Os tempos medidos foram equivalentes dentro da precisão registrada.")
    elif not bfs.found and not astar.found:
        messages.append("Nenhum algoritmo encontrou percurso viável: o mapa pode estar desconectado ou a energia disponível pode ser insuficiente.")
    else:
        messages.append("Houve divergência de sucesso no mesmo espaço de estados; isso deve ser investigado como possível problema de implementação ou interrupção por recursos.")
    messages.append("A expansão visual é virtual; somente o caminho reconstruído consome energia e representa deslocamento físico.")
    return tuple(messages)
