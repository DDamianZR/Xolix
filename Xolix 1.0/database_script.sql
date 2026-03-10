CREATE DATABASE proyecto_escom;

\c proyecto_escom;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(150) NOT NULL,
    rfc VARCHAR(13) NOT NULL,
    curp VARCHAR(18) NOT NULL,
    sexo VARCHAR(10) NOT NULL,
    edad INT NOT NULL,
    direccion TEXT NOT NULL,
    tipo_personal VARCHAR(20) NOT NULL,
    rol VARCHAR(30) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
