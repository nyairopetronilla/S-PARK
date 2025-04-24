document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/analytics")
      .then(res => res.json())
      .then(data => {
        renderLineChart(data.weeklyTrends);
        renderStackedBar(data.weeklyTrends);
        renderSummary(data.summary);
      })
      .catch(err => {
        console.error("Failed to load /api/analytics:", err);
      });
  
    function renderLineChart(data) {
      const ctx = document.getElementById("lineChart").getContext("2d");
      const datasets = [];
  
      for (let i = 1; i <= 6; i++) {
        datasets.push({
          label: "Slot " + i,
          data: data.map(d => d["slot" + i]),
          borderColor: getSlotColor(i),
          fill: false
        });
      }
  
      new Chart(ctx, {
        type: "line",
        data: {
          labels: data.map(d => d.day),
          datasets: datasets
        },
        options: {
          responsive: true,
          plugins: { legend: { position: "bottom" } },
          scales: { y: { beginAtZero: true } }
        }
      });
    }
  

    function renderStackedBar(data) {
      const ctx = document.getElementById("stackedBarChart").getContext("2d");
      const datasets = [];
  
      for (let i = 1; i <= 6; i++) {
        datasets.push({
          label: "Slot " + i,
          data: data.map(d => d["slot" + i]),
          backgroundColor: getSlotColor(i)
        });
      }
  
      new Chart(ctx, {
        type: "bar",
        data: {
          labels: data.map(d => d.day),
          datasets: datasets
        },
        options: {
          responsive: true,
          plugins: { legend: { position: "bottom" } },
          scales: {
            x: { stacked: true },
            y: { stacked: true, beginAtZero: true }
          }
        }
      });
    }
  
    function renderSummary(summary) {
      document.getElementById("mostUsedSlot").textContent = "Slot " + summary.most_used;
      document.getElementById("busiestDay").textContent = summary.busiest_day;
    }
  
    function getSlotColor(index) {
      const colors = ["#3b82f6", "#ef4444", "#f59e0b", "#facc15", "#10b981", "#8b5cf6"];
      return colors[index - 1] || "#fff";
    }
  });
  