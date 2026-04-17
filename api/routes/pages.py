from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["pages"])

RUTA_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_PAGINAS = (RUTA_PROYECTO / "frontend" / "pages").resolve()
RUTA_TEMAS = (RUTA_PAGINAS / "temas").resolve()


def _resolver_archivo(base: Path, relativa: str) -> Path:
    candidato = (base / relativa).resolve()
    try:
        candidato.relative_to(base)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Página no encontrada.") from exc

    if not candidato.is_file():
        raise HTTPException(status_code=404, detail="Página no encontrada.")
    return candidato


def _normalizar_subruta(tema_path: str) -> str:
    partes = [segmento for segmento in tema_path.split("/") if segmento]
    if not partes:
        raise HTTPException(status_code=404, detail="Tema no encontrado.")
    return "/".join(partes)


@router.get("/", include_in_schema=False)
async def pagina_inicio():
    return FileResponse(_resolver_archivo(RUTA_PAGINAS, "index.html"))


@router.get("/index.html", include_in_schema=False)
async def compat_inicio_html():
    return RedirectResponse(url="/", status_code=307)


@router.get("/temas", include_in_schema=False)
@router.get("/temas/", include_in_schema=False)
async def pagina_temas():
    return FileResponse(_resolver_archivo(RUTA_PAGINAS, "temas/index.html"))


@router.get("/temas.html", include_in_schema=False)
async def compat_temas_html():
    return RedirectResponse(url="/temas", status_code=307)


@router.get("/temas/{tema_path:path}/chat", include_in_schema=False)
async def pagina_chat_tema(tema_path: str):
    subruta = _normalizar_subruta(tema_path)
    return FileResponse(_resolver_archivo(RUTA_TEMAS, f"{subruta}/chat.html"))


@router.get("/chat.html", include_in_schema=False)
async def compat_chat_html():
    return RedirectResponse(url="/temas/saludos/chat", status_code=307)


@router.get("/temas/{tema_path:path}", include_in_schema=False)
async def pagina_tema(tema_path: str):
    subruta = _normalizar_subruta(tema_path)
    return FileResponse(_resolver_archivo(RUTA_TEMAS, f"{subruta}/index.html"))


@router.get("/saludos.html", include_in_schema=False)
async def compat_saludos_html():
    return RedirectResponse(url="/temas/saludos", status_code=307)
