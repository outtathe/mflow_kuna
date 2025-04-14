from collections import deque

def max_flow(capacity, source, sink):
    n = len(capacity)
    max_flow_value = 0
    # Инициализируем остаточную способность как копию исходной capacity
    residual = [capacity[i][:] for i in range(n)]

    while True:
        parent = [-1] * n 
        parent[source] = source 
        # BFS queue
        queue = deque([source])
        path_found = False
        # Поиск в ширину по резидуальной сети
        while queue and not path_found:
            u = queue.popleft()
            for v in range(n):
                if residual[u][v] > 0 and parent[v] == -1:
                    parent[v] = u
                    if v == sink:   
                        path_found = True
                        break     
                    queue.append(v)
        if not path_found:
            break 

        # Найдем бутылочное горлышко - минимальную остаточную пропускную способность на пути
        v = sink
        bottleneck = float('inf')
        while v != source:
            u = parent[v]
            bottleneck = min(bottleneck, residual[u][v])
            v = u

        # Пройдем по пути ещё раз и обновим остаточные пропускные способности ребер
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= bottleneck      # уменьшим доступ вперед
            residual[v][u] += bottleneck      # увеличим доступ назад
            v = u

        max_flow_value += bottleneck

    return max_flow_value

# Матрица емкостей графа из примера (S=0, A=1, B=2, C=3, D=4, T=5)
capacity_matrix = [
#   S   A  B  C  D  T
    [0, 8, 0, 0, 3, 0],  #  S (0) в A:8, D:3
    [0, 0, 9, 0, 7, 0],  #  A (1) в B:9, D:7
    [0, 0, 0, 0, 0, 2],  #  B (2) в T:2
    [0, 0, 0, 0, 0, 5],  #  C (3) в T:5
    [0, 0, 0, 4, 0, 0],  #  D (4) в C:4
    [0, 0, 0, 0, 0, 0],  #  T (5) никуда
]
mf_1 = max_flow(capacity_matrix, source=0, sink=5)
print(f"Максимальный поток равен {mf_1}") 
