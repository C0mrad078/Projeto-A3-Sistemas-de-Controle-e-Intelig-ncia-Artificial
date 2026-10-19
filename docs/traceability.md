# Matriz de rastreabilidade acadêmica

| Requisito | Implementação | Evidência automatizada |
|---|---|---|
| Matriz 10 × 10 | `src.maze.Maze.generate` usa `GRID_SIZE = 10` | `tests/test_maze.py::test_generated_maze_obeys_official_constraints` |
| Entrada (1,1) | Coordenada interna `START = (0, 0)` | `tests/test_maze.py::test_generated_maze_obeys_official_constraints` |
| Objetivo (10,10) | Coordenada interna `GOAL = (9, 9)` | `tests/test_maze.py::test_generated_maze_obeys_official_constraints` |
| 10–25 obstáculos | `MIN_OBSTACLES` e `MAX_OBSTACLES` validados pelo gerador | `tests/test_maze.py::test_generated_maze_obeys_official_constraints` e `test_invalid_obstacle_count_is_rejected` |
| Cinco recargas +5 | `Maze.generate` atribui valor 5 às cinco primeiras posições sorteadas | `tests/test_maze.py::test_generated_maze_obeys_official_constraints` |
| Três recargas +10 | `Maze.generate` atribui valor 10 às três posições restantes | `tests/test_maze.py::test_generated_maze_obeys_official_constraints` |
| Energia inicial 30 | `INITIAL_ENERGY = 30` e `initial_state` | `tests/test_energy.py::test_movement_cost_is_applied_before_recharge_without_energy_cap` |
| Custo de 1 por movimento | `src.energy.transition` desconta `MOVEMENT_COST = 1` antes da coleta | `tests/test_energy.py` |
| Recarga consumida uma vez | Máscara de bits em `State.recharge_mask` | `tests/test_energy.py::test_recharge_is_consumed_only_once` |
| Sem limite artificial de energia | Transição soma bônus sem aplicar teto | `tests/test_energy.py::test_movement_cost_is_applied_before_recharge_without_energy_cap` |
| Movimento ortogonal | `Maze.neighbors` retorna cima, baixo, esquerda e direita | `tests/test_maze.py::test_neighbors_are_orthogonal_and_skip_obstacles` e `tests/test_energy.py::test_diagonal_move_is_rejected` |
| Estados completos | `State` contém linha, coluna, energia e máscara | `tests/test_edge_cases.py::test_returning_to_a_cell_with_different_energy_is_a_new_full_state` |
| BFS FIFO | `src.bfs.breadth_first_search` usa `collections.deque` | `tests/test_bfs.py` e `tests/test_edge_cases.py` |
| A* com prioridade | `src.astar.a_star_search` usa `heapq` e descarta entradas obsoletas | `tests/test_astar.py` |
| Heurística Manhattan | `src.search.manhattan_distance` | `tests/test_astar.py::test_astar_uses_manhattan_and_matches_bfs_shortest_length` |
| Caminho mínimo | BFS e A* usam custo unitário de movimento e predecessores | `tests/test_bfs.py::test_bfs_finds_shortest_path_and_reconstructs_states` e `tests/test_edge_cases.py::test_bfs_and_astar_match_minimum_length_across_seeds` |
| Chegada com energia zero | Transição aceita o estado final após pagar o último movimento | `tests/test_energy.py::test_arrival_at_goal_with_zero_energy_is_legal` |
| Cenários sem solução | Resultado usa `found=False` e métricas de chegada nulas | `tests/test_bfs.py::test_bfs_reports_no_solution_when_energy_is_insufficient`, `tests/test_astar.py::test_astar_reports_null_arrival_metrics_without_solution` |
| Reprodutibilidade | `Maze.generate` usa `random.Random(seed)` local | `tests/test_maze.py::test_same_seed_reconstructs_exact_scenario` |
| Comparação no mesmo mapa | `run_algorithms` e `run_experiments` compartilham `Maze` imutável | `tests/test_experiments.py::test_each_scenario_uses_the_same_maze_for_bfs_and_astar` |
| Métricas obrigatórias | `SearchResult` e `ExperimentRecord` registram solução, movimentos, estados, energia, recargas e tempo | `tests/test_experiments.py::test_experiment_metrics_are_consistent_and_progress_is_reported` |
| Animação sem distorcer energia | `explored_sequence` é virtual; `state_sequence` é o percurso físico | `tests/test_visualization.py` e `tests/test_animation.py` |
| Interface visual | `src.dashboard`, `src.visualization` e `st.session_state` | `tests/test_dashboard.py` |
| Lotes 10/30/50 | `run_experiments` restringe `ALLOWED_BATCH_SIZES` | `tests/test_experiments.py::test_only_official_batch_sizes_are_allowed` |
| Gráficos e filtros | `src.analysis` separa sucesso conjunto e métricas solucionadas | `tests/test_analysis.py` |
| Exportação real | `src.export` serializa registros e figuras produzidos | `tests/test_export.py` |
| Documentação e relatório | `README.md`, `docs/architecture.md`, `docs/apresentacao.md` e relatório PDF | Verificação de arquivos e execução do gerador de entrega |
