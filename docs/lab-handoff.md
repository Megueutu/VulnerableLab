# Handoff dos labs

## Identificador

Use `labs/<type>/<stack>-<purpose>-<profile>-<number>/`. Para vários serviços próprios implantáveis separadamente, use `labs/<type>/ms-<stack>-<purpose>-<profile>-<number>/`. O tipo e a stack descrevem a interface e a implementação do ponto de entrada principal. Registre as demais stacks e a quantidade de serviços no catálogo e no README local. Bancos, caches e filas usados como infraestrutura não contam como serviços próprios.

Use `rest`, `graphql`, `grpc`, `web` e `databases` como categorias. Escolha uma finalidade em inglês que descreva o produto, como `fintech`, `bank`, `marketplace`, `ecommerce`, `shop` ou `inventory`. A numeração começa em `01` por combinação de tipo, prefixo, stack, finalidade e perfil. Use no mínimo dois dígitos e preserve IDs publicados.

| Stack | Identificador |
|---|---|
| Spring Boot | `sb` |
| Quarkus | `quarkus` |
| FastAPI | `fast` |
| Django / Django REST Framework | `dj` |
| Ruby on Rails | `rails` |
| NestJS | `nest` |
| Express | `express` |
| ASP.NET Core | `aspnet` |
| Laravel | `laravel` |
| Gin | `gin` |
| PostgreSQL, para labs de banco | `postgres` |

Sem framework de servidor, use o nome da linguagem, como `java`, `go`, `python`, `ruby`, `javascript` ou `typescript`. Bibliotecas de cliente como Axios entram na ficha técnica. Registre novas abreviações nesta tabela antes de usá-las.

| Perfil | Significado |
|---|---|
| `n` | Não especificado. Implementação direta, com arquitetura e revisão proporcionais ao exercício. |
| `v` | Vibe-coded. Simula um briefing escrito só em termos de produto. O agente decide a implementação e valida o fluxo funcional com dados fictícios. |
| `r` | Robusto. Modelagem explícita de permissões e limites de confiança, revisão técnica e testes dos controles relevantes. |

O perfil descreve como o lab foi produzido e revisado. Registre a dificuldade do exercício separadamente quando houver dados para estimá-la.

## Estrutura

Uma API única pode manter o código diretamente na raiz do lab, segundo a estrutura nativa da stack. Em um lab `ms-`, use `services/<service-name>/` para cada serviço próprio e deixe o Compose na raiz.

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
└── ms-sb-fintech-r-01/
    ├── README.md
    ├── compose.yaml
    └── services/
        ├── account-api/
        └── statement-worker/
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
| `rest/ms-sb-fintech-r-01` | Spring Boot na entrada | Fintech | R | 2 | Planejado |
| `rest/quarkus-fintech-r-01` | Quarkus | Fintech | R | 1 | Planejado |
| `rest/fast-shop-v-01` | FastAPI | Shop | V | 1 | Planejado |
| `graphql/nest-ecommerce-n-01` | NestJS | Ecommerce | N | 1 | Planejado |
| `grpc/go-inventory-n-01` | Go com grpc-go | Estoque | N | 1 | Planejado |
| `web/rails-shop-n-01` | Rails | Shop | N | 1 | Planejado |
| `databases/postgres-fintech-r-01` | PostgreSQL | Fintech | R | 0 | Planejado |
