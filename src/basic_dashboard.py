"""Interface Streamlit enxuta para a demonstração acadêmica do simulador.

O módulo mantém somente o fluxo essencial da AV3: gerar um mapa 10x10,
executar BFS ou A* e comparar os dois algoritmos no mesmo cenário. Recursos
experimentais permanecem disponíveis no histórico e em módulos próprios, mas
não competem com a demonstração visual principal.
"""

from __future__ import annotations

import time
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from .astar import a_star_search
from .bfs import breadth_first_search
from .classic_renderer import render_classic_maze
from .futuristic_renderer import render_futuristic_maze
from .forest_renderer import render_forest_maze
from .dungeon_renderer import render_dungeon_maze
from .maze import MAX_OBSTACLES, MIN_OBSTACLES, Maze
from .models import SearchResult

ALGORITHM_NAMES = ("BFS", "A*")
ANIMATION_SPEEDS = {
    "Desligada": 0.0,
    "Rápida": 0.02,
    "Normal": 0.08,
    "Lenta": 0.20,
}


def _initialize_session_state() -> None:
    if "basic_maze" not in st.session_state:
        st.session_state.basic_maze = Maze.generate(seed=42, obstacle_count=15)
    defaults = {
        "basic_seed": 42,
        "basic_use_seed": True,
        "basic_obstacle_count": 15,
        "basic_algorithm": "BFS",
        "basic_animation_speed": "Normal",
        "basic_theme": "Labirinto Clássico",
        "basic_results": {},
        "basic_comparison": None,
        "basic_active_result": None,
        "basic_pending_animation": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _clear_execution_state() -> None:
    st.session_state.basic_results = {}
    st.session_state.basic_comparison = None
    st.session_state.basic_active_result = None
    st.session_state.basic_pending_animation = False


def _metric_value(value: Any, suffix: str = "") -> str:
    if value is None:
        return "Não aplicável"
    if isinstance(value, float):
        return f"{value:.2f}{suffix}"
    return f"{value}{suffix}"


def _run_algorithm(algorithm: str) -> SearchResult:
    maze = st.session_state.basic_maze
    result = breadth_first_search(maze) if algorithm == "BFS" else a_star_search(maze)
    st.session_state.basic_results[algorithm] = result
    st.session_state.basic_active_result = result
    st.session_state.basic_comparison = None
    st.session_state.basic_pending_animation = True
    return result


def _run_comparison() -> None:
    maze = st.session_state.basic_maze
    comparison = {
        "BFS": breadth_first_search(maze),
        "A*": a_star_search(maze),
    }
    st.session_state.basic_comparison = comparison
    st.session_state.basic_results = dict(comparison)
    st.session_state.basic_active_result = comparison[st.session_state.basic_algorithm]
    st.session_state.basic_pending_animation = False


def _render_result_metrics(result: SearchResult) -> None:
    metrics = st.columns(6)
    metrics[0].metric("Algoritmo", result.algorithm)
    metrics[1].metric("Solução", "Sim" if result.found else "Não")
    metrics[2].metric("Movimentos", _metric_value(result.moves))
    metrics[3].metric("Estados", result.explored_states)
    metrics[4].metric("Energia", _metric_value(result.remaining_energy))
    metrics[5].metric("Tempo", _metric_value(result.execution_time_ms, " ms"))
    if result.found:
        recharge_text = ", ".join(
            f"({row + 1},{col + 1})" for row, col in result.recharges_consumed
        ) or "nenhuma"
        st.caption(
            f"Recargas consumidas: {len(result.recharges_consumed)} — {recharge_text}"
        )
    else:
        st.warning(
            "Não existe percurso viável com a energia e as recargas disponíveis."
        )


def _render_maze(maze: Maze, result: SearchResult | None = None) -> None:
    explored = tuple(state.position for state in result.explored_sequence) if result else ()
    path = result.path if result and result.found else ()
    robot_position = path[-1] if path else maze.start
    renderer_arguments = {
        "explored_positions": explored,
        "path": path,
        "robot_position": robot_position,
        "algorithm": result.algorithm if result else "Aguardando execução",
        "moves": result.moves if result else None,
        "explored_states": result.explored_states if result else None,
        "energy": result.remaining_energy if result and result.found else 30,
    }
    if st.session_state.basic_theme == "Laboratório Futurista":
        svg = render_futuristic_maze(maze, **renderer_arguments)
    elif st.session_state.basic_theme == "Floresta":
        svg = render_forest_maze(maze, **renderer_arguments)
    elif st.session_state.basic_theme == "Dungeon Pixel Art":
        svg = render_dungeon_maze(maze, **renderer_arguments)
    else:
        svg = render_classic_maze(
            maze,
            title=("Solução encontrada" if result and result.found else "Robot Maze AI"),
            **renderer_arguments,
        )
    iframe_height = 850 if st.session_state.basic_theme in {
        "Laboratório Futurista",
        "Floresta",
        "Dungeon Pixel Art",
    } else 730
    components.html(svg, height=iframe_height, scrolling=False)


def _render_sidebar() -> None:
    st.sidebar.header("Controles do simulador")
    st.sidebar.number_input("Semente", min_value=0, step=1, key="basic_seed")
    st.sidebar.checkbox("Usar semente reproduzível", key="basic_use_seed")
    st.sidebar.slider(
        "Quantidade de obstáculos",
        min_value=MIN_OBSTACLES,
        max_value=MAX_OBSTACLES,
        key="basic_obstacle_count",
    )
    st.sidebar.selectbox("Algoritmo", ALGORITHM_NAMES, key="basic_algorithm")
    st.sidebar.selectbox(
        "Velocidade da animação",
        tuple(ANIMATION_SPEEDS),
        key="basic_animation_speed",
    )
    st.sidebar.selectbox(
        "Tema visual",
        (
            "Labirinto Clássico",
            "Laboratório Futurista",
            "Floresta",
            "Dungeon Pixel Art",
        ),
        key="basic_theme",
        help="A aparência é estética e não altera o mapa nem os algoritmos.",
    )
    st.sidebar.divider()

    if st.sidebar.button("🧩 Gerar labirinto", use_container_width=True):
        seed = int(st.session_state.basic_seed) if st.session_state.basic_use_seed else int(time.time())
        st.session_state.basic_maze = Maze.generate(
            seed=seed,
            obstacle_count=int(st.session_state.basic_obstacle_count),
        )
        _clear_execution_state()
    if st.sidebar.button("▶ Executar BFS", use_container_width=True):
        _run_algorithm("BFS")
    if st.sidebar.button("▶ Executar A*", use_container_width=True):
        _run_algorithm("A*")
    if st.sidebar.button("⚖ Comparar algoritmos", use_container_width=True):
        _run_comparison()


def _render_simulator_tab() -> None:
    maze = st.session_state.basic_maze
    result = st.session_state.basic_active_result
    if result is None:
        _render_maze(maze)
        st.info("Gere um cenário ou execute um algoritmo pela barra lateral.")
        return

    if st.session_state.basic_pending_animation:
        st.caption(
            "A expansão de estados é virtual. A energia é consumida somente no "
            "percurso físico reconstruído."
        )
        st.session_state.basic_pending_animation = False
    _render_maze(maze, result)
    _render_result_metrics(result)


def _render_comparison_tab() -> None:
    comparison = st.session_state.basic_comparison
    if comparison is None:
        st.info("Use 'Comparar algoritmos' para executar BFS e A* no mesmo cenário.")
        return

    st.subheader("Comparação no mesmo cenário")
    columns = st.columns(2)
    for column, algorithm in zip(columns, ALGORITHM_NAMES):
        result = comparison[algorithm]
        with column:
            st.markdown(f"### {algorithm}")
            _render_maze(st.session_state.basic_maze, result)
            _render_result_metrics(result)

    bfs_result = comparison["BFS"]
    astar_result = comparison["A*"]
    if bfs_result.found and astar_result.found and bfs_result.moves == astar_result.moves:
        st.info(
            "Os dois algoritmos encontraram o mesmo comprimento de caminho. "
            "Isso não torna A* automaticamente superior: observe estados explorados "
            "e tempo neste cenário."
        )
    elif not bfs_result.found or not astar_result.found:
        st.warning("Pelo menos um algoritmo não encontrou solução neste cenário.")
    else:
        st.info("Os comprimentos encontrados diferem; compare também energia e estados.")


def render_basic_dashboard() -> None:
    """Renderiza a interface acadêmica básica sem recursos experimentais."""
    st.set_page_config(
        page_title="Robot Maze AI",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        .stApp { background: #ffffff; color: #111827; }
        [data-testid="stHeader"] { background: #ffffff; }
        section[data-testid="stSidebar"] { background: #f7f7f7; border-right: 1px solid #e5e7eb; }
        section[data-testid="stSidebar"] * { color: #1f2937; }
        section[data-testid="stSidebar"] input { background: #ffffff; color: #1f2937; }
        section[data-testid="stSidebar"] [data-baseweb="select"] > div { background: #ffffff; color: #1f2937; }
        section[data-testid="stSidebar"] button { color: #1f2937 !important; }
        div[data-baseweb="tab-list"] { border-bottom-color: #d1d5db; }
        button[data-baseweb="tab"] { color: #374151; }
        .main-title { color: #1E3A8A; margin-bottom: 0; }
        .subtitle { color: #64748B; margin-top: 0; }
        div[data-testid="stMetric"] {
            background: #F8FAFC; border: 1px solid #E2E8F0;
            padding: 0.7rem; border-radius: 0.7rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    _initialize_session_state()
    _render_sidebar()

    st.markdown('<h1 class="main-title">Robot Maze AI</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Simulador de Inteligência Artificial Simbólica · BFS × A*</p>',
        unsafe_allow_html=True,
    )
    maze = st.session_state.basic_maze
    st.caption(
        f"Matriz {maze.rows}×{maze.cols} · {len(maze.obstacles)} obstáculos · "
        "entrada (1,1) · saída (10,10) · energia inicial 30"
    )

    simulator_tab, comparison_tab = st.tabs(
        ["🧭 Simulador", "⚖ Comparação BFS × A*"]
    )
    with simulator_tab:
        _render_simulator_tab()
    with comparison_tab:
        _render_comparison_tab()
