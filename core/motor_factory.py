from collections.abc import Callable

from engines import MotorFineTuned, MotorRAG, MotorSimpleLLM
from interfaces import MotorInferencia

from .config import ConfiguracionMotor, cargar_configuracion_motor


def _crear_motor_rag(_: ConfiguracionMotor) -> MotorInferencia:
    return MotorRAG()


def _crear_motor_simple_llm(config: ConfiguracionMotor) -> MotorInferencia:
    return MotorSimpleLLM(modelo=config.modelo_simple_llm)


def _crear_motor_fine_tuned(config: ConfiguracionMotor) -> MotorInferencia:
    return MotorFineTuned(modelo=config.modelo_fine_tuned)


FABRICA_MOTORES: dict[str, Callable[[ConfiguracionMotor], MotorInferencia]] = {
    "rag": _crear_motor_rag,
    "simple_llm": _crear_motor_simple_llm,
    "fine_tuned": _crear_motor_fine_tuned,
}


def obtener_tipos_motor_soportados() -> tuple[str, ...]:
    return tuple(sorted(FABRICA_MOTORES))


def crear_motor_activo(config: ConfiguracionMotor | None = None) -> MotorInferencia:
    config_activa = config or cargar_configuracion_motor()
    constructor = FABRICA_MOTORES.get(config_activa.tipo_motor)

    if constructor is None:
        tipos_validos = ", ".join(obtener_tipos_motor_soportados())
        raise ValueError(
            f"TIPO_MOTOR inválido: '{config_activa.tipo_motor}'. "
            f"Usa uno de: {tipos_validos}."
        )

    return constructor(config_activa)
