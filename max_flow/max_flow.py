from collections import deque

def max_flow(capacity, source, sink):
    n = len(capacity)
    max_flow_value = 0
    # Копируем исходную матрицу пропускных способностей для создания остаточной сети
    residual = [capacity[i][:] for i in range(n)]
    
    while True:
        parent = [-1] * n  # Массив для восстановления пути: parent[v] = предок вершины v
        parent[source] = source  # Источник отмечаем как посещённый (его предок — сам он)
        queue = [source]  # Очередь с начальным элементом — источником
        path_found = False
        
        # Реализация поиска в ширину (BFS) с использованием списка как очереди
        while queue and not path_found:
            u = queue.pop(0)  # извлекаем первый элемент очереди
            for v in range(n):
                # если по ребру u->v есть остаточная пропускная способность и v ещё не посещена
                if residual[u][v] > 0 and parent[v] == -1:
                    parent[v] = u   # запоминаем, что мы пришли в v из u
                    if v == sink:   # если достигли стока, то увеличивающий путь найден
                        path_found = True
                        break
                    queue.append(v)   # добавляем вершину в очередь для дальнейшего обхода

        # Если путь не найден, алгоритм завершает работу
        if not path_found:
            break

        # Определяем бутылочное горлышко — минимальную остаточную пропускную способность вдоль найденного пути
        v = sink
        bottleneck = float('inf')
        while v != source:
            u = parent[v]
            bottleneck = min(bottleneck, residual[u][v])
            v = u
        
        # Обновляем остаточную сеть по найденному пути:
        # уменьшаем остаточную пропускную способность на прямых рёбрах и увеличиваем на обратных
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= bottleneck
            residual[v][u] += bottleneck
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
