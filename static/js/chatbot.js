
  const chatBox = document.getElementById("chat-box");
  const inputBox = document.getElementById("message");
  const sendBtn = document.getElementById("send-btn");
  const micBtn = document.getElementById("mic-btn");
  let isVoiceInput = false;
  let recognition;

  function appendMessage(role, text) {
    const msg = document.createElement("div");
    msg.className = role === "user" ? "text-right" : "text-left";
    msg.innerHTML = `<div class="inline-block px-4 py-2 rounded-xl bg-${role === 'user' ? 'blue' : 'gray'}-600">${text}</div>`;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function speak(text) {
    if (!isVoiceInput) return;
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = synth.getVoices().find(v => v.name.includes("Female") || v.name.includes("Zira")) || synth.getVoices()[0];
    synth.speak(utterance);
  }

  function sendMessage(message = null) {
    const msg = message || inputBox.value.trim();
    if (!msg) return;

    appendMessage("user", msg);
    inputBox.value = "";

    axios.post("/api/chat", { message: msg })
      .then(res => {
        const reply = res.data.response;
        appendMessage("bot", reply);
        speak(reply);
        isVoiceInput = false;
      })
      .catch(() => {
        const error = "⚠️ Error getting response.";
        appendMessage("bot", error);
        speak(error);
        isVoiceInput = false;
      });
  }

  micBtn.addEventListener("click", () => {
    if (recognition) recognition.abort();
    isVoiceInput = true;

    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    micBtn.classList.add("animate-pulse", "bg-blue-700");

    recognition.onresult = e => {
      micBtn.classList.remove("animate-pulse", "bg-blue-700");
      const voiceText = e.results[0][0].transcript;
      sendMessage(voiceText);
    };

    recognition.onerror = e => {
      micBtn.classList.remove("animate-pulse", "bg-blue-700");
      appendMessage("bot", "🎤 Voice input error: " + e.error);
    };

    recognition.onend = () => {
      micBtn.classList.remove("animate-pulse", "bg-blue-700");
    };

    recognition.start();
  });

  sendBtn.addEventListener("click", () => sendMessage());

  inputBox.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  });

