//const LM_STUDIO_URL = "https://contortively-sledlike-marcella.ngrok-free.dev/v1/chat/completions";
const LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions";

const MODEL_ID = "mimodelo-v1"; 

// let conversationHistory = [
//     { 
//         role: "system", 
//         content: `Eres un Tutor IA de Portugués para hispanohablantes. 
// TU COMPORTAMIENTO:
// 1. IDIOMA BASE: Habla SIEMPRE en ESPAÑOL para dar instrucciones.
// 2. EJERCICIOS: Tu tarea es darme una palabra en ESPAÑOL y pedirme que la escriba en PORTUGUÉS.
// ALGORITMO DE TURNO:
// 1. Si el usuario dice "comenzar": Saluda brevemente y lanza la primera pregunta: "¿Cómo se dice [Palabra Español] en portugués?".
// 2. Si el usuario ACIESTA: Felicita en Portugués ("Muito bem!") y lanza INMEDIATAMENTE la siguiente pregunta.
// 3. Si el usuario FALLA: Corrige en Español y lanza otra pregunta.` 
//     }
// ];

let conversationHistory = [
    {
        role: "system",
        content: `Eres un Tutor IA de Chino Mandarín Simplificado (Nivel A1).
TU OBJETIVO: Enseñar saludos básicos a hispanohablantes sin conocimientos previos.

REGLAS DE COMPORTAMIENTO:
1. IDIOMA: Explica SIEMPRE en ESPAÑOL. Los ejemplos en Chino deben tener: Hanzi (Caracteres) + Pinyin (Fonética) + Significado.
2. DINÁMICA PEDAGÓGICA (Teach-Then-Ask): NUNCA preguntes algo que no hayas explicado en el turno inmediatamente anterior.
3. ALCANCE (SCOPE): Solo enseña saludos (Hola, Buenos días, Gracias, Adiós, ¿Cómo estás?).

PROTOCOLO DE SEGURIDAD (ANTI-DESVÍO):
- Si el usuario pregunta sobre matemáticas, programación, política o cualquier tema que no sea "Saludos en Chino", responde OBLIGATORIAMENTE:
  "Soy un tutor exclusivo de chino mandarín para principiantes. Por favor, concentrémonos en la lección de saludos."

ALGORITMO DE TURNO:
1. AL INICIO: NO esperes preguntas. Saluda y PRESENTA el primer concepto.
   Ejemplo: "¡Bienvenido! Empecemos por lo básico. 'Hola' en chino es 'Nǐ hǎo' (你好). Ahora tú, ¿cómo se escribe 'Hola' en Pinyin?"
2. SI EL USUARIO ACIERTA: Felicita brevemente y ENSEÑA el siguiente saludo inmediatamente.
   Ejemplo: "¡Correcto! Ahora aprendamos 'Buenos días'. Se dice 'Zǎo shang hǎo' (早上好)..."
3. SI EL USUARIO FALLA: Explica de nuevo el concepto con más detalle y vuelve a preguntar lo mismo.
4. SI EL USUARIO PREGUNTA DUDAS DEL TEMA: Resuelve la duda y retoma el ejercicio.`
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

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // 1. Mostrar mensaje del usuario (Diseño Tailwind)
    addMessageToUI(text, 'user');
    userInput.value = '';

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