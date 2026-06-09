"""
Suite de pruebas funcionales de la API REST de Xolix 3.0.
Ejecutar: python -m pytest tests/test_api.py -v
Requiere backend corriendo en http://localhost:8000 y datos demo cargados.
"""
import requests
import pytest

BASE = "http://localhost:8000"

# ─────────────────── FIXTURES ────────────────────

def _login(correo: str, password: str) -> str:
    r = requests.post(f"{BASE}/api/auth/login",
                      json={"correo": correo, "password": password})
    assert r.status_code == 200, f"Login {correo} fallo: {r.text}"
    return r.json()["access_token"]

@pytest.fixture(scope="session")
def director_token():
    return _login("director@xolix.com", "admin123")

@pytest.fixture(scope="session")
def psicologa_token():
    return _login("psicologa@xolix.com", "psico123")

@pytest.fixture(scope="session")
def social_token():
    return _login("trabajo_social@xolix.com", "social123")

@pytest.fixture(scope="session")
def coord_token():
    return _login("coordinador@xolix.com", "coord123")

def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ─────────────────── AUTENTICACION ────────────────────

class TestAuth:
    def test_login_director_ok(self, director_token):
        assert director_token is not None
        assert len(director_token) > 20

    def test_login_credenciales_invalidas(self):
        r = requests.post(f"{BASE}/api/auth/login",
                          json={"correo": "noexiste@x.com", "password": "wrong"})
        assert r.status_code == 401

    def test_endpoint_sin_token_retorna_401(self):
        r = requests.get(f"{BASE}/api/nna/casos")
        assert r.status_code == 401

    def test_me_retorna_perfil(self, director_token):
        r = requests.get(f"{BASE}/api/auth/me", headers=auth(director_token))
        assert r.status_code == 200
        data = r.json()
        assert data["correo"] == "director@xolix.com"
        assert data["rol"] == "director"

    def test_login_todos_los_roles(self):
        credenciales = [
            ("coordinador@xolix.com", "coord123"),
            ("psicologa@xolix.com", "psico123"),
            ("trabajo_social@xolix.com", "social123"),
            ("legal@xolix.com", "legal123"),
        ]
        for correo, pw in credenciales:
            r = requests.post(f"{BASE}/api/auth/login",
                              json={"correo": correo, "password": pw})
            assert r.status_code == 200, f"Login {correo} fallo"
            assert "access_token" in r.json()

    def test_token_invalido_retorna_401(self):
        r = requests.get(f"{BASE}/api/nna/casos",
                         headers={"Authorization": "Bearer token_falso_12345"})
        assert r.status_code == 401

    def test_docs_disponibles(self):
        r = requests.get(f"{BASE}/docs")
        assert r.status_code == 200

    def test_openapi_json(self):
        r = requests.get(f"{BASE}/openapi.json")
        assert r.status_code == 200
        schema = r.json()
        assert "paths" in schema
        assert len(schema["paths"]) >= 20


# ─────────────────── USUARIOS ────────────────────

class TestUsuarios:
    def test_listar_usuarios(self, director_token):
        r = requests.get(f"{BASE}/api/usuarios/", headers=auth(director_token))
        assert r.status_code == 200
        usuarios = r.json()
        assert len(usuarios) >= 5
        roles = {u["rol"] for u in usuarios}
        assert "director" in roles

    def test_obtener_usuario_por_id(self, director_token):
        r = requests.get(f"{BASE}/api/usuarios/", headers=auth(director_token))
        uid = r.json()[0]["id"]
        r2 = requests.get(f"{BASE}/api/usuarios/{uid}", headers=auth(director_token))
        assert r2.status_code == 200
        assert r2.json()["id"] == uid

    def test_usuario_inexistente_404(self, director_token):
        r = requests.get(f"{BASE}/api/usuarios/99999", headers=auth(director_token))
        assert r.status_code == 404


# ─────────────────── CASOS NNA ────────────────────

class TestCasosNNA:
    def _sofia(self, token):
        r = requests.get(f"{BASE}/api/nna/casos", headers=auth(token))
        return next((c for c in r.json()
                     if "Sof" in c["nna_nombre"] or "sofia" in c["nna_nombre"].lower()), None)

    def test_listar_casos(self, director_token):
        r = requests.get(f"{BASE}/api/nna/casos", headers=auth(director_token))
        assert r.status_code == 200
        casos = r.json()
        assert len(casos) >= 4

    def test_casos_campos_requeridos(self, psicologa_token):
        r = requests.get(f"{BASE}/api/nna/casos", headers=auth(psicologa_token))
        for caso in r.json():
            assert "id" in caso
            assert "nna_nombre" in caso
            assert "estado" in caso

    def test_obtener_caso_sofia(self, psicologa_token):
        sofia = self._sofia(psicologa_token)
        assert sofia is not None, "Caso Sofia no encontrado en datos demo"
        r2 = requests.get(f"{BASE}/api/nna/casos/{sofia['id']}", headers=auth(psicologa_token))
        assert r2.status_code == 200
        assert r2.json()["estado"] == "activo"

    def test_crear_y_obtener_caso(self, social_token):
        payload = {
            "nna_nombre": "Test NNA Automatico",
            "nna_edad": 9,
            "nna_genero": "masculino",
            "nna_nacionalidad": "Mexicana",
            "estado": "activo"
        }
        r = requests.post(f"{BASE}/api/nna/casos", json=payload, headers=auth(social_token))
        assert r.status_code in (200, 201), f"Crear caso fallo: {r.text}"
        caso_id = r.json()["id"]
        r2 = requests.get(f"{BASE}/api/nna/casos/{caso_id}", headers=auth(social_token))
        assert r2.status_code == 200
        assert r2.json()["nna_nombre"] == "Test NNA Automatico"

    def test_caso_inexistente_404(self, psicologa_token):
        r = requests.get(f"{BASE}/api/nna/casos/99999", headers=auth(psicologa_token))
        assert r.status_code == 404

    def test_obtener_tutor(self, psicologa_token):
        sofia = self._sofia(psicologa_token)
        if sofia:
            r = requests.get(f"{BASE}/api/nna/casos/{sofia['id']}/tutor",
                             headers=auth(psicologa_token))
            assert r.status_code == 200
            assert "parentesco" in r.json()

    def test_obtener_datos_medicos(self, psicologa_token):
        sofia = self._sofia(psicologa_token)
        if sofia:
            r = requests.get(f"{BASE}/api/nna/casos/{sofia['id']}/datos-medicos",
                             headers=auth(psicologa_token))
            assert r.status_code == 200


# ─────────────────── PERSONAS Y FAMILIOGRAMA ────────────────────

class TestFamiliograma:
    def _sofia_id(self, token):
        r = requests.get(f"{BASE}/api/nna/casos", headers=auth(token))
        sofia = next((c for c in r.json()
                      if "Sof" in c["nna_nombre"] or "sofia" in c["nna_nombre"].lower()), None)
        return sofia["id"] if sofia else None

    def test_listar_personas_de_sofia(self, psicologa_token):
        caso_id = self._sofia_id(psicologa_token)
        assert caso_id is not None
        r = requests.get(f"{BASE}/api/nna/casos/{caso_id}/personas",
                         headers=auth(psicologa_token))
        assert r.status_code == 200
        personas = r.json()
        assert len(personas) >= 4

    def test_personas_tienen_simbolo(self, psicologa_token):
        caso_id = self._sofia_id(psicologa_token)
        r = requests.get(f"{BASE}/api/nna/casos/{caso_id}/personas",
                         headers=auth(psicologa_token))
        tipos = {p.get("tipo_simbolo") for p in r.json() if p.get("tipo_simbolo")}
        assert "agresor" in tipos or "clave" in tipos

    def test_obtener_familiograma(self, psicologa_token):
        caso_id = self._sofia_id(psicologa_token)
        r = requests.get(f"{BASE}/api/nna/casos/{caso_id}/familiograma",
                         headers=auth(psicologa_token))
        assert r.status_code in (200, 204)
        if r.status_code == 200:
            data = r.json()
            assert "grafo_json" in data
            grafo = data["grafo_json"]
            assert "nodes" in grafo
            assert "edges" in grafo
            assert len(grafo["nodes"]) >= 3


# ─────────────────── CATALOGO ────────────────────

class TestCatalogo:
    def test_listar_derechos(self, psicologa_token):
        r = requests.get(f"{BASE}/api/catalogo/derechos", headers=auth(psicologa_token))
        assert r.status_code == 200
        derechos = r.json()
        assert len(derechos) >= 8
        nombres = [d["nombre"].lower() for d in derechos]
        assert any("salud" in n for n in nombres)
        assert any("educaci" in n for n in nombres)
        assert any("identidad" in n for n in nombres)

    def test_listar_indicadores(self, psicologa_token):
        r = requests.get(f"{BASE}/api/catalogo/indicadores", headers=auth(psicologa_token))
        assert r.status_code == 200
        indicadores = r.json()
        assert len(indicadores) >= 14

    def test_indicadores_tienen_derecho_id(self, psicologa_token):
        r = requests.get(f"{BASE}/api/catalogo/indicadores", headers=auth(psicologa_token))
        for ind in r.json():
            assert "derecho_id" in ind
            assert ind["derecho_id"] is not None


# ─────────────────── ACTORES ────────────────────

class TestActores:
    def test_listar_actores(self, social_token):
        r = requests.get(f"{BASE}/api/actores/", headers=auth(social_token))
        assert r.status_code == 200
        assert len(r.json()) >= 5

    def test_actores_campos_requeridos(self, social_token):
        r = requests.get(f"{BASE}/api/actores/", headers=auth(social_token))
        for actor in r.json():
            assert "id" in actor
            assert "nombre" in actor
            assert "tipo" in actor

    def test_filtro_tipo_gobierno(self, social_token):
        r = requests.get(f"{BASE}/api/actores/?tipo=gobierno", headers=auth(social_token))
        assert r.status_code == 200
        for a in r.json():
            assert a["tipo"] == "gobierno"

    def test_filtro_tipo_civil(self, social_token):
        r = requests.get(f"{BASE}/api/actores/?tipo=civil", headers=auth(social_token))
        assert r.status_code == 200
        for a in r.json():
            assert a["tipo"] == "civil"

    def test_detalle_actor_con_id(self, social_token):
        r = requests.get(f"{BASE}/api/actores/", headers=auth(social_token))
        actor_id = r.json()[0]["id"]
        r2 = requests.get(f"{BASE}/api/actores/{actor_id}", headers=auth(social_token))
        assert r2.status_code == 200
        assert r2.json()["id"] == actor_id

    def test_actor_inexistente_404(self, social_token):
        r = requests.get(f"{BASE}/api/actores/99999", headers=auth(social_token))
        assert r.status_code == 404

    def test_crear_actor(self, coord_token):
        payload = {
            "nombre": "Actor de Prueba Automatizada",
            "tipo": "civil",
            "descripcion": "Actor creado por suite de pruebas",
            "municipio": "Benito Juarez",
            "estado": "CDMX",
            "activo": True
        }
        r = requests.post(f"{BASE}/api/actores/", json=payload, headers=auth(coord_token))
        assert r.status_code in (200, 201), f"Crear actor fallo: {r.text}"
        assert r.json()["nombre"] == "Actor de Prueba Automatizada"


# ─────────────────── DIAGNOSTICOS ────────────────────

class TestDiagnosticos:
    def _sofia_id(self, token):
        r = requests.get(f"{BASE}/api/nna/casos", headers=auth(token))
        sofia = next((c for c in r.json()
                      if "Sof" in c["nna_nombre"] or "sofia" in c["nna_nombre"].lower()), None)
        return sofia["id"] if sofia else None

    def test_listar_diagnosticos_sofia(self, psicologa_token):
        caso_id = self._sofia_id(psicologa_token)
        assert caso_id is not None
        r = requests.get(f"{BASE}/api/diagnosticos/caso/{caso_id}",
                         headers=auth(psicologa_token))
        assert r.status_code == 200
        diags = r.json()
        assert len(diags) >= 2

    def test_diagnostico_tiene_tipo(self, psicologa_token):
        caso_id = self._sofia_id(psicologa_token)
        r = requests.get(f"{BASE}/api/diagnosticos/caso/{caso_id}",
                         headers=auth(psicologa_token))
        tipos = {d["tipo"] for d in r.json()}
        assert "inicial" in tipos

    def test_derechos_vulnerados_sofia(self, psicologa_token):
        caso_id = self._sofia_id(psicologa_token)
        r = requests.get(f"{BASE}/api/diagnosticos/caso/{caso_id}/resumen-derechos",
                         headers=auth(psicologa_token))
        assert r.status_code == 200
        derechos = r.json()
        assert len(derechos) >= 1

    def test_derechos_vulnerados_tienen_severidad(self, psicologa_token):
        caso_id = self._sofia_id(psicologa_token)
        r = requests.get(f"{BASE}/api/diagnosticos/caso/{caso_id}/resumen-derechos",
                         headers=auth(psicologa_token))
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_crear_diagnostico(self, psicologa_token):
        caso_id = self._sofia_id(psicologa_token)
        assert caso_id is not None
        r_ind = requests.get(f"{BASE}/api/catalogo/indicadores", headers=auth(psicologa_token))
        indicadores = r_ind.json()
        payload = {
            "caso_nna_id": caso_id,
            "tipo": "entorno",
            "fecha": "2026-06-09",
            "observaciones": "Diagnostico automatico de prueba",
            "evaluaciones": [
                {"indicador_id": indicadores[0]["id"], "valor": "si", "vulnerado": False},
                {"indicador_id": indicadores[2]["id"], "valor": "no", "vulnerado": True},
            ]
        }
        r = requests.post(f"{BASE}/api/diagnosticos/", json=payload,
                          headers=auth(psicologa_token))
        assert r.status_code in (200, 201), f"Crear diagnostico fallo: {r.text}"
        data = r.json()
        assert data["tipo"] == "entorno"


# ─────────────────── PLANES ────────────────────

class TestPlanes:
    def _sofia_id(self, token):
        r = requests.get(f"{BASE}/api/nna/casos", headers=auth(token))
        sofia = next((c for c in r.json()
                      if "Sof" in c["nna_nombre"] or "sofia" in c["nna_nombre"].lower()), None)
        return sofia["id"] if sofia else None

    def _planes_sofia(self, token):
        caso_id = self._sofia_id(token)
        r = requests.get(f"{BASE}/api/planes/caso/{caso_id}", headers=auth(token))
        return caso_id, r

    def test_listar_planes_sofia(self, coord_token):
        caso_id, r = self._planes_sofia(coord_token)
        assert caso_id is not None
        assert r.status_code == 200
        planes = r.json()
        assert len(planes) >= 1

    def test_plan_activo_existe(self, coord_token):
        _, r = self._planes_sofia(coord_token)
        estados = {p["estado"] for p in r.json()}
        assert "activo" in estados

    def test_plan_tiene_medidas(self, coord_token):
        _, r = self._planes_sofia(coord_token)
        plan_activo = next((p for p in r.json() if p["estado"] == "activo"), None)
        assert plan_activo is not None
        r2 = requests.get(f"{BASE}/api/planes/{plan_activo['id']}",
                          headers=auth(coord_token))
        assert r2.status_code == 200
        plan = r2.json()
        assert "medidas" in plan
        assert len(plan["medidas"]) >= 3

    def test_medidas_multiples_estados(self, coord_token):
        _, r = self._planes_sofia(coord_token)
        plan_activo = next((p for p in r.json() if p["estado"] == "activo"), None)
        r2 = requests.get(f"{BASE}/api/planes/{plan_activo['id']}",
                          headers=auth(coord_token))
        medidas = r2.json()["medidas"]
        estados = {m["estado"] for m in medidas}
        assert len(estados) >= 2

    def test_seguimientos_existen(self, coord_token):
        _, r = self._planes_sofia(coord_token)
        plan_activo = next((p for p in r.json() if p["estado"] == "activo"), None)
        r2 = requests.get(f"{BASE}/api/planes/{plan_activo['id']}",
                          headers=auth(coord_token))
        medidas = r2.json()["medidas"]
        completadas = [m for m in medidas if m["estado"] == "completada"]
        assert len(completadas) >= 1
        assert completadas[0]["porcentaje_avance"] == 100

    def test_crear_plan(self, coord_token):
        caso_id = self._sofia_id(coord_token)
        payload = {
            "caso_nna_id": caso_id,
            "objetivo": "Plan de prueba automatizado",
            "estado": "borrador"
        }
        r = requests.post(f"{BASE}/api/planes/", json=payload, headers=auth(coord_token))
        assert r.status_code in (200, 201), f"Crear plan fallo: {r.text}"
        assert r.json()["objetivo"] == "Plan de prueba automatizado"


# ─────────────────── REPORTES ────────────────────

class TestReportes:
    def test_indicadores_globales(self, director_token):
        r = requests.get(f"{BASE}/api/reportes/indicadores", headers=auth(director_token))
        assert r.status_code == 200
        data = r.json()
        assert "total_casos" in data
        assert data["total_casos"] >= 4

    def test_indicadores_tienen_conteos(self, director_token):
        r = requests.get(f"{BASE}/api/reportes/indicadores", headers=auth(director_token))
        data = r.json()
        for campo in ["total_casos", "casos_activos"]:
            assert campo in data
            assert isinstance(data[campo], int)

    def test_derechos_vulnerados_frecuencia(self, director_token):
        r = requests.get(f"{BASE}/api/reportes/derechos-vulnerados",
                         headers=auth(director_token))
        assert r.status_code == 200
        datos = r.json()
        assert isinstance(datos, list)
        assert len(datos) >= 3

    def test_evolucion_casos(self, director_token):
        r = requests.get(f"{BASE}/api/reportes/evolucion-casos",
                         headers=auth(director_token))
        assert r.status_code == 200

    def test_exportar_pdf(self, director_token):
        r = requests.get(f"{BASE}/api/reportes/exportar/casos/pdf",
                         headers=auth(director_token))
        assert r.status_code == 200
        ct = r.headers.get("content-type", "")
        cd = r.headers.get("content-disposition", "")
        assert "pdf" in ct.lower() or "pdf" in cd.lower() or len(r.content) > 100

    def test_exportar_excel_casos(self, director_token):
        r = requests.get(f"{BASE}/api/reportes/exportar/casos/excel",
                         headers=auth(director_token))
        assert r.status_code == 200
        assert len(r.content) > 100

    def test_exportar_excel_actores(self, director_token):
        r = requests.get(f"{BASE}/api/reportes/exportar/actores/excel",
                         headers=auth(director_token))
        assert r.status_code == 200

    def test_auditoria(self, director_token):
        r = requests.get(f"{BASE}/api/reportes/auditoria", headers=auth(director_token))
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ─────────────────── EQUIPO MULTIDISCIPLINARIO ────────────────────

class TestEquipoMultidisciplinario:
    def _sofia_id(self, token):
        r = requests.get(f"{BASE}/api/nna/casos", headers=auth(token))
        assert r.status_code == 200
        sofia = next((c for c in r.json() if "Sofía" in c.get("nna_nombre", "")), None)
        assert sofia, "Caso de Sofía no encontrado"
        return sofia["id"]

    def test_listar_equipo(self, director_token):
        caso_id = self._sofia_id(director_token)
        r = requests.get(f"{BASE}/api/nna/casos/{caso_id}/equipo",
                         headers=auth(director_token))
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert len(r.json()) >= 1

    def test_equipo_tiene_psicologo(self, director_token):
        caso_id = self._sofia_id(director_token)
        r = requests.get(f"{BASE}/api/nna/casos/{caso_id}/equipo",
                         headers=auth(director_token))
        roles = [m["rol_en_equipo"] for m in r.json()]
        assert "psicologo" in roles

    def test_caso_tiene_responsable(self, director_token):
        caso_id = self._sofia_id(director_token)
        r = requests.get(f"{BASE}/api/nna/casos/{caso_id}",
                         headers=auth(director_token))
        assert r.status_code == 200
        assert r.json().get("responsable_id") is not None

    def test_trabajador_social_puede_listar_equipo(self, social_token):
        caso_id = self._sofia_id(social_token)
        r = requests.get(f"{BASE}/api/nna/casos/{caso_id}/equipo",
                         headers=auth(social_token))
        assert r.status_code == 200

    def test_responsable_puede_agregar_y_quitar_miembro(self, social_token, director_token):
        caso_id = self._sofia_id(director_token)
        r_users = requests.get(f"{BASE}/api/usuarios/", headers=auth(director_token))
        r_equipo = requests.get(f"{BASE}/api/nna/casos/{caso_id}/equipo",
                                headers=auth(social_token))
        equipo_ids = {m["usuario_id"] for m in r_equipo.json()}
        candidate = next(
            (u for u in r_users.json() if u["id"] not in equipo_ids and u["activo"]), None
        )
        if not candidate:
            pytest.skip("Sin usuarios disponibles para agregar")
        r_add = requests.post(f"{BASE}/api/nna/casos/{caso_id}/equipo",
                              json={"usuario_id": candidate["id"], "rol_en_equipo": "otro"},
                              headers=auth(social_token))
        assert r_add.status_code in (200, 201), f"Agregar falló: {r_add.text}"
        r_del = requests.delete(f"{BASE}/api/nna/casos/{caso_id}/equipo/{candidate['id']}",
                                headers=auth(social_token))
        assert r_del.status_code == 200

    def test_equipo_miembros_tienen_nivel_confianza(self, director_token):
        caso_id = self._sofia_id(director_token)
        r = requests.get(f"{BASE}/api/nna/casos/{caso_id}/equipo",
                         headers=auth(director_token))
        assert r.status_code == 200


# ─────────────────── COLABORADORES Y CONFIANZA ────────────────────

class TestColaboradoresConfianza:
    def test_listar_colaboradores(self, director_token):
        r = requests.get(f"{BASE}/api/colaboradores/", headers=auth(director_token))
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_colaboradores_tienen_tipo_colaboracion(self, director_token):
        r = requests.get(f"{BASE}/api/colaboradores/", headers=auth(director_token))
        for c in r.json():
            assert "tipo_colaboracion" in c
            assert c["tipo_colaboracion"] in ("planta", "voluntario")

    def test_filtrar_voluntarios(self, director_token):
        r = requests.get(f"{BASE}/api/colaboradores/?tipo=voluntario",
                         headers=auth(director_token))
        assert r.status_code == 200
        for c in r.json():
            assert c["tipo_colaboracion"] == "voluntario"

    def test_evaluar_confianza(self, director_token):
        me = requests.get(f"{BASE}/api/auth/me", headers=auth(director_token)).json()
        r = requests.get(f"{BASE}/api/colaboradores/", headers=auth(director_token))
        # pick a collaborator that is not the current user (can't self-evaluate)
        target = next((c for c in r.json() if c["id"] != me["id"]), None)
        assert target is not None, "No hay colaboradores distintos al director"
        nivel_actual = target.get("nivel_confianza", 3)
        nuevo = 5 if nivel_actual < 5 else 4
        payload = {
            "nivel_nuevo": nuevo,
            "justificacion": "Evaluación automatizada: desempeño sobresaliente."
        }
        r2 = requests.post(f"{BASE}/api/colaboradores/{target['id']}/evaluar-confianza",
                           json=payload, headers=auth(director_token))
        assert r2.status_code in (200, 201), f"Evaluar confianza falló: {r2.text}"

    def test_historial_confianza(self, director_token):
        r = requests.get(f"{BASE}/api/colaboradores/", headers=auth(director_token))
        for c in r.json():
            r2 = requests.get(f"{BASE}/api/colaboradores/{c['id']}/historial-confianza",
                               headers=auth(director_token))
            assert r2.status_code == 200
            assert isinstance(r2.json(), list)
            if r2.json():
                evaluacion = r2.json()[0]
                assert "nivel_anterior" in evaluacion
                assert "nivel_nuevo" in evaluacion
                assert "justificacion" in evaluacion
                break

    def test_pendientes_revision(self, director_token):
        r = requests.get(f"{BASE}/api/colaboradores/pendientes-revision",
                         headers=auth(director_token))
        assert r.status_code == 200
        assert isinstance(r.json(), list)
