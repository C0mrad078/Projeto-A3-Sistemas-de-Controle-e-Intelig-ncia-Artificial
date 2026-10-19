# Robot Maze AI

Projeto acadêmico da AV3 de Sistemas de Controle e Inteligência Artificial (Unisul). O núcleo simula a navegação de um robô em labirintos usando Inteligência Artificial Simbólica, Busca em Largura (BFS) e Busca A*.

## Requisitos e execução

- Python 3.11 ou superior;
- `pytest` para os testes automatizados.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py --seed 42 --obstacles 10
.venv/bin/python -m pytest
```

O comando da aplicação gera um cenário reproduzível e executa os dois algoritmos com a mesma configuração. O núcleo também pode ser usado diretamente:

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

## Exploração simbólica e robô físico

As buscas clássicas exploram virtualmente nós do espaço de estados: o mapa está disponível para a função de sucessores, mas cada expansão consulta apenas os quatro vizinhos do estado atual. Isso não representa um robô físico que já conhece todo o mapa. Um robô físico precisaria descobrir, durante o deslocamento, quais células existem e quais estão livres, mantendo um mapa parcial e tomando decisões online. Essa distinção será preservada em futuras interfaces e experimentos.

## Estrutura

```text
app.py                 Execução programática e CLI
src/models.py          Estado e resultado padronizado
src/maze.py            Geração, validação e vizinhança
src/energy.py          Transição única de energia
src/search.py          Heurística e reconstrução compartilhada
src/bfs.py             Busca em Largura
src/astar.py           Busca A*
src/metrics.py         Medição de tempo
tests/                 Testes de domínio e algoritmos
docs/                  Documentação acadêmica
results/               Espaço para resultados futuros
```
