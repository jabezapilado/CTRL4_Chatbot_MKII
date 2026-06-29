# from __future__ import annotations
# from pathlib import Path

# from flask import Flask, jsonify
# from flask_cors import CORS

# from .config import Config
# from .db import initialize_database
# from .auth import auth_bp
# from .routes import api_bp



# def create_app() -> Flask:
#     # app = Flask(__name__)
#     BASE_DIR = Path(__file__).resolve().parent.parent.parent

#     app = Flask(
#         __name__,
#         template_folder=str(BASE_DIR / "frontend" / "templates"),
#         static_folder=str(BASE_DIR / "frontend" / "static"),
#     )
    
#     app.config.from_object(Config())
#     CORS(app)
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(api_bp)

#     @app.errorhandler(404)
#     def not_found(_error):
#         return jsonify({"error": "Not found"}), 404

#     with app.app_context():
#         initialize_database()

#     return app

from __future__ import annotations
from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .db import initialize_database
from .auth import auth_bp
from .routes import api_bp


def create_app() -> Flask:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "frontend" / "templates"),
        static_folder=str(BASE_DIR / "frontend" / "static"),
    )

    app.config.from_object(Config())
    CORS(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Not found"}), 404

    with app.app_context():
        initialize_database()

    return app