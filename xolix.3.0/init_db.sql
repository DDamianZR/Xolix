--
-- PostgreSQL database dump
--

\restrict eoU5gyU2azaqgm4NXkjx8eWgSHcg3Xks9CcfKhRx87PRS3kwuiQIINbMsrMYzn9

-- Dumped from database version 18.2
-- Dumped by pg_dump version 18.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: estadoproceso; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estadoproceso AS ENUM (
    'pendiente',
    'en_proceso',
    'terminado'
);


ALTER TYPE public.estadoproceso OWNER TO postgres;

--
-- Name: permisoexpediente; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.permisoexpediente AS ENUM (
    'lectura',
    'edicion'
);


ALTER TYPE public.permisoexpediente OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: expedientes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expedientes (
    id integer NOT NULL,
    nombre character varying(200) NOT NULL,
    descripcion text,
    archivo_path character varying(500) NOT NULL,
    tipo_archivo character varying(50) NOT NULL,
    propietario_id integer NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT now(),
    fecha_actualizacion timestamp without time zone DEFAULT now()
);


ALTER TABLE public.expedientes OWNER TO postgres;

--
-- Name: expedientes_compartidos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expedientes_compartidos (
    id integer NOT NULL,
    expediente_id integer NOT NULL,
    usuario_id integer NOT NULL,
    permiso public.permisoexpediente NOT NULL,
    fecha_compartido timestamp without time zone DEFAULT now()
);


ALTER TABLE public.expedientes_compartidos OWNER TO postgres;

--
-- Name: expedientes_compartidos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expedientes_compartidos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.expedientes_compartidos_id_seq OWNER TO postgres;

--
-- Name: expedientes_compartidos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expedientes_compartidos_id_seq OWNED BY public.expedientes_compartidos.id;


--
-- Name: expedientes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expedientes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.expedientes_id_seq OWNER TO postgres;

--
-- Name: expedientes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expedientes_id_seq OWNED BY public.expedientes.id;


--
-- Name: proceso_usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.proceso_usuarios (
    proceso_id integer NOT NULL,
    usuario_id integer NOT NULL
);


ALTER TABLE public.proceso_usuarios OWNER TO postgres;

--
-- Name: procesos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.procesos (
    id integer NOT NULL,
    titulo character varying(200) NOT NULL,
    descripcion text,
    estado public.estadoproceso NOT NULL,
    expediente_id integer,
    creador_id integer NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT now(),
    fecha_actualizacion timestamp without time zone DEFAULT now()
);


ALTER TABLE public.procesos OWNER TO postgres;

--
-- Name: procesos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.procesos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.procesos_id_seq OWNER TO postgres;

--
-- Name: procesos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.procesos_id_seq OWNED BY public.procesos.id;


--
-- Name: subtareas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subtareas (
    id integer NOT NULL,
    proceso_id integer NOT NULL,
    titulo character varying(200) NOT NULL,
    completada boolean,
    fecha_creacion timestamp without time zone DEFAULT now()
);


ALTER TABLE public.subtareas OWNER TO postgres;

--
-- Name: subtareas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subtareas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subtareas_id_seq OWNER TO postgres;

--
-- Name: subtareas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subtareas_id_seq OWNED BY public.subtareas.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    nombre character varying(50) NOT NULL,
    apellido_paterno character varying(50) NOT NULL,
    apellido_materno character varying(50) NOT NULL,
    rfc character varying(13) NOT NULL,
    curp character varying(18) NOT NULL,
    sexo character varying(10) NOT NULL,
    fecha_nacimiento date NOT NULL,
    edad integer NOT NULL,
    estado character varying(50) NOT NULL,
    municipio character varying(100) NOT NULL,
    colonia character varying(100) NOT NULL,
    calle character varying(100) NOT NULL,
    numero character varying(20) NOT NULL,
    codigo_postal character varying(5) NOT NULL,
    calles_aledanas text,
    tipo_personal character varying(20) NOT NULL,
    rol character varying(30) NOT NULL,
    correo character varying(100) NOT NULL,
    password character varying(255) NOT NULL,
    activo boolean,
    verificado boolean,
    foto_perfil character varying(500),
    fecha_creacion timestamp without time zone DEFAULT now()
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: expedientes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expedientes ALTER COLUMN id SET DEFAULT nextval('public.expedientes_id_seq'::regclass);


--
-- Name: expedientes_compartidos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expedientes_compartidos ALTER COLUMN id SET DEFAULT nextval('public.expedientes_compartidos_id_seq'::regclass);


--
-- Name: procesos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.procesos ALTER COLUMN id SET DEFAULT nextval('public.procesos_id_seq'::regclass);


--
-- Name: subtareas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subtareas ALTER COLUMN id SET DEFAULT nextval('public.subtareas_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: expedientes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expedientes (id, nombre, descripcion, archivo_path, tipo_archivo, propietario_id, fecha_creacion, fecha_actualizacion) FROM stdin;
\.


--
-- Data for Name: expedientes_compartidos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expedientes_compartidos (id, expediente_id, usuario_id, permiso, fecha_compartido) FROM stdin;
\.


--
-- Data for Name: proceso_usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.proceso_usuarios (proceso_id, usuario_id) FROM stdin;
\.


--
-- Data for Name: procesos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.procesos (id, titulo, descripcion, estado, expediente_id, creador_id, fecha_creacion, fecha_actualizacion) FROM stdin;
\.


--
-- Data for Name: subtareas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subtareas (id, proceso_id, titulo, completada, fecha_creacion) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, nombre, apellido_paterno, apellido_materno, rfc, curp, sexo, fecha_nacimiento, edad, estado, municipio, colonia, calle, numero, codigo_postal, calles_aledanas, tipo_personal, rol, correo, password, activo, verificado, foto_perfil, fecha_creacion) FROM stdin;
1	Jennifer	Director	Prueba	JENX900101AAA	JENX900101MDFRRL09	F	1990-01-01	36	Ciudad de México	Gustavo A. Madero	Residencial la Escalera	Av. Juan de Dios Bátiz	S/N	07320	Casi esquina con Miguel Bernard	empleado	director	jennifer@xolix.com	$2b$12$kO2vZBWBPjpiYS2CG5ZNjOWD837laOcVzDy1aEcp2NN2aKkoDRy1y	t	t	\N	2026-03-25 22:08:03.967291
2	Juan Carlos	Hernandéz	López	HELJ950412A12	HELJ950412HDFRPN09	M	1995-04-12	30	CDMX	Álvaro Obregón	Olivar del Conde	10	123	01408	Entre calles: Calle 9 y Calle 11	empleado	abogado	dzr012296@gmail.com	$2b$12$h1eFMkR/u9khDOCrBZJVjeRYp0CVG..hYkpEpg1WC.rGkrbBT8r.e	t	f	\N	2026-03-25 22:56:42.834049
\.


--
-- Name: expedientes_compartidos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expedientes_compartidos_id_seq', 1, false);


--
-- Name: expedientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expedientes_id_seq', 1, false);


--
-- Name: procesos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.procesos_id_seq', 1, false);


--
-- Name: subtareas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subtareas_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: expedientes_compartidos expedientes_compartidos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expedientes_compartidos
    ADD CONSTRAINT expedientes_compartidos_pkey PRIMARY KEY (id);


--
-- Name: expedientes expedientes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expedientes
    ADD CONSTRAINT expedientes_pkey PRIMARY KEY (id);


--
-- Name: proceso_usuarios proceso_usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proceso_usuarios
    ADD CONSTRAINT proceso_usuarios_pkey PRIMARY KEY (proceso_id, usuario_id);


--
-- Name: procesos procesos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.procesos
    ADD CONSTRAINT procesos_pkey PRIMARY KEY (id);


--
-- Name: subtareas subtareas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subtareas
    ADD CONSTRAINT subtareas_pkey PRIMARY KEY (id);


--
-- Name: users users_correo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_correo_key UNIQUE (correo);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_expedientes_compartidos_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expedientes_compartidos_id ON public.expedientes_compartidos USING btree (id);


--
-- Name: ix_expedientes_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_expedientes_id ON public.expedientes USING btree (id);


--
-- Name: ix_procesos_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_procesos_id ON public.procesos USING btree (id);


--
-- Name: ix_subtareas_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_subtareas_id ON public.subtareas USING btree (id);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: expedientes_compartidos expedientes_compartidos_expediente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expedientes_compartidos
    ADD CONSTRAINT expedientes_compartidos_expediente_id_fkey FOREIGN KEY (expediente_id) REFERENCES public.expedientes(id) ON DELETE CASCADE;


--
-- Name: expedientes_compartidos expedientes_compartidos_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expedientes_compartidos
    ADD CONSTRAINT expedientes_compartidos_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: expedientes expedientes_propietario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expedientes
    ADD CONSTRAINT expedientes_propietario_id_fkey FOREIGN KEY (propietario_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: proceso_usuarios proceso_usuarios_proceso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proceso_usuarios
    ADD CONSTRAINT proceso_usuarios_proceso_id_fkey FOREIGN KEY (proceso_id) REFERENCES public.procesos(id) ON DELETE CASCADE;


--
-- Name: proceso_usuarios proceso_usuarios_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proceso_usuarios
    ADD CONSTRAINT proceso_usuarios_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: procesos procesos_creador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.procesos
    ADD CONSTRAINT procesos_creador_id_fkey FOREIGN KEY (creador_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: procesos procesos_expediente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.procesos
    ADD CONSTRAINT procesos_expediente_id_fkey FOREIGN KEY (expediente_id) REFERENCES public.expedientes(id) ON DELETE SET NULL;


--
-- Name: subtareas subtareas_proceso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subtareas
    ADD CONSTRAINT subtareas_proceso_id_fkey FOREIGN KEY (proceso_id) REFERENCES public.procesos(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict eoU5gyU2azaqgm4NXkjx8eWgSHcg3Xks9CcfKhRx87PRS3kwuiQIINbMsrMYzn9

