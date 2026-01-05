-- SQL Migration: Optimization & Premium Features
USE `CRM`;

-- 1. Estandarización de Identificadores (RUT/NIT)
-- Cambiamos bigint a VARCHAR para soportar guiones o formatos internacionales
ALTER TABLE `companies` MODIFY `tax_id` VARCHAR(50) NOT NULL;

-- 2. Índices de Rendimiento (Búsqueda Instantánea)
-- Añadimos índices en campos que se filtran frecuentemente
ALTER TABLE `companies` ADD INDEX `idx_legal_name` (`legal_name`);
ALTER TABLE `companies` ADD INDEX `idx_commercial_name` (`commercial_name`);
ALTER TABLE `users` ADD INDEX `idx_last_name` (`last_name`);
ALTER TABLE `users` ADD INDEX `idx_tax_id` (`tax_id`);

-- 3. Trazabilidad (Auditoría) en Tablas de Contacto
-- Añadimos marcas de tiempo para saber cuándo se creó/actualizó cada dato

-- Correos
ALTER TABLE `emails` 
ADD COLUMN `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Teléfonos
ALTER TABLE `phones` 
ADD COLUMN `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Direcciones
ALTER TABLE `addresses` 
ADD COLUMN `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- 4. Precisión Geográfica
-- Cambiamos código postal a VARCHAR para no perder ceros iniciales
ALTER TABLE `addresses` MODIFY `postal_code` VARCHAR(10);

-- Confirmación del estado final
SHOW COLUMNS FROM `companies`;
SHOW COLUMNS FROM `addresses`;
