"""Small stateless service for exercising delivery and recovery."""
import os
from flask import Flask, jsonify

def create_app():
    app = Flask(__name__)

    @app.get("/")
    def index():
        return jsonify(service="core-api", version=os.getenv("APP_VERSION", "development"))

    @app.get("/healthz")
    def health():
        return jsonify(status="ok")

    @app.get("/readyz")
    def ready():
        return jsonify(status="ready")

    @app.errorhandler(404)
    def missing(_error):
        return jsonify(error="not_found"), 404

    return app

app = create_app()
