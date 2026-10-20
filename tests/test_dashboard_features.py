"""Testes da interface acadêmica básica do dashboard."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).parents[1] / "app.py"


def test_dashboard_exposes_only_the_academic_tabs() -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()

    assert len(app.exception) == 0
    assert [tab.label for tab in app.tabs] == [
        "🧭 Simulador",
        "⚖ Comparação BFS × A*",
    ]


def test_dashboard_generates_an_academic_scenario_without_changing_the_grid() -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()

    generate_button = next(button for button in app.button if button.label == "🧩 Gerar labirinto")
    generate_button.click().run()

    assert len(app.exception) == 0
    assert app.session_state.basic_maze.mode == "Aleatório"
    assert len(app.session_state.basic_maze.obstacles) == 15
    assert app.session_state.basic_maze.start == (0, 0)
    assert app.session_state.basic_maze.goal == (9, 9)


def test_dashboard_exposes_comparison_after_execution() -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
    compare_button = next(button for button in app.button if button.label == "⚖ Comparar algoritmos")
    compare_button.click().run()

    assert len(app.exception) == 0
    assert set(app.session_state.basic_comparison) == {"BFS", "A*"}


def test_dashboard_theme_change_preserves_the_logical_maze() -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
    maze_before = app.session_state.basic_maze

    app.selectbox[2].select("Laboratório Futurista").run()

    assert len(app.exception) == 0
    assert app.session_state.basic_maze == maze_before
    assert app.session_state.basic_theme == "Laboratório Futurista"


def test_dashboard_exposes_forest_theme_without_changing_the_map() -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
    maze_before = app.session_state.basic_maze

    app.selectbox[2].select("Floresta").run()

    assert len(app.exception) == 0
    assert app.session_state.basic_maze == maze_before
    assert app.session_state.basic_theme == "Floresta"
