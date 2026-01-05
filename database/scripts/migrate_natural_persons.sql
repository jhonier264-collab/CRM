-- SQL Migration: Final Identity Consolidation (B2B/B2C Clean-up)
USE `CRM`;

-- 1. Identificar y marcar a los usuarios que pertenecen a la empresa dummy (ID 1)
-- Les ponemos el flag de persona natural y aseguramos que su RUT esté registrado.
UPDATE `users` u
JOIN `user_companies` uc ON u.id = uc.user_id
SET u.is_natural_person = 1
WHERE uc.company_id = 1;

-- 2. Limpieza de Vínculos Obsoletos
-- Borramos las relaciones con la empresa dummy (ID 1)
DELETE FROM `user_companies` WHERE company_id = 1;

-- 3. Eliminación de la Empresa Dummy
-- Eliminamos definitivamente la empresa "Persona Natura"
DELETE FROM `companies` WHERE id = 1;

-- 4. Verificación de Resultados
SELECT id, first_name, last_name, rut_nit, is_natural_person 
FROM `users` 
WHERE is_natural_person = 1;
