from fastapi import HTTPException, Request

from interfaces import MotorInferencia


def obtener_motor_activo(request: Request) -> MotorInferencia:
    motor_activo = getattr(request.app.state, "motor_activo", None)
    if motor_activo is None:
        raise HTTPException(status_code=500, detail="El motor de inferencia no está inicializado.")
    return motor_activo
