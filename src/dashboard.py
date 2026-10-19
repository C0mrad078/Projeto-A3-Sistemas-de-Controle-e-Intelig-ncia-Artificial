"""Dashboard Streamlit do Robot Maze AI."""

from __future__ import annotations

import time
from typing import Any

import streamlit as st
from matplotlib import pyplot as plt

from .analysis import build_comparison_figure, comparison_summary
from .animation import sample_states
from .astar import a_star_search
from .bfs import breadth_first_search
from .experiments import records_to_dataframe, run_experiments
from .export import (
    dataframe_to_csv_bytes,
    figure_to_png_bytes,
    records_to_csv_bytes,
    save_experiment_csv,
    save_figure_png,
)
from .maze import MAX_OBSTACLES, MIN_OBSTACLES, Maze
from .models import SearchResult
from .visualization import render_maze

ALGORITHM_NAMES = ("BFS", "A*")
ANIMATION_SPEEDS = {
    "Desligada": 0.0,
    "Rápida": 0.02,
    "Normal": 0.08,
    "Lenta": 0.20,
}


def _initialize_session_state() -> None:
    if "maze" not in st.session_state:
        st.session_state.maze = Maze.generate(seed=42, obstacle_count=15)
    st.session_state.setdefault("maze_seed", 42)
    st.session_state.setdefault("obstacle_count", 15)
    st.session_state.setdefault("selected_algorithm", "BFS")
    st.session_state.setdefault("animation_speed", "Normal")
    st.session_state.setdefault("results", {})
    st.session_state.setdefault("comparison_results", None)
    st.session_state.setdefault("experiment_records", None)
    st.session_state.setdefault("active_result", None)
    st.session_state.setdefault("pending_animation", False)


def _clear_execution_state() -> None:
    st.session_state.results = {}
    st.session_state.comparison_results = None
    st.session_state.active_result = None
    st.session_state.pending_animation = False


def _run_single_algorithm(algorithm: str) -> SearchResult:
    maze = st.session_state.maze
    if algorithm == "BFS":
        result = breadth_first_search(maze)
    else:
        result = a_star_search(maze)
    st.session_state.results[algorithm] = result
    st.session_state.active_result = result
    st.session_state.comparison_results = None
    st.session_state.pending_animation = True
    return result


def _metric_value(value: Any, suffix: str = "") -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.2f}{suffix}"
    return f"{value}{suffix}"


def _display_result_metrics(result: SearchResult) -> None:
    metrics = st.columns(6)
    metrics[0].metric("Algoritmo", result.algorithm)
    metrics[1].metric("Solução", "Sim" if result.found else "Não")
    metrics[2].metric("Movimentos", _metric_value(result.moves))
    metrics[3].metric("Estados", _metric_value(result.explored_states))
    metrics[4].metric("Energia", _metric_value(result.remaining_energy))
    metrics[5].metric("Tempo", _metric_value(result.execution_time_ms, " ms"))
    if result.found:
        st.caption(
            f"Recargas consumidas: {len(result.recharges_consumed)} — "
            f"{', '.join(f'({row + 1},{col + 1})' for row, col in result.recharges_consumed) or 'nenhuma'}"
        )
    else:
        st.warning("Não existe percurso viável com a energia e as recargas disponíveis.")


def _render_figure(figure) -> None:
    st.pyplot(figure)
    plt.close(figure)


def _render_result(maze: Maze, result: SearchResult, speed: float, animate: bool) -> None:
    explored_positions = tuple(state.position for state in result.explored_sequence)
    path_positions = tuple(state.position for state in result.state_sequence)
    frame_area = st.empty()
    status_area = st.empty()

    if animate and speed > 0:
        virtual_frames = sample_states(result.explored_sequence)
        for index, state in enumerate(virtual_frames, start=1):
            status_area.info(
                f"Expansão virtual: frame {index}/{len(virtual_frames)}. "
                "Isso não representa movimentos físicos nem consome energia."
            )
            figure = render_maze(
                maze,
                explored_positions=tuple(frame.position for frame in virtual_frames[:index]),
                title="Exploração virtual de estados",
            )
            frame_area.pyplot(figure)
            plt.close(figure)
            time.sleep(speed)

        physical_frames = sample_states(result.state_sequence)
        for index, state in enumerate(physical_frames, start=1):
            status_area.info(
                f"Percurso físico: movimento visual {index - 1}/{max(len(physical_frames) - 1, 0)} "
                f"| energia {state.energy}"
            )
            figure = render_maze(
                maze,
                explored_positions=explored_positions,
                path=tuple(frame.position for frame in physical_frames[:index]),
                robot_position=state.position,
                title="Percurso físico do robô",
            )
            frame_area.pyplot(figure)
            plt.close(figure)
            time.sleep(speed)

    status_area.empty()
    figure = render_maze(
        maze,
        explored_positions=explored_positions,
        path=path_positions,
        robot_position=path_positions[-1] if path_positions else None,
        title=("Solução encontrada" if result.found else "Busca sem solução"),
    )
    frame_area.pyplot(figure)
    plt.close(figure)
    _display_result_metrics(result)


def _render_current_maze(maze: Maze) -> None:
    figure = render_maze(maze, title="Cenário atual — aguardando execução")
    _render_figure(figure)


def _sidebar() -> None:
    st.sidebar.header("Controles do simulador")
    st.sidebar.number_input("Semente aleatória", min_value=0, step=1, key="maze_seed")
    st.sidebar.slider(
        "Quantidade de obstáculos",
        min_value=MIN_OBSTACLES,
        max_value=MAX_OBSTACLES,
        key="obstacle_count",
    )
    st.sidebar.selectbox("Algoritmo", ALGORITHM_NAMES, key="selected_algorithm")
    st.sidebar.selectbox(
        "Velocidade da animação",
        tuple(ANIMATION_SPEEDS),
        key="animation_speed",
    )
    st.sidebar.divider()

    if st.sidebar.button("🧩 Gerar labirinto", use_container_width=True):
        st.session_state.maze = Maze.generate(
            seed=int(st.session_state.maze_seed),
            obstacle_count=int(st.session_state.obstacle_count),
        )
        _clear_execution_state()

    if st.sidebar.button("▶ Executar BFS", use_container_width=True):
        _run_single_algorithm("BFS")

    if st.sidebar.button("▶ Executar A*", use_container_width=True):
        _run_single_algorithm("A*")

    if st.sidebar.button("⚖ Comparar algoritmos", use_container_width=True):
        maze = st.session_state.maze
        st.session_state.comparison_results = {
            "BFS": breadth_first_search(maze),
            "A*": a_star_search(maze),
        }
        st.session_state.active_result = st.session_state.comparison_results[
            st.session_state.selected_algorithm
        ]
        st.session_state.pending_animation = False


def _render_simulator_tab() -> None:
    maze = st.session_state.maze
    result = st.session_state.active_result
    if result is None:
        _render_current_maze(maze)
        st.info("Gere um cenário ou execute um algoritmo pela barra lateral.")
        return

    animate = st.session_state.pending_animation
    st.session_state.pending_animation = False
    _render_result(
        maze,
        result,
        ANIMATION_SPEEDS[st.session_state.animation_speed],
        animate,
    )


def _render_comparison_tab() -> None:
    comparison = st.session_state.comparison_results
    if comparison is None:
        st.info("Use 'Comparar algoritmos' para executar BFS e A* no mesmo cenário.")
        return

    st.subheader("Comparação no mesmo cenário")
    columns = st.columns(2)
    for column, algorithm in zip(columns, ALGORITHM_NAMES):
        result = comparison[algorithm]
        with column:
            st.markdown(f"### {algorithm}")
            figure = render_maze(
                st.session_state.maze,
                explored_positions=tuple(state.position for state in result.explored_sequence),
                path=result.path,
                robot_position=result.path[-1] if result.path else None,
                title=algorithm,
            )
            _render_figure(figure)
            st.metric("Solução", "Sim" if result.found else "Não")
            st.metric("Movimentos", _metric_value(result.moves))
            st.metric("Estados explorados", result.explored_states)
            st.metric("Energia restante", _metric_value(result.remaining_energy))
            st.metric("Tempo", _metric_value(result.execution_time_ms, " ms"))

    bfs_result = comparison["BFS"]
    astar_result = comparison["A*"]
    if bfs_result.found and astar_result.found and bfs_result.moves == astar_result.moves:
        st.info(
            "Os dois algoritmos encontraram o mesmo comprimento de caminho. "
            "Isso não torna A* automaticamente superior; estados explorados e tempo "
            "devem ser observados neste cenário."
        )
    elif not bfs_result.found or not astar_result.found:
        st.warning("Pelo menos um algoritmo não encontrou solução neste cenário.")
    else:
        st.info("Os comprimentos encontrados diferem; compare também energia e estados explorados.")


def _render_experiments_tab() -> None:
    st.subheader("Laboratório de experimentos")
    batch_size = st.selectbox("Quantidade de labirintos", (10, 30, 50), key="batch_size")
    seed_start = st.number_input("Semente inicial dos experimentos", min_value=0, step=1, value=10_000)
    if st.button("🚀 Executar lote reproduzível", type="primary"):
        progress = st.progress(0, text="Preparando experimentos...")

        def update_progress(completed: int, total: int) -> None:
            percentage = int(completed * 100 / total)
            progress.progress(percentage, text=f"Executando {completed}/{total} algoritmos...")

        records = run_experiments(
            int(batch_size),
            seed_start=int(seed_start),
            progress_callback=update_progress,
        )
        st.session_state.experiment_records = records
        progress.progress(100, text="Experimentos concluídos.")

    records = st.session_state.experiment_records
    if records is None:
        st.info("Escolha um lote para gerar dados reais de comparação.")
        return

    frame = records_to_dataframe(records)
    summary = comparison_summary(frame)
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.markdown("#### Médias e taxa de sucesso")
    st.dataframe(summary, use_container_width=True, hide_index=True)

    figure = build_comparison_figure(frame)
    _render_figure(figure)
    figure_bytes = figure_to_png_bytes(figure)
    st.download_button(
        "⬇ Baixar resultados completos (CSV)",
        data=records_to_csv_bytes(records),
        file_name="experimentos_robot_maze.csv",
        mime="text/csv",
    )
    st.download_button(
        "⬇ Baixar tabela comparativa (CSV)",
        data=dataframe_to_csv_bytes(summary),
        file_name="comparacao_robot_maze.csv",
        mime="text/csv",
    )
    st.download_button(
        "⬇ Baixar gráficos (PNG)",
        data=figure_bytes,
        file_name="comparacao_robot_maze.png",
        mime="image/png",
    )
    if st.button("💾 Salvar arquivos em results/"):
        csv_path = save_experiment_csv(records)
        png_path = save_figure_png(figure)
        st.success(f"Arquivos salvos: `{csv_path}` e `{png_path}`")


def render_dashboard() -> None:
    """Renderiza a aplicação Streamlit completa."""
    st.set_page_config(
        page_title="Robot Maze AI",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        .main-title { color: #1E3A8A; margin-bottom: 0; }
        .subtitle { color: #64748B; margin-top: 0; }
        div[data-testid="stMetric"] { background: #F8FAFC; border: 1px solid #E2E8F0; padding: 0.7rem; border-radius: 0.7rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    _initialize_session_state()
    _sidebar()

    st.markdown('<h1 class="main-title">🤖 Robot Maze AI</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Simulador de Inteligência Artificial Simbólica · BFS × A*</p>',
        unsafe_allow_html=True,
    )
    maze = st.session_state.maze
    st.caption(
        f"Cenário atual: semente {st.session_state.maze_seed} · "
        f"{len(maze.obstacles)} obstáculos · entrada (1,1) · saída (10,10)"
    )

    simulator_tab, comparison_tab, experiments_tab = st.tabs(
        ["🧭 Simulador", "⚖ Comparação BFS × A*", "🧪 Experimentos"]
    )
    with simulator_tab:
        _render_simulator_tab()
    with comparison_tab:
        _render_comparison_tab()
    with experiments_tab:
        _render_experiments_tab()
