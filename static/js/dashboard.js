function fetchLCDData() {
  fetch("/lcd-data")
    .then(response => response.json())
    .then(data => {
      console.log("📡 Polled Data:", data);

      const available = data.available_slots;
      const color = available === 0 ? 'text-red-500' : 'text-emerald-400';
      document.getElementById("available").innerHTML = `<span class="${color} font-bold">${available}</span>`;

      // Update slots
      for (let i = 1; i <= 6; i++) {
        const slotBox = document.getElementById(`s${i}`);
        const slotStatus = document.getElementById(`s${i}-status`);
        const slot = data.slots.find(s => s.id === i);

        let statusText = "❔ Unknown";
        let boxStyle = "bg-gray-600 text-white";
        let statusIcon = "❔";

        if (slot) {
          if (slot.occupied) {
            statusText = "🚗 Occupied";
            boxStyle = "bg-rose-600 border-2 border-rose-400 shadow-xl text-white";
          } else if (slot.reserved) {
            statusText = "🟡 Reserved";
            boxStyle = "bg-yellow-400 border-2 border-yellow-300 shadow-lg text-black";
          } else {
            statusText = "✅ Available";
            boxStyle = "bg-emerald-600 border-2 border-emerald-300 shadow-md text-white";

            // 🔔 Optional: Sound alert when new slot becomes available
            if (!slotStatus.dataset.wasAvailable) {
              const audio = new Audio("/static/sounds/notify.mp3");
              audio.play();
            }
          }
        }

        // Save current state
        slotStatus.dataset.wasAvailable = (!slot?.occupied && !slot?.reserved).toString();

        // Apply new style with transition
        slotBox.className = `flex flex-col items-center justify-center p-4 rounded-xl font-bold transition-all duration-500 ease-in-out ${boxStyle}`;
        slotStatus.innerText = statusText;
      }

      // Push Notification (if granted)
      if (Notification.permission === "granted") {
        new Notification("🚗 Smart Parking Update", {
          body: `${available} slot(s) available.`,
          icon: "/static/icon.png"
        });
      }
    })
    .catch(error => {
      console.error("❌ Error fetching /lcd-data:", error);
    });
}

// Ask for push permission
if (Notification.permission !== "granted") {
  Notification.requestPermission().then(perm => {
    if (perm === "granted") {
      new Notification("🔔 Notifications Enabled", {
        body: "You'll get real-time slot updates.",
        icon: "/static/icon.png"
      });
    }
  });
}

// Poll every 2s
setInterval(fetchLCDData, 2000);
fetchLCDData();
