CREATE TABLE IF NOT EXISTS settings (
    name TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    measure TEXT NOT NULL,
    icon TEXT NOT NULL,
    tone TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
    stock INTEGER NOT NULL CHECK (stock >= 0)
);

CREATE TABLE IF NOT EXISTS pickup_slots (
    starts_at TEXT PRIMARY KEY,
    capacity INTEGER NOT NULL CHECK (capacity > 0)
);

CREATE TABLE IF NOT EXISTS reservations (
    code TEXT PRIMARY KEY,
    draft_key TEXT NOT NULL UNIQUE,
    customer TEXT NOT NULL,
    contact TEXT NOT NULL,
    starts_at TEXT NOT NULL REFERENCES pickup_slots (starts_at),
    status TEXT NOT NULL CHECK (status IN ('pending', 'preparing', 'ready', 'collected', 'cancelled')),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reservation_items (
    reservation_code TEXT NOT NULL REFERENCES reservations (code),
    product_id INTEGER NOT NULL REFERENCES products (id),
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0),
    PRIMARY KEY (reservation_code, product_id)
);
