# Mercearia da Praça

Aplicativo em Flask e SQLite para reservar produtos de uma mercearia fictícia e retirar na loja. A vitrine, o acompanhamento e o painel da equipe estão em português.

## Rodar com Docker

```bash
docker compose up --build
```

Abra [http://127.0.0.1:8083](http://127.0.0.1:8083). O banco fica no volume `shop-data`. O primeiro acesso ao banco carrega os produtos e as reservas de exemplo.

Para entrar em **Área da equipe**, use a senha local gerada pelo aplicativo. O comando abaixo a mostra no terminal com o serviço em execução.

```bash
docker compose exec shop flask --app app staff-access
```

Se quiser definir outra senha, exporte `STAFF_PASSWORD` antes de iniciar o Compose.

## Rodar com Python

Requer Python 3.12.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
flask --app app run --host 127.0.0.1 --port 8083
```

O banco local é criado em `instance/shop.sqlite3`. Em outro terminal com a mesma virtualenv ativa, use `flask --app app staff-access` para consultar a senha da equipe. Defina `SHOP_DATABASE` para usar outro arquivo SQLite.

## Experimentar os fluxos

1. Na vitrine, busque por **pão**, **hortifruti** ou um termo sem resultados. **Café da Vila** aparece esgotado.
2. Adicione produtos, confira as quantidades e o total, escolha um horário e revise a reserva. Após confirmar, guarde o código para consultar o pedido em **Acompanhar reserva**.
3. Em uma instalação nova, a única **Geleia de morango artesanal** está na reserva pendente `PRACA-EXEMPLO`. Tente escolhê-la na vitrine e veja o aviso de esgotamento. Acompanhe e cancele a reserva de exemplo para liberar a unidade.
4. Para testar o conflito após a revisão, abra duas sessões independentes, por exemplo uma janela comum e uma anônima. Com a geleia disponível, coloque a última unidade nas duas cestas e avance até a revisão. Confirme em uma janela e depois na outra. A segunda confirmação informa o esgotamento e mantém os demais itens, o nome, o contato e o horário se ainda houver vaga.
5. No painel da equipe, consulte as reservas agrupadas por horário. `PRACA-PREPARO` pode avançar para **Pronta** e depois **Retirada**. As reservas `PRACA-PRONTA`, `PRACA-RETIRADA` e `PRACA-CANCELADA` também ilustram os respectivos estados. Use **Estoque disponível** para ajustar as unidades que ainda podem ser reservadas.

O estoque e a vaga são separados na confirmação. Cancelar uma reserva pendente libera os itens e a vaga. Cada horário aceita até quatro reservas.
