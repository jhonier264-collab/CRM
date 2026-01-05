-- SQL Migration: Soft Delete Support (Phase 9)
USE `CRM`;

-- Añadir soporte de borrado lógico a usuarios
ALTER TABLE `users` ADD COLUMN IF NOT EXISTS `deleted_at` TIMESTAMP NULL DEFAULT NULL AFTER `updated_at`;

-- Añadir soporte de borrado lógico a empresas
ALTER TABLE `companies` ADD COLUMN IF NOT EXISTS `deleted_at` TIMESTAMP NULL DEFAULT NULL AFTER `updated_at`;

-- Índice para optimizar búsquedas de registros activos
CREATE INDEX idx_users_deleted_at ON `users`(`deleted_at`);
CREATE INDEX idx_companies_deleted_at ON `companies`(`deleted_at`);
