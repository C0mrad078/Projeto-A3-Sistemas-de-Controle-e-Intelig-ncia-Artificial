"""Testes do catálogo visual independente da lógica acadêmica."""

from src.astar import a_star_search
from src.maze import Maze
from src.scenarios import custom_scenario
from src.visual_config import (
    CHARACTERS,
    THEMES,
    character_options,
    get_character,
    get_theme,
    theme_options,
)


def test_four_characters_and_four_themes_are_available_locally() -> None:
    assert len(CHARACTERS) == 4
    assert len(THEMES) == 4
    assert len(set(character_options())) == 4
    assert len(set(theme_options())) == 4
    assert get_character("Robô Pixel Art").style == "square"
    assert get_theme("Floresta").key == "floresta"


def test_visual_selection_does_not_change_the_logical_result() -> None:
    maze = custom_scenario(Maze.generate(seed=44, obstacle_count=10)).maze
    baseline = a_star_search(maze)

    for character in CHARACTERS:
        for theme in THEMES:
            assert character.primary_color
            assert theme.floor_color
            repeated = a_star_search(maze)
            assert repeated.path == baseline.path
            assert repeated.moves == baseline.moves
            assert repeated.remaining_energy == baseline.remaining_energy
