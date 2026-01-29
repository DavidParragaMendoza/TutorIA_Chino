const LM_STUDIO_URL = "https://contortively-sledlike-marcella.ngrok-free.dev/v1/chat/completions";
//const LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions";

//const MODEL_ID = "mimodelo-v1"; 
//const MODEL_ID = "tutoria-v0"; 
const MODEL_ID = "chino-v4"; 

let conversationHistory = [
    {
        role: "system",
        content: `Eres un profesor de chino HSK 1.
                    TU IDENTIDAD: Te llamas "TutorIA".
                    TU OBJETIVO: Enseñar exclusivamente el módulo de SALUDOS en mandarín.
                    
                    ### GUIÓN DE LA CLASE (Sigue este orden ESTRICTAMENTE):
                    
                    FASE 1: INICIO
                        Si el usuario dice "comenzar" o saluda por primera vez, responde con este saludo estándar:
                        "Bienvenido al módulo de saludos en mandarín, yo soy TutorIA. ¿Estás listo para aprender los saludos básicos del mandarín?"
                    
                    FASE 2: TEORÍA (Solo cuando el usuario confirme estar listo)
                        Antes de los saludos, explica brevemente dos conceptos clave:
                        1. Los Tonos: Explica que hay 4 tonos y que cambian el significado (como música).
                        2. La Caligrafía: Menciona que se usan caracteres (Hanzi) y Pinyin (sonido).
                        Termina preguntando: "¿Entendido? ¿Podemos pasar a los ejemplos?"
                    
                    FASE 3: PRÁCTICA CON ESCENARIOS (El núcleo de la clase)
                        Usa personajes como Pedro, José, María o Pepe para dar contexto.
                        Dinámica de enseñanza:
                        1. Plantea la situación: "Pedro va caminando y ve a José. Se saludan. ¿Sabes cómo se dice 'Hola' en mandarín?"
                        2. Espera la respuesta.
                        3. EXPLICACIÓN: Si no saben, enseña: "Se dice **Nǐ hǎo (你好)**."
                        4. VERIFICACIÓN: Inmediatamente pon un reto: "Ahora tú: Si María se encuentra a Pepe, ¿qué le dice?"
                    
                    ### REGLAS DE SEGURIDAD:
                        - Si el usuario se desvía (pregunta de código, clima, política), responde: "En este módulo solo puedo enseñarte saludos en mandarín. Volvamos a la clase."
                        - Usa siempre ESPAÑOL para explicar y CHINO (Hanzi + Pinyin) para los ejemplos.`
    }
];

const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

async function sendMessage(customText = null) {
    const isManual = typeof customText === 'string';
    const text = isManual ? customText : userInput.value.trim();

    if (!text) return;

    // 1. Mostrar mensaje del usuario (Diseño Tailwind)
    addMessageToUI(text, 'user');
    
    if (!isManual) {
        userInput.value = '';
    }

    conversationHistory.push({ role: "user", content: text });

    // Indicador de "Escribiendo..." (Opcional, visualmente agradable)
    // showTypingIndicator(); 

    try {
        const response = await fetch(LM_STUDIO_URL, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "ngrok-skip-browser-warning": "true"
            },
            body: JSON.stringify({
                model: MODEL_ID,
                messages: conversationHistory,
                temperature: 0.7
            })
        });

        const data = await response.json();
        const aiResponse = data.choices[0].message.content;

        // 2. Mostrar respuesta IA (Diseño Tailwind)
        addMessageToUI(aiResponse, 'assistant');
        conversationHistory.push({ role: "assistant", content: aiResponse });

    } catch (error) {
        addMessageToUI("Error de conexión con el Tutor.", 'system');
        console.error(error);
    }
}

// ESTA ES LA FUNCIÓN CLAVE QUE DEBES CAMBIAR
// Ahora genera HTML complejo en lugar de texto plano
function addMessageToUI(text, role) {
    const div = document.createElement('div');
    const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Convertimos saltos de línea en <br>
    const formattedText = text.replace(/\n/g, '<br>');

    if (role === 'user') {
        // DISEÑO PARA EL USUARIO (Alineado a la derecha, burbuja azul)
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
        // DISEÑO PARA EL ASISTENTE (Alineado a la izquierda, burbuja oscura)
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

// Iniciar conversación automáticamente al cargar
sendMessage("comenzar");