from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# ----- Блок хранения "сессии" или данных о графе ------
# В реальном приложении можно хранить это в БД или Session; тут - в глобальных переменных для простоты.

graph_data = {
    "n_left": 0,
    "n_right": 0,
    "edges": []     # список кортежей (v_left, v_right)
}

# Список шагов алгоритма (для визуализации).
# Каждый элемент steps будет содержать инфу о вершинах/рёбрах, подсветках и т.д.
steps = []


# ----- Алгоритм Куна с логированием шагов ------
def kuhn_with_steps(n_left, n_right, edges):
    """
    n_left  : кол-во вершин левой доли (номеруются 0..n_left-1)
    n_right : кол-во вершин правой доли (0..n_right-1)
    edges   : список (v, u), где v - индекс левой, u - индекс правой

    Возвращает:
      matchR : массив размера n_right (matchR[u] = v, если правая u занята левой v, иначе -1)
      steps  : список "снимков" процесса работы
    """

    # Сформируем список смежности для левых вершин
    adj = [[] for _ in range(n_left)]
    for (v, u) in edges:
        adj[v].append(u)

    matchR = [-1] * n_right  # какая левая вершина связана с правой u
    result_steps = []

    def dfs(v, used):
        """
        Модифицированный DFS для поиска увеличивающего пути.
        Логируем каждый раз, когда обращаемся к вершине/ребру.
        """
        if used[v]:
            return False
        used[v] = True

        # Для лога: запомним, что мы пришли в вершину v (из левой доли)
        result_steps.append({
            "type": "visit_left_vertex",
            "vertex_left": v
        })

        for u in adj[v]:
            # Логируем попытку обработать ребро (v -> u)
            result_steps.append({
                "type": "explore_edge",
                "edge_left": v,
                "edge_right": u
            })

            # Если правая вершина u свободна или можно освободить
            if matchR[u] == -1:
                # Логируем факт, что "свободная правая вершина u нашлась"
                result_steps.append({
                    "type": "found_free_right",
                    "vertex_right": u
                })
                matchR[u] = v
                return True
            else:
                # Попробуем "сместить" вершину matchR[u]
                v2 = matchR[u]
                result_steps.append({
                    "type": "right_taken",
                    "vertex_right": u,
                    "occupied_by": v2
                })
                if dfs(v2, used):
                    # Переподключаем
                    matchR[u] = v
                    return True

        return False

    # Основной цикл по всем левым вершинам
    for v in range(n_left):
        used = [False] * n_left
        dfs(v, used)

    return matchR, result_steps


# ----- Роуты ------
@app.route("/")
def index():
    """
    Стартовая страница: форма для ввода количества вершин и списка рёбер
    """
    return render_template("index.html")


@app.route("/set_graph", methods=["POST"])
def set_graph():
    """
    Обрабатывает форму с параметрами графа: n_left, n_right, edges
    """
    global graph_data, steps

    n_left = int(request.form.get("n_left", 0))
    n_right = int(request.form.get("n_right", 0))
    edges_str = request.form.get("edges", "")
    
    edges_list = []
    for part in edges_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            left_s, right_s = part.split("-")
            v = int(left_s.strip())
            u = int(right_s.strip())
            edges_list.append((v, u))

    graph_data = {
        "n_left": n_left,
        "n_right": n_right,
        "edges": edges_list
    }

    matchR, steps_local = kuhn_with_steps(n_left, n_right, edges_list)
    steps = steps_local 

    return redirect(url_for("visualize"))


@app.route("/visualize")
def visualize():
    """
    Отображение страницы с визуализацией пошагового алгоритма
    """
    return render_template("visualize.html")


@app.route("/get_steps")
def get_steps():
    """
    Возвращает весь список шагов в формате JSON,
    который фронтенд будет отображать последовательно.
    """
    return jsonify(steps)


if __name__ == "__main__":
    app.run(debug=True)
