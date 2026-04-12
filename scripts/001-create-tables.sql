-- PetQR Database Schema
-- Run this script to create all required tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Usuarios table
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    telefono VARCHAR(50),
    password_hash VARCHAR(255),
    provider VARCHAR(50) DEFAULT 'credentials',
    provider_id VARCHAR(255),
    rol VARCHAR(20) DEFAULT 'usuario',
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Mascotas table
CREATE TABLE IF NOT EXISTS mascotas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    nombre VARCHAR(255) NOT NULL,
    especie VARCHAR(50) NOT NULL,
    raza VARCHAR(100),
    color VARCHAR(100),
    edad_aproximada VARCHAR(50),
    foto_url TEXT,
    notas TEXT,
    estado VARCHAR(20) DEFAULT 'en_casa',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Codigos QR table
CREATE TABLE IF NOT EXISTS codigos_qr (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) UNIQUE NOT NULL,
    mascota_id UUID REFERENCES mascotas(id) ON DELETE SET NULL,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Escaneos (scan history) table
CREATE TABLE IF NOT EXISTS escaneos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    qr_id UUID REFERENCES codigos_qr(id) ON DELETE CASCADE,
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    direccion_aproximada TEXT,
    mensaje_encontrador TEXT,
    telefono_encontrador VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_mascotas_usuario ON mascotas(usuario_id);
CREATE INDEX IF NOT EXISTS idx_qr_mascota ON codigos_qr(mascota_id);
CREATE INDEX IF NOT EXISTS idx_qr_codigo ON codigos_qr(codigo);
CREATE INDEX IF NOT EXISTS idx_escaneos_qr ON escaneos(qr_id);
CREATE INDEX IF NOT EXISTS idx_escaneos_fecha ON escaneos(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
