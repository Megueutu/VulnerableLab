"""A volunteer shift board for a fictional neighborhood repair café."""

from dataclasses import dataclass
from hashlib import sha256
from hmac import compare_digest, digest
from html import escape
from http import HTTPStatus
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs
import os
import secrets
import string


@dataclass
class Shift:
    title: str
    time: str
    activity: str
    owner: str | None = None


SHIFTS = {
    "welcome": Shift("Welcome desk", "09:00–10:30", "Greet visitors and write repair tickets."),
    "tools": Shift("Tool table", "10:30–12:00", "Check shared tools in and out.", "staff"),
    "sorting": Shift("Parts sorting", "12:00–13:30", "Sort donated parts into labeled bins."),
}
SHIFTS_LOCK = Lock()
SESSION_COOKIE = "shift_session"
SIGNING_KEY = secrets.token_bytes(32)
SESSION_ID_LENGTH = 48
STYLE = Path(__file__).with_name("board.css").read_bytes()
NOTICES = {
    "reserved": "Shift reserved.",
    "released": "Shift released.",
    "unavailable": "That shift is already reserved.",
    "not-yours": "Only the browser that reserved a shift can release it.",
}


def sign(purpose, session_id):
    return digest(SIGNING_KEY, f"{purpose}:{session_id}".encode("ascii"), sha256).hex()


def get_session_id(cookie_header):
    cookies = SimpleCookie()
    try:
        cookies.load(cookie_header)
    except CookieError:
        return None

    cookie = cookies.get(SESSION_COOKIE)
    if cookie is None:
        return None

    session_id, separator, signature = cookie.value.partition(".")
    if not separator or len(session_id) != SESSION_ID_LENGTH or len(signature) != 64:
        return None
    if any(character not in string.hexdigits for character in session_id + signature):
        return None
    if compare_digest(signature, sign("session", session_id)):
        return session_id
    return None


def render_board(session_id, notice):
    csrf = sign("form", session_id)
    with SHIFTS_LOCK:
        rows = [(key, shift.title, shift.time, shift.activity, shift.owner)
                for key, shift in SHIFTS.items()]

    cards = []
    for key, title, time, activity, owner in rows:
        form = ""
        if owner is None:
            badge, label = "open", "Open"
            action, button = "reserve", "Reserve shift"
        elif owner == session_id:
            badge, label = "yours", "Your shift"
            action, button = "release", "Release shift"
        else:
            badge, label = "taken", "Reserved"
            action = None

        if action is not None:
            form = f"""
              <form method="post" action="/shifts">
                <input type="hidden" name="shift" value="{escape(key)}">
                <input type="hidden" name="csrf" value="{escape(csrf)}">
                <button class="{action}" name="action" value="{action}"
                        aria-label="{button}: {escape(title)}">{button}</button>
              </form>"""

        cards.append(f"""
          <article class="shift">
            <div class="shift-meta">
              <span>{escape(time)}</span>
              <span class="badge {badge}">{label}</span>
            </div>
            <h2>{escape(title)}</h2>
            <p>{escape(activity)}</p>
            {form}
          </article>""")

    feedback = f'<p class="notice" role="status">{escape(notice)}</p>' if notice else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Volunteer shift board | Maple Street Repair Café</title>
  <link rel="stylesheet" href="/board.css">
</head>
<body>
  <main>
    <header>
      <p class="event">Maple Street Repair Café</p>
      <h1>Volunteer shift board</h1>
      <p>Choose a shift for the next community repair session.</p>
    </header>
    {feedback}
    <section class="shifts" aria-label="Volunteer shifts">
      {"".join(cards)}
    </section>
  </main>
</body>
</html>
""".encode("utf-8")


class ShiftBoardHandler(BaseHTTPRequestHandler):
    server_version = "ShiftBoard/1.0"
    sys_version = ""

    def local_host(self):
        port = self.server.server_port
        expected = {f"127.0.0.1:{port}", f"localhost:{port}"}
        hosts = self.headers.get_all("Host", [])
        return len(hosts) == 1 and hosts[0] in expected

    def reply(self, status, body=b"", content_type="text/plain; charset=utf-8",
              headers=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; style-src 'self'; form-action 'self'; "
                         "base-uri 'none'; frame-ancestors 'none'")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self.local_host():
            self.reply(HTTPStatus.BAD_REQUEST, b"Use the local board address.\n")
            return

        path, _, query = self.path.partition("?")
        if path == "/board.css":
            self.reply(HTTPStatus.OK, STYLE, "text/css; charset=utf-8")
            return
        if path != "/":
            self.reply(HTTPStatus.NOT_FOUND, b"Page not found.\n")
            return

        session_id = get_session_id(self.headers.get("Cookie", ""))
        headers = {}
        if session_id is None:
            session_id = secrets.token_hex(SESSION_ID_LENGTH // 2)
            value = f'{session_id}.{sign("session", session_id)}'
            headers["Set-Cookie"] = f"{SESSION_COOKIE}={value}; Path=/; HttpOnly; SameSite=Strict"

        notice = NOTICES.get(query.removeprefix("notice="), "")
        self.reply(HTTPStatus.OK, render_board(session_id, notice),
                   "text/html; charset=utf-8", headers)

    def do_POST(self):
        if not self.local_host():
            self.reply(HTTPStatus.BAD_REQUEST, b"Use the local board address.\n")
            return
        if self.path != "/shifts":
            self.reply(HTTPStatus.NOT_FOUND, b"Page not found.\n")
            return
        if self.headers.get_content_type() != "application/x-www-form-urlencoded":
            self.reply(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, b"Use the shift board form.\n")
            return

        lengths = self.headers.get_all("Content-Length", [])
        if (len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit()
                or len(lengths[0]) > 4 or self.headers.get("Transfer-Encoding") is not None):
            self.reply(HTTPStatus.BAD_REQUEST, b"Invalid form body length.\n")
            return
        length = int(lengths[0])
        if length > 1024:
            self.reply(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, b"Form exceeds 1024 bytes.\n")
            return

        body = self.rfile.read(length)
        if len(body) != length:
            self.reply(HTTPStatus.BAD_REQUEST, b"Incomplete form body.\n")
            return

        try:
            fields = parse_qs(body.decode("ascii"),
                              strict_parsing=True, errors="strict", max_num_fields=3)
        except ValueError:
            self.reply(HTTPStatus.BAD_REQUEST, b"Invalid form body.\n")
            return
        if set(fields) != {"shift", "csrf", "action"} or any(
                len(values) != 1 for values in fields.values()):
            self.reply(HTTPStatus.BAD_REQUEST, b"Invalid form fields.\n")
            return

        session_id = get_session_id(self.headers.get("Cookie", ""))
        csrf = fields["csrf"][0]
        if session_id is None or not csrf.isascii() or not compare_digest(
                csrf, sign("form", session_id)):
            self.reply(HTTPStatus.FORBIDDEN, b"Open the shift board and try again.\n")
            return

        key = fields["shift"][0]
        action = fields["action"][0]
        if key not in SHIFTS or action not in {"reserve", "release"}:
            self.reply(HTTPStatus.BAD_REQUEST, b"Unknown shift or action.\n")
            return

        with SHIFTS_LOCK:
            shift = SHIFTS[key]
            if action == "reserve":
                if shift.owner in (None, session_id):
                    shift.owner = session_id
                    notice = "reserved"
                else:
                    notice = "unavailable"
            elif shift.owner == session_id:
                shift.owner = None
                notice = "released"
            else:
                notice = "not-yours"

        self.reply(HTTPStatus.SEE_OTHER, headers={"Location": f"/?notice={notice}"})


if __name__ == "__main__":
    host = os.environ.get("SHIFT_BOARD_HOST", "127.0.0.1")
    with ThreadingHTTPServer((host, 8084), ShiftBoardHandler) as server:
        print("Volunteer shift board listening on port 8084", flush=True)
        server.serve_forever()
