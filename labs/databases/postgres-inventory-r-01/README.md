# PostgreSQL · permissões de estoque

Laboratório local de menor privilégio com PostgreSQL 17 e um estoque fictício. O contrato SQL usa a tabela `stock.items(sku, name, quantity)`. O servidor escuta no loopback do contêiner, acessível pelos exemplos com `docker compose exec`.

| Papel | Consultar | Inserir | Atualizar | Excluir | Criar tabela em `stock` |
|---|---|---|---|---|---|
| `inventory_reader` | Sim | Bloqueado | Bloqueado | Bloqueado | Bloqueado |
| `inventory_writer` | Sim | Sim | Sim | Bloqueado | Bloqueado |

Na pasta do laboratório, inicie o serviço.

```sh
docker compose up -d --wait
```

## Exercício

1. Entre com o papel de leitura. O primeiro comando SQL retorna o estoque. O segundo deve produzir um erro de permissão.

   ```sh
   docker compose exec -e PGPASSWORD=lab_reader db psql -X -h 127.0.0.1 -U inventory_reader -d inventory
   ```

   ```sql
   SELECT current_user, sku, name, quantity FROM stock.items ORDER BY sku;
   UPDATE stock.items SET quantity = 10 WHERE sku = 'CAB-01';
   \q
   ```

2. Entre com o papel de escrita. Registre uma entrada de estoque e consulte o resultado. A tentativa de exclusão deve retornar um erro de permissão. O rollback desfaz as mudanças do exercício.

   ```sh
   docker compose exec -e PGPASSWORD=lab_writer db psql -X -h 127.0.0.1 -U inventory_writer -d inventory
   ```

   ```sql
   BEGIN;
   INSERT INTO stock.items VALUES ('EX-01', 'Adaptador HDMI', 2);
   UPDATE stock.items SET quantity = 3 WHERE sku = 'EX-01';
   SELECT sku, name, quantity FROM stock.items WHERE sku = 'EX-01';
   DELETE FROM stock.items WHERE sku = 'EX-01';
   ROLLBACK;
   \q
   ```

3. Compare os resultados com os comandos `GRANT` em [sql/01-inventory.sql](sql/01-inventory.sql). Identifique as permissões necessárias para conectar ao banco, acessar o esquema e escrever na tabela.

## Verificação

O script assume cada papel em uma transação, executa operações permitidas e verifica o código `42501` nas operações bloqueadas. Ele desfaz as alterações ao terminar. As senhas dos exemplos pertencem ao ambiente local.

```sh
docker compose exec -T -e PGPASSWORD=lab_admin db psql -X -h 127.0.0.1 -U postgres -d inventory < sql/verify.sql
docker compose down
```
