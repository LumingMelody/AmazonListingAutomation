CREATE TABLE IF NOT EXISTS ad_performance (
    id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(100) NOT NULL,
    ad_group_id VARCHAR(100),
    keyword VARCHAR(200),
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    spend DECIMAL(10, 2) DEFAULT 0,
    sales DECIMAL(10, 2) DEFAULT 0,
    orders INTEGER DEFAULT 0,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ad_performance_campaign_date ON ad_performance(campaign_id, date);
CREATE INDEX IF NOT EXISTS idx_ad_performance_date ON ad_performance(date);

CREATE TABLE IF NOT EXISTS listing_metrics (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(20) NOT NULL,
    sku VARCHAR(50),
    sessions INTEGER DEFAULT 0,
    page_views INTEGER DEFAULT 0,
    units_ordered INTEGER DEFAULT 0,
    units_ordered_b2b INTEGER DEFAULT 0,
    unit_session_percentage DECIMAL(5, 2),
    ordered_product_sales DECIMAL(10, 2) DEFAULT 0,
    total_order_items INTEGER DEFAULT 0,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_listing_metrics_asin_date ON listing_metrics(asin, date);
CREATE INDEX IF NOT EXISTS idx_listing_metrics_sku_date ON listing_metrics(sku, date);

CREATE TABLE IF NOT EXISTS alert_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    condition VARCHAR(20) NOT NULL,
    threshold_value DECIMAL(10, 4) NOT NULL,
    time_window INTEGER DEFAULT 24,
    severity VARCHAR(20) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alert_history (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES alert_rules(id),
    asin VARCHAR(20),
    sku VARCHAR(50),
    metric_value DECIMAL(10, 4),
    threshold_value DECIMAL(10, 4),
    message TEXT,
    severity VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_alert_history_status ON alert_history(status);
CREATE INDEX IF NOT EXISTS idx_alert_history_created_at ON alert_history(created_at);
