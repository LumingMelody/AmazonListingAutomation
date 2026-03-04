CREATE TABLE IF NOT EXISTS experiment_configs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    min_sample_size INTEGER DEFAULT 100,
    cvr_threshold DECIMAL(5, 4),
    refund_rate_threshold DECIMAL(5, 4),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS listing_lifecycle (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(20) NOT NULL,
    sku VARCHAR(50),
    status VARCHAR(20) NOT NULL,
    stage VARCHAR(20) NOT NULL,
    score DECIMAL(5, 2),
    sessions_total INTEGER DEFAULT 0,
    orders_total INTEGER DEFAULT 0,
    cvr DECIMAL(5, 4),
    refund_rate DECIMAL(5, 4),
    test_start_date DATE,
    test_end_date DATE,
    decision VARCHAR(20),
    decision_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_lifecycle_asin ON listing_lifecycle(asin);
CREATE INDEX IF NOT EXISTS idx_lifecycle_status ON listing_lifecycle(status);
CREATE INDEX IF NOT EXISTS idx_lifecycle_stage ON listing_lifecycle(stage);

CREATE TABLE IF NOT EXISTS competitor_snapshots (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(20) NOT NULL,
    competitor_asin VARCHAR(20) NOT NULL,
    price DECIMAL(10, 2),
    rating DECIMAL(3, 2),
    review_count INTEGER,
    rank INTEGER,
    availability VARCHAR(50),
    snapshot_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_competitor_asin_date ON competitor_snapshots(asin, snapshot_date);
CREATE INDEX IF NOT EXISTS idx_competitor_competitor_asin ON competitor_snapshots(competitor_asin);

CREATE TABLE IF NOT EXISTS action_recommendations (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(20) NOT NULL,
    sku VARCHAR(50),
    recommendation_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    data JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_action_recommendation_asin_status ON action_recommendations(asin, status);
CREATE INDEX IF NOT EXISTS idx_action_recommendation_type ON action_recommendations(recommendation_type);
