CREATE TABLE IF NOT EXISTS compliance_rules (
    id SERIAL PRIMARY KEY,
    rule_type VARCHAR(50) NOT NULL,
    pattern TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,
    action VARCHAR(20) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blacklist_keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_blacklist_keyword ON blacklist_keywords(keyword);

CREATE TABLE IF NOT EXISTS qa_checkpoints (
    id SERIAL PRIMARY KEY,
    checkpoint_name VARCHAR(100) NOT NULL,
    checkpoint_type VARCHAR(50) NOT NULL,
    validation_rule JSONB NOT NULL,
    weight DECIMAL(3, 2) DEFAULT 1.0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS approval_records (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL,
    job_type VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20),
    approver VARCHAR(100),
    action VARCHAR(20) DEFAULT 'pending',
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_approval_job_id ON approval_records(job_id);

CREATE TABLE IF NOT EXISTS compliance_check_results (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL,
    check_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    findings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_compliance_result_job_id ON compliance_check_results(job_id);
