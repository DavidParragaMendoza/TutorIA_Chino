from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from interfaces import MotorInferencia

MODELO_FINE_TUNED = "tutoria-finetuned"

TEMPLATE_FINE_TUNED = """Eres TutorIA con ajuste fino para clases de chino mandarin.
Responde de forma breve, precisa y orientada a aprendizaje.
Cuando uses chino, agrega Hanzi y Pinyin.
Si hay historial, continúa desde ese punto y no reinicies la clase.

HISTORIAL PREVIO:
{historial}

PREGUNTA DEL ESTUDIANTE:
{pregunta}

RESPUESTA:"""


class MotorFineTuned(MotorInferencia):
    def __init__(self, modelo: str = MODELO_FINE_TUNED, temperature: float = 0.2) -> None:
        prompt = ChatPromptTemplate.from_template(TEMPLATE_FINE_TUNED)
        llm = ChatOllama(model=modelo, temperature=temperature)
        self._cadena = prompt | llm | StrOutputParser()

    def generar_respuesta(self, pregunta: str, historial: str = "") -> str:
        return self._cadena.invoke({"pregunta": pregunta, "historial": historial})
