-- Module: Business Pipeline
-- Description: Manages deals, stages and quotes for a specific tenant.

-- 1. Deal Stages (Predefined stages)
CREATE TABLE IF NOT EXISTS deal_stages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    display_order INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO deal_stages (name, display_order) VALUES 
('Prospecting', 1),
('Proposal', 2),
('Execution', 3),
('Closed Won', 4),
('Closed Lost', 5);

-- 2. Deals (Business Opportunities)
CREATE TABLE IF NOT EXISTS deals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company_id INT DEFAULT NULL,
    contact_id INT DEFAULT NULL,
    value DECIMAL(15, 2) DEFAULT 0.00,
    stage_id INT DEFAULT 1,
    expected_closing_date DATE DEFAULT NULL,
    agent_id INT DEFAULT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (stage_id) REFERENCES deal_stages(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Quotes (Financial Proposals)
CREATE TABLE IF NOT EXISTS quotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    deal_id INT NOT NULL,
    quote_number VARCHAR(50) NOT NULL UNIQUE,
    total_amount DECIMAL(15, 2) DEFAULT 0.00,
    status ENUM('Draft', 'Sent', 'Accepted', 'Rejected', 'Expired') DEFAULT 'Draft',
    valid_until DATE DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (deal_id) REFERENCES deals(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
