from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import os

from app.dependencies import get_db, get_current_user
from app.services import expediente_service

router = APIRouter(prefix="/api/expedientes", tags=["Expedientes"])


@router.post("/")
def subir_expediente(
    nombre: str = Form(...),
    descripcion: Optional[str] = Form(None),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id")
    exp = expediente_service.crear_expediente(db, nombre, descripcion, archivo, user_id)
    return {"mensaje": "Expediente subido correctamente", "id": exp.id}


@router.get("/propios")
def listar_propios(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id")
    expedientes = expediente_service.obtener_expedientes_propios(db, user_id)
    return [
        {
            "id": e.id,
            "nombre": e.nombre,
            "descripcion": e.descripcion,
            "tipo_archivo": e.tipo_archivo,
            "fecha_creacion": e.fecha_creacion,
        }
        for e in expedientes
    ]


@router.get("/compartidos")
def listar_compartidos(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id")
    return [
        {
            "id": item["expediente"].id,
            "nombre": item["expediente"].nombre,
            "descripcion": item["expediente"].descripcion,
            "tipo_archivo": item["expediente"].tipo_archivo,
            "permiso": item["permiso"],
            "fecha_creacion": item["expediente"].fecha_creacion,
        }
        for item in expediente_service.obtener_expedientes_compartidos(db, user_id)
    ]


@router.get("/{expediente_id}/descargar")
def descargar_expediente(
    expediente_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    exp = expediente_service.obtener_expediente(db, expediente_id)
    if not exp:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    if not os.path.exists(exp.archivo_path):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el servidor")
    return FileResponse(exp.archivo_path, filename=f"{exp.nombre}.{exp.tipo_archivo}")


@router.post("/{expediente_id}/compartir")
def compartir(
    expediente_id: int,
    correo_destino: str = Form(...),
    permiso: str = Form("lectura"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id")
    expediente_service.compartir_expediente(db, expediente_id, correo_destino, permiso, user_id)
    return {"mensaje": "Expediente compartido correctamente"}


@router.delete("/{expediente_id}")
def eliminar(
    expediente_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id")
    expediente_service.eliminar_expediente(db, expediente_id, user_id)
    return {"mensaje": "Expediente eliminado correctamente"}
