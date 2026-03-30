# Instalación de FAISS para este proyecto

## 1) Windows (PowerShell)

En Windows, `faiss-gpu` no suele estar disponible vía `pip`.
Para evitar errores, instala FAISS CPU:

```powershell
c:/Users/General/Documents/inferencia/TutorIA_Chino/.venv/Scripts/python.exe -m pip uninstall -y faiss-gpu faiss-cpu
c:/Users/General/Documents/inferencia/TutorIA_Chino/.venv/Scripts/python.exe -m pip install -r requirements.txt
```

Con esto, el proyecto funciona y no se rompe.

## 2) GPU real con FAISS (recomendado: WSL2 Ubuntu)

Si quieres aceleración GPU real, usa Linux/WSL2 + drivers CUDA:

1. Instala WSL2 y Ubuntu.
2. Crea un entorno en Ubuntu (idealmente Python 3.11/3.12).
3. Instala dependencias:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Verifica FAISS:

```bash
python -c "import faiss; print('GPUs:', faiss.get_num_gpus() if hasattr(faiss, 'get_num_gpus') else 0)"
```

## 3) Comportamiento del código

El proyecto ahora intenta usar GPU automáticamente al cargar la base vectorial.
Si no hay GPU o no hay soporte, cae a CPU sin fallar.

Puedes forzar CPU con:

```powershell
$env:FAISS_USE_GPU="0"
```

o en Linux:

```bash
export FAISS_USE_GPU=0
```