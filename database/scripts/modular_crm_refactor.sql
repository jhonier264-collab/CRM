-- SQL Migration: CRM Modular & Reciprocal Relations (Phase 8)
USE `CRM`;

-- 1. Refactorización de Usuarios (Traducción y Expansión Google Style)
-- Renombramos los campos en español identificados en users.csv
ALTER TABLE `users` 
    CHANGE COLUMN `fonetica_nombre` `phonetic_first_name` TEXT NULL,
    CHANGE COLUMN `fonetica_segundo_nombre` `phonetic_middle_name` TEXT NULL,
    CHANGE COLUMN `fonetica_apellido` `phonetic_last_name` TEXT NULL,
    CHANGE COLUMN `seudonimo` `nickname` VARCHAR(255) NULL,
    CHANGE COLUMN `archivar_como` `file_as` VARCHAR(255) NULL;

-- Añadir campos de datos únicos que no estaban (Google Standard)
ALTER TABLE `users`
    ADD COLUMN IF NOT EXISTS `birthday` DATE NULL AFTER `rut_nit`,
    ADD COLUMN IF NOT EXISTS `gender` VARCHAR(50) NULL AFTER `birthday`,
    ADD COLUMN IF NOT EXISTS `notes` TEXT NULL AFTER `gender`;

-- 2. Sistema de Relaciones Recíprocas (Empresas y Usuarios)
-- Corregimos la tabla de tipos para que sea genérica y tenga reciprocidad
ALTER TABLE `relation_types` 
    CHANGE COLUMN `first_name` `name` VARCHAR(100) NOT NULL,
    ADD COLUMN IF NOT EXISTS `inverse_name` VARCHAR(100) NULL AFTER `name`;

-- Insertar nombres inversos para las relaciones de empresas existentes
UPDATE `relation_types` SET `inverse_name` = 'Subsidiaria / Secundaria' WHERE `id` = 1; -- Si 1 es Matriz
UPDATE `relation_types` SET `inverse_name` = 'Matriz / Principal' WHERE `id` = 2; -- Si 2 es Subsidiaria
UPDATE `relation_types` SET `inverse_name` = 'Aliada Estratégica' WHERE `id` = 3; -- Simétrica
UPDATE `relation_types` SET `inverse_name` = 'Asocida' WHERE `id` = 4; -- Simétrica

-- 3. Tabla de Relaciones entre Usuarios (Personas)
CREATE TABLE IF NOT EXISTS `user_user_relations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `from_user_id` INT NOT NULL,
    `to_user_id` INT NOT NULL,
    `relation_type_id` INT NOT NULL,
    `custom_label` VARCHAR(100) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`from_user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`to_user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`relation_type_id`) REFERENCES `relation_types`(`id`),
    UNIQUE KEY `unique_user_rel` (`from_user_id`, `to_user_id`, `relation_type_id`)
);

-- 4. Sistema Modular de Etiquetas (Tags)
CREATE TABLE IF NOT EXISTS `tags` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL UNIQUE,
    `color` VARCHAR(20) DEFAULT '#808080',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `user_tags` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `tag_id` INT NOT NULL,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`tag_id`) REFERENCES `tags`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_user_tag` (`user_id`, `tag_id`)
);

-- 5. Metadatos del Esquema (Para el Gestor de Columnas Dinámicas)
CREATE TABLE IF NOT EXISTS `custom_columns_metadata` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `table_name` VARCHAR(100) NOT NULL,
    `column_name` VARCHAR(100) NOT NULL,
    `display_name` VARCHAR(100) NOT NULL,
    `data_type` VARCHAR(50) NOT NULL,
    `is_protected` TINYINT(1) DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `unique_col` (`table_name`, `column_name`)
);
