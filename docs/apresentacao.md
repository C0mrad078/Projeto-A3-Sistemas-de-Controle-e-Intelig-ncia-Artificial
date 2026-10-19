# Roteiro de apresentação — Robot Maze AI

Duração sugerida: aproximadamente 10 minutos. A duração é apenas uma proposta para organizar a demonstração, não uma exigência atribuída ao professor.

## Divisão sugerida entre integrantes

- **Aluno 1 — problema e modelagem:** apresenta o objetivo, as regras do labirinto, energia e estado completo.
- **Aluno 2 — BFS:** explica fila FIFO, expansão por profundidade e optimalidade em movimentos unitários.
- **Aluno 3 — A*:** explica `g`, Manhattan, fila de prioridade e descarte de entradas obsoletas.
- **Aluno 4 — interface e experimentos:** demonstra o Streamlit, comparação, lotes e gráficos.
- **Aluno 5 — resultados e limitações:** interpreta os dados, discute limites e responde perguntas.

Para grupos menores, os blocos podem ser acumulados: dois alunos podem dividir problema/algoritmos e interface/resultados; três alunos podem usar os três primeiros blocos, com o terceiro também apresentando os experimentos.

## Sequência de aproximadamente 10 minutos

### 0:00–1:00 — problema

Apresente o Robot Maze AI como um simulador de Inteligência Artificial Simbólica. O robô deve sair de (1,1) e chegar a (10,10), em uma matriz 10 × 10, evitando obstáculos e administrando energia.

### 1:00–2:30 — espaço de estados

Mostre que um estado é `(linha, coluna, energia, máscara de recargas)`. Explique que duas visitas à mesma célula podem ser diferentes se a energia ou as recargas consumidas forem diferentes. Reforce que há cinco recargas +5 e três +10, cada uma consumida no máximo uma vez.

### 2:30–4:00 — BFS e A*

Explique que BFS usa fila FIFO e encontra o menor número de movimentos quando cada movimento tem custo 1. Em seguida, mostre A* com `f(n) = g(n) + h(n)` e `h` Manhattan. Diga que a heurística não recebe bônus de energia e que os dois algoritmos usam a mesma transição.

### 4:00–5:30 — demonstração do simulador

Execute `.venv/bin/streamlit run app.py`. Gere um mapa com semente conhecida, escolha “Desligada” para mostrar o caminho estático e execute BFS. Depois gere o mesmo mapa novamente, execute A* e abra a aba de comparação. Mostre a legenda: expansão virtual em azul, caminho físico em roxo, recargas e marcadores de entrada/saída.

### 5:30–7:00 — animação e energia

Selecione uma velocidade de animação. Explique que a expansão virtual não é deslocamento físico e não consome energia. Na etapa do percurso, o robô acompanha `state_sequence`, a energia muda conforme a transição e a chegada com zero é permitida.

### 7:00–8:30 — laboratório

Abra “Experimentos”, execute o lote de 10 e mostre a barra de progresso, tabela, taxa de sucesso e gráficos. Explique que os lotes finais usam sementes reproduzíveis: 10000–10009, 20000–20029 e 30000–30049. Se o tempo permitir, mostre os CSVs e PNGs disponíveis para download.

### 8:30–10:00 — conclusão crítica

Apresente os resultados reais: ambos obtiveram 90% nos lotes de 10 e 30 e 88% no lote de 50. A* explorou menos estados nos três lotes, mas a vantagem de tempo variou e ficou pequena no lote de 50. Conclua que os resultados dependem do cenário e não sustentam superioridade absoluta.

## Perguntas prováveis e respostas

### Por que a máscara de recargas faz parte do estado?

Porque uma posição visitada com recargas disponíveis não é equivalente à mesma posição depois de consumir uma recarga. A máscara preserva essa diferença e impede podar estados que podem ter futuros distintos.

### BFS e A* sempre encontram o mesmo caminho?

Eles encontram o mesmo comprimento mínimo quando ambos resolvem o mesmo problema com custo unitário. A ordem de desempate pode escolher caminhos diferentes entre várias soluções mínimas, e a energia final pode ser diferente se os caminhos consumirem recargas diferentes.

### Por que A* não considera energia na heurística?

O requisito define Manhattan como heurística. Ela fornece um limite inferior de movimentos e evita bônus artificiais ou custos negativos. A energia continua sendo tratada corretamente na transição e no estado.

### O robô conhece o mapa inteiro?

A busca clássica recebe o mapa para responder à consulta dos quatro vizinhos do estado expandido, mas não pré-calcula um caminho. Isso é uma exploração virtual de nós. Um robô físico teria sensores e um mapa parcial, uma extensão futura do projeto.

### Por que um cenário pode não ter solução?

Obstáculos podem separar a entrada da saída ou a energia disponível pode ser insuficiente para alcançar uma recarga e completar o percurso. O sistema preserva esses casos e retorna métricas de chegada nulas.

### A* é sempre mais rápido que BFS?

Não. Nos lotes realizados, A* explorou menos estados, mas a diferença de tempo depende do cenário, do custo de renderização e do ambiente de execução. A conclusão deve ser baseada nos dados medidos.

### Por que a Manhattan pode ser limitada?

Ela ignora obstáculos, energia e localização das recargas. Assim, pode orientar pouco em mapas que exigem desvios longos ou que tenham recursos difíceis de alcançar, embora continue sendo um limite inferior de movimentos.

### Como os resultados podem ser reproduzidos?

Instale as dependências, execute `scripts/generate_final_artifacts.py` a partir da raiz e compare as sementes e registros gerados com `results/experimentos_finais.csv`. O tempo pode variar, mas cenários, sucesso, movimentos e estados devem permanecer reproduzíveis.
