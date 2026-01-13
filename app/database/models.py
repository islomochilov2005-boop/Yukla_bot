"""Ma'lumotlar bazasi modellari"""

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(100),
    first_name VARCHAR(255),
    join_date TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW(),
    is_blocked BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_users_active ON users(last_active);

CREATE TABLE IF NOT EXISTS downloads (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    platform VARCHAR(20) NOT NULL,
    quality VARCHAR(10) NOT NULL,
    file_size BIGINT,
    date TIMESTAMP DEFAULT NOW(),
    success BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_downloads_date ON downloads(date);
CREATE INDEX IF NOT EXISTS idx_downloads_user ON downloads(user_id);

-- URL mapping jadvali (callback_data qisqartirish uchun)
CREATE TABLE IF NOT EXISTS url_mappings (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_url_mappings_url ON url_mappings(url);
"""