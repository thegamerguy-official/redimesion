-- ==============================================================================
-- REDIMENSION - Script de Seeding (PostgreSQL)
-- Basado en los casos del "Experimento del Aire"
-- ==============================================================================

-- 1. LIMPIEZA DE TABLAS (Opcional, útil para re-ejecutar el seed)
DROP TABLE IF EXISTS "order_items" CASCADE;
DROP TABLE IF EXISTS "orders" CASCADE;
DROP TABLE IF EXISTS "products" CASCADE;
DROP TABLE IF EXISTS "box_types" CASCADE;

-- 2. CREACIÓN DE ESQUEMA (MVP)
CREATE TABLE "box_types" (
    "id" VARCHAR(50) PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "width" NUMERIC(10, 2) NOT NULL,
    "height" NUMERIC(10, 2) NOT NULL,
    "depth" NUMERIC(10, 2) NOT NULL,
    "max_weight" NUMERIC(10, 2) NOT NULL,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "products" (
    "id" VARCHAR(50) PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "category" VARCHAR(100),
    "width" NUMERIC(10, 2) NOT NULL,
    "height" NUMERIC(10, 2) NOT NULL,
    "depth" NUMERIC(10, 2) NOT NULL,
    "weight" NUMERIC(10, 2) NOT NULL,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "orders" (
    "id" VARCHAR(50) PRIMARY KEY,
    "status" VARCHAR(50) DEFAULT 'PENDING', -- PENDING, PACKED, SHIPPED
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "order_items" (
    "id" SERIAL PRIMARY KEY,
    "order_id" VARCHAR(50) REFERENCES "orders"("id") ON DELETE CASCADE,
    "product_id" VARCHAR(50) REFERENCES "products"("id") ON DELETE RESTRICT,
    "quantity" INTEGER NOT NULL,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================================
-- 3. INSERCIÓN DE DATOS
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- CATÁLOGO DE CAJAS (BoxTypes)
-- Dimensiones en cm, peso en kg.
-- ------------------------------------------------------------------------------
INSERT INTO "box_types" ("id", "name", "width", "height", "depth", "max_weight") VALUES
('BOX-KRAFT-A5', 'Sobre Kraft Acolchado A5', 25.0, 15.0, 2.0, 1.0),
('BOX-CUBIC', 'Caja Cúbica', 25.0, 20.0, 15.0, 5.0),
('BOX-STD-L', 'Caja Estándar Grande', 40.0, 30.0, 20.0, 20.0),
('BOX-STD-M', 'Caja Estándar Mediana', 30.0, 20.0, 15.0, 10.0),
('BOX-TUBE', 'Tubo Postal', 10.0, 10.0, 60.0, 2.0);


-- ------------------------------------------------------------------------------
-- CATÁLOGO DE PRODUCTOS (SKUs)
-- Dimensiones en cm, peso en kg.
-- ------------------------------------------------------------------------------
INSERT INTO "products" ("id", "name", "category", "width", "height", "depth", "weight") VALUES
-- Caso 1 (Micro-producto)
('SKU-USB-32G', 'Memoria USB 32GB', 'Electrónica', 5.0, 2.0, 1.0, 0.05),

-- Caso 2 (Textil Múltiple) - Asumiendo dimensiones plegadas
('SKU-PANT-JEAN', 'Pantalón Vaquero Clásico', 'Ropa', 30.0, 20.0, 5.0, 0.50),
('SKU-SHIRT-WHT', 'Camiseta Básica Blanca', 'Ropa', 25.0, 15.0, 2.0, 0.20),
('SKU-BELT-LTHR', 'Cinturón de Cuero (Enrollado)', 'Ropa', 10.0, 10.0, 4.0, 0.15),

-- Caso 3 (Efecto Tetris)
('SKU-BOOK-HD', 'Libro Tapa Dura (Novela)', 'Libros', 23.0, 15.0, 3.0, 0.80),
('SKU-NOTEBOOK', 'Libreta A5', 'Libros', 21.0, 14.0, 1.0, 0.30);


-- ------------------------------------------------------------------------------
-- PEDIDOS DE PRUEBA (Experimento del Aire)
-- ------------------------------------------------------------------------------

-- CASO 1: Micro-producto (1 Memoria USB)
-- Output Esperado: Sobre Kraft Acolchado A5 (eliminando el 88.9% de volumen)
INSERT INTO "orders" ("id", "status") VALUES ('ORD-EXP-001', 'PENDING');
INSERT INTO "order_items" ("order_id", "product_id", "quantity") VALUES 
('ORD-EXP-001', 'SKU-USB-32G', 1);

-- CASO 2: Textil Múltiple (1 pantalón, 2 camisetas, 1 cinturón)
-- Output Esperado: Caja compacta (reducción del 70.6%)
INSERT INTO "orders" ("id", "status") VALUES ('ORD-EXP-002', 'PENDING');
INSERT INTO "order_items" ("order_id", "product_id", "quantity") VALUES 
('ORD-EXP-002', 'SKU-PANT-JEAN', 1),
('ORD-EXP-002', 'SKU-SHIRT-WHT', 2),
('ORD-EXP-002', 'SKU-BELT-LTHR', 1);

-- CASO 3: Efecto Tetris (3 libros tapa dura, 1 libreta)
-- Output Esperado: Apilado vertical con rotación 90 grados de la libreta, logrando caja cúbica
INSERT INTO "orders" ("id", "status") VALUES ('ORD-EXP-003', 'PENDING');
INSERT INTO "order_items" ("order_id", "product_id", "quantity") VALUES 
('ORD-EXP-003', 'SKU-BOOK-HD', 3),
('ORD-EXP-003', 'SKU-NOTEBOOK', 1);

-- OTROS PEDIDOS PARA TESTS VARIOS
INSERT INTO "orders" ("id", "status") VALUES ('ORD-TEST-004', 'PENDING');
INSERT INTO "order_items" ("order_id", "product_id", "quantity") VALUES 
('ORD-TEST-004', 'SKU-BOOK-HD', 1),
('ORD-TEST-004', 'SKU-USB-32G', 2);

-- ==============================================================================
-- FIN DEL SCRIPT
-- ==============================================================================
