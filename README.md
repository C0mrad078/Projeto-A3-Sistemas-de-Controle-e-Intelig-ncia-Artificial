# Robot Maze AI

Projeto acadêmico da AV3 de Sistemas de Controle e Inteligência Artificial (Unisul). O núcleo simula a navegação de um robô em labirintos usando Inteligência Artificial Simbólica, Busca em Largura (BFS) e Busca A*.

## Requisitos e execução

- Python 3.11 ou superior;
- Streamlit, Pandas, Matplotlib e Plotly para a aplicação e os gráficos;
- Kaleido para exportar gráficos interativos em PNG;
- `pytest` para os testes automatizados.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/streamlit run app.py
.venv/bin/python -m pytest
```

O dashboard abre localmente e permite gerar cenários, executar algoritmos, comparar resultados e iniciar lotes experimentais. O núcleo também pode ser usado diretamente:

```python
from app import run_algorithms

maze, (bfs_result, astar_result) = run_algorithms(seed=42)
```

## Regras do domínio

Internamente, as coordenadas começam em zero: `(0, 0)` representa a posição acadêmica `(1, 1)` e `(9, 9)` representa `(10, 10)`. Cada cenário oficial possui matriz 10 × 10, entrada e saída livres, entre 10 e 25 obstáculos, cinco recargas de 5 pontos e três recargas de 10 pontos. A geração usa uma semente pseudoaleatória e não força a existência de solução.

O estado completo é `(linha, coluna, energia, máscara_de_recargas)`. A máscara de bits distingue recargas já consumidas; por isso estados com a mesma posição não são automaticamente equivalentes.

Toda transição passa pela função única `src.energy.transition`, usada tanto por BFS quanto por A*:

1. verifica vizinho ortogonal livre;
2. desconta 1 ponto pelo movimento;
3. coleta a recarga da célula de destino, se ainda não consumida;
4. valida e aceita o estado resultante.

Não existe limite máximo artificial de energia. A chegada ao objetivo com energia zero é legal quando o último movimento começou com energia 1.

## Busca e métricas

- BFS usa fila FIFO e encontra o menor percurso em movimentos entre os percursos viáveis.
- A* usa fila de prioridade, `g(n)` igual ao número de movimentos, `h(n)` igual à distância Manhattan e `f(n) = g(n) + h(n)`.
- Os dois algoritmos expandem somente os vizinhos do estado que está sendo processado; não há caminho pré-calculado.
- `SearchResult` registra algoritmo, sucesso, movimentos, estados completos expandidos, energia final, caminho, recargas, tempo em milissegundos e sequência de estados para animação futura. Métricas dependentes da chegada ficam nulas quando não há solução.

## Modalidades de geração

O gerador oferece cinco modalidades:

- **Fácil:** 10–14 obstáculos;
- **Médio:** 15–19 obstáculos;
- **Difícil:** 20–25 obstáculos;
- **Aleatório:** quantidade sorteada entre 10 e 25;
- **Personalizado:** quantidade configurável, editor visual, validação, salvamento, importação e exportação JSON.

Uma semente informada reconstrói exatamente o mesmo cenário. Sem semente, o modo aleatório usa uma nova semente. A quantidade de obstáculos é um indicador de configuração, não uma garantia de dificuldade real: a distribuição dos obstáculos, as recargas e a conectividade determinam a dificuldade observada.

O formato JSON usa coordenadas acadêmicas de 1 a 10 e armazena semente, modalidade, obstáculos e recargas. A configuração só pode ser executada após validar 10×10, entrada `(1,1)`, saída `(10,10)`, 10–25 obstáculos, cinco recargas `+5` e três `+10`.

## Interface e experimentos

O dashboard possui cinco abas:

- **Visão Geral:** metadados do cenário, indicadores geométricos, cards BFS/A*, tabela comparativa e interpretação didática.
- **Comparação de Caminhos:** dois mapas lado a lado, expansão virtual separada do percurso físico e controles de início, pausa, reinício e passos.
- **Desempenho dos Algoritmos:** gráficos Plotly de estados, tempo, movimentos e energia, com exportação PNG.
- **Análise de Energia:** evolução real da energia, recargas coletadas, tabela por movimento e exportação CSV.
- **Laboratório de Experimentos:** lotes de 10, 30, 50 ou quantidade personalizada entre 1 e 100, por modalidade, com sementes, progresso, estatísticas condicionadas à solução e classificação de cada cenário.

A expansão virtual é apresentada em azul e o caminho físico em roxo. A expansão não consome energia; somente a sequência de estados do caminho físico representa movimentos do robô.

Os resultados podem ser baixados em CSV, JSON e PNG. O botão de persistência grava dados reais em `results/`; a semente e a modalidade são preservadas para reprodução. Métricas de movimentos, energia e recargas médias exibem o tamanho da amostra solucionada e não substituem cenários sem solução por zeros.

## Entrega acadêmica e reprodução

O relatório final está em [`docs/relatorio_robot_maze_ai.pdf`](/Users/jhonatan/Projeto-A3-Sistemas-de-Controle-e-Intelig-ncia-Artificial/docs/relatorio_robot_maze_ai.pdf), com campos editáveis para integrantes. O roteiro de exposição está em [`docs/apresentacao.md`](/Users/jhonatan/Projeto-A3-Sistemas-de-Controle-e-Intelig-ncia-Artificial/docs/apresentacao.md) e a matriz de requisitos em [`docs/traceability.md`](/Users/jhonatan/Projeto-A3-Sistemas-de-Controle-e-Intelig-ncia-Artificial/docs/traceability.md).

Os resultados finais versionados ficam em [`results/experimentos_finais.csv`](/Users/jhonatan/Projeto-A3-Sistemas-de-Controle-e-Intelig-ncia-Artificial/results/experimentos_finais.csv), [`results/resumo_finais.csv`](/Users/jhonatan/Projeto-A3-Sistemas-de-Controle-e-Intelig-ncia-Artificial/results/resumo_finais.csv) e nos três PNGs de comparação. Para reproduzi-los:

```bash
.venv/bin/python scripts/generate_final_artifacts.py
.venv/bin/python scripts/generate_report.py
```

As sementes finais são 10000–10009, 20000–20029 e 30000–30049. O tempo de execução pode variar por máquina; cenário, solução, movimentos e estados permanecem reproduzíveis.

## Limitações conhecidas

O modelo simula conhecimento local consultando os quatro vizinhos em um mapa disponível ao simulador; não implementa sensores nem descoberta online de um robô físico. A heurística Manhattan não modela obstáculos, energia ou recargas. Os tempos são dependentes do ambiente e devem ser interpretados junto com estados explorados e taxas de sucesso.

## Exploração simbólica e robô físico

As buscas clássicas exploram virtualmente nós do espaço de estados: o mapa está disponível para a função de sucessores, mas cada expansão consulta apenas os quatro vizinhos do estado atual. Isso não representa um robô físico que já conhece todo o mapa. Um robô físico precisaria descobrir, durante o deslocamento, quais células existem e quais estão livres, mantendo um mapa parcial e tomando decisões online. Essa distinção será preservada em futuras interfaces e experimentos.

## Estrutura

```text
app.py                 Ponto de entrada Streamlit e API programática
src/models.py          Estado e resultado padronizado
src/maze.py            Geração, validação e vizinhança
src/scenarios.py       Modalidades, editor e JSON de cenários
src/energy.py          Transição única de energia
src/search.py          Heurística e reconstrução compartilhada
src/bfs.py             Busca em Largura
src/astar.py           Busca A*
src/metrics.py         Medição de tempo
src/experiments.py     Lotes reproduzíveis e registros tabulares
src/analysis.py        Médias, filtros e gráficos comparativos
src/dashboard_analysis.py Indicadores, Plotly e interpretações didáticas
src/visualization.py   Renderer do labirinto
src/animation.py       Amostragem segura de frames
src/export.py          Exportação CSV e PNG
src/dashboard.py       Interface Streamlit
scripts/               Geradores de resultados e relatório PDF
tests/                 Testes de domínio e algoritmos
docs/                  Documentação acadêmica
results/               Espaço para resultados futuros
```
