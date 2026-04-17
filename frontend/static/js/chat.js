const API_URL = window.APP_CONFIG?.apiUrl || "/chat";
const PROMPT_INICIAL = `Inicia la clase de saludos de chino mandarín HSK 1. Saluda breve y pregunta qué quiere practicar primero (saludos básicos, formales o despedidas).`;

const chatContainer = document.getElementById("chatContainer");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const historialConversacion = [];

sendBtn.addEventListener("click", sendMessage);

userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        sendMessage();
    }
});

async function solicitarRespuestaTutor(pregunta, historial) {
    const response = await fetch(API_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            pregunta,
            historial,
        }),
    });

    if (!response.ok) {
        throw new Error(`Error HTTP ${response.status}`);
    }

    const data = await response.json();
    const respuesta = data?.respuesta?.trim();
    if (!respuesta) {
        throw new Error("Respuesta vacía del tutor.");
    }

    return respuesta;
}

async function iniciarSesionTutor() {
    try {
        const respuestaInicial = await solicitarRespuestaTutor(PROMPT_INICIAL, []);
        historialConversacion.push({ rol: "asistente", contenido: respuestaInicial });
        addMessageToUI(respuestaInicial, "assistant");
    } catch (error) {
        addMessageToUI("Error de conexión con el Tutor.", "system");
        console.error(error);
    }
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessageToUI(text, "user");
    userInput.value = "";

    const historialParaPeticion = [...historialConversacion];

    try {
        const aiResponse = await solicitarRespuestaTutor(text, historialParaPeticion);

        historialConversacion.push({ rol: "usuario", contenido: text });
        historialConversacion.push({ rol: "asistente", contenido: aiResponse });
        addMessageToUI(aiResponse, "assistant");
    } catch (error) {
        addMessageToUI("Error de conexión con el Tutor.", "system");
        console.error(error);
    }
}

function addMessageToUI(text, role) {
    const div = document.createElement("div");
    const timeNow = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    const formattedText = text.replace(/\n/g, "<br>");

    if (role === "user") {
        div.className = "flex gap-4 max-w-2xl ml-auto justify-end";
        div.innerHTML = `
            <div class="space-y-1.5 flex flex-col items-end">
                <div class="bg-primary p-4 rounded-2xl rounded-tr-none shadow-lg shadow-primary/10">
                    <p class="text-white font-medium text-sm lg:text-base">${formattedText}</p>
                </div>
                <p class="text-[10px] text-slate-500 mr-1 uppercase font-bold tracking-widest">Tú • ${timeNow}</p>
            </div>
            <div class="w-9 h-9 rounded-full bg-slate-800 bg-cover bg-center shrink-0 border border-border-dark" style="background-image: url('https://lh3.googleusercontent.com/a/default-user')"></div>
        `;
    } else {
        div.className = "flex gap-4 max-w-2xl";
        div.innerHTML = `
            <div class="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined text-primary text-lg">smart_toy</span>
            </div>
            <div class="space-y-1.5">
                <div class="bg-surface-dark border border-border-dark p-4 rounded-2xl rounded-tl-none shadow-sm">
                    <p class="text-slate-200 text-sm lg:text-base leading-relaxed">${formattedText}</p>
                </div>
                <p class="text-[10px] text-slate-500 ml-1 uppercase font-bold tracking-widest">Tutor IA • ${timeNow}</p>
            </div>
        `;
    }

    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

iniciarSesionTutor();
