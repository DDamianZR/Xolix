"""
Validadores para RFC, CURP y otros identificadores mexicanos.
"""
import re
from datetime import date


# ═══════════════════════════════════════════════════
# RFC — Registro Federal de Contribuyentes
# Formato: 4 letras + 6 dígitos (fecha) + 3 homoclave
# Ejemplo: GARC850101AB1
# ═══════════════════════════════════════════════════

RFC_PATTERN = re.compile(
    r'^[A-ZÑ&]{3,4}'      # 3 (moral) o 4 (física) letras
    r'\d{2}'               # Año (2 dígitos)
    r'(0[1-9]|1[0-2])'    # Mes (01-12)
    r'(0[1-9]|[12]\d|3[01])'  # Día (01-31)
    r'[A-Z\d]{3}$',       # Homoclave (3 caracteres alfanuméricos)
    re.IGNORECASE
)


def validar_rfc(rfc: str) -> tuple[bool, str]:
    """Valida estructura del RFC mexicano."""
    rfc = rfc.strip().upper()
    if len(rfc) < 12 or len(rfc) > 13:
        return False, "El RFC debe tener 12 o 13 caracteres"
    if not RFC_PATTERN.match(rfc):
        return False, "Formato de RFC inválido"
    return True, ""


# ═══════════════════════════════════════════════════
# CURP — Clave Única de Registro de Población
# 18 caracteres:
#   4 letras + 6 dígitos (fecha) + 1 (sexo) + 2 (estado)
#   + 3 consonantes + 1 (homoclave) + 1 (dígito verificador)
# ═══════════════════════════════════════════════════

ESTADOS_CURP = {
    'AS', 'BC', 'BS', 'CC', 'CL', 'CM', 'CS', 'CH', 'DF', 'DG',
    'GT', 'GR', 'HG', 'JC', 'MC', 'MN', 'MS', 'NT', 'NL', 'OC',
    'PL', 'QT', 'QR', 'SP', 'SL', 'SR', 'TC', 'TS', 'TL', 'VZ',
    'YN', 'ZS', 'NE',  # NE = Nacido en el Extranjero
}

CURP_PATTERN = re.compile(
    r'^[A-Z]{4}'           # 4 letras iniciales
    r'\d{2}'               # Año (2 dígitos)
    r'(0[1-9]|1[0-2])'    # Mes (01-12)
    r'(0[1-9]|[12]\d|3[01])'  # Día (01-31)
    r'[HM]'               # Sexo (H o M)
    r'[A-Z]{2}'           # Estado (2 letras)
    r'[B-DF-HJ-NP-TV-Z]{3}'  # 3 consonantes internas
    r'[A-Z\d]'            # Homoclave
    r'\d$',               # Dígito verificador
    re.IGNORECASE
)


def validar_curp(curp: str) -> tuple[bool, str]:
    """Valida estructura del CURP mexicano."""
    curp = curp.strip().upper()
    if len(curp) != 18:
        return False, "La CURP debe tener exactamente 18 caracteres"
    if not CURP_PATTERN.match(curp):
        return False, "Formato de CURP inválido"

    # Validar estado
    estado = curp[11:13]
    if estado not in ESTADOS_CURP:
        return False, f"Código de estado '{estado}' no válido en CURP"

    return True, ""


def validar_curp_fecha(curp: str, fecha_nacimiento: date) -> tuple[bool, str]:
    """Valida que la fecha de nacimiento en la CURP coincida con la proporcionada."""
    curp = curp.strip().upper()

    if len(curp) < 18:
        return False, "CURP demasiado corta para extraer fecha"

    # Extraer fecha de CURP (posiciones 4-9)
    anio_curp = int(curp[4:6])
    mes_curp = int(curp[6:8])
    dia_curp = int(curp[8:10])

    # El carácter 17 (índice 16) determina el siglo:
    # 0-9 para fechas de nacimiento hasta 1999
    # A-Z para fechas a partir del 2000
    if curp[16].isdigit():
        siglo = 1900
    else:
        siglo = 2000
    anio_completo = siglo + anio_curp

    if (
        fecha_nacimiento.year != anio_completo
        or fecha_nacimiento.month != mes_curp
        or fecha_nacimiento.day != dia_curp
    ):
        return False, "La fecha de nacimiento no coincide con la CURP"

    return True, ""


def validar_curp_sexo(curp: str, sexo: str) -> tuple[bool, str]:
    """Valida que el sexo en la CURP coincida con el proporcionado."""
    curp = curp.strip().upper()
    if len(curp) < 11:
        return False, "CURP demasiado corta para extraer sexo"

    sexo_curp = curp[10]  # H o M
    sexo_map = {'M': 'H', 'F': 'M'}  # M(asculino) -> H, F(emenino) -> M

    sexo_esperado = sexo_map.get(sexo.upper())
    if sexo_esperado and sexo_curp != sexo_esperado:
        return False, "El sexo no coincide con la CURP"

    return True, ""
