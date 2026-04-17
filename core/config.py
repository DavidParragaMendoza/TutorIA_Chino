import os
from dataclasses import dataclass
from pathlib import Path

RUTA_RAIZ = Path(__file__).resolve().parent.parent
RUTA_ENV = RUTA_RAIZ / ".env"


def _cargar_env_desde_archivo() -> None:
    if not RUTA_ENV.exists():
        return

    for linea in RUTA_ENV.read_text(encoding="utf-8").splitlines():
        limpia = linea.strip()
        if not limpia or limpia.startswith("#") or "=" not in limpia:
            continue

        clave, valor = limpia.split("=", 1)
        clave = clave.strip()
        if not clave:
            continue

        valor = valor.strip().strip("'").strip('"')
        os.environ.setdefault(clave, valor)


def _leer_env(clave: str, por_defecto: str) -> str:
    valor = os.getenv(clave, por_defecto).strip()
    return valor or por_defecto


@dataclass(frozen=True)
class ConfiguracionMotor:
    tipo_motor: str
    modelo_simple_llm: str
    modelo_fine_tuned: str


def cargar_configuracion_motor() -> ConfiguracionMotor:
    _cargar_env_desde_archivo()

    return ConfiguracionMotor(
        tipo_motor=_leer_env("TIPO_MOTOR", "rag").lower(),
        modelo_simple_llm=_leer_env("MODELO_LLM_SIMPLE", "qwen2.5:3b"),
        modelo_fine_tuned=_leer_env("MODELO_FINE_TUNED", "tutoria-finetuned"),
    )
