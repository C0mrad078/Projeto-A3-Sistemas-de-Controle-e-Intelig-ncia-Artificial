"""Catálogo local de personagens e temas visuais do simulador.

Os objetos deste módulo são puramente estéticos: não participam da geração do
labirinto, das transições de energia ou dos algoritmos de busca.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CharacterSpec:
    """Descrição de um personagem desenhado localmente pelo renderer."""

    key: str
    name: str
    description: str
    glyph: str
    primary_color: str
    accent_color: str
    style: str


@dataclass(frozen=True, slots=True)
class ThemeSpec:
    """Paleta e símbolos do cenário, sem alterar sua estrutura lógica."""

    key: str
    name: str
    description: str
    floor_color: str
    floor_alt_color: str
    obstacle_color: str
    obstacle_edge: str
    recharge_5_color: str
    recharge_10_color: str
    start_color: str
    goal_color: str
    explored_color: str
    path_color: str
    grid_color: str
    text_color: str


CHARACTERS: tuple[CharacterSpec, ...] = (
    CharacterSpec(
        key="classico",
        name="Robô Clássico",
        description="Robô simpático em azul e branco para demonstrações didáticas.",
        glyph="R",
        primary_color="#2563EB",
        accent_color="#DBEAFE",
        style="circular",
    ),
    CharacterSpec(
        key="futurista",
        name="Robô Futurista",
        description="Explorador tecnológico com núcleo luminoso.",
        glyph="◈",
        primary_color="#06B6D4",
        accent_color="#67E8F9",
        style="hexagonal",
    ),
    CharacterSpec(
        key="pixel",
        name="Robô Pixel Art",
        description="Personagem retrô desenhado com formas geométricas locais.",
        glyph="P",
        primary_color="#F59E0B",
        accent_color="#FDE68A",
        style="square",
    ),
    CharacterSpec(
        key="mascote",
        name="Mascote",
        description="Companheiro expressivo que comemora a chegada ao objetivo.",
        glyph="M",
        primary_color="#EC4899",
        accent_color="#FBCFE8",
        style="friendly",
    ),
)


THEMES: tuple[ThemeSpec, ...] = (
    ThemeSpec(
        key="laboratorio",
        name="Laboratório Futurista",
        description="Piso escuro tecnológico com detalhes ciano luminosos.",
        floor_color="#0F172A",
        floor_alt_color="#111827",
        obstacle_color="#334155",
        obstacle_edge="#67E8F9",
        recharge_5_color="#22D3EE",
        recharge_10_color="#A78BFA",
        start_color="#38BDF8",
        goal_color="#F472B6",
        explored_color="#164E63",
        path_color="#F0ABFC",
        grid_color="#475569",
        text_color="#E2E8F0",
    ),
    ThemeSpec(
        key="classico",
        name="Labirinto Clássico",
        description="Alto contraste e leitura limpa para apresentações acadêmicas.",
        floor_color="#F8FAFC",
        floor_alt_color="#F1F5F9",
        obstacle_color="#1F2937",
        obstacle_edge="#111827",
        recharge_5_color="#FDE68A",
        recharge_10_color="#FDBA74",
        start_color="#2563EB",
        goal_color="#DC2626",
        explored_color="#BFDBFE",
        path_color="#7C3AED",
        grid_color="#CBD5E1",
        text_color="#0F172A",
    ),
    ThemeSpec(
        key="floresta",
        name="Floresta",
        description="Grama, pedras e trilhas verdes vistas de cima.",
        floor_color="#DCFCE7",
        floor_alt_color="#BBF7D0",
        obstacle_color="#166534",
        obstacle_edge="#14532D",
        recharge_5_color="#FACC15",
        recharge_10_color="#FB923C",
        start_color="#0284C7",
        goal_color="#B91C1C",
        explored_color="#86EFAC",
        path_color="#92400E",
        grid_color="#86B98B",
        text_color="#14532D",
    ),
    ThemeSpec(
        key="dungeon",
        name="Dungeon Pixel Art",
        description="Pedra, portais e itens de energia em estilo retrô.",
        floor_color="#292524",
        floor_alt_color="#44403C",
        obstacle_color="#0C0A09",
        obstacle_edge="#A8A29E",
        recharge_5_color="#84CC16",
        recharge_10_color="#EAB308",
        start_color="#38BDF8",
        goal_color="#C084FC",
        explored_color="#57534E",
        path_color="#FDE047",
        grid_color="#78716C",
        text_color="#FAFAF9",
    ),
)


def character_options() -> tuple[str, ...]:
    return tuple(character.name for character in CHARACTERS)


def theme_options() -> tuple[str, ...]:
    return tuple(theme.name for theme in THEMES)


def get_character(value: str) -> CharacterSpec:
    for character in CHARACTERS:
        if value in {character.key, character.name}:
            return character
    raise ValueError(f"Personagem desconhecido: {value!r}.")


def get_theme(value: str) -> ThemeSpec:
    for theme in THEMES:
        if value in {theme.key, theme.name}:
            return theme
    raise ValueError(f"Tema desconhecido: {value!r}.")
