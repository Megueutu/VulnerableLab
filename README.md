# VulnerableLab

Catálogo de ambientes locais para estudar segurança de APIs.

## Início rápido

Use Git com `git subtree`, GNU Make e Docker com o plugin Compose. No Windows, os comandos do Makefile usam um shell POSIX, como no WSL.

Importe o crAPI uma vez em um clone limpo, a partir da raiz do repositório:

```sh
git subtree add --prefix=labs/rest/crapi https://github.com/OWASP/crAPI.git v1.1.6 --squash
```

```sh
make list
make up LAB=rest/crapi
make status LAB=rest/crapi
make logs LAB=rest/crapi
make down LAB=rest/crapi
```

O crAPI é o lab padrão. O Makefile configura o bind em `127.0.0.1`. A interface fica em <http://127.0.0.1:8888>.

Quando o subtree for publicado, um clone normal já trará os arquivos. Para atualizar depois, use `git subtree pull` com o mesmo prefixo e upstream e a nova tag. Atualize também a versão das imagens no script de inicialização. Preserve os commits do subtree ao integrar a importação.

## Catálogo

| Lab ou proposta | Tipo | Framework | O que comparar | Estado |
|---|---|---|---|---|
| `rest/crapi` | REST | Múltiplas stacks | Fronteiras entre serviços | Importação inicial via subtree |
| `rest/pedidos-java` | REST | Spring Boot | Filtros e autorização por recurso | Planejado |
| `rest/pedidos-python` | REST | FastAPI | Dependências de autenticação e validação | Planejado |
| `graphql/pedidos` | GraphQL | NestJS | Resolvers e autorização por campo | Planejado |
| `grpc/estoque` | gRPC | Go com grpc-go | Interceptores e contratos Protobuf | Planejado |

Comparar a mesma API REST em Spring Boot e FastAPI ajuda a observar o efeito do framework. Depois, comparar REST, GraphQL e gRPC mostra como o contrato e a unidade de autorização mudam. Autenticação, autorização e validação continuam relevantes em todos.

Cada lab novo fica em `labs/<tipo>/<nome>/`, com um `compose.yaml` para execução local e um `README.md` com framework, contrato, endereço local e instruções específicas. Mantenha arquivos de upstream intactos dentro do subtree.
