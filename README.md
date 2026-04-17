# TutorChino

Aplicación de tutoría de mandarín con arquitectura modular (FastAPI + motores de inferencia intercambiables + frontend por temas).

## Estructura del proyecto

```text
TUTORCHINO/
├─ api/                  # Rutas HTTP, dependencias y schemas
├─ core/                 # Configuración, fábrica de motores y utilidades de servidor/FAISS
├─ engines/              # Implementaciones de motores (rag, simple_llm, fine_tuned)
├─ interfaces/           # Contratos (MotorInferencia)
├─ frontend/
│  ├─ pages/             # HTML por secciones y temas
│  ├─ static/            # CSS/JS estáticos servidos por FastAPI
│  └─ src/               # Fuente de Tailwind (input.css + assets de referencia)
├─ scripts/              # Scripts auxiliares (construcción FAISS y consulta por consola)
├─ docs/                 # Documentación adicional
├─ main.py               # Entry point del backend
├─ requirements.txt
├─ package.json
└─ .env.example
```

## Configuración rápida

1. **Backend (Python)**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Frontend (Tailwind)**
   ```powershell
   npm install
   npm run build
   ```

3. **Variables de entorno**
   - Copia `.env.example` a `.env`
   - Configura `TIPO_MOTOR`:
     - `rag`
     - `simple_llm`
     - `fine_tuned`

## Ejecutar la aplicación

```powershell
python main.py
```

La app sirve:
- Páginas: `/`, `/temas`, `/temas/{tema}`, `/temas/{tema}/chat`
- API: `POST /chat`
- Estáticos: `/static/...`

## Frontend en Vercel + API en ngrok

Si publicas solo el frontend en Vercel y quieres usar tu laptop como backend:

1. Levanta tu backend local (`python main.py`) y expón el puerto con ngrok.
2. Edita `frontend/pages/temas/saludos/chat.html`.
3. En `window.APP_CONFIG.apiUrl`, coloca tu URL pública de ngrok terminando en `/chat`.

Ejemplo:

```html
apiUrl: "https://xxxx-xx-xx-xx-xx.ngrok-free.app/chat"
```

## Scripts útiles

Construir la base vectorial:

```powershell
python -m scripts.construir_bd
```

Probar consulta RAG por consola:

```powershell
python -m scripts.consultar
```
