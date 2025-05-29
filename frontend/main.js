

// Глобальні змінні
let allArticles = [];

// Безпечне отримання елементів
const filterSelect = document.getElementById("filter-select");
const tableBody = document.querySelector("#articles-table tbody");
const canvas = document.getElementById("sentiment-chart");
if (!filterSelect || !tableBody || !canvas) {
  console.error("Відсутні необхідні елементи DOM");
}

const canvasCtx = canvas.getContext("2d");

// 1) Функція завантаження даних
async function loadData() {
  try {
    // 1.1) Перший POST (fetch)
    const fetchResponse = await fetch(`${API_BASE}/fetch/${STUDENT_ID}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });

    if (!fetchResponse.ok) {
      throw new Error(`Помилка fetch: ${fetchResponse.status} ${fetchResponse.statusText}`);
    }

    // 1.2) Другий POST (analyze)
    const analyzeResponse = await fetch(`${API_BASE}/analyze/${STUDENT_ID}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });

    if (!analyzeResponse.ok) {
      throw new Error(`Помилка analyze: ${analyzeResponse.status} ${analyzeResponse.statusText}`);
    }

    const data = await analyzeResponse.json();

    if (!data.articles) {
      throw new Error("Відсутній ключ 'articles' в відповіді сервера");
    }

    allArticles = data.articles.map(a => ({
      ...a,
      date: a.published ? new Date(a.published) : new Date()
    }));

    render();
  } catch (err) {
    console.error("Помилка під час завантаження даних:", err);
    tableBody.innerHTML = `<tr><td colspan="3" style="color:red;">Помилка завантаження даних. Спробуйте пізніше.</td></tr>`;
    chart.data.datasets[0].data = [0, 0, 0];
    chart.update();
  }
}

// 2) Рендер таблиці
function renderTable(filtered) {
  if (filtered.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="3">Немає статей для відображення</td></tr>`;
    return;
  }

  tableBody.innerHTML = filtered
    .sort((a, b) => b.date - a.date)
    .map(a => `
      <tr>
        <td>${a.date.toLocaleString()}</td>
        <td>${a.sentiment || "N/A"}</td>
        <td><a href="${a.link}" target="_blank" rel="noopener noreferrer">${a.title}</a></td>
      </tr>
    `).join("");
}

// 3) Рендер діаграми
function renderChart(filtered) {
  const counts = { positive: 0, neutral: 0, negative: 0 };

  filtered.forEach(a => {
    if (a.sentiment && counts.hasOwnProperty(a.sentiment)) {
      counts[a.sentiment]++;
    }
  });

  chart.data.datasets[0].data = [
    counts.positive,
    counts.neutral,
    counts.negative
  ];
  chart.update();
}

// 4) Основний рендер
function render() {
  const filter = filterSelect.value;
  const filtered = allArticles.filter(a =>
    filter === "all" ? true : (a.sentiment && a.sentiment === filter)
  );

  renderTable(filtered);
  renderChart(filtered);
}

// 5) Chart.js ініціалізація
const chart = new Chart(canvasCtx, {
  type: 'pie',
  data: {
    labels: ['Позитивні', 'Нейтральні', 'Негативні'],
    datasets: [{
      data: [0, 0, 0],
      backgroundColor: ['#4caf50', '#ffca28', '#f44336']
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2,
    plugins: {
      legend: { position: 'top' }
    }
  }
});

// 6) Обробка зміни фільтра
filterSelect.addEventListener("change", render);

// 7) Завантаження даних при завантаженні сторінки
window.addEventListener("load", loadData);
