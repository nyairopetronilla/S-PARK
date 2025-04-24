const socket = io();
const display = document.getElementById("data-display");
const slotsContainer = document.getElementById("slot-statuses");
const slotsHeader = document.getElementById("available-slots");
const lastUpdated = document.getElementById("last-updated");
const loadingStatus = document.getElementById("loading-status");

// 🌗 Theme Toggle Logic
const html = document.documentElement;
const toggleBtn = document.getElementById("themeToggle");
const savedTheme = localStorage.getItem("theme");

if (savedTheme === "dark") {
  html.classList.add("dark");
} else {
  html.classList.remove("dark");
}

toggleBtn.addEventListener("click", () => {
  html.classList.toggle("dark");
  const newTheme = html.classList.contains("dark") ? "dark" : "light";
  localStorage.setItem("theme", newTheme);
});

// Real-time update handler
socket.on("update", (data) => {
  if (!data || !data.slots) return;

  const occupiedCount = data.slots.filter(s => s.occupied).length;
  const availableCount = data.total_slots - occupiedCount;

  slotsHeader.textContent = `Available Slots: ${availableCount} / ${data.total_slots}`;
  slotsContainer.innerHTML = "";

  data.slots.forEach(slot => {
    const box = document.createElement("div");
    box.className = "p-4 rounded shadow bg-gray-200 dark:bg-gray-700";

    const label = document.createElement("p");
    label.className = "text-sm font-semibold";
    label.textContent = `Slot ${slot.id}:`;

    const status = document.createElement("p");

    if (slot.id === 6) {
      status.textContent = "🅿 Reserved";
      status.className = "text-yellow-400";
      label.classList.add("text-yellow-400");
    } else if (slot.occupied) {
      status.textContent = "🚗 Occupied";
      status.className = "text-red-500";
      label.classList.add("text-red-500");
    } else {
      status.textContent = "✅ Available";
      status.className = "text-green-500";
      label.classList.add("text-green-500");
    }

    box.appendChild(label);
    box.appendChild(status);
    slotsContainer.appendChild(box);
  });

  // Show time of update
  lastUpdated.textContent = `Updated: ${new Date().toLocaleTimeString()}`;

  // Hide loading after first update
  if (loadingStatus) loadingStatus.remove();
});
