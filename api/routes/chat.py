from fastapi import APIRouter, Depends

from api.dependencies import obtener_motor_activo
from api.schemas import ChatRequest, ChatResponse
from interfaces import MotorInferencia

router = APIRouter(tags=["chat"])


def _formatear_historial_chat(payload: ChatRequest) -> str:
    lineas: list[str] = []

    for mensaje in payload.historial:
        contenido = mensaje.contenido.strip()
        if not contenido:
            continue

        rol = "Estudiante" if mensaje.rol == "usuario" else "Tutor"
        lineas.append(f"{rol}: {contenido}")

    return "\n".join(lineas)


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    payload: ChatRequest,
    motor_activo: MotorInferencia = Depends(obtener_motor_activo),
):
    historial_formateado = _formatear_historial_chat(payload)
    respuesta = motor_activo.generar_respuesta(
        payload.pregunta,
        historial=historial_formateado,
    )
    return ChatResponse(respuesta=respuesta)
