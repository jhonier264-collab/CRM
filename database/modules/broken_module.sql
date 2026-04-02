-- Broken Module: Rollback Test
-- This script contains a syntax error at the end to trigger a rollback.

CREATE TABLE IF NOT EXISTS rollback_success (id INT PRIMARY KEY);

-- Intentional error
CREATE TABLE rollback_fail (id INT PRIMARY KEY, broken_col INVALID_TYPE);
