from abc import ABC, abstractmethod


class MotorInferencia(ABC):
    @abstractmethod
    def generar_respuesta(self, pregunta: str, historial: str = "") -> str:
        """Genera una respuesta usando la pregunta actual y el historial previo."""
