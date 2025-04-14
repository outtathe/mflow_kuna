let steps = [];
let currentStepIndex = 0;

window.addEventListener('load', () => {
    // Сразу при загрузке запросим шаги
    fetch('/get_steps')
        .then(resp => resp.json())
        .then(data => {
            steps = data;
            console.log("Steps loaded:", steps);
        });

    // Навесим обработчик на кнопку "Следующий шаг"
    document.getElementById('btnNext').addEventListener('click', showNextStep);
});


function showNextStep() {
    if (currentStepIndex < steps.length) {
        const step = steps[currentStepIndex];
        currentStepIndex++;
        displayStep(step);
    } else {
        const logDiv = document.getElementById('log');
        logDiv.innerHTML += "<p>Алгоритм завершён. Больше шагов нет.</p>";
    }
}

function displayStep(step) {
    const logDiv = document.getElementById('log');
    let msg = "";
    switch(step.type) {
        case "visit_left_vertex":
            msg = `Посетили левую вершину v = ${step.vertex_left}`;
            break;
        case "explore_edge":
            msg = `Рассматриваем ребро (${step.edge_left} -> ${step.edge_right})`;
            break;
        case "found_free_right":
            msg = `Найдена свободная правая вершина u = ${step.vertex_right}, связываем её!`;
            break;
        case "right_taken":
            msg = `Правая вершина ${step.vertex_right} занята левой ${step.occupied_by}, пытаемся сместить...`;
            break;
        default:
            msg = "Неизвестный шаг";
    }
    logDiv.innerHTML += `<p>${currentStepIndex}. ${msg}</p>`;
    logDiv.scrollTop = logDiv.scrollHeight;
}
