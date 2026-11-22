# Decisões dos três labs originais

## Rodada 1 — Objetivo

1. **O que o perfil V representa?** Um briefing que descreve o produto sem prescrever a solução técnica. A aplicação serve de material para observar e revisar o comportamento que resulta desse processo. Os nomes, rotas e regras definitivas ficam no próprio lab.
2. **O que os dois outros labs precisam acrescentar?** Duas superfícies distintas. O quadro de turnos é um exercício de aplicação web com formulários. O inventário PostgreSQL é um exercício de privilégios no banco. A mercearia também usa a categoria web porque o exercício começa no navegador, mas tem um fluxo de produto mais completo e usa Flask.
3. **Qual é o limite dos ambientes?** Instâncias locais, separadas, com dados fictícios. A mercearia e o quadro de turnos expõem interfaces em loopback. O PostgreSQL é acessado pelo contêiner.

## Rodada 2 — Isolamento do briefing e contratos

4. **Quem redige e quem implementa o briefing?** Um subagente de produto elabora os prompts sem herdar a sessão. Outro subagente, também sem histórico, recebe os três prompts em ordem em uma única mensagem. Flask, caminho, porta e arquivos de execução entram num envelope de integração separado do briefing.
5. **Onde ficam as entradas do experimento?** Em `labs/web/flask-shop-v-01/prompts/`, com os textos numerados e o envelope registrado. São os textos efetivamente entregues ao implementador. Uma futura execução com três interações separadas deve ser identificada no registro.
6. **O que define a mercearia completa?** Catálogo, busca, quantidades, revisão, confirmação, acompanhamento e cancelamento. Para a equipe, fila de retirada, alterações de estado e atualização de disponibilidade. A disputa pela última unidade faz parte da regra de estoque do produto.
7. **O que cada um dos outros labs entrega?** No quadro de turnos, a interação passa por páginas e formulários. No PostgreSQL, a atividade compara operações permitidas e negadas para papéis diferentes com dados de inventário fictícios.

## Rodada 3 — Aceite e continuidade

8. **Como executar os três?** Cada diretório tem README e Compose próprios. O catálogo registra a categoria e o perfil. A seleção usa `make up LAB=<type>/<id>`.
9. **Como declarar o que passou?** Registre resultados de testes de aplicação separados de testes com Docker Compose. Um teste local pode comprovar o comportamento funcional sem verificar a implantação.
10. **Como repetir o lab V?** Reutilize os prompts e o envelope em um contexto novo, guarde o código como uma nova variante e registre quais entradas mudaram. O perfil V identifica o processo do briefing.

## Verificação da entrega

- Mercearia: cliente de teste Flask verificou catálogo, reserva, disputa pela última unidade, acompanhamento, cancelamento e mudanças de estado pela equipe.
- Quadro de turnos: fluxo HTTP local de reserva e liberação, isolamento de sessões e validação do token de formulário.
- Inventário: SQL executado no PostgreSQL embarcado PGlite, com adaptação do nome do banco e remoção do metacomando do cliente psql. As operações permitidas e negadas e o rollback passaram.
- Docker Compose: revisão estática da configuração e verificação do encaminhamento do Makefile. A execução com contêineres ficou pendente porque o ambiente não tem Docker.
