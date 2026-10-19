"""Testes das novas áreas de navegação e configuração do dashboard."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).parents[1] / "app.py"


def test_dashboard_exposes_the_five_analysis_tabs() -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()

    assert len(app.exception) == 0
    assert [tab.label for tab in app.tabs] == [
        "📊 Visão Geral",
        "🧭 Comparação de Caminhos",
        "📈 Desempenho dos Algoritmos",
        "⚡ Análise de Energia",
        "🧪 Laboratório de Experimentos",
    ]


def test_dashboard_generates_a_custom_scenario_without_changing_the_grid() -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()

    app.selectbox[3].select("Personalizado").run()
    generate_button = next(button for button in app.button if button.label == "🧩 Gerar labirinto")
    generate_button.click().run()

    assert len(app.exception) == 0
    assert app.session_state.maze.mode == "Personalizado"
    assert len(app.session_state.maze.obstacles) == 15
    assert app.session_state.maze.start == (0, 0)
    assert app.session_state.maze.goal == (9, 9)


def test_dashboard_exposes_replay_controls_after_comparison() -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
    app.selectbox[2].select("Desligada").run()
    compare_button = next(button for button in app.button if button.label == "⚖ Comparar algoritmos")
    compare_button.click().run()

    labels = {button.label for button in app.button}
    assert {"▶ Iniciar animação", "⏸ Pausar", "⏵ Continuar", "⏭ Próximo passo", "⏮ Passo anterior"} <= labels
    assert set(app.session_state.replays) == {"BFS", "A*"}
