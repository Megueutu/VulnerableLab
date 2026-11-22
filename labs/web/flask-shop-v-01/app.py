import hmac
import os
import re
import secrets
import sqlite3
import unicodedata
from datetime import datetime, timedelta
from functools import wraps
from itertools import groupby
from pathlib import Path
from zoneinfo import ZoneInfo

import click
from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for


APP_ROOT = Path(__file__).resolve().parent
STORE_TZ = ZoneInfo("America/Sao_Paulo")
STORE_ADDRESS = "Praça das Flores, 42 · Vila Nova, São Paulo – SP"
CATEGORIES = ("Hortifruti", "Padaria", "Frios e laticínios", "Mercearia")
STATUS = {
    "pending": "Pendente",
    "preparing": "Em preparo",
    "ready": "Pronta",
    "collected": "Retirada",
    "cancelled": "Cancelada",
}
NEXT_STATUS = {"pending": "preparing", "preparing": "ready", "ready": "collected"}
WEEKDAYS = ("segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo")
PRODUCTS = [
    ("Banana-prata", "Hortifruti", "Madura e docinha, direto da banca.", "1 kg", "🍌", "yellow", 690, 16),
    ("Tomate italiano", "Hortifruti", "Firme e suculento para molhos e saladas.", "500 g", "🍅", "pink", 560, 12),
    ("Abacate manteiga", "Hortifruti", "Polpa cremosa, ótimo para vitaminas.", "unidade", "🥑", "green", 790, 8),
    ("Pão da praça", "Padaria", "Pão de fermentação natural, casca crocante.", "400 g", "🍞", "ochre", 1490, 9),
    ("Pão de queijo", "Padaria", "Feito com queijo meia-cura.", "6 unidades", "🧀", "yellow", 1190, 10),
    ("Geleia de morango artesanal", "Mercearia", "Pote de um pequeno produtor do bairro.", "200 g", "🍓", "pink", 1890, 1),
    ("Queijo minas frescal", "Frios e laticínios", "Leve e macio, para qualquer hora.", "350 g", "🧀", "ochre", 2190, 6),
    ("Iogurte natural", "Frios e laticínios", "Tradicional, sem adição de açúcar.", "170 g", "🥛", "blue", 390, 14),
    ("Café da Vila", "Mercearia", "Café moído de torra média.", "250 g", "☕", "ochre", 2390, 0),
    ("Laranja-pera", "Hortifruti", "Fresca, doce e cheia de suco.", "1 kg", "🍊", "yellow", 720, 11),
    ("Ovos caipiras", "Mercearia", "Ovos frescos de produção local.", "6 unidades", "🥚", "blue", 1090, 7),
    ("Manteiga com sal", "Frios e laticínios", "Cremosa, feita com creme de leite.", "200 g", "🧈", "green", 1690, 5),
]

app = Flask(__name__)
app.config.update(
    DATABASE=os.environ.get("SHOP_DATABASE") or str(Path(app.instance_path) / "shop.sqlite3"),
    MAX_CONTENT_LENGTH=32 * 1024,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("SHOP_HTTPS") == "1",
)


def get_db():
    if "db" not in g:
        db = sqlite3.connect(app.config["DATABASE"], timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        g.db = db
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def local_now():
    return datetime.now(STORE_TZ)


def create_slots(db, now):
    slots = []
    for days_ahead in range(8):
        day = now.date() + timedelta(days=days_ahead)
        for hour in (9, 11, 14, 16, 18):
            start = datetime.combine(day, datetime.min.time(), STORE_TZ).replace(hour=hour)
            if start > now:
                slots.append((start.isoformat(timespec="minutes"), 4))
    db.executemany("INSERT OR IGNORE INTO pickup_slots VALUES (?, ?)", slots)
    return [start for start, _ in slots]


def initialize():
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    db = get_db()
    db.executescript((APP_ROOT / "schema.sql").read_text(encoding="utf-8"))
    now = local_now()
    with db:
        db.execute("BEGIN IMMEDIATE")
        for key, value in (("session_key", secrets.token_hex(32)), ("staff_password", secrets.token_urlsafe(18))):
            db.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)", (key, value))
        if db.execute("SELECT 1 FROM settings WHERE name = 'seeded'").fetchone():
            return
        db.executemany(
            """INSERT INTO products (name, category, description, measure, icon, tone, price_cents, stock)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            PRODUCTS,
        )
        slots = create_slots(db, now)
        examples = [
            ("PRACA-EXEMPLO", "Ana Lima", "ana@example.com", "pending", slots[0], [(6, 1)]),
            ("PRACA-PREPARO", "Rafael Sá", "rafael@example.com", "preparing", slots[0], [(2, 2)]),
            ("PRACA-PRONTA", "Júlia Rosa", "julia@example.com", "ready", slots[1], [(4, 1), (8, 2)]),
            ("PRACA-RETIRADA", "Lia Ramos", "lia@example.com", "collected", slots[2], [(3, 1)]),
            ("PRACA-CANCELADA", "Ivo Reis", "ivo@example.com", "cancelled", slots[2], [(1, 2)]),
        ]
        for code, customer, contact, status, starts_at, quantities in examples:
            db.execute(
                "INSERT INTO reservations VALUES (?, ?, ?, ?, ?, ?, ?)",
                (code, code, customer, contact, starts_at, status, now.isoformat()),
            )
            for product_id, quantity in quantities:
                product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
                record_item(db, code, product, quantity, release=status == "cancelled")
        db.execute("INSERT INTO settings VALUES ('seeded', '1')")


def record_item(db, code, product, quantity, *, release=False):
    db.execute(
        "INSERT INTO reservation_items VALUES (?, ?, ?, ?, ?)",
        (code, product["id"], product["name"], quantity, product["price_cents"]),
    )
    if not release:
        db.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product["id"]))


def setting(name):
    return get_db().execute("SELECT value FROM settings WHERE name = ?", (name,)).fetchone()["value"]


with app.app_context():
    initialize()
    app.secret_key = os.environ.get("SHOP_SECRET_KEY") or setting("session_key")


@app.cli.command("staff-access")
def staff_access():
    """Show the password for the fictitious shop's staff dashboard."""
    click.echo(os.environ.get("STAFF_PASSWORD") or setting("staff_password"))


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(24)
    return session["csrf"]


@app.before_request
def check_post():
    if request.method == "POST":
        token = session.get("csrf", "")
        submitted = request.form.get("csrf", "")
        if not token or not hmac.compare_digest(token.encode(), submitted.encode()):
            abort(400, "A sessão do formulário expirou. Volte à página e tente novamente.")


@app.context_processor
def template_defaults():
    return {
        "csrf_token": csrf_token,
        "cart_count": sum(session.get("cart", {}).values()),
        "store_address": STORE_ADDRESS,
        "status_label": STATUS,
    }


@app.template_filter("money")
def money(cents):
    whole, fraction = divmod(cents, 100)
    return f"R$ {whole:,}".replace(",", ".") + f",{fraction:02}"


@app.template_filter("pickup_day")
def pickup_day(value):
    date = datetime.fromisoformat(value)
    return f"{WEEKDAYS[date.weekday()].capitalize()}, {date:%d/%m}"


@app.template_filter("pickup_time")
def pickup_time(value):
    return datetime.fromisoformat(value).strftime("%H:%M")


def search_key(value):
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def cart_lines(db):
    cart = {int(product_id): quantity for product_id, quantity in session.get("cart", {}).items()}
    if not cart:
        return []
    placeholders = ",".join("?" for _ in cart)
    products = db.execute(f"SELECT * FROM products WHERE id IN ({placeholders}) ORDER BY id", tuple(cart))
    return [
        dict(product, quantity=cart[product["id"]], subtotal=cart[product["id"]] * product["price_cents"])
        for product in products
    ]


def cart_total(lines):
    return sum(line["subtotal"] for line in lines)


def stock_errors(lines):
    errors = []
    for line in lines:
        if line["quantity"] <= line["stock"]:
            continue
        if line["stock"] == 0:
            errors.append(f'{line["name"]} está esgotado. Remova o item para continuar.')
        else:
            errors.append(
                f'{line["name"]} tem {line["stock"]} unidade(s) disponível(is). Ajuste a quantidade para continuar.'
            )
    return errors


def save_cart(cart):
    session["cart"] = cart
    session.pop("draft_key", None)


@app.get("/")
def catalog():
    search = request.args.get("q", "").strip()
    category = request.args.get("categoria", "")
    products = [
        dict(product)
        for product in get_db().execute("SELECT * FROM products ORDER BY id")
        if (not category or product["category"] == category)
        and search_key(search) in search_key(f"{product['name']} {product['category']}")
    ]
    lines = cart_lines(get_db())
    return render_template(
        "catalog.html", products=products, search=search, category=category, categories=CATEGORIES,
        lines=lines, total=cart_total(lines), reserved=session.get("cart", {}),
    )


@app.post("/cesta/adicionar/<int:product_id>")
def add_product(product_id):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        abort(404)
    quantity = request.form.get("quantity", type=int)
    cart = session.get("cart", {}).copy()
    key = str(product_id)
    if quantity is None or quantity < 1:
        flash("Escolha uma quantidade a partir de 1.", "error")
    elif not product["stock"]:
        flash(f'{product["name"]} está esgotado.', "error")
    elif quantity + cart.get(key, 0) > min(product["stock"], 99):
        flash(f'Você pode colocar até {min(product["stock"], 99)} unidade(s) de {product["name"]} na cesta.', "error")
    else:
        cart[key] = cart.get(key, 0) + quantity
        save_cart(cart)
        flash(f'{product["name"]} entrou na sua cesta.', "success")
    return redirect(
        url_for("catalog", q=request.form.get("q") or None, categoria=request.form.get("categoria") or None, _anchor=f"produto-{product_id}"),
        code=303,
    )


@app.route("/cesta", methods=["GET", "POST"])
def basket():
    db = get_db()
    lines = cart_lines(db)
    errors = []
    if request.method == "POST":
        cart = session.get("cart", {}).copy()
        remove = request.form.get("remove", "")
        for line in lines:
            key = str(line["id"])
            if remove == key:
                cart.pop(key, None)
                continue
            quantity = request.form.get(f"quantity_{key}", type=int)
            if quantity is None or not 0 <= quantity <= 99:
                errors.append(f'Escolha uma quantidade de 0 a 99 para {line["name"]}.')
            elif not quantity:
                cart.pop(key, None)
            elif quantity > line["stock"]:
                errors.append(f'{line["name"]} tem {line["stock"]} unidade(s) disponível(is).')
            else:
                cart[key] = quantity
        save_cart(cart)
        if not errors:
            destination = "checkout" if cart and request.form.get("continue") else "basket"
            return redirect(url_for(destination), code=303)
        lines = cart_lines(db)
    errors.extend(error for error in stock_errors(lines) if error not in errors)
    return render_template("basket.html", lines=lines, total=cart_total(lines), errors=errors)


def load_slots(db):
    now = local_now()
    with db:
        create_slots(db, now)
    return db.execute(
        """SELECT pickup_slots.*, COUNT(reservations.code) AS occupied
           FROM pickup_slots
           LEFT JOIN reservations ON reservations.starts_at = pickup_slots.starts_at
             AND reservations.status != 'cancelled'
           WHERE pickup_slots.starts_at > ?
           GROUP BY pickup_slots.starts_at
           ORDER BY pickup_slots.starts_at""",
        (now.isoformat(timespec="minutes"),),
    ).fetchall()


def slot_available(db, starts_at):
    if not starts_at or starts_at <= local_now().isoformat(timespec="minutes"):
        return False
    slot = db.execute(
        """SELECT capacity, COUNT(reservations.code) AS occupied
           FROM pickup_slots LEFT JOIN reservations
             ON reservations.starts_at = pickup_slots.starts_at AND reservations.status != 'cancelled'
           WHERE pickup_slots.starts_at = ?
           GROUP BY pickup_slots.starts_at""",
        (starts_at,),
    ).fetchone()
    return bool(slot and slot["occupied"] < slot["capacity"])


def contact_valid(value):
    if re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
        return True
    return bool(re.fullmatch(r"[+() .0-9-]+", value) and 10 <= len(re.sub(r"\D", "", value)) <= 15)


def checkout_errors(db, details, lines):
    errors = {}
    if not 2 <= len(details.get("name", "")) <= 100:
        errors["name"] = "Informe o seu nome (de 2 a 100 caracteres)."
    contact = details.get("contact", "")
    if not contact or len(contact) > 120 or not contact_valid(contact):
        errors["contact"] = "Informe um e-mail ou telefone válido com DDD."
    if not details.get("slot"):
        errors["slot"] = "Escolha um horário de retirada."
    elif not slot_available(db, details["slot"]):
        errors["slot"] = "Este horário ficou indisponível. Escolha outro horário."
    if not lines:
        errors["cart"] = "Adicione um produto para fazer a reserva."
    else:
        for index, error in enumerate(stock_errors(lines)):
            errors[f"cart_{index}"] = error
    return errors


def render_checkout(db, details, lines, errors, status=200):
    slots = load_slots(db)
    return render_template(
        "checkout.html", details=details, lines=lines, total=cart_total(lines), errors=errors, slots=slots,
        chosen_slot_shown=any(slot["starts_at"] == details.get("slot") for slot in slots),
    ), status


@app.route("/reserva", methods=["GET", "POST"])
def checkout():
    db = get_db()
    lines = cart_lines(db)
    if not lines:
        return redirect(url_for("basket"))
    details = session.get("details", {})
    errors = {}
    if request.method == "POST":
        details = {
            key: request.form.get(key, "").strip()[: maximum + 1]
            for key, maximum in (("name", 100), ("contact", 120), ("slot", 25))
        }
        session["details"] = details
        session.pop("draft_key", None)
        errors = checkout_errors(db, details, lines)
        if not errors:
            session["draft_key"] = secrets.token_hex(16)
            return redirect(url_for("review"), code=303)
    return render_checkout(db, details, lines, errors, 422 if errors else 200)


@app.get("/reserva/revisar")
def review():
    if not session.get("draft_key"):
        return redirect(url_for("checkout"))
    db = get_db()
    lines = cart_lines(db)
    details = session.get("details", {})
    errors = checkout_errors(db, details, lines)
    if errors:
        return render_checkout(db, details, lines, errors, 409)
    return render_template("review.html", lines=lines, total=cart_total(lines), details=details)


@app.post("/reserva/confirmar")
def confirm():
    draft_key = request.form.get("draft_key", "")
    code = None
    db = get_db()
    details = session.get("details", {})
    with db:
        db.execute("BEGIN IMMEDIATE")
        previous = db.execute("SELECT code FROM reservations WHERE draft_key = ?", (draft_key,)).fetchone()
        if previous and draft_key and draft_key in (session.get("draft_key"), session.get("confirmed_key")):
            return redirect(url_for("reservation", code=previous["code"]), code=303)
        if not draft_key or draft_key != session.get("draft_key"):
            return redirect(url_for("checkout"), code=303)
        lines = cart_lines(db)
        errors = checkout_errors(db, details, lines)
        if not errors:
            code = f"PRACA-{secrets.token_hex(7).upper()}"
            while db.execute("SELECT 1 FROM reservations WHERE code = ?", (code,)).fetchone():
                code = f"PRACA-{secrets.token_hex(7).upper()}"
            db.execute(
                "INSERT INTO reservations VALUES (?, ?, ?, ?, ?, 'pending', ?)",
                (code, draft_key, details["name"], details["contact"], details["slot"], local_now().isoformat()),
            )
            for line in lines:
                record_item(db, code, line, line["quantity"])
    if errors:
        return render_checkout(db, details, lines, errors, 409)
    save_cart({})
    session.pop("details", None)
    session["confirmed_key"] = draft_key
    flash("Reserva confirmada. Guarde o código para acompanhar a retirada.", "success")
    return redirect(url_for("reservation", code=code), code=303)


def get_reservation(code, db):
    record = db.execute("SELECT * FROM reservations WHERE code = ?", (code,)).fetchone()
    if record is None:
        abort(404, "Confira se o código da reserva foi digitado corretamente.")
    return record


def reservation_lines(code, db):
    return db.execute(
        """SELECT *, quantity * unit_price_cents AS subtotal
           FROM reservation_items WHERE reservation_code = ? ORDER BY product_id""",
        (code,),
    ).fetchall()


@app.route("/acompanhar", methods=["GET", "POST"])
def tracking():
    error = None
    code = ""
    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()[:32]
        existing = get_db().execute("SELECT 1 FROM reservations WHERE code = ?", (code,)).fetchone()
        if existing:
            return redirect(url_for("reservation", code=code), code=303)
        error = "Reserva não encontrada. Confira o código e tente novamente."
    return render_template("tracking.html", error=error, code=code), 404 if error else 200


@app.get("/reservas/<code>")
def reservation(code):
    db = get_db()
    record = get_reservation(code, db)
    lines = reservation_lines(record["code"], db)
    return render_template("reservation.html", reservation=record, lines=lines, total=cart_total(lines))


@app.post("/reservas/<code>/cancelar")
def cancel(code):
    db = get_db()
    with db:
        db.execute("BEGIN IMMEDIATE")
        record = get_reservation(code, db)
        if record["status"] == "pending":
            db.execute("UPDATE reservations SET status = 'cancelled' WHERE code = ?", (code,))
            for item in reservation_lines(code, db):
                db.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (item["quantity"], item["product_id"]))
            flash("Reserva cancelada.", "success")
        else:
            flash("Só é possível cancelar reservas pendentes.", "error")
    return redirect(url_for("reservation", code=code), code=303)


def staff_required(view):
    @wraps(view)
    def decorated(*args, **kwargs):
        if not session.get("staff"):
            return redirect(url_for("staff_login"))
        return view(*args, **kwargs)

    return decorated


@app.route("/equipe/entrar", methods=["GET", "POST"])
def staff_login():
    if session.get("staff"):
        return redirect(url_for("staff"))
    error = None
    if request.method == "POST":
        password = os.environ.get("STAFF_PASSWORD") or setting("staff_password")
        if hmac.compare_digest(request.form.get("password", "").encode(), password.encode()):
            session["staff"] = True
            session.pop("csrf", None)
            return redirect(url_for("staff"), code=303)
        error = "Senha incorreta."
    return render_template("staff_login.html", error=error), 401 if error else 200


@app.post("/equipe/sair")
@staff_required
def staff_logout():
    session.pop("staff", None)
    session.pop("csrf", None)
    return redirect(url_for("catalog"), code=303)


@app.get("/equipe")
@staff_required
def staff():
    db = get_db()
    orders = db.execute("SELECT * FROM reservations ORDER BY starts_at, created_at, code").fetchall()
    products = db.execute("SELECT * FROM products ORDER BY category, name").fetchall()
    grouped = [
        (time, [(order, reservation_lines(order["code"], db)) for order in reservations])
        for time, reservations in groupby(orders, key=lambda order: order["starts_at"])
    ]
    return render_template("staff.html", groups=grouped, products=products, next_status=NEXT_STATUS)


@app.post("/equipe/reservas/<code>/status")
@staff_required
def update_status(code):
    db = get_db()
    with db:
        db.execute("BEGIN IMMEDIATE")
        record = get_reservation(code, db)
        next_value = NEXT_STATUS.get(record["status"])
        if next_value and request.form.get("status") == next_value:
            db.execute("UPDATE reservations SET status = ? WHERE code = ?", (next_value, code))
            flash(f'Reserva {code}: {STATUS[next_value].lower()}.', "success")
        else:
            flash("O status já mudou. Confira a situação atual da reserva.", "error")
    return redirect(url_for("staff", _anchor="reservas"), code=303)


@app.post("/equipe/produtos/<int:product_id>/estoque")
@staff_required
def update_stock(product_id):
    db = get_db()
    stock = request.form.get("stock", type=int)
    if stock is None or not 0 <= stock <= 999:
        flash("Informe um estoque disponível de 0 a 999 unidades.", "error")
    else:
        expected = request.form.get("current_stock", type=int)
        with db:
            db.execute("BEGIN IMMEDIATE")
            product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            if product is None:
                abort(404)
            if product["stock"] != expected:
                flash("O estoque mudou desde a abertura da página. Confira a quantidade e tente novamente.", "error")
            else:
                db.execute("UPDATE products SET stock = ? WHERE id = ?", (stock, product_id))
                flash(f'Estoque de {product["name"]} atualizado.', "success")
    return redirect(url_for("staff", _anchor="estoque"), code=303)


@app.errorhandler(400)
@app.errorhandler(404)
def friendly_error(error):
    return render_template("error.html", error=error), error.code
