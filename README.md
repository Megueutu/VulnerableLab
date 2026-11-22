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

## Labs próprios

```sh
make up LAB=rest/python-shop-n-01
make up LAB=rest/fintech-r-01
```

## Catálogo

Consulte o [handoff dos labs](docs/lab-handoff.md) para ver os identificadores, as stacks, os perfis e as instruções para criar e entregar um lab.
