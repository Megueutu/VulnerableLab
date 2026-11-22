# Fintech

Diretório público de agências fictícias. Use `make up LAB=rest/fintech-r-01` na raiz. Consulte `GET http://127.0.0.1:8082/branches` e `GET http://127.0.0.1:8082/health`. Pare com `make down LAB=rest/fintech-r-01`.

## Arquitetura

O serviço bank recebe tráfego no loopback e consulta account-data por uma rede interna. Account-data serve dados fictícios e não publica porta no host. O contrato público é de leitura e limitado a agências. A saúde indica que o processo de borda está ativo. O diretório responde com 502 quando a dependência está indisponível.
