from typing import Literal

from pydantic import BaseModel, Field


class HistorialMensaje(BaseModel):
    rol: Literal["usuario", "asistente"]
    contenido: str


class ChatRequest(BaseModel):
    pregunta: str
    historial: list[HistorialMensaje] = Field(default_factory=list)


class ChatResponse(BaseModel):
    respuesta: str
