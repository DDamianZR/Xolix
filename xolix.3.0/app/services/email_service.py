import jwt
from datetime import datetime, timedelta, timezone
import os

SECRET_KEY = os.getenv("SECRET_KEY", "b3af140b99147517c5bde8b625cf0c9a")
ALGORITHM = "HS256"

def generar_token_verificacion(correo: str) -> str:
    """Genera un JWT que expira en 24 horas para verificar el correo."""
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": correo,
        "exp": expire,
        "tipo": "verificacion_email"
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def enviar_correo_verificacion(correo: str, nombre_completo: str) -> None:
    """
    Simula el envío de un correo electrónico con un enlace de verificación único.
    En el futuro, esto se puede reemplazar con smtplib, aiosmtplib, o un API de correos (ej. SendGrid).
    """
    token = generar_token_verificacion(correo)
    enlace = f"http://localhost:5173/verificar?token={token}"
    
    print("\n" + "="*60)
    print("✉️ SIMULADOR DE ENVÍO DE CORREO ✉️")
    print("="*60)
    print(f"Para: {nombre_completo} <{correo}>")
    print("Asunto: Verificación de Cuenta en Xolix 3.0\n")
    print("Hola, gracias por registrarte en el sistema.")
    print("Por favor haz click en el siguiente enlace para activar tu cuenta:")
    print(f"\n👉 {enlace}\n")
    print("="*60 + "\n")
