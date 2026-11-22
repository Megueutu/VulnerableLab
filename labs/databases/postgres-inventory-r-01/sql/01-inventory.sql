BEGIN;

CREATE ROLE inventory_reader LOGIN PASSWORD 'lab_reader';
CREATE ROLE inventory_writer LOGIN PASSWORD 'lab_writer';

REVOKE ALL ON DATABASE inventory FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT CONNECT ON DATABASE inventory TO inventory_reader, inventory_writer;

CREATE SCHEMA stock;
CREATE TABLE stock.items (
    sku text PRIMARY KEY,
    name text NOT NULL,
    quantity integer NOT NULL CHECK (quantity >= 0)
);

INSERT INTO stock.items (sku, name, quantity) VALUES
    ('CAB-01', 'Cabo USB-C', 12),
    ('SUP-01', 'Suporte de monitor', 4);

GRANT USAGE ON SCHEMA stock TO inventory_reader, inventory_writer;
GRANT SELECT ON stock.items TO inventory_reader;
GRANT SELECT, INSERT, UPDATE ON stock.items TO inventory_writer;

COMMIT;
