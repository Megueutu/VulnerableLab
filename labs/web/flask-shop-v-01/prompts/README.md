# Registro dos prompts

O subagente de produto recebeu a tarefa de escrever três prompts curtos, em português, na perspectiva de uma pessoa de produto sem instruções técnicas. O subagente implementador recebeu os três textos abaixo em um único envio, nessa ordem, em contexto novo.

1. [Catálogo](01-catalog.md)
2. [Reserva](02-reservation.md)
3. [Operação da loja](03-store-operations.md)

## Envelope de integração

A instrução externa ao briefing pediu uma aplicação completa em Flask, no caminho local `/tmp/vlab-wave/labs/web/flask-shop-v-01`, com Dockerfile, Compose na porta local 8083, README, nomes de arquivos em inglês e validação dos fluxos. O implementador recebeu também a instrução de manter os padrões normais do framework e não publicar por conta própria. A escolha de Flask e esses requisitos vieram da integração com o repositório.
