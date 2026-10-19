"""Gera o relatório acadêmico PDF a partir dos artefatos medidos."""

from __future__ import annotations

import sys
import textwrap
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

RESULTS_DIR = PROJECT_ROOT / "results"
PDF_PATH = PROJECT_ROOT / "docs" / "relatorio_robot_maze_ai.pdf"


def _text_page(pdf: PdfPages, title: str, paragraphs: list[str]) -> None:
    figure = plt.figure(figsize=(8.27, 11.69))
    figure.text(0.08, 0.94, title, fontsize=19, weight="bold", color="#1E3A8A")
    y_position = 0.88
    for paragraph in paragraphs:
        for line in textwrap.wrap(paragraph, width=92):
            figure.text(0.08, y_position, line, fontsize=10.5, va="top")
            y_position -= 0.022
        y_position -= 0.018
    figure.text(0.08, 0.035, "Robot Maze AI — AV3 — Unisul", fontsize=8, color="#64748B")
    pdf.savefig(figure, bbox_inches="tight")
    plt.close(figure)


def _cover_page(pdf: PdfPages) -> None:
    figure = plt.figure(figsize=(8.27, 11.69))
    figure.text(0.5, 0.82, "UNIVERSIDADE DO SUL DE SANTA CATARINA", ha="center", fontsize=13)
    figure.text(0.5, 0.72, "Sistemas de Controle e Inteligência Artificial", ha="center", fontsize=12)
    figure.text(0.5, 0.57, "ROBOT MAZE AI", ha="center", fontsize=28, weight="bold", color="#1E3A8A")
    figure.text(0.5, 0.51, "Simulador de Inteligência Artificial Simbólica", ha="center", fontsize=14)
    figure.text(0.5, 0.35, "Integrantes: ______________________________________________", ha="center", fontsize=11)
    figure.text(0.5, 0.31, "Professor(a): _____________________________________________", ha="center", fontsize=11)
    figure.text(0.5, 0.18, "Relatório da Avaliação 3", ha="center", fontsize=11)
    figure.text(0.5, 0.13, "19 de outubro de 2026", ha="center", fontsize=10)
    pdf.savefig(figure, bbox_inches="tight")
    plt.close(figure)


def _results_table_page(pdf: PdfPages, summary: pd.DataFrame) -> None:
    columns = [
        "lote",
        "algoritmo",
        "taxa_sucesso_pct",
        "media_estados_explorados",
        "media_tempo_execucao_ms",
        "media_movimentos_sucesso",
        "media_energia_sucesso",
    ]
    table_data = summary[columns].copy()
    table_data.columns = ["Lote", "Algoritmo", "Sucesso (%)", "Estados médios", "Tempo médio (ms)", "Movimentos médios", "Energia média"]
    for column in table_data.columns[2:]:
        table_data[column] = table_data[column].map(
            lambda value: "—" if pd.isna(value) else f"{value:.2f}"
        )
    figure, axis = plt.subplots(figsize=(11.7, 8.27))
    axis.axis("off")
    axis.set_title("Resultados agregados dos experimentos reais", fontsize=16, pad=20)
    axis.table(
        cellText=table_data.values,
        colLabels=table_data.columns,
        loc="center",
        cellLoc="center",
        colColours=["#DBEAFE"] * len(table_data.columns),
    ).auto_set_font_size(False)
    figure.text(0.08, 0.07, "Movimentos e energia são agregados somente entre execuções solucionadas.", fontsize=9)
    pdf.savefig(figure, bbox_inches="tight")
    plt.close(figure)


def _graph_pages(pdf: PdfPages) -> None:
    for batch_size in (10, 30, 50):
        image_path = RESULTS_DIR / f"comparacao_lote_{batch_size}.png"
        image = plt.imread(image_path)
        figure = plt.figure(figsize=(11.69, 8.27))
        figure.text(0.08, 0.94, f"Gráficos comparativos — lote de {batch_size} cenários", fontsize=17, weight="bold", color="#1E3A8A")
        axis = figure.add_axes((0.05, 0.06, 0.90, 0.84))
        axis.imshow(image)
        axis.axis("off")
        pdf.savefig(figure, bbox_inches="tight")
        plt.close(figure)


def _result_analysis(summary: pd.DataFrame) -> list[str]:
    paragraphs = []
    for batch_size in (10, 30, 50):
        batch = summary[summary["lote"] == batch_size].set_index("algoritmo")
        bfs = batch.loc["BFS"]
        astar = batch.loc["A*"]
        state_reduction = (1 - astar["media_estados_explorados"] / bfs["media_estados_explorados"]) * 100
        time_reduction = (1 - astar["media_tempo_execucao_ms"] / bfs["media_tempo_execucao_ms"]) * 100
        paragraphs.append(
            f"No lote de {batch_size} cenários, BFS e A* tiveram taxa de sucesso de "
            f"{bfs['taxa_sucesso_pct']:.2f}% e {astar['taxa_sucesso_pct']:.2f}%, respectivamente. "
            f"Os movimentos médios solucionados foram {bfs['media_movimentos_sucesso']:.2f} para ambos. "
            f"A* explorou, em média, {state_reduction:.2f}% menos estados e apresentou diferença média de "
            f"{time_reduction:.2f}% no tempo em relação ao BFS; esses valores são específicos do lote e não "
            "sustentam uma superioridade universal."
        )
    return paragraphs


def generate_report() -> Path:
    summary = pd.read_csv(RESULTS_DIR / "resumo_finais.csv")
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(PDF_PATH) as pdf:
        _cover_page(pdf)
        _text_page(pdf, "2. Identificação do projeto e integrantes", [
            "Projeto: Robot Maze AI. Disciplina: Sistemas de Controle e Inteligência Artificial. Instituição: Universidade do Sul de Santa Catarina (Unisul).",
            "Integrantes: campo editável na capa. O repositório não recebeu nomes que não foram fornecidos pelo grupo.",
        ])
        _text_page(pdf, "3. Resumo", [
            "Este trabalho apresenta um simulador de navegação robótica em uma matriz 10 × 10 com obstáculos e recargas de energia. O sistema implementa Busca em Largura e A* com heurística de distância Manhattan, compara os algoritmos em cenários reproduzíveis e oferece uma interface Streamlit para visualização, animação e experimentação.",
            "Os resultados finais foram produzidos por 10, 30 e 50 cenários reais, com sementes registradas nos arquivos CSV versionados em results/.",
        ])
        _text_page(pdf, "4. Introdução", [
            "Encontrar caminhos em ambientes discretos é um problema clássico de Inteligência Artificial. Neste projeto, o robô deve alcançar a saída desviando de obstáculos e administrando energia limitada, enquanto recargas distribuídas podem tornar percursos originalmente inviáveis possíveis.",
            "A implementação foi organizada para separar domínio, busca, métricas, experimentos, visualização e interface, permitindo reprodução acadêmica e evolução posterior.",
        ])
        _text_page(pdf, "5. Objetivos gerais e específicos", [
            "Objetivo geral: desenvolver e comparar um simulador simbólico de navegação em labirintos.",
            "Objetivos específicos: gerar mapas reproduzíveis; modelar energia e recargas; implementar BFS e A*; medir estados, movimentos, energia e tempo; visualizar exploração e percurso; executar lotes experimentais; exportar dados e gráficos.",
        ])
        _text_page(pdf, "6. Fundamentação teórica", [
            "O labirinto é modelado como um grafo implícito: cada estado é um nó e cada movimento ortogonal legal é uma aresta de custo unitário. A busca sistemática mantém uma fronteira e predecessores para reconstruir a solução.",
            "A energia e a máscara de recargas ampliam o espaço de estados. Consequentemente, a mesma posição com recursos diferentes representa nós distintos.",
        ])
        _text_page(pdf, "7. Inteligência Artificial Simbólica", [
            "A solução usa representação explícita de símbolos: posições, obstáculos, energia, recargas e regras de transição. Não há aprendizado estatístico; as decisões são deduzidas por regras e algoritmos de busca sobre estados discretos.",
            "A exploração virtual consulta somente vizinhos imediatos do estado expandido. Isso é diferente de um robô físico, que descobriria o mapa por sensores durante o deslocamento.",
        ])
        _text_page(pdf, "8. Busca em Largura (BFS)", [
            "BFS utiliza uma fila FIFO e expande estados por profundidade. Como todos os movimentos têm custo 1, o primeiro objetivo retirado da fila possui o menor número de movimentos entre os percursos viáveis.",
            "O conjunto de visitados usa o estado completo, incluindo energia e máscara de recargas; a implementação não reduz estados diferentes à mesma posição.",
        ])
        _text_page(pdf, "9. Busca A*", [
            "A* prioriza estados por f(n) = g(n) + h(n), mantendo o melhor custo g conhecido para cada estado completo. Entradas obsoletas da fila de prioridade são descartadas.",
            "A busca compartilha exatamente a função de transição de energia usada pelo BFS, evitando que os algoritmos comparem regras diferentes.",
        ])
        _text_page(pdf, "10. Distância de Manhattan", [
            "A heurística é h(n) = |linha atual − linha objetivo| + |coluna atual − coluna objetivo|. Ela considera apenas o deslocamento ortogonal mínimo e não atribui bônus artificiais à energia.",
            "A heurística ignora obstáculos e recursos, portanto pode ser pouco informativa em mapas complexos, mas permanece um limite inferior de movimentos para o objetivo.",
        ])
        _text_page(pdf, "11. Modelagem do espaço de estados", [
            "O estado contém linha, coluna, energia disponível e máscara de bits das oito recargas consumidas. A ordenação determinística das recargas transforma cada posição especial em um bit estável.",
            "A sequência de estados do caminho é distinta da sequência de estados expandidos. A primeira representa o percurso físico; a segunda representa a exploração virtual para fins didáticos.",
        ])
        _text_page(pdf, "12. Gerenciamento de energia", [
            "A transição valida o vizinho, desconta um ponto, coleta uma recarga inédita e aceita o estado. Não há teto artificial de energia. Uma chegada com energia zero é válida se o movimento final começou com um ponto.",
            "Uma recarga revisitada não fornece bônus novamente. A regra é compartilhada por BFS, A*, comparação e experimentos.",
        ])
        _text_page(pdf, "13. Metodologia de implementação", [
            "O projeto foi desenvolvido incrementalmente com commits atômicos, testes pytest e pushes imediatos. O gerador usa sementes determinísticas, os algoritmos recebem o mesmo Maze imutável e cada execução cria energia e máscara novas.",
            "Os lotes finais usaram as faixas de sementes 10000–10009, 20000–20029 e 30000–30049 para 10, 30 e 50 cenários.",
        ])
        _text_page(pdf, "14. Arquitetura do software", [
            "models.py define State, SearchResult e tipos básicos; maze.py gera e valida mapas; energy.py centraliza transições; bfs.py e astar.py implementam as buscas; experiments.py executa lotes; analysis.py agrega resultados; visualization.py e dashboard.py apresentam a aplicação; export.py produz CSV e PNG.",
            "A arquitetura mantém o núcleo independente da interface e usa session_state somente na camada Streamlit.",
        ])
        _text_page(pdf, "15. Geração dos labirintos", [
            "Cada mapa oficial tem 100 células, entrada (1,1), saída (10,10), de 10 a 25 obstáculos, cinco recargas +5 e três recargas +10. Obstáculos, recargas, entrada e saída não se sobrepõem.",
            "A mesma semente e a mesma quantidade configurada reconstruem o cenário. Mapas sem solução são preservados como resultados válidos.",
        ])
        _text_page(pdf, "16. Experimentos realizados", [
            "Foram executados 180 registros: dois algoritmos em cada um dos 90 cenários. Cada registro contém lote, semente, obstáculos, algoritmo, solução, movimentos, estados, energia, recargas e tempo.",
            "Os arquivos experimentos_finais.csv e resumo_finais.csv permitem reproduzir as tabelas. Os PNGs correspondem aos lotes 10, 30 e 50.",
        ])
        _results_table_page(pdf, summary)
        _graph_pages(pdf)
        _text_page(pdf, "18. Comparação dos algoritmos", _result_analysis(summary))
        _text_page(pdf, "19. Discussão crítica", [
            "Nos lotes de 10 e 30, A* apresentou redução expressiva na média de estados explorados e no tempo. No lote de 50, a média de estados ainda foi menor, mas a diferença de tempo foi pequena; a mediana mostra que alguns cenários atípicos influenciaram a média do BFS.",
            "Os comprimentos médios e as energias médias dos percursos solucionados foram iguais entre os algoritmos em cada lote. Isso é esperado quando ambos encontram soluções ótimas em movimentos, mas não implica que toda escolha de caminho tenha a mesma energia final.",
            "Obstáculos aumentam a exploração necessária e podem criar cenários sem solução. Recargas expandem a energia disponível e podem transformar um percurso longo em viável, mas também aumentam a quantidade de estados possíveis por posição.",
        ])
        _text_page(pdf, "20. Limitações", [
            "A Manhattan não representa diretamente obstáculos, energia ou recargas; ela é um limite inferior de movimentos, não uma previsão completa do custo de viabilidade.",
            "O modelo de conhecimento local é simulado em um mapa conhecido pelo mecanismo de sucessores. Um robô físico precisaria de sensores, mapa parcial e exploração online, que não fazem parte desta etapa.",
            "Os tempos dependem do computador e do ambiente Python; por isso a comparação deve considerar tendências e estados explorados, não tratar milissegundos como constantes universais.",
        ])
        _text_page(pdf, "21. Conclusão", [
            "O Robot Maze AI atende ao modelo acadêmico de labirinto, energia e busca simbólica, mantendo BFS e A* sob as mesmas regras. A aplicação permite inspeção visual, comparação e experimentos reproduzíveis.",
            "Os dados medidos indicam que A* reduziu a exploração nos lotes realizados, mas a magnitude variou por cenário e não autoriza uma afirmação absoluta de superioridade. O projeto está preparado para uma futura camada de simulação física mais realista.",
        ])
        _text_page(pdf, "22. Referências bibliográficas", [
            "DIJKSTRA, E. W. A note on two problems in connexion with graphs. Numerische Mathematik, v. 1, p. 269–271, 1959. DOI: https://doi.org/10.1007/BF01386390",
            "HART, P. E.; NILSSON, N. J.; RAPHAEL, B. A formal basis for the heuristic determination of minimum cost paths. IEEE Transactions on Systems Science and Cybernetics, v. 4, n. 2, p. 100–107, 1968. DOI: https://doi.org/10.1109/TSSC.1968.300136",
            "RUSSELL, S.; NORVIG, P. Artificial Intelligence: A Modern Approach. 4. ed. Pearson, 2020. https://www.pearson.com/en-us/subject-catalog/p/artificial-intelligence-a-modern-approach/P200000003500/9780134610993",
            "CORMEN, T. H. et al. Introduction to Algorithms. 3. ed. MIT Press, 2009. https://mitpress.mit.edu/9780262033848/introduction-to-algorithms/",
            "STREAMLIT. Documentation. https://docs.streamlit.io/ (documentação técnica consultada para session_state, tabs, progresso e downloads).",
        ])
    return PDF_PATH


if __name__ == "__main__":
    print(generate_report())
