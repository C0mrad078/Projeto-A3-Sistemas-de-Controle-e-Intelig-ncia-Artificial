# Arquitetura simbólica do Robot Maze AI

## Modelo de estado

O espaço de estados é finito e explícito. Um estado contém a posição do robô, sua energia disponível e uma máscara de oito bits indicando quais recargas já foram utilizadas. O custo de cada aresta é um movimento, portanto BFS e A* podem comparar soluções pela mesma métrica.

Uma posição não é uma chave suficiente para visitados: voltar à mesma célula com mais energia ou com outra máscara de recargas pode permitir uma continuação diferente. A máscara é indexada pelas posições de recarga em ordem determinística de linha e coluna.

## Ordem da transição

`src.energy.transition` é a única implementação das regras de movimento. BFS e A* não calculam energia por conta própria. Para uma tentativa de destino:

1. o destino deve aparecer entre os vizinhos ortogonais livres do estado atual;
2. o robô precisa ter pelo menos 1 ponto;
3. o custo de 1 ponto é pago;
4. a recarga do destino é aplicada se o respectivo bit ainda estiver desligado;
5. o novo estado é produzido sem limitar sua energia máxima.

Assim, uma célula de recarga pode ser visitada novamente, mas o bônus só é recebido uma vez. Se o custo levar a energia a zero, o estado continua válido; isso permite alcançar a saída legalmente no último movimento.

## Geração do cenário

`Maze.generate(seed, obstacle_count)` usa `random.Random` local, garantindo que a mesma semente e configuração reconstruam o mesmo conjunto de obstáculos e recargas. A entrada e a saída são removidas das candidatas antes do sorteio. O gerador valida a matriz 10 × 10, de 10 a 25 obstáculos e exatamente oito recargas, distribuídas como cinco de 5 pontos e três de 10 pontos.

Mapas sem solução não são corrigidos nem descartados. Eles são resultados válidos para os experimentos, e os algoritmos retornam `found=False`, caminho vazio e `None` nas métricas que dependeriam da chegada.

## Busca

Na expansão, cada algoritmo solicita `maze.neighbors(current.position)` e aplica a transição compartilhada a cada destino. Não há pré-cálculo de caminho completo. BFS utiliza uma fila FIFO e um conjunto de estados completos visitados. A* utiliza uma fila de prioridade, mantém o melhor `g` por estado completo e ignora entradas obsoletas quando uma entrada removida da fila não corresponde mais ao melhor custo conhecido.

A heurística A* é:

```text
h(n) = |linha_atual - linha_objetivo|
     + |coluna_atual - coluna_objetivo|
```

Ela não inclui energia, bônus ou custos negativos. A reconstrução segue os predecessores armazenados e produz simultaneamente posições e estados, o que deixa a execução pronta para animação futura.

## Limite da simulação de conhecimento

Neste núcleo, “conhecer somente posições imediatamente adjacentes” significa que a função de sucessores consulta apenas as quatro células ortogonais do estado expandido. Como em buscas clássicas o mapa inteiro é fornecido ao simulador para responder essa consulta, a exploração dos nós é virtual. Um robô físico teria sensores, um mapa parcial e incerteza: descobriria obstáculos ao se deslocar e não poderia explorar virtualmente uma célula ainda não visitada. A futura camada de interface deve manter essa diferença explícita ao apresentar os resultados.

## Interface web e estado

`src.dashboard` mantém o labirinto atual em `st.session_state` e só o substitui quando o usuário aciona “Gerar labirinto”. Alterar algoritmo, velocidade, gráficos ou abas não gera obstáculos novos. Cada execução chama BFS ou A* com um novo estado inicial, energia inicial de 30 e máscara de recargas vazia.

O renderer usa camadas distintas: células expandidas virtualmente, linha do percurso físico, posição atual do robô, obstáculos, entrada, saída e recargas. A animação amostra sequências longas apenas para reduzir atualizações da interface; o `SearchResult` original permanece completo e as métricas são calculadas antes da animação.

## Experimentos e exportação

O laboratório usa as sementes `seed_start + índice` e compartilha cada objeto `Maze` imutável entre BFS e A*. Os registros guardam semente, cenário, obstáculos, algoritmo, sucesso, movimentos, estados, energia, recargas e tempo. CSVs e PNGs disponibilizados pela interface são serializados diretamente desses registros e não contêm dados inventados.
