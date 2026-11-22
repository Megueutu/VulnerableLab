# Volunteer shift board

A fictional repair café coordinates volunteer shifts through a server-rendered board. The app uses Python's standard library HTTP server, HTML forms, and CSS.

## Run locally

Run this command from the lab directory.

```sh
docker compose up --build -d
```

Open <http://127.0.0.1:8084>. To stop the board, run `docker compose down`. For a local run without containers, use Python 3.13 and execute `python app.py` from this directory.

## Try the board

1. Reserve **Welcome desk**. The board confirms the reservation and labels the shift **Your shift**.
2. Open the same address in a private window. The shift appears as **Reserved** there.
3. Return to the first window and release the shift. Refresh the private window to see it available again.

The app keeps reservations in memory and resets them on restart. Reservations belong to the browser session. Use the same address throughout the walkthrough, since `localhost` and `127.0.0.1` have separate cookies.

## Form contract

| Request | Behavior |
|---|---|
| `GET /` | Renders the board and issues a signed session cookie when needed. |
| `POST /shifts` | Accepts the shift identifier, action, and session-bound form token as URL-encoded fields. |
| `GET /board.css` | Serves the board stylesheet. |

The server checks form length and fields before applying a change. The browser receives a redirect to the board after a valid submission. The server checks reservation ownership and serializes changes under a lock. The cookie is `HttpOnly` and `SameSite=Strict`, and the app serves plain HTTP on the loopback interface.
