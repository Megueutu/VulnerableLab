\set ON_ERROR_STOP on

BEGIN;

SET LOCAL ROLE inventory_reader;

DO $$
DECLARE
    statement text;
BEGIN
    PERFORM sku, name, quantity FROM stock.items LIMIT 1;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'O estoque de exemplo está vazio';
    END IF;
    RAISE NOTICE '%: SELECT permitido', current_user;

    FOREACH statement IN ARRAY ARRAY[
        'INSERT INTO stock.items VALUES (gen_random_uuid()::text, ''Item de teste'', 1)',
        'UPDATE stock.items SET quantity = 0',
        'DELETE FROM stock.items',
        'CREATE TABLE stock.denied_table (id integer)'
    ] LOOP
        BEGIN
            EXECUTE statement;
            RAISE EXCEPTION '% executou um comando que deveria ser bloqueado: %',
                current_user, statement;
        EXCEPTION WHEN insufficient_privilege THEN
            RAISE NOTICE '%: % bloqueado (SQLSTATE %)',
                current_user, split_part(statement, ' ', 1), SQLSTATE;
        END;
    END LOOP;
END;
$$;

RESET ROLE;
SET LOCAL ROLE inventory_writer;

DO $$
DECLARE
    test_sku text := gen_random_uuid()::text;
    statement text;
BEGIN
    INSERT INTO stock.items VALUES (test_sku, 'Item de teste', 1);
    UPDATE stock.items SET quantity = 2 WHERE sku = test_sku;
    PERFORM 1 FROM stock.items WHERE sku = test_sku AND quantity = 2;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'A alteração de estoque não foi encontrada';
    END IF;
    RAISE NOTICE '%: INSERT, UPDATE e SELECT permitidos', current_user;

    FOREACH statement IN ARRAY ARRAY[
        'DELETE FROM stock.items',
        'CREATE TABLE stock.denied_table (id integer)'
    ] LOOP
        BEGIN
            EXECUTE statement;
            RAISE EXCEPTION '% executou um comando que deveria ser bloqueado: %',
                current_user, statement;
        EXCEPTION WHEN insufficient_privilege THEN
            RAISE NOTICE '%: % bloqueado (SQLSTATE %)',
                current_user, split_part(statement, ' ', 1), SQLSTATE;
        END;
    END LOOP;
END;
$$;

ROLLBACK;
