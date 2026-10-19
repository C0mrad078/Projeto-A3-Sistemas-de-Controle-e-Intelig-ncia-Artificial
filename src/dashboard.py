"""Dashboard Streamlit do Robot Maze AI, em português brasileiro."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt

from .astar import a_star_search
from .bfs import breadth_first_search
from .dashboard_analysis import (
    comparison_table,
    energy_figure,
    energy_rows,
    experiment_figures,
    experiment_summary,
    interpret_results,
    performance_figures,
    scenario_indicators,
    scenario_outcomes,
)
from .experiments import records_to_dataframe, run_experiments
from .export import (
    dataframe_to_csv_bytes,
    plotly_figure_to_png_bytes,
    records_to_csv_bytes,
    save_experiment_csv,
    save_figure_png,
)
from .maze import MAX_OBSTACLES, MIN_OBSTACLES, Maze
from .models import SearchResult
from .scenarios import (
    CELL_KINDS,
    GENERATION_MODES,
    apply_cell_edit,
    config_from_json,
    config_to_json,
    custom_scenario,
    custom_validation,
    generate_scenario,
    obstacle_range,
)
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
        st.session_state.maze = generate_scenario(
            "Aleatório", seed=42, obstacle_count=15
        ).maze
    defaults = {
        "maze_seed": 42,
        "use_seed": True,
        "obstacle_count": 15,
        "selected_algorithm": "BFS",
        "animation_speed": "Normal",
        "generation_mode": "Aleatório",
        "results": {},
        "comparison_results": None,
        "experiment_records": None,
        "active_result": None,
        "custom_editor_maze": None,
        "custom_base_maze": None,
        "saved_custom_json": None,
        "animation_phase": "exploração",
        "animation_index": 0,
        "animation_playing": False,
        "show_explored": True,
        "only_final_path": False,
        "experiment_mode": "Aleatório",
        "experiment_batch_preset": "10",
        "experiment_custom_batch": 10,
        "experiment_seed_start": 10_000,
        "experiment_repeat_custom": True,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _clear_execution_state() -> None:
    st.session_state.results = {}
    st.session_state.comparison_results = None
    st.session_state.active_result = None
    st.session_state.animation_phase = "exploração"
    st.session_state.animation_index = 0
    st.session_state.animation_playing = False


def _run_single_algorithm(algorithm: str) -> SearchResult | None:
    if not _custom_map_is_ready():
        return None
    maze = st.session_state.maze
    result = breadth_first_search(maze) if algorithm == "BFS" else a_star_search(maze)
    st.session_state.results[algorithm] = result
    st.session_state.active_result = result
    st.session_state.comparison_results = None
    st.session_state.animation_phase = "exploração"
    st.session_state.animation_index = 0
    return result


def _run_comparison() -> None:
    if not _custom_map_is_ready():
        return
    maze = st.session_state.maze
    comparison = {
        "BFS": breadth_first_search(maze),
        "A*": a_star_search(maze),
    }
    st.session_state.comparison_results = comparison
    st.session_state.results = dict(comparison)
    st.session_state.active_result = comparison[st.session_state.selected_algorithm]
    st.session_state.animation_phase = "exploração"
    st.session_state.animation_index = 0
    st.session_state.animation_playing = False


def _metric_value(value: Any, suffix: str = "") -> str:
    if value is None:
        return "Não aplicável"
    if isinstance(value, float):
        return f"{value:.2f}{suffix}"
    return f"{value}{suffix}"


def _parse_seed() -> int | None:
    return int(st.session_state.maze_seed) if st.session_state.use_seed else None


def _custom_map_is_ready() -> bool:
    if st.session_state.maze.mode != "Personalizado":
        return True
    valid, errors = custom_validation(st.session_state.maze)
    if not valid:
        st.warning(
            "O cenário personalizado ainda não está pronto para execução: "
            + " ".join(errors)
        )
    return valid


def _generate_from_controls() -> None:
    mode = st.session_state.generation_mode
    seed = _parse_seed()
    count = int(st.session_state.obstacle_count)
    if mode == "Personalizado":
        generated = generate_scenario("Aleatório", seed=seed, obstacle_count=count)
        custom = custom_scenario(generated.maze, seed=generated.seed)
        st.session_state.maze = custom.maze
        st.session_state.custom_base_maze = custom.maze
        st.session_state.custom_editor_maze = custom.maze
    else:
        scenario = generate_scenario(mode, seed=seed)
        st.session_state.maze = scenario.maze
        st.session_state.custom_base_maze = None
        st.session_state.custom_editor_maze = None
    _clear_execution_state()


def _render_sidebar() -> None:
    st.sidebar.header("Controles do simulador")
    st.sidebar.number_input("Semente", min_value=0, step=1, key="maze_seed")
    st.sidebar.checkbox("Usar semente reproduzível", key="use_seed")
    st.sidebar.slider(
        "Quantidade de obstáculos",
        min_value=MIN_OBSTACLES,
        max_value=MAX_OBSTACLES,
        key="obstacle_count",
        help="Aplicado ao modo Personalizado; os demais modos usam sua própria faixa.",
    )
    # Algoritmo e velocidade continuam no fluxo principal da barra lateral.
    st.sidebar.selectbox("Algoritmo", ALGORITHM_NAMES, key="selected_algorithm")
    st.sidebar.selectbox(
        "Velocidade da animação", tuple(ANIMATION_SPEEDS), key="animation_speed"
    )
    st.sidebar.selectbox("Modalidade", GENERATION_MODES, key="generation_mode")
    mode = st.session_state.generation_mode
    lower, upper = obstacle_range(mode)
    st.sidebar.caption(
        f"Faixa da modalidade: {lower}–{upper} obstáculos. "
        "Mais obstáculos não garantem maior dificuldade real."
    )
    st.sidebar.divider()

    if st.sidebar.button("🧩 Gerar labirinto", width="stretch"):
        _generate_from_controls()
    if st.sidebar.button("▶ Executar BFS", width="stretch"):
        _run_single_algorithm("BFS")
    if st.sidebar.button("▶ Executar A*", width="stretch"):
        _run_single_algorithm("A*")
    if st.sidebar.button("⚖ Comparar algoritmos", width="stretch"):
        _run_comparison()


def _render_scenario_metadata(maze: Maze) -> None:
    indicators = scenario_indicators(maze, st.session_state.active_result)
    st.subheader("Cenário atual")
    metadata = st.columns(5)
    metadata[0].metric("Identificador", maze.scenario_id or "não informado")
    metadata[1].metric("Modalidade", maze.mode)
    metadata[2].metric("Semente", "não informada" if maze.seed is None else maze.seed)
    metadata[3].metric("Obstáculos", len(maze.obstacles))
    metadata[4].metric("Células livres", len(maze.free_positions))
    metadata = st.columns(5)
    metadata[0].metric("Recargas +5", sum(value == 5 for value in maze.recharges.values()))
    metadata[1].metric("Recargas +10", sum(value == 10 for value in maze.recharges.values()))
    metadata[2].metric("Energia inicial", 30)
    metadata[3].metric("Entrada", "(1,1)")
    metadata[4].metric("Saída", "(10,10)")
    st.caption(
        f"Distância Manhattan: {indicators['distancia_manhattan']} · "
        f"Caminho geométrico ignorando energia: "
        f"{'sim' if indicators['caminho_geometrico_existe'] else 'não'} · "
        f"Distância geométrica mínima: {_metric_value(indicators['distancia_geometrica_minima'])} · "
        f"Energia adicional no caminho escolhido: "
        f"{_metric_value(indicators['energia_adicional_necessaria'])}"
    )
    st.info(
        "Indicadores geométricos consideram apenas obstáculos. Um caminho geométrico "
        "não garante que exista percurso viável com energia e recargas."
    )


def _render_custom_editor() -> None:
    if st.session_state.generation_mode != "Personalizado":
        return
    maze = st.session_state.custom_editor_maze or st.session_state.maze
    st.subheader("Editor visual do cenário personalizado")
    st.caption(
        "Clique nas células para alternar Livre → Obstáculo → +5 → +10. "
        "A entrada e a saída permanecem protegidas."
    )
    for row in range(10):
        columns = st.columns(10, gap="small")
        for col, column in enumerate(columns):
            position = (row, col)
            if position in {maze.start, maze.goal}:
                label = "ENT" if position == maze.start else "SAÍ"
                kind = "Livre"
            elif position in maze.obstacles:
                label, kind = "■", "Obstáculo"
            elif position in maze.recharges:
                value = maze.recharges[position]
                label, kind = f"+{value}", f"Recarga +{value}"
            else:
                label, kind = "·", "Livre"
            next_kind = CELL_KINDS[(CELL_KINDS.index(kind) + 1) % len(CELL_KINDS)]
            if column.button(
                label,
                key=f"editor_cell_{row}_{col}",
                help=f"Linha {row + 1}, coluna {col + 1}: {kind}. Próximo: {next_kind}.",
                width="stretch",
            ):
                try:
                    edited_maze = apply_cell_edit(
                        maze, position, next_kind
                    )
                    st.session_state.custom_editor_maze = edited_maze
                    st.session_state.maze = edited_maze
                    _clear_execution_state()
                except ValueError as error:
                    st.warning(str(error))
    edited = st.session_state.custom_editor_maze or maze
    valid, errors = custom_validation(edited)
    if valid:
        st.success("Configuração válida: pronta para executar os algoritmos.")
    else:
        st.warning("Configuração temporariamente incompleta: " + " ".join(errors))
    actions = st.columns(4)
    with actions[0]:
        if st.button("Salvar cenário", key="save_custom_scenario"):
            st.session_state.saved_custom_json = config_to_json(edited, mode="Personalizado")
            st.success("Cenário salvo na sessão.")
    with actions[1]:
        if st.button("Restaurar cenário", key="restore_custom_scenario"):
            if st.session_state.saved_custom_json:
                scenario = config_from_json(st.session_state.saved_custom_json)
                st.session_state.custom_editor_maze = scenario.maze
                st.session_state.maze = scenario.maze
                _clear_execution_state()
    with actions[2]:
        if st.button("Limpar alterações", key="clear_custom_edits"):
            st.session_state.custom_editor_maze = st.session_state.custom_base_maze or maze
            _clear_execution_state()
    with actions[3]:
        st.download_button(
            "Exportar JSON",
            data=config_to_json(edited, mode="Personalizado"),
            file_name="cenario_personalizado.json",
            mime="application/json",
            key="download_custom_json",
        )
    uploaded = st.file_uploader(
        "Importar configuração JSON válida", type="json", key="custom_json_upload"
    )
    if uploaded is not None:
        try:
            scenario = config_from_json(uploaded.getvalue().decode("utf-8"))
            st.session_state.custom_editor_maze = scenario.maze
            st.session_state.maze = scenario.maze
            st.success("Configuração importada. Execute os algoritmos quando desejar.")
        except (UnicodeDecodeError, ValueError) as error:
            st.error(f"Não foi possível importar o cenário: {error}")


def _render_maze(maze: Maze, result: SearchResult | None = None) -> None:
    explored = (
        tuple(state.position for state in result.explored_sequence)
        if result is not None and st.session_state.overview_show_explored
        else ()
    )
    path = result.path if result is not None and result.found else ()
    figure = render_maze(
        maze,
        explored_positions=explored,
        path=path,
        robot_position=path[-1] if path else None,
        title="Labirinto e resultado selecionado" if result else "Labirinto aguardando execução",
    )
    st.pyplot(figure, use_container_width=True)
    plt.close(figure)


def _render_result_card(column, result: SearchResult | None, algorithm: str) -> None:
    with column.container(border=True):
        st.markdown(f"### {'🔵' if algorithm == 'BFS' else '🟣'} {algorithm}")
        if result is None:
            st.info("Ainda não executado")
            return
        st.metric("Solução encontrada", "Sim" if result.found else "Não")
        left, right = st.columns(2)
        left.metric("Movimentos", _metric_value(result.moves))
        right.metric("Estados explorados", result.explored_states)
        left.metric("Energia restante", _metric_value(result.remaining_energy))
        right.metric("Tempo", _metric_value(result.execution_time_ms, " ms"))
        st.metric("Recargas consumidas", len(result.recharges_consumed) if result.found else "Não aplicável")
        if not result.found:
            st.caption("Nenhuma trajetória completa será inventada para este algoritmo.")


def _render_overview() -> None:
    maze = st.session_state.maze
    _render_scenario_metadata(maze)
    _render_custom_editor()
    st.checkbox("Mostrar células exploradas", key="overview_show_explored")
    selected = st.session_state.active_result
    results = st.session_state.comparison_results or st.session_state.results
    _render_maze(maze, selected)
    cards = st.columns(2)
    for column, algorithm in zip(cards, ALGORITHM_NAMES):
        _render_result_card(column, results.get(algorithm), algorithm)
    if len(results) == 2:
        st.subheader("Tabela comparativa")
        st.dataframe(comparison_table(results), use_container_width=True, hide_index=True)
        st.subheader("O que estes resultados significam?")
        for message in interpret_results(results):
            st.write(f"• {message}")
    elif selected is None:
        st.info("Gere um cenário e execute BFS, A* ou a comparação pela barra lateral.")


def _animation_view(result: SearchResult) -> dict[str, Any]:
    phase = st.session_state.animation_phase
    index = st.session_state.animation_index
    if phase == "exploração":
        explored = tuple(state.position for state in result.explored_sequence[: index + 1])
        return {"explored": explored, "path": (), "robot": None, "title": "Expansão virtual"}
    if not result.found:
        return {"explored": (), "path": (), "robot": None, "title": "Busca sem solução"}
    visible = result.state_sequence[: min(index + 1, len(result.state_sequence))]
    return {
        "explored": tuple(state.position for state in result.explored_sequence),
        "path": tuple(state.position for state in visible),
        "robot": visible[-1].position,
        "title": "Percurso físico do robô",
    }


def _advance_animation(direction: int = 1) -> None:
    results = st.session_state.comparison_results or st.session_state.results
    if not results:
        return
    if direction < 0:
        if st.session_state.animation_phase == "físico" and st.session_state.animation_index > 0:
            st.session_state.animation_index -= 1
        else:
            st.session_state.animation_phase = "exploração"
            st.session_state.animation_index = max(0, st.session_state.animation_index - 1)
        return
    max_exploration = max((len(result.explored_sequence) - 1 for result in results.values()), default=0)
    if st.session_state.animation_phase == "exploração":
        if st.session_state.animation_index < max_exploration:
            st.session_state.animation_index += 1
        else:
            st.session_state.animation_phase = "físico"
            st.session_state.animation_index = 0
    else:
        max_physical = max((len(result.state_sequence) - 1 for result in results.values() if result.found), default=0)
        st.session_state.animation_index = min(st.session_state.animation_index + 1, max_physical)


def _render_comparison_paths() -> None:
    comparison = st.session_state.comparison_results
    if comparison is None:
        st.info("Use 'Comparar algoritmos' para executar BFS e A* no mesmo cenário.")
        return
    controls = st.columns(6)
    if controls[0].button("▶ Iniciar animação", key="animation_start"):
        st.session_state.animation_phase = "exploração"
        st.session_state.animation_index = 0
        st.session_state.animation_playing = True
    if controls[1].button("⏸ Pausar", key="animation_pause"):
        st.session_state.animation_playing = False
    if controls[2].button("↻ Reiniciar", key="animation_reset"):
        st.session_state.animation_phase = "exploração"
        st.session_state.animation_index = 0
        st.session_state.animation_playing = False
    if controls[3].button("⏭ Próximo passo", key="animation_next"):
        _advance_animation(1)
        st.session_state.animation_playing = False
    if controls[4].button("⏮ Passo anterior", key="animation_previous"):
        _advance_animation(-1)
        st.session_state.animation_playing = False
    controls[5].checkbox("Mostrar exploração", key="show_explored")
    st.checkbox("Mostrar apenas o caminho final", key="only_final_path")
    st.caption(
        "Expansão virtual consulta estados sem representar deslocamento físico. "
        "A energia só muda nos estados do caminho físico."
    )
    columns = st.columns(2)
    for column, algorithm in zip(columns, ALGORITHM_NAMES):
        result = comparison[algorithm]
        view = _animation_view(result)
        with column:
            st.markdown(f"### {'🔵' if algorithm == 'BFS' else '🟣'} {algorithm}")
            figure = render_maze(
                st.session_state.maze,
                explored_positions=(
                    () if st.session_state.only_final_path or not st.session_state.show_explored else view["explored"]
                ),
                path=view["path"] if result.found else (),
                robot_position=view["robot"],
                title=view["title"],
            )
            st.pyplot(figure, use_container_width=True)
            plt.close(figure)
            st.metric("Estados explorados", result.explored_states)
            st.metric("Movimentos", _metric_value(result.moves))
            st.metric("Energia", _metric_value(result.remaining_energy))
    if st.session_state.animation_playing and ANIMATION_SPEEDS[st.session_state.animation_speed] > 0:
        _advance_animation(1)
        time.sleep(ANIMATION_SPEEDS[st.session_state.animation_speed])
        st.rerun()


def _render_performance() -> None:
    results = st.session_state.comparison_results or st.session_state.results
    if len(results) < 2:
        st.info("Execute a comparação para visualizar o desempenho dos dois algoritmos.")
        return
    figures = performance_figures(results)
    for left_key, right_key in (("estados", "tempo"), ("movimentos", "energia")):
        columns = st.columns(2)
        for column, key in zip(columns, (left_key, right_key)):
            with column:
                st.plotly_chart(figures[key], use_container_width=True)
                st.download_button(
                    f"⬇ PNG — {key}",
                    data=plotly_figure_to_png_bytes(figures[key]),
                    file_name=f"{key}_robot_maze.png",
                    mime="image/png",
                    key=f"download_performance_{key}",
                )
    bfs = results["BFS"]
    astar = results["A*"]
    if bfs.found and astar.found:
        st.write(
            f"Diferença de estados (A* − BFS): **{astar.explored_states - bfs.explored_states}** · "
            f"diferença de tempo (A* − BFS): **{astar.execution_time_ms - bfs.execution_time_ms:.3f} ms**. "
            "As unidades são apresentadas separadamente."
        )
    st.subheader("Entenda o resultado")
    for message in interpret_results(results):
        st.write(f"• {message}")


def _render_energy() -> None:
    results = st.session_state.comparison_results or st.session_state.results
    if not results or not any(result.found for result in results.values()):
        st.warning("Nenhum algoritmo possui uma solução para detalhar a energia.")
        return
    figure = energy_figure(st.session_state.maze, results)
    st.plotly_chart(figure, use_container_width=True)
    st.download_button(
        "⬇ PNG — evolução da energia",
        data=plotly_figure_to_png_bytes(figure),
        file_name="energia_robot_maze.png",
        mime="image/png",
        key="download_energy_png",
    )
    solved = {algorithm: result for algorithm, result in results.items() if result.found}
    selection = st.selectbox("Algoritmo do percurso detalhado", tuple(solved), key="energy_algorithm")
    rows = energy_rows(st.session_state.maze, solved[selection])
    frame = pd.DataFrame(rows)
    movement = st.selectbox(
        "Movimento para inspeção",
        options=[0] + [row["movimento"] for row in rows],
        format_func=lambda value: "Estado inicial" if value == 0 else f"Movimento {value}",
        key="energy_movement",
    )
    if movement == 0:
        st.info("Estado inicial: posição (1,1), energia 30, sem custo de movimento.")
    else:
        st.dataframe(frame[frame["movimento"] == movement], use_container_width=True, hide_index=True)
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇ CSV — percurso de energia",
        data=dataframe_to_csv_bytes(frame),
        file_name=f"energia_{selection.lower().replace('*', 'astar')}.csv",
        mime="text/csv",
        key="download_energy_csv",
    )


def _render_experiments() -> None:
    st.subheader("Laboratório de experimentos")
    mode = st.radio(
        "Modalidade dos cenários",
        GENERATION_MODES,
        key="experiment_mode",
        horizontal=True,
    )
    batch_preset = st.selectbox(
        "Quantidade de cenários", ("10", "30", "50", "Personalizada"), key="experiment_batch_preset"
    )
    if batch_preset == "Personalizada":
        batch_size = int(st.number_input("Quantidade personalizada (1–100)", min_value=1, max_value=100, value=10, step=1, key="experiment_custom_batch"))
        custom_batch = True
    else:
        batch_size = int(batch_preset)
        custom_batch = False
    seed_start = st.number_input("Semente inicial", min_value=0, step=1, key="experiment_seed_start")
    repeat_custom = False
    if mode == "Personalizado":
        repeat_custom = st.checkbox(
            "Repetir exatamente o cenário personalizado atual",
            key="experiment_repeat_custom",
            help="Desmarcado: gera cenários personalizados diferentes com a mesma quantidade de obstáculos.",
        )
    if st.button("🚀 Executar lote reproduzível", type="primary", key="run_experiments"):
        progress = st.progress(0, text="Preparando experimentos...")

        def update_progress(completed: int, total: int) -> None:
            progress.progress(int(completed * 100 / total), text=f"Executando {completed}/{total} algoritmos...")

        records = run_experiments(
            batch_size,
            seed_start=int(seed_start),
            mode=mode,
            obstacle_count=(int(st.session_state.obstacle_count) if mode == "Personalizado" and not repeat_custom else None),
            custom_maze=(st.session_state.maze if mode == "Personalizado" and repeat_custom else None),
            custom_batch=custom_batch,
            progress_callback=update_progress,
        )
        st.session_state.experiment_records = records
        progress.progress(100, text="Experimentos concluídos.")

    records = st.session_state.experiment_records
    if records is None:
        st.info("Escolha os parâmetros e execute um lote para gerar dados reais.")
        return
    frame = records_to_dataframe(records)
    summary = experiment_summary(frame)
    outcomes = scenario_outcomes(frame)
    st.metric("Registros produzidos", len(frame))
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.subheader("Resumo por modalidade e algoritmo")
    st.dataframe(summary, use_container_width=True, hide_index=True)
    figures = experiment_figures(frame)
    for left_key, right_key in (("sucesso", "estados"), ("tempo", "movimentos"), ("energia", "recargas")):
        columns = st.columns(2)
        for column, key in zip(columns, (left_key, right_key)):
            with column:
                st.plotly_chart(figures[key], use_container_width=True)
                st.download_button(
                    f"⬇ PNG — {key}",
                    data=plotly_figure_to_png_bytes(figures[key]),
                    file_name=f"experimentos_{key}.png",
                    mime="image/png",
                    key=f"download_experiment_{key}",
                )
    st.subheader("Resultado por cenário")
    st.dataframe(outcomes, use_container_width=True, hide_index=True)
    st.caption("Movimentos, energia e recargas médias consideram somente execuções solucionadas; a coluna amostra_solucoes mostra o tamanho dessa amostra.")
    st.download_button(
        "⬇ CSV — resultados individuais",
        data=records_to_csv_bytes(records),
        file_name="experimentos_robot_maze.csv",
        mime="text/csv",
        key="download_experiment_records",
    )
    st.download_button(
        "⬇ CSV — resumo comparativo",
        data=dataframe_to_csv_bytes(summary),
        file_name="resumo_experimentos_robot_maze.csv",
        mime="text/csv",
        key="download_experiment_summary",
    )
    st.download_button(
        "⬇ JSON — configuração do cenário atual",
        data=config_to_json(st.session_state.maze),
        file_name="cenario_robot_maze.json",
        mime="application/json",
        key="download_experiment_scenario",
    )
    if st.button("💾 Salvar dados em results/", key="save_experiment_files"):
        csv_path = save_experiment_csv(records)
        summary_path = Path("results") / "resumo_experimentos.csv"
        summary_path.write_bytes(dataframe_to_csv_bytes(summary))
        scenario_figure = render_maze(st.session_state.maze)
        png_path = save_figure_png(scenario_figure, filename="cenario_experimentos.png")
        plt.close(scenario_figure)
        st.success(f"Arquivos salvos: `{csv_path}`, `{summary_path}` e `{png_path}`")


def render_dashboard() -> None:
    """Renderiza o dashboard completo sem alterar os resultados do núcleo."""
    st.set_page_config(page_title="Robot Maze AI", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")
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
    _render_sidebar()
    st.markdown('<h1 class="main-title">🤖 Robot Maze AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Simulador de Inteligência Artificial Simbólica · BFS × A*</p>', unsafe_allow_html=True)
    maze = st.session_state.maze
    st.caption(f"Cenário {maze.scenario_id or 'sem identificador'} · {maze.mode} · {len(maze.obstacles)} obstáculos · entrada (1,1) · saída (10,10)")

    overview_tab, paths_tab, performance_tab, energy_tab, experiments_tab = st.tabs(
        ["📊 Visão Geral", "🧭 Comparação de Caminhos", "📈 Desempenho dos Algoritmos", "⚡ Análise de Energia", "🧪 Laboratório de Experimentos"]
    )
    with overview_tab:
        _render_overview()
    with paths_tab:
        _render_comparison_paths()
    with performance_tab:
        _render_performance()
    with energy_tab:
        _render_energy()
    with experiments_tab:
        _render_experiments()
