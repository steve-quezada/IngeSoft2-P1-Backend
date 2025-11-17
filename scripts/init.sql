-- ========================================
-- Script de inicialización de base de datos
-- P1-Backend - Ingeniería de Software 2
-- ========================================

-- Crear extensión para generar UUIDs (opcional pero recomendado)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- Tabla: questions
-- ========================================
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- Tabla: answers
-- ========================================
CREATE TABLE IF NOT EXISTS answers (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    votes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_question
        FOREIGN KEY(question_id) 
        REFERENCES questions(id)
        ON DELETE CASCADE
);

-- ========================================
-- Tabla: votes (opcional - para tracking de votos individuales)
-- ========================================
CREATE TABLE IF NOT EXISTS votes (
    id SERIAL PRIMARY KEY,
    answer_id INTEGER NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    voted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_answer
        FOREIGN KEY(answer_id) 
        REFERENCES answers(id)
        ON DELETE CASCADE
);

-- ========================================
-- Índices para mejorar rendimiento
-- ========================================
CREATE INDEX IF NOT EXISTS idx_answers_question_id ON answers(question_id);
CREATE INDEX IF NOT EXISTS idx_votes_answer_id ON votes(answer_id);
CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_answers_votes ON answers(votes DESC);

-- ========================================
-- Función para actualizar updated_at automáticamente
-- ========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para updated_at
CREATE TRIGGER update_questions_updated_at
    BEFORE UPDATE ON questions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_answers_updated_at
    BEFORE UPDATE ON answers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- Datos de ejemplo (opcional - para testing)
-- ========================================
INSERT INTO questions (title, description) VALUES
    ('¿Cómo funciona Docker?', 'Necesito entender los conceptos básicos de Docker y contenedores.'),
    ('¿Qué es PostgreSQL?', 'Busco información sobre bases de datos relacionales y PostgreSQL.')
ON CONFLICT DO NOTHING;

INSERT INTO answers (question_id, text, votes) VALUES
    (1, 'Docker es una plataforma para desarrollar, enviar y ejecutar aplicaciones en contenedores.', 5),
    (1, 'Los contenedores son unidades ligeras de software que empaquetan código y dependencias.', 3),
    (2, 'PostgreSQL es un sistema de gestión de bases de datos relacional de código abierto.', 7)
ON CONFLICT DO NOTHING;

-- ========================================
-- Mensajes de confirmación
-- ========================================
DO $$
BEGIN
    RAISE NOTICE 'Base de datos inicializada correctamente';
    RAISE NOTICE 'Tablas creadas: questions, answers, votes';
    RAISE NOTICE 'Índices y triggers configurados';
END $$;
