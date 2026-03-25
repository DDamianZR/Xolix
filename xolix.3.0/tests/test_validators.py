"""
Tests para los validadores de identificaciones mexicanas.
"""
import pytest
from datetime import date

from app.validators.mexican_ids import (
    validar_rfc,
    validar_curp,
    validar_curp_fecha,
    validar_curp_sexo,
)


class TestRFC:
    def test_rfc_valid_persona_fisica(self):
        ok, _ = validar_rfc("GARC850101AB1")
        assert ok

    def test_rfc_valid_persona_moral(self):
        ok, _ = validar_rfc("GAR850101AB1")
        assert ok

    def test_rfc_too_short(self):
        ok, msg = validar_rfc("GARC85")
        assert not ok
        assert "12 o 13" in msg

    def test_rfc_invalid_format(self):
        ok, msg = validar_rfc("1234567890123")
        assert not ok


class TestCURP:
    def test_curp_valid(self):
        ok, _ = validar_curp("GARC850101HDFRRL09")
        assert ok

    def test_curp_too_short(self):
        ok, msg = validar_curp("GARC8501")
        assert not ok
        assert "18 caracteres" in msg

    def test_curp_invalid_state(self):
        ok, msg = validar_curp("GARC850101HXXRRL09")
        assert not ok
        assert "estado" in msg.lower()

    def test_curp_invalid_format(self):
        ok, msg = validar_curp("123456789012345678")
        assert not ok


class TestCURPFecha:
    def test_fecha_matches(self):
        ok, _ = validar_curp_fecha("GARC850101HDFRRL09", date(1985, 1, 1))
        assert ok

    def test_fecha_mismatch(self):
        ok, msg = validar_curp_fecha("GARC850101HDFRRL09", date(1990, 5, 15))
        assert not ok
        assert "fecha" in msg.lower()


class TestCURPSexo:
    def test_sexo_hombre_matches(self):
        ok, _ = validar_curp_sexo("GARC850101HDFRRL09", "M")
        assert ok

    def test_sexo_mujer_matches(self):
        ok, _ = validar_curp_sexo("GARC850101MDFRRL09", "F")
        assert ok

    def test_sexo_mismatch(self):
        ok, msg = validar_curp_sexo("GARC850101HDFRRL09", "F")
        assert not ok
        assert "sexo" in msg.lower()
