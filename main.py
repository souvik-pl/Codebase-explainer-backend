from flask import Flask
from flask_cors import CORS

from api.upload_api import upload_bp


def create_app() -> Flask:
    flask_app = Flask(__name__)
    CORS(flask_app)

    flask_app.register_blueprint(upload_bp)

    return flask_app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
