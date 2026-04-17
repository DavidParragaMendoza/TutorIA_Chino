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

## Frontend en Vercel + API en ngrok (usando tu hardware local)

Este proyecto puede desplegarse en Vercel como sitio estático y consumir el backend que corre en tu laptop.

1. Inicia el backend en tu PC:
   ```powershell
   python main.py
   ```
2. En otra terminal, expón el backend con ngrok:
   ```powershell
   ngrok http 8000
   ```
3. Toma la URL pública HTTPS de ngrok y abre tu chat en Vercel una vez con:
   `https://tu-frontend.vercel.app/temas/saludos/chat?apiUrl=https://tu-subdominio.ngrok-free.app/chat`
4. Esa URL de API se guarda en `localStorage` y el chat seguirá usando tu backend local en próximas visitas.

## Scripts útiles

Construir la base vectorial:

```powershell
python -m scripts.construir_bd
```

Probar consulta RAG por consola:

```powershell
python -m scripts.consultar
```
