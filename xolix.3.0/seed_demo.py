"""
Script de datos demo para Xolix.
Crea usuarios, casos NNA completos, actores, diagnósticos, planes y seguimientos.
Ejecutar: python seed_demo.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date, timedelta, datetime
import bcrypt as _bcrypt
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.caso import Caso, HechoVictimal, CasoParticipante, NotaCaso
from app.models.nna import (
    CasoNNA, EntrevistaFamilia, PersonaFamiliar, Familiograma,
    RelacionFamiliar, ObservacionNoVerbal, TutorNNA, DatosMedicosNNA,
    GeneroNNA, EstadoCasoNNA, TipoSimboloFamiliar, TipoRelacionFamiliar
)
from app.models.catalogo import Derecho, Indicador, CategoriaDerecho
from app.models.actor import Actor, ResponsableActor, HorarioActor, ServicioActor, TipoActor, TipoServicio
from app.models.diagnostico import (
    Diagnostico, IndicadorDiagnostico, DerechoVulnerado,
    TipoDiagnostico, SeveridadVulneracion
)
from app.models.plan import (
    PlanRestitucion, MedidaRestitucion, SeguimientoMedida,
    EstadoPlan, EstadoMedida, TipoMedida
)
from app.models.proceso import Proceso, Subtarea
from app.models.expediente import Expediente
from app.models.extras import AuditLog, Comentario, Notificacion
from app.models.equipo import EquipoCaso, EvaluacionConfianza

def hash_pw(pw: str) -> str:
    return _bcrypt.hashpw(pw.encode(), _bcrypt.gensalt()).decode()


def seed(db: Session):
    print("🌱 Iniciando carga de datos demo...")

    # ─── LIMPIAR DATOS PREVIOS DE DEMO ─────────────────────────────
    print("  Limpiando datos previos...")
    for m in [SeguimientoMedida, MedidaRestitucion, PlanRestitucion,
              DerechoVulnerado, IndicadorDiagnostico, Diagnostico,
              ObservacionNoVerbal, RelacionFamiliar, Familiograma,
              DatosMedicosNNA, TutorNNA, PersonaFamiliar, EntrevistaFamilia,
              EvaluacionConfianza, EquipoCaso,
              CasoNNA, NotaCaso, CasoParticipante, HechoVictimal, Caso,
              ServicioActor, HorarioActor, ResponsableActor, Actor,
              Indicador, Derecho, AuditLog, User]:
        db.query(m).delete()
    db.commit()

    # ─── USUARIOS ───────────────────────────────────────────────────
    print("  Creando usuarios...")
    users_data = [
        dict(nombre="Ana Lucía", apellido_paterno="Ramírez", apellido_materno="Torres",
             rfc="RATA850315AAA", curp="RATA850315MDFMRN09", sexo="F",
             fecha_nacimiento=date(1985,3,15), edad=41,
             estado="CDMX", municipio="Cuauhtémoc", colonia="Centro",
             calle="Av. Juárez", numero="23", codigo_postal="06010",
             tipo_personal="empleado", rol="director",
             correo="director@xolix.com", password=hash_pw("admin123"), activo=True, verificado=True,
             tipo_colaboracion="planta", nivel_confianza=5, fecha_ingreso=date(2020,1,15)),
        dict(nombre="Carlos", apellido_paterno="Mendoza", apellido_materno="Vega",
             rfc="MEVC910720BBB", curp="MEVC910720HDFNGR05", sexo="M",
             fecha_nacimiento=date(1991,7,20), edad=34,
             estado="CDMX", municipio="Iztapalapa", colonia="San Miguel",
             calle="Calle 5", numero="10", codigo_postal="09000",
             tipo_personal="empleado", rol="coordinador",
             correo="coordinador@xolix.com", password=hash_pw("coord123"), activo=True, verificado=True,
             tipo_colaboracion="planta", nivel_confianza=4, fecha_ingreso=date(2021,3,1)),
        dict(nombre="María Fernanda", apellido_paterno="López", apellido_materno="Ruiz",
             rfc="LORM930501CCC", curp="LORM930501MDFPZR08", sexo="F",
             fecha_nacimiento=date(1993,5,1), edad=32,
             estado="CDMX", municipio="Gustavo A. Madero", colonia="Lindavista",
             calle="Norte 45", numero="6", codigo_postal="07300",
             tipo_personal="empleado", rol="psicologo",
             correo="psicologa@xolix.com", password=hash_pw("psico123"), activo=True, verificado=True,
             tipo_colaboracion="planta", nivel_confianza=4, fecha_ingreso=date(2022,6,1)),
        dict(nombre="Roberto", apellido_paterno="Sánchez", apellido_materno="Cruz",
             rfc="SACR880901DDD", curp="SACR880901HDFNRB06", sexo="M",
             fecha_nacimiento=date(1988,9,1), edad=37,
             estado="CDMX", municipio="Tlalpan", colonia="San Pedro",
             calle="Sur 12", numero="3", codigo_postal="14000",
             tipo_personal="empleado", rol="trabajador_social",
             correo="trabajo_social@xolix.com", password=hash_pw("social123"), activo=True, verificado=True,
             tipo_colaboracion="planta", nivel_confianza=5, fecha_ingreso=date(2021,9,1)),
        dict(nombre="Daniela", apellido_paterno="García", apellido_materno="Morales",
             rfc="GAMD951210EEE", curp="GAMD951210MDFRRN07", sexo="F",
             fecha_nacimiento=date(1995,12,10), edad=30,
             estado="CDMX", municipio="Coyoacán", colonia="Del Valle",
             calle="Av. Universidad", numero="100", codigo_postal="04100",
             tipo_personal="empleado", rol="legal",
             correo="legal@xolix.com", password=hash_pw("legal123"), activo=True, verificado=True,
             tipo_colaboracion="voluntario", nivel_confianza=3, fecha_ingreso=date(2023,2,1)),
    ]
    users = []
    for d in users_data:
        u = User(**d)
        db.add(u)
        users.append(u)
    db.flush()
    director, coord, psicologa, trabajador_social, abogada = users

    # ─── DERECHOS ───────────────────────────────────────────────────
    print("  Creando catálogo de derechos e indicadores...")
    derechos_data = [
        ("Derecho a la salud", "Acceso a servicios de salud física y mental", CategoriaDerecho.salud, "Art. 4 CPEUM"),
        ("Derecho a la educación", "Acceso y permanencia en el sistema educativo", CategoriaDerecho.educacion, "Art. 3 CPEUM"),
        ("Derecho a la identidad", "Registro civil, nombre y nacionalidad", CategoriaDerecho.identidad, "Art. 29 CDN"),
        ("Derecho a vivir en familia", "Entorno familiar seguro y afectuoso", CategoriaDerecho.familia, "Art. 9 CDN"),
        ("Protección contra la violencia", "Libre de abuso, negligencia y explotación", CategoriaDerecho.proteccion, "Art. 19 CDN"),
        ("Derecho a la alimentación", "Alimentación suficiente y nutritiva", CategoriaDerecho.alimentacion, "Art. 4 CPEUM"),
        ("Derecho a la vivienda", "Vivienda digna y segura", CategoriaDerecho.vivienda, "Art. 4 CPEUM"),
        ("Derecho a la participación", "Expresar opinión en asuntos propios", CategoriaDerecho.participacion, "Art. 12 CDN"),
    ]
    derechos = []
    for nombre, desc, cat, art in derechos_data:
        d = Derecho(nombre=nombre, descripcion=desc, categoria=cat, articulo_referencia=art)
        db.add(d); derechos.append(d)
    db.flush()
    d_salud, d_edu, d_identidad, d_familia, d_proteccion, d_alim, d_vivienda, d_part = derechos

    indicadores_data = [
        (d_salud, "Cuenta con cartilla de vacunación actualizada"),
        (d_salud, "Tiene acceso a atención médica regular"),
        (d_salud, "Presenta señales visibles de desnutrición"),
        (d_salud, "Recibe atención psicológica"),
        (d_edu, "Está inscrito en escuela actualmente"),
        (d_edu, "Asiste regularmente a clases"),
        (d_edu, "Tiene materiales escolares básicos"),
        (d_identidad, "Cuenta con acta de nacimiento"),
        (d_identidad, "Tiene CURP registrado"),
        (d_familia, "Vive con al menos un familiar responsable"),
        (d_familia, "El entorno familiar es seguro y estable"),
        (d_proteccion, "Ha sufrido maltrato físico"),
        (d_proteccion, "Ha sufrido maltrato psicológico"),
        (d_proteccion, "Ha sufrido abuso sexual"),
        (d_proteccion, "Hay presencia de agresor en el hogar"),
        (d_alim, "Recibe al menos 3 comidas al día"),
        (d_vivienda, "Tiene un lugar seguro donde dormir"),
        (d_part, "Se le permite expresar su opinión"),
    ]
    indicadores = []
    for der, nombre in indicadores_data:
        ind = Indicador(derecho_id=der.id, nombre=nombre, tipo_evaluacion="si_no")
        db.add(ind); indicadores.append(ind)
    db.flush()

    # ─── ACTORES ────────────────────────────────────────────────────
    print("  Creando actores y servicios...")
    actores_def = [
        dict(nombre="DIF Ciudad de México", tipo=TipoActor.gobierno,
             descripcion="Sistema para el Desarrollo Integral de la Familia del CDMX. Brinda apoyo social, psicológico y legal a familias en situación vulnerable.",
             direccion="Av. Insurgentes Sur 1480, Barrio San Lucas", municipio="Xochimilco", estado="CDMX",
             telefono="55-1234-5678", correo="atencion@dif.cdmx.gob.mx", sitio_web="www.dif.cdmx.gob.mx"),
        dict(nombre="IMSS — Clínica 1 Cuauhtémoc", tipo=TipoActor.gobierno,
             descripcion="Clínica del IMSS con servicio pediátrico y atención a familias.",
             direccion="Dr. Navarro 33, Doctores", municipio="Cuauhtémoc", estado="CDMX",
             telefono="800-623-2323", correo="atencion@imss.gob.mx"),
        dict(nombre="Casa Alianza México", tipo=TipoActor.civil,
             descripcion="Organización internacional que protege, rehabilita y reintegra a menores en situación de riesgo en las calles.",
             direccion="Chimalpopoca 8, Obrera", municipio="Cuauhtémoc", estado="CDMX",
             telefono="55-5543-5823", correo="info@casaalianza.mx", sitio_web="www.casaalianza.mx"),
        dict(nombre="Consejo de la Judicatura Federal", tipo=TipoActor.gobierno,
             descripcion="Órgano judicial que gestiona los procesos legales federales de protección a menores.",
             direccion="Liverpool 4, Juárez", municipio="Cuauhtémoc", estado="CDMX",
             telefono="55-5229-5600"),
        dict(nombre="Fundación Dibujando un Mañana", tipo=TipoActor.civil,
             descripcion="Organización civil que brinda educación alternativa y apoyo emocional a NNA en situación de vulnerabilidad.",
             direccion="Moctezuma 400, Tepito", municipio="Venustiano Carranza", estado="CDMX",
             telefono="55-6677-8899", correo="contacto@dibujanmañana.org"),
    ]
    actores = []
    for adef in actores_def:
        a = Actor(**adef, activo=True)
        db.add(a); actores.append(a)
    db.flush()
    a_dif, a_imss, a_alianza, a_jud, a_fundacion = actores

    resp_dif = ResponsableActor(actor_id=a_dif.id, nombre="Lic. Patricia Herrera", cargo="Jefa de Área de Menores", telefono="55-1234-5679", es_principal=True)
    resp_alianza = ResponsableActor(actor_id=a_alianza.id, nombre="Mtro. Javier Fuentes", cargo="Director de Programas", telefono="55-5543-5824", es_principal=True)
    db.add_all([resp_dif, resp_alianza])

    for dia in ["lunes","martes","miércoles","jueves","viernes"]:
        db.add(HorarioActor(actor_id=a_dif.id, dia_semana=dia, hora_inicio="09:00", hora_fin="17:00"))
        db.add(HorarioActor(actor_id=a_alianza.id, dia_semana=dia, hora_inicio="08:00", hora_fin="18:00"))
    db.add(HorarioActor(actor_id=a_alianza.id, dia_semana="sábado", hora_inicio="09:00", hora_fin="13:00"))

    servicios_def = [
        (a_dif, "Apoyo psicológico infantil", "Terapia individual y grupal para NNA víctimas de violencia", d_salud, True),
        (a_dif, "Asesoría legal familiar", "Orientación jurídica en materia de familia y tutela", d_proteccion, True),
        (a_dif, "Apoyo nutricional", "Dotación de despensas y orientación alimentaria", d_alim, True),
        (a_imss, "Atención pediátrica", "Consultas médicas y seguimiento de salud infantil", d_salud, True),
        (a_alianza, "Programa de refugio temporal", "Albergue seguro para NNA en situación de riesgo", d_vivienda, True),
        (a_alianza, "Apoyo educativo", "Clases de regularización y materiales escolares", d_edu, True),
        (a_jud, "Representación legal", "Asistencia jurídica en procesos de protección", d_proteccion, True),
        (a_fundacion, "Talleres artísticos terapéuticos", "Arte, música y teatro como herramienta de recuperación emocional", d_salud, True),
    ]
    servicios = []
    for actor, nombre, desc, derecho, gratuito in servicios_def:
        s = ServicioActor(actor_id=actor.id, nombre=nombre, descripcion=desc,
                          derecho_id=derecho.id, es_gratuito=gratuito, tipo=TipoServicio.servicio, activo=True)
        db.add(s); servicios.append(s)
    db.flush()

    # ─── CASO NNA 1: Sofía — caso activo completo ──────────────────
    print("  Creando Caso 1: Sofía Herrera (activo, completo)...")
    sofia = CasoNNA(
        nna_nombre="Sofía Herrera Jiménez", nna_curp="HEJS140805MDFRRN09",
        nna_fecha_nacimiento=date(2014,8,5), nna_edad=11,
        nna_genero=GeneroNNA.femenino, nna_nacionalidad="Mexicana",
        estado=EstadoCasoNNA.activo, creador_id=psicologa.id,
        responsable_id=trabajador_social.id
    )
    db.add(sofia); db.flush()

    db.add(TutorNNA(
        caso_id=sofia.id, nombre="Martha", apellido_paterno="Jiménez", apellido_materno="Vázquez",
        parentesco="Madre", telefono="55-9988-7766", correo="martha.jimenez@gmail.com",
        direccion="Calle Magnolia 34, Colonia Flores, Iztapalapa",
        documento_identificacion="INE", numero_documento="JIMV840312MDFZRR03",
        ocupacion="Empleada doméstica"
    ))
    db.add(DatosMedicosNNA(
        caso_id=sofia.id, historial_medico="Fracturas en brazo izquierdo (2023). Golpes en cabeza. Infección urinaria recurrente.",
        alergias="Penicilina", discapacidades="Ninguna", tipo_sangre="O+",
        medico_responsable="Dr. Ernesto Alcántara", institucion_medica="IMSS Clínica 1",
        cartilla_vacunacion=[
            {"vacuna": "BCG", "fecha": "2014-08-10", "dosis": "1"},
            {"vacuna": "Hepatitis B", "fecha": "2014-08-10", "dosis": "1"},
            {"vacuna": "DPT", "fecha": "2014-10-05", "dosis": "2"},
        ]
    ))

    personas_sofia = [
        PersonaFamiliar(caso_id=sofia.id, nombre="Sofía Herrera Jiménez", edad=11,
                        genero=GeneroNNA.femenino, rol_en_familia="Hija (NNA)",
                        tipo_simbolo=TipoSimboloFamiliar.clave, vive_con_nna=True),
        PersonaFamiliar(caso_id=sofia.id, nombre="Martha Jiménez Vázquez", edad=40,
                        genero=GeneroNNA.femenino, rol_en_familia="Madre",
                        tipo_simbolo=TipoSimboloFamiliar.cuidador, vive_con_nna=True,
                        es_responsable_legal=True, telefono="55-9988-7766"),
        PersonaFamiliar(caso_id=sofia.id, nombre="Ernesto Herrera García", edad=43,
                        genero=GeneroNNA.masculino, rol_en_familia="Padre",
                        tipo_simbolo=TipoSimboloFamiliar.agresor, vive_con_nna=False,
                        observaciones="Agresor identificado. Orden de restricción vigente."),
        PersonaFamiliar(caso_id=sofia.id, nombre="Rosario Vázquez (Abuela)", edad=65,
                        genero=GeneroNNA.femenino, rol_en_familia="Abuela materna",
                        tipo_simbolo=TipoSimboloFamiliar.normal, vive_con_nna=False,
                        telefono="55-1122-3344"),
        PersonaFamiliar(caso_id=sofia.id, nombre="Miguel Herrera Jiménez", edad=8,
                        genero=GeneroNNA.masculino, rol_en_familia="Hermano",
                        tipo_simbolo=TipoSimboloFamiliar.normal, vive_con_nna=True),
    ]
    for p in personas_sofia: db.add(p)
    db.flush()
    ps_sofia, pm_sofia, pp_sofia, pab_sofia, ph_sofia = personas_sofia

    db.add(RelacionFamiliar(caso_id=sofia.id, persona_origen_id=pm_sofia.id, persona_destino_id=ps_sofia.id, tipo_relacion=TipoRelacionFamiliar.biologica, descripcion="Relación madre-hija"))
    db.add(RelacionFamiliar(caso_id=sofia.id, persona_origen_id=pp_sofia.id, persona_destino_id=ps_sofia.id, tipo_relacion=TipoRelacionFamiliar.conflictiva, descripcion="Padre agresor con orden de restricción"))
    db.add(RelacionFamiliar(caso_id=sofia.id, persona_origen_id=pab_sofia.id, persona_destino_id=pm_sofia.id, tipo_relacion=TipoRelacionFamiliar.biologica, descripcion="Abuela materna"))
    db.add(RelacionFamiliar(caso_id=sofia.id, persona_origen_id=pm_sofia.id, persona_destino_id=ph_sofia.id, tipo_relacion=TipoRelacionFamiliar.biologica, descripcion="Madre-hijo"))
    db.flush()

    familiograma_sofia = Familiograma(caso_id=sofia.id, grafo_json={
        "nodes": [
            {"id": str(ps_sofia.id), "data": {"label": "Sofía (NNA)", "tipo": "clave"}, "position": {"x": 300, "y": 200}, "type": "nnaNode"},
            {"id": str(pm_sofia.id), "data": {"label": "Martha (Madre)", "tipo": "cuidador"}, "position": {"x": 150, "y": 50}, "type": "familiarNode"},
            {"id": str(pp_sofia.id), "data": {"label": "Ernesto (Padre)", "tipo": "agresor"}, "position": {"x": 450, "y": 50}, "type": "familiarNode"},
            {"id": str(pab_sofia.id), "data": {"label": "Rosario (Abuela)", "tipo": "normal"}, "position": {"x": 0, "y": 50}, "type": "familiarNode"},
            {"id": str(ph_sofia.id), "data": {"label": "Miguel (Hermano)", "tipo": "normal"}, "position": {"x": 300, "y": 350}, "type": "familiarNode"},
        ],
        "edges": [
            {"id": "e1", "source": str(pm_sofia.id), "target": str(ps_sofia.id), "label": "biológica", "type": "smoothstep"},
            {"id": "e2", "source": str(pp_sofia.id), "target": str(ps_sofia.id), "label": "conflictiva", "style": {"stroke": "red"}, "type": "smoothstep"},
            {"id": "e3", "source": str(pab_sofia.id), "target": str(pm_sofia.id), "label": "biológica", "type": "smoothstep"},
        ]
    })
    db.add(familiograma_sofia)

    entrevista_sofia = EntrevistaFamilia(
        caso_id=sofia.id, grado_negacion=3, completada=True,
        observaciones_negacion="Sofía muestra señales de miedo al hablar del padre. Llora cuando se menciona el hogar.",
        frases_comunicadas=[
            {"id": "f1", "texto": "Me da miedo que regrese", "comunicada": True, "notas": "Referencia directa al padre"},
            {"id": "f2", "texto": "No quiero ir a la escuela", "comunicada": True, "notas": "Dijo que en la escuela se burlan de sus moretones"},
            {"id": "f3", "texto": "Mi mamá llora mucho", "comunicada": True, "notas": "Indica que es consciente de la situación emocional de la madre"},
        ],
        dia_comun={
            "quien_despierta": "La madre",
            "rutina_matutina": "Sofía no desayuna regularmente, llega tarde a la escuela con frecuencia",
            "cuidador_dia": "Se queda sola al salir la madre a trabajar",
            "relaciones_externas": "Poco contacto con amigos. Permanece aislada en casa.",
            "nna_es_central": "no",
            "adulto_dificultad": "si",
            "personas_mencionadas": ["mamá", "papá", "abuela Rosario", "Miguelito"]
        }
    )
    db.add(entrevista_sofia)
    db.flush()

    # Diagnósticos de Sofía
    diag1 = Diagnostico(caso_nna_id=sofia.id, tipo=TipoDiagnostico.inicial,
                        fecha=date.today() - timedelta(days=30),
                        responsable_id=psicologa.id,
                        observaciones="Primer contacto. Sofía presenta signos evidentes de violencia física. Muy reservada. La madre relata incidentes repetidos de maltrato por parte del padre.")
    db.add(diag1); db.flush()

    ind_map = {ind.nombre: ind for ind in indicadores}
    eval_data = [
        ("Cuenta con cartilla de vacunación actualizada", "si", False),
        ("Tiene acceso a atención médica regular", "no", True),
        ("Presenta señales visibles de desnutrición", "si", True),
        ("Recibe atención psicológica", "no", True),
        ("Está inscrito en escuela actualmente", "si", False),
        ("Asiste regularmente a clases", "no", True),
        ("Cuenta con acta de nacimiento", "si", False),
        ("Tiene CURP registrado", "si", False),
        ("Vive con al menos un familiar responsable", "si", False),
        ("El entorno familiar es seguro y estable", "no", True),
        ("Ha sufrido maltrato físico", "si", True),
        ("Ha sufrido maltrato psicológico", "si", True),
        ("Hay presencia de agresor en el hogar", "no", False),
        ("Recibe al menos 3 comidas al día", "no", True),
    ]
    derechos_vulnerados_ids = set()
    for nombre, valor, vulnerado in eval_data:
        ind = ind_map.get(nombre)
        if ind:
            db.add(IndicadorDiagnostico(diagnostico_id=diag1.id, indicador_id=ind.id, valor=valor, vulnerado=vulnerado))
            if vulnerado:
                derechos_vulnerados_ids.add(ind.derecho_id)
    db.flush()

    severidades = {d_salud.id: SeveridadVulneracion.grave, d_edu.id: SeveridadVulneracion.moderada,
                   d_familia.id: SeveridadVulneracion.grave, d_proteccion.id: SeveridadVulneracion.critica,
                   d_alim.id: SeveridadVulneracion.moderada}
    recomendaciones = {
        d_salud.id: "Canalizar de inmediato a IMSS para evaluación médica completa y seguimiento nutricional.",
        d_edu.id: "Contactar escuela para plan de regularización y apoyo a la asistencia.",
        d_familia.id: "Evaluar posibilidad de acogimiento familiar temporal con abuela.",
        d_proteccion.id: "Activar protocolo de protección inmediata. Notificar a la Fiscalía. Orden de restricción vigente.",
        d_alim.id: "Gestionar apoyo alimentario mensual a través del DIF.",
    }
    for d_id in derechos_vulnerados_ids:
        sev = severidades.get(d_id, SeveridadVulneracion.moderada)
        rec = recomendaciones.get(d_id, "Dar seguimiento en próxima sesión.")
        db.add(DerechoVulnerado(diagnostico_id=diag1.id, derecho_id=d_id, severidad=sev,
                                recomendacion=rec, generado_automaticamente=True))
    db.flush()

    diag2 = Diagnostico(caso_nna_id=sofia.id, tipo=TipoDiagnostico.tutor,
                        fecha=date.today() - timedelta(days=25),
                        responsable_id=trabajador_social.id,
                        observaciones="Entrevista con la madre. Martha muestra agotamiento emocional, culpa y miedo. Desconoce sus derechos. Sin red de apoyo formal. Dependencia económica del agresor hasta hace 2 semanas.")
    db.add(diag2); db.flush()
    db.add(DerechoVulnerado(diagnostico_id=diag2.id, derecho_id=d_familia.id,
                            severidad=SeveridadVulneracion.grave,
                            recomendacion="Ofrecer apoyo psicológico a la madre e informar sobre apoyos económicos del DIF.",
                            generado_automaticamente=False))

    # Plan de restitución de Sofía
    plan_sofia = PlanRestitucion(
        caso_nna_id=sofia.id,
        objetivo="Garantizar la seguridad física y emocional de Sofía, restituir su derecho a la salud, educación y un entorno familiar libre de violencia en un plazo de 6 meses.",
        derechos_afectados=[d_salud.id, d_edu.id, d_familia.id, d_proteccion.id, d_alim.id],
        responsable_id=coord.id,
        fecha_inicio=date.today() - timedelta(days=20),
        fecha_termino=date.today() + timedelta(days=160),
        estado=EstadoPlan.activo,
        observaciones="Plan aprobado por directora. Equipo multidisciplinario asignado."
    )
    db.add(plan_sofia); db.flush()

    medidas_sofia = [
        MedidaRestitucion(plan_id=plan_sofia.id, tipo=TipoMedida.medica,
                          descripcion="Canalizar a Sofía con médico pediatra del IMSS para evaluación completa de lesiones y estado nutricional.",
                          responsable_id=trabajador_social.id, actor_id=a_imss.id,
                          estado=EstadoMedida.completada, porcentaje_avance=100,
                          fecha_inicio=date.today()-timedelta(days=18), fecha_limite=date.today()-timedelta(days=10)),
        MedidaRestitucion(plan_id=plan_sofia.id, tipo=TipoMedida.psicologica,
                          descripcion="Iniciar terapia psicológica individual, 2 sesiones semanales con énfasis en trauma y autoestima.",
                          responsable_id=psicologa.id, actor_id=a_dif.id,
                          estado=EstadoMedida.en_proceso, porcentaje_avance=40,
                          fecha_inicio=date.today()-timedelta(days=15), fecha_limite=date.today()+timedelta(days=75)),
        MedidaRestitucion(plan_id=plan_sofia.id, tipo=TipoMedida.legal,
                          descripcion="Tramitar ampliación de orden de restricción y gestionar proceso de custodia exclusiva para la madre.",
                          responsable_id=abogada.id, actor_id=a_jud.id,
                          estado=EstadoMedida.en_proceso, porcentaje_avance=30,
                          fecha_inicio=date.today()-timedelta(days=20), fecha_limite=date.today()+timedelta(days=90)),
        MedidaRestitucion(plan_id=plan_sofia.id, tipo=TipoMedida.educativa,
                          descripcion="Reunión con dirección escolar para plan de regularización y seguimiento de asistencia.",
                          responsable_id=trabajador_social.id,
                          estado=EstadoMedida.pendiente, porcentaje_avance=0,
                          fecha_inicio=date.today()+timedelta(days=5), fecha_limite=date.today()+timedelta(days=30)),
        MedidaRestitucion(plan_id=plan_sofia.id, tipo=TipoMedida.social,
                          descripcion="Tramitar apoyo alimentario mensual del DIF y orientar a la madre sobre apoyo económico disponible.",
                          responsable_id=trabajador_social.id, actor_id=a_dif.id,
                          estado=EstadoMedida.completada, porcentaje_avance=100,
                          fecha_inicio=date.today()-timedelta(days=18), fecha_limite=date.today()-timedelta(days=5)),
    ]
    for m in medidas_sofia: db.add(m)
    db.flush()
    med_medica, med_psico, med_legal, med_edu, med_social = medidas_sofia

    db.add(SeguimientoMedida(medida_id=med_medica.id, registrado_por_id=trabajador_social.id,
        fecha_seguimiento=date.today()-timedelta(days=15),
        descripcion_avance="Sofía fue atendida en IMSS Clínica 1. Dr. Alcántara confirmó fractura sanada y descartó nuevas lesiones. Derivada a nutrióloga.",
        porcentaje_cumplimiento=100, observaciones="El médico documentó huellas de violencia para expediente legal."))
    db.add(SeguimientoMedida(medida_id=med_psico.id, registrado_por_id=psicologa.id,
        fecha_seguimiento=date.today()-timedelta(days=10),
        descripcion_avance="Primera sesión terapéutica. Sofía mostró resistencia inicial pero comenzó a hablar en la segunda mitad. Se aplicó técnica de juego terapéutico.",
        porcentaje_cumplimiento=20))
    db.add(SeguimientoMedida(medida_id=med_psico.id, registrado_por_id=psicologa.id,
        fecha_seguimiento=date.today()-timedelta(days=3),
        descripcion_avance="Tercera sesión. Sofía dibujó su familia. Importante avance: expresó por primera vez que no fue su culpa. Comenzó a sonreír.",
        porcentaje_cumplimiento=40))
    db.add(SeguimientoMedida(medida_id=med_legal.id, registrado_por_id=abogada.id,
        fecha_seguimiento=date.today()-timedelta(days=14),
        descripcion_avance="Presentada solicitud de ampliación de orden de restricción. Pendiente audiencia en Juzgado Familiar No. 3.",
        porcentaje_cumplimiento=30))
    db.add(SeguimientoMedida(medida_id=med_social.id, registrado_por_id=trabajador_social.id,
        fecha_seguimiento=date.today()-timedelta(days=12),
        descripcion_avance="Se tramitó despensa mensual DIF. Primera entrega realizada. Martha inscrita en programa 'Mujeres Jefas de Familia'.",
        porcentaje_cumplimiento=100))
    db.flush()

    # ─── CASO NNA 2: Diego — caso en seguimiento ───────────────────
    print("  Creando Caso 2: Diego Morales (en seguimiento)...")
    diego = CasoNNA(
        nna_nombre="Diego Morales Reyes", nna_curp="MORD170321HDFRLG07",
        nna_fecha_nacimiento=date(2017,3,21), nna_edad=8,
        nna_genero=GeneroNNA.masculino, nna_nacionalidad="Mexicana",
        estado=EstadoCasoNNA.activo, creador_id=trabajador_social.id,
        responsable_id=trabajador_social.id
    )
    db.add(diego); db.flush()

    db.add(TutorNNA(caso_id=diego.id, nombre="Claudia", apellido_paterno="Reyes",
                    apellido_materno="Mendoza", parentesco="Madre",
                    telefono="55-4455-6677", ocupacion="Vendedora ambulante"))
    db.add(DatosMedicosNNA(caso_id=diego.id,
                           historial_medico="Sin historial de lesiones. Bajo peso para su edad.",
                           discapacidades="Ninguna", tipo_sangre="A+"))

    personas_diego = [
        PersonaFamiliar(caso_id=diego.id, nombre="Diego Morales Reyes", edad=8,
                        genero=GeneroNNA.masculino, rol_en_familia="Hijo (NNA)",
                        tipo_simbolo=TipoSimboloFamiliar.clave, vive_con_nna=True),
        PersonaFamiliar(caso_id=diego.id, nombre="Claudia Reyes Mendoza", edad=29,
                        genero=GeneroNNA.femenino, rol_en_familia="Madre",
                        tipo_simbolo=TipoSimboloFamiliar.cuidador, vive_con_nna=True,
                        es_responsable_legal=True),
        PersonaFamiliar(caso_id=diego.id, nombre="Abuelo Juan Reyes", edad=58,
                        genero=GeneroNNA.masculino, rol_en_familia="Abuelo materno",
                        tipo_simbolo=TipoSimboloFamiliar.normal, vive_con_nna=True),
    ]
    for p in personas_diego: db.add(p)
    db.flush()
    pd_nna, pd_mama, pd_abuelo = personas_diego

    db.add(RelacionFamiliar(caso_id=diego.id, persona_origen_id=pd_mama.id, persona_destino_id=pd_nna.id,
                            tipo_relacion=TipoRelacionFamiliar.biologica))
    db.add(RelacionFamiliar(caso_id=diego.id, persona_origen_id=pd_abuelo.id, persona_destino_id=pd_mama.id,
                            tipo_relacion=TipoRelacionFamiliar.biologica))
    db.add(Familiograma(caso_id=diego.id, grafo_json={
        "nodes": [
            {"id": str(pd_nna.id), "data": {"label": "Diego (NNA)", "tipo": "clave"}, "position": {"x": 200, "y": 200}},
            {"id": str(pd_mama.id), "data": {"label": "Claudia (Madre)", "tipo": "cuidador"}, "position": {"x": 100, "y": 50}},
            {"id": str(pd_abuelo.id), "data": {"label": "Juan (Abuelo)", "tipo": "normal"}, "position": {"x": 0, "y": 50}},
        ],
        "edges": [
            {"id": "e1", "source": str(pd_mama.id), "target": str(pd_nna.id)},
            {"id": "e2", "source": str(pd_abuelo.id), "target": str(pd_mama.id)},
        ]
    }))

    diag_diego = Diagnostico(caso_nna_id=diego.id, tipo=TipoDiagnostico.inicial,
                             fecha=date.today()-timedelta(days=15),
                             responsable_id=trabajador_social.id,
                             observaciones="Diego presenta señales de negligencia. No asiste a la escuela. Madre en situación de pobreza extrema. No hay violencia física pero sí descuido.")
    db.add(diag_diego); db.flush()

    eval_diego = [
        ("Presenta señales visibles de desnutrición", "si", True),
        ("Está inscrito en escuela actualmente", "no", True),
        ("Tiene materiales escolares básicos", "no", True),
        ("Cuenta con acta de nacimiento", "no", True),
        ("Vive con al menos un familiar responsable", "si", False),
        ("Recibe al menos 3 comidas al día", "no", True),
        ("Tiene un lugar seguro donde dormir", "si", False),
    ]
    dv_diego_ids = set()
    for nombre, valor, vuln in eval_diego:
        ind = ind_map.get(nombre)
        if ind:
            db.add(IndicadorDiagnostico(diagnostico_id=diag_diego.id, indicador_id=ind.id, valor=valor, vulnerado=vuln))
            if vuln: dv_diego_ids.add(ind.derecho_id)
    db.flush()
    for d_id in dv_diego_ids:
        db.add(DerechoVulnerado(diagnostico_id=diag_diego.id, derecho_id=d_id,
                                severidad=SeveridadVulneracion.moderada, generado_automaticamente=True,
                                recomendacion="Canalizar al DIF para apoyo correspondiente."))

    plan_diego = PlanRestitucion(
        caso_nna_id=diego.id,
        objetivo="Garantizar acceso a educación, alimentación e identidad legal para Diego Morales en los próximos 3 meses.",
        derechos_afectados=[d_edu.id, d_identidad.id, d_alim.id],
        responsable_id=trabajador_social.id,
        fecha_inicio=date.today()-timedelta(days=10),
        fecha_termino=date.today()+timedelta(days=80),
        estado=EstadoPlan.activo
    )
    db.add(plan_diego); db.flush()
    med_d1 = MedidaRestitucion(plan_id=plan_diego.id, tipo=TipoMedida.educativa,
                                descripcion="Inscribir a Diego en escuela primaria más cercana y gestionar útiles escolares.",
                                responsable_id=trabajador_social.id,
                                estado=EstadoMedida.en_proceso, porcentaje_avance=50,
                                fecha_inicio=date.today()-timedelta(days=8))
    db.add(med_d1); db.flush()
    db.add(SeguimientoMedida(medida_id=med_d1.id, registrado_por_id=trabajador_social.id,
        fecha_seguimiento=date.today()-timedelta(days=5),
        descripcion_avance="Se presentó solicitud de inscripción en Primaria Benito Juárez. Dirección escolar requiere acta de nacimiento primero.",
        porcentaje_cumplimiento=50))
    db.flush()

    # ─── CASO NNA 3: Valentina — caso cerrado ──────────────────────
    print("  Creando Caso 3: Valentina (cerrado, historia de éxito)...")
    valentina = CasoNNA(
        nna_nombre="Valentina Castillo Nava", nna_fecha_nacimiento=date(2012,11,15),
        nna_edad=13, nna_curp="CANV121115MDFSVL05",
        nna_genero=GeneroNNA.femenino, nna_nacionalidad="Mexicana",
        estado=EstadoCasoNNA.cerrado, creador_id=psicologa.id
    )
    db.add(valentina); db.flush()

    diag_val = Diagnostico(caso_nna_id=valentina.id, tipo=TipoDiagnostico.inicial,
                           fecha=date.today()-timedelta(days=120),
                           responsable_id=psicologa.id, completado=True,
                           observaciones="Valentina fue canalizada tras denuncia escolar. Caso de abandono paterno y sobrecarga de responsabilidades domésticas.")
    db.add(diag_val); db.flush()
    db.add(DerechoVulnerado(diagnostico_id=diag_val.id, derecho_id=d_familia.id,
                            severidad=SeveridadVulneracion.moderada,
                            recomendacion="Apoyo psicológico y fortalecimiento del vínculo materno.", generado_automaticamente=False))
    plan_val = PlanRestitucion(
        caso_nna_id=valentina.id,
        objetivo="Restituir ambiente familiar estable y apoyo emocional para Valentina.",
        responsable_id=psicologa.id,
        fecha_inicio=date.today()-timedelta(days=115),
        fecha_termino=date.today()-timedelta(days=10),
        estado=EstadoPlan.completado
    )
    db.add(plan_val); db.flush()

    # ─── CASO NNA 4: Emilio — recién ingresado ─────────────────────
    print("  Creando Caso 4: Emilio (nuevo ingreso)...")
    emilio = CasoNNA(
        nna_nombre="Emilio Sandoval Torres", nna_fecha_nacimiento=date(2016,6,8),
        nna_edad=9, nna_genero=GeneroNNA.masculino, nna_nacionalidad="Mexicana",
        estado=EstadoCasoNNA.activo, creador_id=coord.id
    )
    db.add(emilio); db.flush()
    db.add(TutorNNA(caso_id=emilio.id, nombre="Lorena", apellido_paterno="Torres",
                    parentesco="Tía", telefono="55-3344-5566",
                    ocupacion="Empleada de limpieza"))

    # ─── EQUIPOS MULTIDISCIPLINARIOS ───────────────────────────────
    print("  Creando equipos multidisciplinarios...")
    from datetime import datetime as dt
    equipo_sofia = [
        EquipoCaso(caso_id=sofia.id, usuario_id=psicologa.id,
                   rol_en_equipo="psicologo", asignado_por_id=trabajador_social.id,
                   activo=True, fecha_asignacion=dt.now() - timedelta(days=20),
                   observaciones="Terapia individual 2 veces por semana"),
        EquipoCaso(caso_id=sofia.id, usuario_id=abogada.id,
                   rol_en_equipo="legal", asignado_por_id=trabajador_social.id,
                   activo=True, fecha_asignacion=dt.now() - timedelta(days=20),
                   observaciones="Gestión de orden de restricción y proceso de custodia"),
        EquipoCaso(caso_id=sofia.id, usuario_id=coord.id,
                   rol_en_equipo="coordinador", asignado_por_id=trabajador_social.id,
                   activo=True, fecha_asignacion=dt.now() - timedelta(days=19)),
    ]
    for e in equipo_sofia: db.add(e)

    db.add(EquipoCaso(caso_id=diego.id, usuario_id=psicologa.id,
                      rol_en_equipo="psicologo", asignado_por_id=trabajador_social.id,
                      activo=True, fecha_asignacion=dt.now() - timedelta(days=12)))
    db.flush()

    # ─── EVALUACIONES DE CONFIANZA ──────────────────────────────────
    print("  Creando evaluaciones de confianza...")
    db.add(EvaluacionConfianza(
        usuario_id=abogada.id, evaluador_id=director.id,
        nivel_anterior=2, nivel_nuevo=3,
        justificacion="Buen desempeño en gestión de expedientes legales durante los primeros meses.",
        fecha=dt.now() - timedelta(days=180)
    ))
    db.add(EvaluacionConfianza(
        usuario_id=psicologa.id, evaluador_id=director.id,
        nivel_anterior=3, nivel_nuevo=4,
        justificacion="Excelente progreso con casos complejos de trauma infantil. Alta eficacia terapéutica.",
        fecha=dt.now() - timedelta(days=90)
    ))
    abogada.fecha_ultima_evaluacion = date.today() - timedelta(days=180)
    psicologa.fecha_ultima_evaluacion = date.today() - timedelta(days=90)
    db.flush()

    db.commit()
    print("\n✅ Datos demo cargados correctamente.")
    print("\n👥 USUARIOS DE PRUEBA:")
    print("   director@xolix.com     | admin123  | Director")
    print("   coordinador@xolix.com  | coord123  | Coordinador")
    print("   psicologa@xolix.com    | psico123  | Psicóloga")
    print("   trabajo_social@xolix.com | social123 | Trabajo Social")
    print("   legal@xolix.com        | legal123  | Área Legal")
    print("\n📋 CASOS NNA DEMO:")
    print(f"   #{sofia.id} Sofía Herrera (activo) — caso completo con diagnóstico, plan y seguimientos")
    print(f"   #{diego.id} Diego Morales (activo) — negligencia, plan en proceso")
    print(f"   #{valentina.id} Valentina Castillo (cerrado) — historia de éxito")
    print(f"   #{emilio.id} Emilio Sandoval (activo) — nuevo ingreso")
    print(f"\n🏢 ACTORES: {len(actores)} actores con servicios")
    print(f"📚 CATÁLOGO: {len(derechos)} derechos, {len(indicadores)} indicadores")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback; traceback.print_exc()
    finally:
        db.close()
