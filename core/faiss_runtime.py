import os


def _gpu_habilitada_por_config() -> bool:
    valor = os.getenv("FAISS_USE_GPU", "1").strip().lower()
    return valor not in {"0", "false", "no", "off"}


def activar_gpu_si_disponible(db):
    if not _gpu_habilitada_por_config():
        print("-> FAISS GPU deshabilitado por configuración (FAISS_USE_GPU=0).")
        return db

    try:
        import faiss
    except Exception as exc:
        print(f"-> No se pudo importar faiss: {exc}. Se mantiene CPU.")
        return db

    if not hasattr(faiss, "StandardGpuResources") or not hasattr(faiss, "index_cpu_to_gpu"):
        print("-> Este build de FAISS no incluye soporte GPU. Se mantiene CPU.")
        return db

    try:
        cantidad_gpu = faiss.get_num_gpus() if hasattr(faiss, "get_num_gpus") else 0
    except Exception:
        cantidad_gpu = 0

    if cantidad_gpu <= 0:
        print("-> No se detectaron GPUs compatibles para FAISS. Se mantiene CPU.")
        return db

    indice_actual = getattr(db, "index", None)
    if indice_actual is None:
        return db

    nombre_indice = type(indice_actual).__name__.lower()
    if "gpu" in nombre_indice:
        print("-> El índice FAISS ya está en GPU.")
        return db

    try:
        recursos_gpu = faiss.StandardGpuResources()
        db.index = faiss.index_cpu_to_gpu(recursos_gpu, 0, indice_actual)
        db._faiss_gpu_resources = recursos_gpu
        print("-> Índice FAISS movido a GPU (GPU 0).")
    except Exception as exc:
        print(f"-> No se pudo mover el índice FAISS a GPU: {exc}. Se mantiene CPU.")

    return db


def preparar_indice_para_guardar(db):
    try:
        import faiss
    except Exception:
        return db

    indice_actual = getattr(db, "index", None)
    if indice_actual is None:
        return db

    nombre_indice = type(indice_actual).__name__.lower()
    if "gpu" not in nombre_indice:
        return db

    if not hasattr(faiss, "index_gpu_to_cpu"):
        return db

    db.index = faiss.index_gpu_to_cpu(indice_actual)
    return db
