let steps = [];
let currentStepIndex = 0;

// Храним координаты для вершин
let vertexPositions = {};

// Также сохраним matchR с бэкенда (результат паросочетания)
let matchR = [];
let nLeft = 0;
let nRight = 0;
let edges = [];

window.addEventListener('load', () => {
    loadGraphData();
    const btnBack = document.getElementById('btnBack');
    btnBack.addEventListener('click', () => {
        window.location.href = '/';
    });
});

function loadGraphData() {
    fetch('/get_graph_data')
        .then(resp => resp.json())
        .then(data => {
            // Сохраним данные
            nLeft = data.n_left;
            nRight = data.n_right;
            edges = data.edges;
            matchR = data.matchR;  // итоговое сопоставление

            drawGraphSVG(); // рисуем пустой SVG (вершины, рёбра)
            return fetch('/get_steps');
        })
        .then(resp => resp.json())
        .then(dataSteps => {
            steps = dataSteps;
            // Вешаем обработчик на кнопку
            document.getElementById('btnNext').addEventListener('click', showNextStep);
        })
        .catch(err => {
            console.error("Ошибка:", err);
        });
}

// 1) Рисуем изначальный граф
function drawGraphSVG() {
    const svg = document.getElementById('graph-svg');
    svg.innerHTML = "";

    // Координаты левых вершин (x=100), правых (x=400)
    let spacing = 60;
    let startYLeft = 50;
    let startYRight = 50;

    for (let v = 0; v < nLeft; v++) {
        let x = 100;
        let y = startYLeft + spacing * v;
        vertexPositions[`L-${v}`] = {x, y};
    }
    for (let u = 0; u < nRight; u++) {
        let x = 400;
        let y = startYRight + spacing * u;
        vertexPositions[`R-${u}`] = {x, y};
    }

    // Рёбра
    edges.forEach(([v, u]) => {
        const leftPos = vertexPositions[`L-${v}`];
        const rightPos = vertexPositions[`R-${u}`];
        let line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", leftPos.x);
        line.setAttribute("y1", leftPos.y);
        line.setAttribute("x2", rightPos.x);
        line.setAttribute("y2", rightPos.y);
        line.setAttribute("stroke", "#2C2C2C"); // изначальный цвет путей
        line.setAttribute("stroke-width", "2");
        line.setAttribute("id", `edge-L${v}-R${u}`);
        svg.appendChild(line);
    });

    // Вершины левые
    for (let v = 0; v < nLeft; v++) {
        const pos = vertexPositions[`L-${v}`];
        drawVertexCircle(svg, pos.x, pos.y, `left-${v}`, "#522546"); // обычная вершина (левая)
        drawVertexLabel(svg, pos.x, pos.y, `l${v}`);
    }

    // Вершины правые
    for (let u = 0; u < nRight; u++) {
        const pos = vertexPositions[`R-${u}`];
        drawVertexCircle(svg, pos.x, pos.y, `right-${u}`, "#522546"); // обычная вершина (правая)
        drawVertexLabel(svg, pos.x, pos.y, `r${u}`);
    }
}

function drawVertexCircle(svg, cx, cy, id, color) {
    let circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", cx);
    circle.setAttribute("cy", cy);
    circle.setAttribute("r", 15);
    circle.setAttribute("fill", color);
    circle.setAttribute("id", id);
    svg.appendChild(circle);
}

function drawVertexLabel(svg, cx, cy, labelText) {
    let text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", cx);
    text.setAttribute("y", cy + 5);
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("font-size", "14px");
    text.setAttribute("fill", "#ffffff");
    text.textContent = labelText; 
    svg.appendChild(text);
}

// 2) Покадровый показ шагов
function showNextStep() {
    if (currentStepIndex < steps.length) {
        let step = steps[currentStepIndex];
        currentStepIndex++;
        displayStep(step, currentStepIndex);
    } else {
        // Если шагов больше нет — выводим итог
        logMessage(`алгоритм завершён. больше шагов нет.`);

        // Выведем результат паросочетания
        showFinalMatching();
    }
}

function displayStep(step, stepNum) {
    resetHighlights();

    switch (step.type) {
        case "visit_left_vertex":
            highlightLeftVertex(step.vertex_left, "#88304E");
            logMessage(`${stepNum}. ищем пару для l${step.vertex_left}`);
            break;

        case "explore_edge":
            highlightEdge(step.edge_left, step.edge_right, "#F7374F");
            logMessage(`${stepNum}. рассматриваем ребро (l${step.edge_left} -> r${step.edge_right})`);
            break;

        case "found_free_right":
            highlightRightVertex(step.vertex_right, "#88304E");
            logMessage(`${stepNum}. найдена свободная вершина r${step.vertex_right}, связываем её`);
            break;

        case "right_taken":
            highlightRightVertex(step.vertex_right, "#F7374F");
            highlightLeftVertex(step.occupied_by, "#F7374F");
            logMessage(`${stepNum}. правая вершина r${step.vertex_right} занята (l${step.occupied_by}), пытаемся сместить...`);
            break;

        default:
            logMessage(`${stepNum}. неизвестный шаг: ${JSON.stringify(step)}`);
    }
}

// Сброс подсветок
function resetHighlights() {
    const svg = document.getElementById('graph-svg');

    // Восстанавливаем все вершины
    let circles = svg.getElementsByTagName('circle');
    for (let i = 0; i < circles.length; i++) {
        circles[i].setAttribute("fill", "#522546"); // обычная вершина
    }

    // Восстанавливаем все рёбра
    let lines = svg.getElementsByTagName('line');
    for (let i = 0; i < lines.length; i++) {
        lines[i].setAttribute("stroke", "#2C2C2C"); // изначальный цвет
        lines[i].setAttribute("stroke-width", "2");
    }
}

// Подсветка
function highlightLeftVertex(v, color) {
    let circle = document.getElementById(`left-${v}`);
    if (circle) {
        circle.setAttribute("fill", color);
    }
}
function highlightRightVertex(u, color) {
    let circle = document.getElementById(`right-${u}`);
    if (circle) {
        circle.setAttribute("fill", color);
    }
}
function highlightEdge(v, u, color) {
    let line = document.getElementById(`edge-L${v}-R${u}`);
    if (line) {
        line.setAttribute("stroke", color);
        line.setAttribute("stroke-width", "4");
    }
}

// Лог - выводим в #log
function logMessage(msg) {
    let logDiv = document.getElementById('log');
    logDiv.innerHTML += `<p>${msg}</p>`;
    logDiv.scrollTop = logDiv.scrollHeight;
}

// 3) Финальный вывод паросочетания
function showFinalMatching() {
    // matchR[u] = v => (v, u) в паросочетании
    // Соберём пары (l..., r...)
    let pairs = [];
    for (let u = 0; u < matchR.length; u++) {
        let v = matchR[u];
        if (v !== -1) {
            pairs.push(`(l${v}, r${u})`);
        }
    }

    let length = pairs.length;
    let msg = `максимальное паросочетание = { ${pairs.join(", ")} }, его длина = ${length}`;
    // Выведем в div #final-result
    let frDiv = document.getElementById('final-result');
    frDiv.innerHTML = `<p>${msg}</p>`;
}
