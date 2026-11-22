# Handoff dos labs

## Identificador

Para uma aplicação única, use `labs/<type>/<stack>-<purpose>-<profile>-<number>/`. Para uma aplicação com vários serviços próprios, use `labs/<type>/<purpose>-<profile>-<number>/` e dê a cada serviço uma pasta `ms-<stack>-<role>/` na raiz do lab. A stack e a função ficam no serviço, pois podem variar dentro do mesmo cenário.

Use `rest`, `graphql`, `grpc`, `web` e `databases` como categorias. Escolha uma finalidade em inglês que descreva o produto, como `fintech`, `bank`, `marketplace`, `ecommerce`, `shop` ou `inventory`. A numeração começa em `01` por combinação de tipo, finalidade, perfil e stack nos labs de aplicação única. Nos labs multisserviço, a sequência pertence à combinação de tipo, finalidade e perfil. Use no mínimo dois dígitos e preserve IDs publicados.

| Stack | Identificador |
|---|---|
| Spring Boot | `sb` |
| Quarkus | `quarkus` |
| FastAPI | `fast` |
| Flask | `flask` |
| Django / Django REST Framework | `dj` |
| Ruby on Rails | `rails` |
| NestJS | `nest` |
| Express | `express` |
| ASP.NET Core | `aspnet` |
| Laravel | `laravel` |
| Gin | `gin` |
| grpc-go | `grpcgo` |
| PostgreSQL, para labs de banco | `postgres` |

Sem framework de servidor, use o nome da linguagem, como `java`, `go`, `python`, `ruby`, `javascript` ou `typescript`. Bibliotecas de cliente como Axios entram na ficha técnica. Registre novas abreviações nesta tabela antes de usá-las.

| Perfil | Significado |
|---|---|
| `n` | Não especificado. Implementação direta, com arquitetura e revisão proporcionais ao exercício. |
| `v` | Vibe-coded. Simula um briefing escrito só em termos de produto. O agente decide a implementação e valida o fluxo funcional com dados fictícios. |
| `r` | Robusto. Modelagem explícita de permissões e limites de confiança, revisão técnica e testes dos controles relevantes. |

O perfil descreve como o lab foi produzido e revisado. Registre a dificuldade do exercício separadamente quando houver dados para estimá-la.

## Estrutura

Uma API única pode manter o código diretamente na raiz do lab, segundo a estrutura nativa da stack. Em um lab com vários serviços, deixe o Compose e o README na raiz e crie uma pasta `ms-<stack>-<role>/` por serviço próprio. Bancos, caches e filas são dependências. Se houver um serviço de acesso a dados, nomeie-o pela função que desempenha, como `ms-python-account-data`.

```text
labs/rest/
├── sb-fintech-r-01/
│   ├── README.md
│   ├── compose.yaml
│   └── src/
├── java-fintech-n-02/
│   ├── README.md
│   ├── compose.yaml
│   └── src/
└── fintech-r-01/
    ├── README.md
    ├── compose.yaml
    ├── ms-python-bank/
    └── ms-python-account-data/
```

Os nomes de diretórios e arquivos são em inglês. Use o case idiomático da stack, como `AccountController.java` e `account_controller.rb`. Use kebab-case nos IDs e nomes de serviços. Preserve nomes exigidos por ferramentas, como `README.md` e `Dockerfile`. Subtrees externos preservam o nome e o layout do upstream. Cenários que combinam várias superfícies podem ter seu próprio diretório em `scenarios/<name>/`.

## Instruções para agentes

1. Defina finalidade, interface de entrada, perfil e topologia antes de implementar. Reserve o identificador no catálogo.
2. Varie arquitetura, padrões de código, profundidade do planejamento e revisão conforme o perfil. Em `n`, priorize o fluxo direto. Em `v`, parta de jornadas escritas em linguagem de produto e registre as decisões tomadas a partir delas. Em `r`, documente as decisões, revise os controles e cubra os casos permitidos e negados. Em comparações de stacks, mantenha o contrato e as regras de negócio equivalentes.
3. Use dados e contas fictícios. Publique apenas a interface local prevista e mantenha dependências internas na rede do Compose. Descreva permissões e conexões esperadas, incluindo quais serviços acessam banco, cache ou fila.
4. Entregue `README.md` e `compose.yaml` na raiz do lab. No README, inclua objetivo, stack, contrato, ponto de entrada, contas de teste e comandos. Registre a topologia e a revisão em uma seção de arquitetura separada do enunciado inicial.
5. Verifique que o lab sobe, responde pela interface documentada e pode ser parado. Registre quais verificações executou. Use `make up LAB=<type>/<id>` nas categorias suportadas.

## Catálogo

| Caminho relativo a `labs/` | Stack | Finalidade | Perfil | Serviços próprios | Estado |
|---|---|---|---|---:|---|
| `rest/crapi` | Múltiplas | API veicular | Upstream | — | Importação pendente |
| `rest/sb-fintech-r-01` | Spring Boot | Fintech | R | 1 | Planejado |
| `rest/java-fintech-n-02` | Java sem framework | Fintech | N | 1 | Exemplo de ID |
| `rest/fintech-r-01` | Python padrão | Fintech | R | 2 | Implementado |
| `rest/python-shop-n-01` | Python padrão | Shop | N | 1 | Implementado |
| `rest/quarkus-fintech-r-01` | Quarkus | Fintech | R | 1 | Planejado |
| `rest/fast-shop-v-01` | FastAPI | Shop | V | 1 | Planejado |
| `graphql/nest-ecommerce-n-01` | NestJS | Ecommerce | N | 1 | Planejado |
| `grpc/grpcgo-inventory-n-01` | Go com grpc-go | Estoque | N | 1 | Planejado |
| `web/rails-shop-n-01` | Rails | Shop | N | 1 | Planejado |
| `databases/postgres-fintech-r-01` | PostgreSQL | Fintech | R | 0 | Planejado |
| `web/flask-shop-v-01` | Flask | Mercearia | V | 1 | Implementado |
| `web/python-shifts-n-01` | Python padrão | Turnos | N | 1 | Implementado |
| `databases/postgres-inventory-r-01` | PostgreSQL | Inventário | R | 0 | Implementado |

A rodada dos três labs originais está em [decisões de design](original-labs-design.md).

## Decisões de revisão

### Rodada 1 — Identidade e escopo

| Pergunta | Decisão |
|---|---|
| O que o diretório raiz identifica? | Uma aplicação executável. Em aplicação única, o ID inclui a stack. Em aplicação multisserviço, o ID usa finalidade, perfil e número. |
| Quando um cenário tem múltiplas interfaces? | A interface principal para quem inicia o exercício define a categoria. Interfaces secundárias aparecem no catálogo e no README. Use `scenarios/` para experiências que agrupam aplicações independentes ou têm várias entradas igualmente centrais. |
| O perfil é dificuldade ou processo? | É uma escolha sobre implementação e revisão. Dificuldade fica em campo separado e só é estimada quando houver um exercício definido. N, V e R bastam nesta fase. |
| A finalidade é livre? | Use um termo curto em inglês e reaproveite um termo já catalogado quando descrever o mesmo domínio. |

### Rodada 2 — Topologia e contrato de execução

| Pergunta | Decisão |
|---|---|
| Onde entram stack e função de cada serviço? | Em `ms-<stack>-<role>/`, direto na raiz do lab. Exemplos válidos são `ms-quarkus-bank`, `ms-sb-auth` e `ms-python-account-data`. Python sem framework segue a regra da linguagem por extenso. |
| O que conta como serviço próprio? | API, frontend com processo próprio ou worker implantável. Banco, fila e cache padrão são dependências do Compose. Uma API própria de acesso a dados conta como serviço. |
| Onde fica o ponto de entrada? | O Compose declara as portas publicadas e o README informa o endereço de entrada. Na fintech atual, só `bank` publica uma porta em loopback. `account-data` fica na rede interna `data`. |
| Como o Make seleciona o lab? | `LAB=<type>/<id>` aponta para o Compose na raiz. Os nomes das pastas `ms-` não entram nesse seletor. Subtrees seguem o layout do upstream, como acontece com o caminho previsto para o crAPI. |
| Como manter atividades independentes? | Cada lab tem seu Compose. Use portas locais distintas para os exemplos que podem rodar juntos. A loja usa 8081 e a fintech usa 8082. |

### Rodada 3 — Evolução e verificação

| Pergunta | Decisão |
|---|---|
| Quando criar outro ID? | Quando surgir uma variante com outro perfil, finalidade ou contrato de exercício. Ao ampliar uma aplicação multisserviço, mantenha seu ID e atualize a ficha. Se uma aplicação única virar multisserviço, registre a mudança de caminho explicitamente e vincule os IDs no catálogo. |
| Como comparar implementações? | Registre os IDs relacionados e declare a variável da comparação, como stack, perfil ou topologia. Só chame de comparação controlada quando o contrato e as regras de negócio forem equivalentes. |
| O que os dois primeiros exemplos demonstram? | A loja demonstra uma pasta de aplicação única. A fintech demonstra dois serviços e uma rede interna no Compose. Como os contratos diferem, são exemplos de layout, não um experimento controlado de topologia. |
| O que conta como validado? | Registre separadamente testes HTTP, verificação do Compose e execução dos contêineres. Um teste HTTP local pode provar o contrato sem provar o isolamento da implantação. |
| O que falta para comparar os perfis? | Um par de labs do mesmo domínio com contrato e dados de teste equivalentes, critérios de revisão explícitos e a variável escolhida registrada no catálogo. A implementação atual já fornece exemplos de nomenclatura e execução para começar. |

Os primeiros exemplos usam somente dados públicos fictícios, sem contas de teste. A fintech aplica R ao isolamento e ao tratamento de falha da dependência neste recorte. As rotas e a integração HTTP foram verificadas localmente em Python. A execução pelo Compose ficou pendente.
