from __future__ import annotations

from server import create_app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=app.config.get("PORT", 5001),
        debug=app.config.get("DEBUG", True),
        use_reloader=False,
    )