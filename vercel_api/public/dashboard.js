async function fetchSignals(){
  const res = await fetch('/api/signals', { cache: 'no-store' });
  if(!res.ok){
    const text = await res.text();
    throw new Error('API error: '+text);
  }
  const json = await res.json();
  return json.signals || json; // supports both shapes
}

function signalLabel(v){
  if (v > 0) return 'BUY';
  if (v < 0) return 'SELL';
  return 'NEUTRAL';
}

function signalClass(v){
  if (v > 0) return 'sig-buy';
  if (v < 0) return 'sig-sell';
  return 'sig-neutral';
}

let chart;

function renderChart(data){
  const ctx = document.getElementById('scoreChart').getContext('2d');
  const labels = data.map(d => new Date(d.timestamp).toISOString().replace('T',' ').replace('Z',''));
  const scores = data.map(d => d.score);
  if(chart){ chart.destroy(); }
  chart = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets: [{ label: 'Score', data: scores, tension: 0.2, pointRadius: 2 }] },
    options: {
      responsive: true,
      scales: { y: { suggestedMin: -1, suggestedMax: 1 } },
      plugins: { legend: { display: false } }
    }
  });
}

function renderTable(data){
  const tbody = document.querySelector('#signalsTable tbody');
  tbody.innerHTML='';
  const last = data.slice(-100).reverse(); // show last 100, newest first
  for (const row of last){
    const tr = document.createElement('tr');
    const ts = new Date(row.timestamp).toISOString().replace('T',' ').replace('Z','');
    tr.innerHTML = `
      <td>${ts}</td>
      <td>${row.score.toFixed(3)}</td>
      <td class="${signalClass(row.signal)}">${signalLabel(row.signal)}</td>
    `;
    tbody.appendChild(tr);
  }
}

async function refresh(){
  const status = document.getElementById('status');
  try{
    status.textContent = 'loading…';
    const data = await fetchSignals();
    if(Array.isArray(data) && data.length){
      renderChart(data);
      renderTable(data);
      status.textContent = 'live';
    } else {
      status.textContent = 'no data yet';
    }
  }catch(e){
    console.error(e);
    status.textContent = 'error (see console)';
  }
}

refresh();
setInterval(refresh, 10000);
