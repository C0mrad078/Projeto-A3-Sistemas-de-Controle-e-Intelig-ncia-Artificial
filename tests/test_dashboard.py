"""Testes de estado do dashboard Streamlit."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).parents[1] / "app.py"


def _load_app() -> AppTest:
    return AppTest.from_file(str(APP_PATH), default_timeout=30).run()


def test_dashboard_starts_without_errors_and_keeps_maze_on_visual_changes() -> None:
    app = _load_app()
    maze_before = app.session_state.maze

    assert len(app.exception) == 0
    assert {button.label for button in app.button} >= {
        "🧩 Gerar labirinto",
        "▶ Executar BFS",
        "▶ Executar A*",
        "⚖ Comparar algoritmos",
    }

    app.selectbox[1].select("A*").run()
    app.selectbox[2].select("Desligada").run()

    assert len(app.exception) == 0
    assert app.session_state.maze == maze_before


def test_dashboard_runs_bfs_and_astar_independently_on_same_maze() -> None:
    app = _load_app()
    app.selectbox[2].select("Desligada").run()
    maze_before = app.session_state.maze

    app.button[2].click().run()
    bfs_result = app.session_state.active_result
    app.button[3].click().run()
    astar_result = app.session_state.active_result

    assert len(app.exception) == 0
    assert bfs_result.algorithm == "BFS"
    assert astar_result.algorithm == "A*"
    assert set(app.session_state.results) == {"BFS", "A*"}
    assert app.session_state.maze == maze_before
