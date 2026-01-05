-- SQL Migration: Gender Normalization & Relation Separation (Phase 8.2)
USE `CRM`;

-- 1. Normalización de Géneros
CREATE TABLE IF NOT EXISTS `genders` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL UNIQUE
);

INSERT IGNORE INTO `genders` (`name`) VALUES ('Masculino'), ('Femenino'), ('Otro');

-- Cambiar columna gender en users por gender_id
-- Primero añadimos la nueva columna
ALTER TABLE `users` ADD COLUMN IF NOT EXISTS `gender_id` INT NULL AFTER `birthday`;

-- (Opcional) Si ya había datos en 'gender', podríamos intentar un mapeo, 
-- pero como es una implementación nueva, procedemos a borrar la antigua.
ALTER TABLE `users` DROP COLUMN IF EXISTS `gender`;

-- Añadir FK
ALTER TABLE `users` ADD CONSTRAINT `fk_user_gender` FOREIGN KEY (`gender_id`) REFERENCES `genders`(`id`);

-- 2. Separación de Tipos de Relación
-- Renombrar la tabla actual que se usa para empresas
RENAME TABLE `relation_types` TO `company_relation_types`;

-- Crear la tabla específica para relaciones entre usuarios (humanas)
CREATE TABLE IF NOT EXISTS `user_relation_types` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `inverse_name` VARCHAR(100) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar algunos tipos por defecto para humanos
INSERT IGNORE INTO `user_relation_types` (`name`, `inverse_name`) VALUES 
('Jefe', 'Empleado'),
('Asistente', 'Superior'),
('Familiar', 'Familiar'),
('Mentor', 'Aprendiz'),
('Amigo', 'Amigo');

-- 3. Actualización de Claves Foráneas
-- En company_associations ya apunta a lo que ahora es company_relation_types (por el rename)
-- Pero vamos a asegurar el nombre de la FK e integridad
ALTER TABLE `company_associations` DROP FOREIGN KEY `fk_holding_type`;
ALTER TABLE `company_associations` ADD CONSTRAINT `fk_company_rel_type` 
    FOREIGN KEY (`relation_type_id`) REFERENCES `company_relation_types`(`id`);

-- En user_user_relations, debemos re-apuntar a user_relation_types
ALTER TABLE `user_user_relations` DROP FOREIGN KEY `user_user_relations_ibfk_3`; -- Nombre por defecto de MySQL
ALTER TABLE `user_user_relations` ADD CONSTRAINT `fk_user_rel_type` 
    FOREIGN KEY (`relation_type_id`) REFERENCES `user_relation_types`(`id`);
