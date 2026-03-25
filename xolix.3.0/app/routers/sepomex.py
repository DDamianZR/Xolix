"""
Consulta de códigos postales de México.
Usa la API pública de SEPOMEX vía copomex.com o api-sepomex.
Fallback: usa la API gratuita de https://api.zippopotam.us/
"""
from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter(prefix="/api/sepomex", tags=["SEPOMEX"])


@router.get("/cp/{codigo_postal}")
async def buscar_codigo_postal(codigo_postal: str):
    """
    Busca información de dirección por código postal usando la API pública zippopotam.
    Retorna estado, municipio y colonias disponibles.
    """
    if not codigo_postal.isdigit() or len(codigo_postal) != 5:
        raise HTTPException(status_code=400, detail="El código postal debe tener 5 dígitos")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"https://api.zippopotam.us/MX/{codigo_postal}")

        if res.status_code == 404:
            raise HTTPException(status_code=404, detail="Código postal no encontrado")

        if res.status_code != 200:
            raise HTTPException(status_code=502, detail="Error al consultar servicio de códigos postales")

        data = res.json()

        places = data.get("places", [])
        if not places:
            raise HTTPException(status_code=404, detail="No se encontraron datos para este código postal")

        estado = places[0].get("state", "")
        municipio = places[0].get("place name", "")
        colonias = [p.get("place name", "") for p in places]

        return {
            "codigo_postal": codigo_postal,
            "estado": estado,
            "municipio": municipio,
            "colonias": colonias,
        }

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout al consultar servicio de códigos postales")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Error de conexión con servicio de códigos postales")
