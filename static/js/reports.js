$(document).ready(function () {
  console.log("✅ reports.js loaded!");

  const table = $("#reportsTable").DataTable({
    columns: [
      { title: "Timestamp", data: "created_at" },
      { title: "Device", data: "device_id" },
      { title: "Available", data: "available_slots" },
      { title: "Slot 1", data: "slot1", render: d => d ? "🚗" : "✅" },
      { title: "Slot 2", data: "slot2", render: d => d ? "🚗" : "✅" },
      { title: "Slot 3", data: "slot3", render: d => d ? "🚗" : "✅" },
      { title: "Slot 4", data: "slot4", render: d => d ? "🚗" : "✅" },
      { title: "Slot 5", data: "slot5", render: d => d ? "🚗" : "✅" },
      { title: "Slot 6", data: "slot6", render: d => d ? "🅿" : "✅" }
    ],
    dom: "Bfrtip",
    buttons: ["copy", "csv", "excel", "pdf", "print"],
    responsive: true,
    pageLength: 10,
    order: [[0, "desc"]],
    language: {
      emptyTable: "No reports found. Please wait for Arduino to send updates!"
    }
  });

  function fetchAndDisplayReports(start = null, end = null) {
    let url = "/api/reports";
    if (start && end) {
      url += `?start=${start}&end=${end}`;
    }

    fetch(url)
      .then(res => res.json())
      .then(data => {
        console.log("📦 Reports received:", data);
        table.clear().rows.add(data).draw();
        updateChart(data);
      })
      .catch(err => console.error("❌ Failed to fetch reports:", err));
  }

  // Load today's reports by default
  const today = moment().format("YYYY-MM-DD");
  fetchAndDisplayReports(today, today);

  // Date Range Picker Setup
  $("#daterange").daterangepicker({
    opens: "left",
    locale: { format: "YYYY-MM-DD" },
    startDate: today,
    endDate: today
  }, function (start, end) {
    fetchAndDisplayReports(start.format("YYYY-MM-DD"), end.format("YYYY-MM-DD"));
  });

  // Chart Updater
  function updateChart(data) {
    const slotCounts = [0, 0, 0, 0, 0, 0];
    data.forEach(report => {
      for (let i = 0; i < 6; i++) {
        if (report[`slot${i + 1}`]) slotCounts[i]++;
      }
    });

    const ctx = document.getElementById("slotChart")?.getContext("2d");
    if (!ctx) return;

    if (window.slotChartRef) {
      window.slotChartRef.data.datasets[0].data = slotCounts;
      window.slotChartRef.update();
    } else {
      window.slotChartRef = new Chart(ctx, {
        type: "bar",
        data: {
          labels: ["Slot 1", "Slot 2", "Slot 3", "Slot 4", "Slot 5", "Slot 6"],
          datasets: [{
            label: "Times Occupied",
            data: slotCounts,
            backgroundColor: "#3b82f6"
          }]
        },
        options: {
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true } }
        }
      });
    }
  }
});
