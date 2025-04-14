from flask import Flask, render_template, request, redirect, url_for, jsonify, flash

app = Flask(__name__)

app.secret_key = '8'
graph_data = {
    "n_left": 0,
    "n_right": 0,
    "edges": [],
    "matchR": []
}
steps = []

def is_bipartite(n_left, n_right, edges):
    """
    Проверяет, что каждое ребро (v, u) удовлетворяет:
      - 0 <= v < n_left
      - 0 <= u < n_right
    Если хотя бы одно ребро не удовлетворяет, считаем, что граф недвудольный.
    """
    for (v, u) in edges:
        if v < 0 or v >= n_left or u < 0 or u >= n_right:
            return False
    return True


# ----- АЛГОРИТМ КУНА С ЛОГИРОВАНИЕМ ------
def kuhn_with_steps(n_left, n_right, edges):
    """
    Выполняет алгоритм Куна, возвращая:
      - matchR: массив размера n_right (matchR[u] = v, если вершина u сопоставлена с v, иначе -1)
      - steps_list: список "шагов", для визуализации.
    """
    # Построим список смежности для левых вершин
    adj = [[] for _ in range(n_left)]
    for (v, u) in edges:
        adj[v].append(u)

    matchR = [-1] * n_right
    result_steps = []  # сюда пишем логи шагов

    def dfs(v, used):
        if used[v]:
            return False
        used[v] = True

        # Логируем: "посетили левую вершину v"
        result_steps.append({
            "type": "visit_left_vertex",
            "vertex_left": v
        })

        for u in adj[v]:
            # Логируем: "рассматриваем ребро (v -> u)"
            result_steps.append({
                "type": "explore_edge",
                "edge_left": v,
                "edge_right": u
            })

            if matchR[u] == -1:
                # Нашли свободную вершину справа
                result_steps.append({
                    "type": "found_free_right",
                    "vertex_right": u
                })
                matchR[u] = v
                return True
            else:
                # Правая вершина u уже занята левой v2
                v2 = matchR[u]
                result_steps.append({
                    "type": "right_taken",
                    "vertex_right": u,
                    "occupied_by": v2
                })
                # Пытаемся освободить u, "сместив" v2
                if dfs(v2, used):
                    matchR[u] = v
                    return True

        return False

    for v in range(n_left):
        used = [False] * n_left
        dfs(v, used)

    return matchR, result_steps

@app.route("/")
def index():
    """
    Стартовая страница с формой ввода данных о графе.
    """
    return render_template("index.html")


@app.route("/set_graph", methods=["POST"])
def set_graph():
    """
    Принимает POST-данные с формы: n_left, n_right, edges
    Парсит строки, сохраняет в глобальной переменной,
    запускает алгоритм Куна и логирует шаги.
    Затем редиректит на /visualize.
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

    if not is_bipartite(n_left, n_right, edges_list):
        flash("введённый граф недвудолен. пожалуйста, введите корректный двудольный граф.")
        return redirect(url_for("index"))

    matchR, local_steps = kuhn_with_steps(n_left, n_right, edges_list)
    steps = local_steps 

    graph_data = {
        "n_left": n_left,
        "n_right": n_right,
        "edges": edges_list,
        "matchR": matchR 
    }

    return redirect(url_for("visualize"))


@app.route("/visualize")
def visualize():
    """
    Просто отдаёт HTML-шаблон visualize.html,
    где находится наша SVG-анимация.
    """
    return render_template("visualize.html")


@app.route("/get_graph_data")
def get_graph_data():
    """
    Возвращает JSON с информацией о графе:
    {
       "n_left": ...,
       "n_right": ...,
       "edges": [ (v, u), (v, u), ...]
    }
    """
    return jsonify(graph_data)


@app.route("/get_steps")
def get_steps_data():
    """
    Возвращает JSON со списком шагов:
    steps = [ {...}, {...}, ... ]
    """
    return jsonify(steps)


if __name__ == "__main__":
    app.run(debug=True)
